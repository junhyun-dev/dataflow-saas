"""
Excel Loader - 파일 읽기만 담당

책임:
- 파일 열기 (로컬)
- 시트 목록 조회
- 시트를 raw DataFrame으로 반환

하지 않는 것:
- 헤더 처리
- 데이터 변환
- Config 해석
"""

import re
from pathlib import Path
from typing import Optional

import pandas as pd


class ExcelLoader:
    """Excel 파일 로더"""

    def __init__(self, engine: str = "openpyxl"):
        """
        Args:
            engine: pandas read_excel 엔진 (openpyxl, xlrd)
        """
        self.engine = engine
        self._file_path: Optional[Path] = None
        self._excel_file: Optional[pd.ExcelFile] = None

    def load(self, file_path: str | Path) -> "ExcelLoader":
        """파일 열기"""
        self._file_path = Path(file_path)

        if not self._file_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없음: {self._file_path}")

        self._excel_file = pd.ExcelFile(self._file_path, engine=self.engine)
        return self

    @property
    def sheet_names(self) -> list[str]:
        """전체 시트 목록"""
        if self._excel_file is None:
            raise RuntimeError("파일이 로드되지 않음. load()를 먼저 호출하세요.")
        return self._excel_file.sheet_names

    def filter_sheets(self, pattern: str) -> list[str]:
        """패턴과 매칭되는 시트만 반환"""
        regex = re.compile(pattern)
        return [name for name in self.sheet_names if regex.search(name)]

    def read_sheet(self, sheet_name: str) -> pd.DataFrame:
        """
        시트를 raw DataFrame으로 반환

        - header=None (헤더 처리 안 함)
        - 모든 셀을 그대로 읽음
        """
        if self._excel_file is None:
            raise RuntimeError("파일이 로드되지 않음. load()를 먼저 호출하세요.")

        return pd.read_excel(
            self._excel_file,
            sheet_name=sheet_name,
            header=None,  # 헤더 처리는 Parser에서
            dtype=object,  # 모든 셀을 object로 (타입 변환은 나중에)
        )

    def close(self):
        """리소스 해제"""
        if self._excel_file is not None:
            self._excel_file.close()
            self._excel_file = None

    def __enter__(self) -> "ExcelLoader":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
