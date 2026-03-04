"""
Table Parser - 테이블 파싱 담당

책임:
- 시작/종료 행 찾기
- 헤더 추출
- 본문 추출
- 타입 변환

하지 않는 것:
- 파일 I/O
- 결과 저장
"""

import logging
import re
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

from ..config.schema import TableConfig


class TableParser:
    """테이블 파서"""

    def __init__(self, config: TableConfig):
        self.config = config
        self._pattern_cache: dict[str, re.Pattern] = {}

    def parse(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        raw DataFrame → 정제된 DataFrame

        Steps:
        1. 시작 행 찾기
        2. 헤더 추출
        3. 종료 행 찾기
        4. 본문 추출
        5. 컬럼 필터링
        6. 타입 변환
        """
        # 1. 시작 행
        start_row = self._find_start_row(raw_df)

        # 2. 헤더 추출
        header_rows = self.config.rows.header_rows
        header = self._extract_header(raw_df, start_row, header_rows)

        # 3. 종료 행
        body_start = start_row + header_rows
        end_row = self._find_end_row(raw_df, body_start)

        # 4. 본문 추출
        body_df = raw_df.iloc[body_start:end_row].copy()
        body_df.columns = header

        # 5. 빈 행/컬럼 제거
        body_df = self._clean_dataframe(body_df)

        # 6. 컬럼 필터링
        if self.config.columns:
            existing_cols = [c for c in self.config.columns if c in body_df.columns]
            body_df = body_df[existing_cols]

        # 7. 타입 변환
        body_df = self._convert_types(body_df)

        # 인덱스 리셋
        body_df = body_df.reset_index(drop=True)

        return body_df

    def _find_start_row(self, df: pd.DataFrame) -> int:
        """시작 행 찾기"""
        start = self.config.rows.start

        if isinstance(start, int):
            return start

        # 패턴 매칭
        return self._find_row_by_pattern(df, start) or 0

    def _find_end_row(self, df: pd.DataFrame, start_from: int) -> Optional[int]:
        """종료 행 찾기"""
        end = self.config.rows.end

        if end is None:
            return len(df)

        if isinstance(end, int):
            return min(end, len(df))

        # 패턴 매칭
        found = self._find_row_by_pattern(df, end, start_from)
        return found if found else len(df)

    def _find_row_by_pattern(
        self,
        df: pd.DataFrame,
        pattern: str,
        start_from: int = 0
    ) -> Optional[int]:
        """패턴으로 행 찾기 (첫 번째 컬럼에서)"""
        regex = self._get_pattern(pattern)

        for idx in range(start_from, len(df)):
            cell_value = str(df.iloc[idx, 0]) if pd.notna(df.iloc[idx, 0]) else ""
            if regex.search(cell_value):
                return idx

        return None

    def _get_pattern(self, pattern: str) -> re.Pattern:
        """캐싱된 패턴 반환"""
        if pattern not in self._pattern_cache:
            self._pattern_cache[pattern] = re.compile(pattern)
        return self._pattern_cache[pattern]

    def _extract_header(
        self,
        df: pd.DataFrame,
        start_row: int,
        header_rows: int
    ) -> list[str]:
        """헤더 추출"""
        if header_rows == 1:
            # 단일 헤더
            header = df.iloc[start_row].tolist()
        else:
            # 멀티 헤더 (행들을 합침)
            headers = []
            for i in range(header_rows):
                row = df.iloc[start_row + i].tolist()
                headers.append(row)

            # 컬럼별로 합치기
            header = []
            for col_idx in range(len(headers[0])):
                parts = [str(h[col_idx]) for h in headers if pd.notna(h[col_idx])]
                header.append("_".join(parts) if parts else f"col_{col_idx}")

        # 빈 헤더 처리
        header = [
            str(h) if pd.notna(h) and str(h).strip() else f"col_{i}"
            for i, h in enumerate(header)
        ]

        # 중복 헤더 처리
        seen = {}
        result = []
        for h in header:
            if h in seen:
                seen[h] += 1
                result.append(f"{h}_{seen[h]}")
            else:
                seen[h] = 0
                result.append(h)

        return result

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """빈 행/컬럼 제거"""
        # 모든 값이 NaN인 행 제거
        df = df.dropna(how="all")

        # 모든 값이 NaN인 컬럼 제거
        df = df.dropna(axis=1, how="all")

        return df

    def _convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """타입 변환"""
        for col, dtype in self.config.column_types.items():
            if col not in df.columns:
                continue

            try:
                if dtype == "int":
                    df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
                elif dtype == "float":
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                elif dtype == "datetime":
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                elif dtype == "str":
                    df[col] = df[col].astype(str)
            except Exception as e:
                # 변환 실패 시 원본 유지하되, 로깅으로 기록
                logger.warning(
                    f"타입 변환 실패 - 컬럼: {col}, 타입: {dtype}, "
                    f"에러: {e}, 샘플값: {df[col].head(3).tolist()}"
                )

        return df
