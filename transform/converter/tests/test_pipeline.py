"""
Pipeline 테스트
"""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from ..config.schema import ConvertConfig, TableConfig, RowsConfig
from ..pipeline import Pipeline


@pytest.fixture
def sample_excel(tmp_path: Path) -> Path:
    """샘플 Excel 파일 생성"""
    file_path = tmp_path / "sample.xlsx"

    # 샘플 데이터
    df = pd.DataFrame({
        "이름": ["홍길동", "김철수", "이영희"],
        "나이": [30, 25, 28],
        "부서": ["개발팀", "마케팅팀", "개발팀"],
        "급여": [5000, 4000, 4500]
    })

    df.to_excel(file_path, index=False, sheet_name="직원목록")
    return file_path


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """출력 디렉토리"""
    out = tmp_path / "output"
    out.mkdir()
    return out


class TestPipeline:
    """Pipeline 테스트"""

    def test_simple_run(self, sample_excel: Path, output_dir: Path):
        """간단한 실행 테스트"""
        result = Pipeline.simple_run(sample_excel, output_dir)

        assert result.success_count >= 1
        assert result.fail_count == 0
        assert result.total_rows == 3

    def test_with_config(self, sample_excel: Path, output_dir: Path):
        """설정을 사용한 실행"""
        config = ConvertConfig(
            tables=[
                TableConfig(
                    name="employees",
                    sheet_pattern="직원.*",
                    columns=["이름", "부서"]
                )
            ]
        )

        pipeline = Pipeline(config, output_dir)
        result = pipeline.run(sample_excel)

        assert result.success_count == 1

        # 출력 파일 확인
        parquet_files = list(output_dir.glob("*.parquet"))
        assert len(parquet_files) == 1

        # 데이터 확인
        df = pd.read_parquet(parquet_files[0])
        assert list(df.columns) == ["이름", "부서"]
        assert len(df) == 3

    def test_file_not_found(self, output_dir: Path):
        """존재하지 않는 파일"""
        config = ConvertConfig.simple()
        pipeline = Pipeline(config, output_dir)

        with pytest.raises(FileNotFoundError):
            pipeline.run("not_exists.xlsx")


class TestConvertConfig:
    """Config 테스트"""

    def test_simple_config(self):
        """간단한 설정 생성"""
        config = ConvertConfig.simple("test_table")

        assert len(config.tables) == 1
        assert config.tables[0].name == "test_table"

    def test_rows_config(self):
        """행 설정"""
        rows = RowsConfig(start=1, end=10, header_rows=2)

        assert rows.start == 1
        assert rows.end == 10
        assert rows.header_rows == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
