"""
Excel Converter - Excel 파일을 Parquet으로 변환

구조:
    Pipeline (오케스트레이션)
    ├── ExcelLoader (I/O)
    ├── TableParser (변환)
    └── ParquetWriter (출력)
"""

from .pipeline import Pipeline
from .config.schema import ConvertConfig

__all__ = ["Pipeline", "ConvertConfig"]
