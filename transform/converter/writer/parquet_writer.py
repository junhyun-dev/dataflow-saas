"""
Parquet Writer - 결과 저장 담당

책임:
- Parquet 출력
- 메타데이터 JSON

하지 않는 것:
- 데이터 변환
- CSV 출력 (deprecated)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd


class ParquetWriter:
    """Parquet 출력"""

    def __init__(
        self,
        output_dir: str | Path,
        compression: str = "zstd"
    ):
        """
        Args:
            output_dir: 출력 디렉토리
            compression: 압축 방식 (zstd, snappy, gzip, None)
        """
        self.output_dir = Path(output_dir)
        self.compression = compression

        # 출력 디렉토리 생성
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write(
        self,
        df: pd.DataFrame,
        name: str,
        metadata: Optional[dict] = None
    ) -> Path:
        """
        DataFrame을 Parquet으로 저장

        Args:
            df: 저장할 DataFrame
            name: 파일 이름 (확장자 제외)
            metadata: 추가 메타데이터

        Returns:
            저장된 파일 경로
        """
        output_path = self.output_dir / f"{name}.parquet"

        # Parquet 저장
        df.to_parquet(
            output_path,
            compression=self.compression,
            index=False
        )

        # 메타데이터 저장
        meta = self._build_metadata(df, name, metadata)
        meta_path = self.output_dir / f"{name}.meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2, default=str)

        return output_path

    def _build_metadata(
        self,
        df: pd.DataFrame,
        name: str,
        extra: Optional[dict] = None
    ) -> dict:
        """메타데이터 생성"""
        meta = {
            "name": name,
            "created_at": datetime.now().isoformat(),
            "rows": len(df),
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "compression": self.compression,
        }

        if extra:
            meta["extra"] = extra

        return meta
