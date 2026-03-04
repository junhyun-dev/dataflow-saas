"""
Warehouse 설정

Pydantic 기반 설정 (Collector 패턴과 일관성 유지)
"""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DuckDBConfig(BaseModel):
    """DuckDB 설정"""

    model_config = ConfigDict(
        # Path 직렬화 지원 (Pydantic v2 방식)
        ser_json_bytes="utf8",
    )

    # 데이터베이스 경로 (None이면 in-memory)
    db_path: Optional[Path] = Field(
        default=None,
        description="DuckDB 파일 경로. None이면 in-memory (:memory:)",
    )

    # 읽기 전용 모드
    read_only: bool = Field(
        default=False,
        description="읽기 전용 모드로 열기",
    )

    # 스레드 수 (0 = auto)
    threads: int = Field(
        default=0,
        ge=0,
        description="사용할 스레드 수 (0 = 자동)",
    )

    # 메모리 제한
    memory_limit: Optional[str] = Field(
        default=None,
        description="메모리 제한 (예: '4GB')",
    )

    @property
    def connection_string(self) -> str:
        """연결 문자열 반환"""
        if self.db_path is None:
            return ":memory:"
        return str(self.db_path)
