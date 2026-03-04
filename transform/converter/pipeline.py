"""
Pipeline - 전체 흐름 오케스트레이션

책임:
- Loader, Parser, Writer 연결
- 시트/테이블 반복
- 에러 수집 및 결과 집계

하지 않는 것:
- 실제 파싱 로직
- 파일 I/O
- 데이터 변환
"""

import logging
import re
import traceback
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Literal, Optional

import pandas as pd

logger = logging.getLogger(__name__)

# 파일명에 사용할 수 없는 문자 패턴
_UNSAFE_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def _sanitize_filename(name: str) -> str:
    """파일명에 안전한 문자열로 변환"""
    # 특수문자를 언더스코어로 치환
    sanitized = _UNSAFE_FILENAME_CHARS.sub("_", name)
    # 연속 언더스코어 정리
    sanitized = re.sub(r"_+", "_", sanitized)
    # 앞뒤 언더스코어 제거
    return sanitized.strip("_")

from .config.schema import ConvertConfig, TableConfig
from .loader.excel_loader import ExcelLoader
from .parser.table_parser import TableParser
from .writer.parquet_writer import ParquetWriter


@dataclass
class ConvertResult:
    """단일 변환 결과"""
    status: Literal["success", "fail", "skip"]
    sheet: str
    table: str
    output: Optional[Path] = None
    error: Optional[str] = None
    rows_count: int = 0


@dataclass
class PipelineResult:
    """파이프라인 실행 결과"""
    file_path: str
    results: list[ConvertResult] = field(default_factory=list)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.status == "success")

    @property
    def fail_count(self) -> int:
        return sum(1 for r in self.results if r.status == "fail")

    @property
    def total_rows(self) -> int:
        return sum(r.rows_count for r in self.results)

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "status": "success" if self.fail_count == 0 else "partial",
            "total": len(self.results),
            "success": self.success_count,
            "fail": self.fail_count,
            "total_rows": self.total_rows,
            "results": [asdict(r) for r in self.results]
        }

    def __str__(self) -> str:
        return (
            f"PipelineResult({self.file_path}): "
            f"{self.success_count} success, {self.fail_count} fail, "
            f"{self.total_rows} rows"
        )


class Pipeline:
    """Excel → Parquet 변환 파이프라인"""

    def __init__(
        self,
        config: ConvertConfig,
        output_dir: str | Path
    ):
        """
        Args:
            config: 변환 설정
            output_dir: 출력 디렉토리
        """
        self.config = config
        self.output_dir = Path(output_dir)
        self.writer = ParquetWriter(output_dir)

    def run(self, file_path: str | Path) -> PipelineResult:
        """
        파이프라인 실행

        Args:
            file_path: 입력 Excel 파일 경로

        Returns:
            변환 결과
        """
        file_path = Path(file_path)
        result = PipelineResult(file_path=str(file_path))

        with ExcelLoader() as loader:
            loader.load(file_path)

            # 테이블 설정이 없으면 기본 설정 사용
            tables = self.config.tables or [
                TableConfig(name="default")
            ]

            for table_config in tables:
                # 시트 필터링
                sheet_pattern = (
                    table_config.sheet_pattern
                    or self.config.default_sheet_pattern
                )
                sheets = loader.filter_sheets(sheet_pattern)

                for sheet_name in sheets:
                    convert_result = self._process_sheet(
                        loader, sheet_name, table_config
                    )
                    result.results.append(convert_result)

        return result

    def _process_sheet(
        self,
        loader: ExcelLoader,
        sheet_name: str,
        table_config: TableConfig
    ) -> ConvertResult:
        """단일 시트 처리"""
        # 파일명에 안전한 문자열로 변환
        table_name = _sanitize_filename(f"{table_config.name}_{sheet_name}")

        try:
            # 1. 시트 읽기
            raw_df = loader.read_sheet(sheet_name)

            # 2. 파싱
            parser = TableParser(table_config)
            parsed_df = parser.parse(raw_df)

            # 빈 DataFrame 체크
            if parsed_df.empty:
                return ConvertResult(
                    status="skip",
                    sheet=sheet_name,
                    table=table_config.name,
                    error="빈 데이터"
                )

            # 3. 저장
            output_path = self.writer.write(
                parsed_df,
                table_name,
                metadata={
                    "source_sheet": sheet_name,
                    "table_config": table_config.model_dump()
                }
            )

            return ConvertResult(
                status="success",
                sheet=sheet_name,
                table=table_config.name,
                output=output_path,
                rows_count=len(parsed_df)
            )

        except (pd.errors.ParserError, pd.errors.EmptyDataError) as e:
            # 예상 가능한 파싱 에러
            logger.warning(f"파싱 에러 [{sheet_name}]: {e}")
            return ConvertResult(
                status="fail",
                sheet=sheet_name,
                table=table_config.name,
                error=f"파싱 에러: {e}"
            )
        except FileNotFoundError as e:
            logger.error(f"파일 없음 [{sheet_name}]: {e}")
            return ConvertResult(
                status="fail",
                sheet=sheet_name,
                table=table_config.name,
                error=f"파일 없음: {e}"
            )
        except Exception as e:
            # 예상치 못한 에러 - 전체 traceback 로깅
            logger.error(
                f"예상치 못한 에러 [{sheet_name}]: {e}\n"
                f"{traceback.format_exc()}"
            )
            return ConvertResult(
                status="fail",
                sheet=sheet_name,
                table=table_config.name,
                error=str(e)
            )

    @classmethod
    def simple_run(
        cls,
        file_path: str | Path,
        output_dir: str | Path
    ) -> PipelineResult:
        """
        간단한 실행 (기본 설정)

        사용법:
            result = Pipeline.simple_run("input.xlsx", "output/")
        """
        config = ConvertConfig.simple()
        pipeline = cls(config, output_dir)
        return pipeline.run(file_path)
