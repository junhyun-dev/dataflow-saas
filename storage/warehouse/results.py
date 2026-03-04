"""
결과 객체

Collector의 CollectResult 패턴과 일관성 유지
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class InsertResult:
    """데이터 삽입 결과"""

    table: str
    rows_affected: int
    status: str  # "success" | "fail"

    # 메타데이터
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None
    errors: list[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None

    def finish(self, status: str = "success") -> "InsertResult":
        """완료 처리"""
        self.finished_at = datetime.now()
        self.status = status
        return self

    def add_error(self, error: str) -> None:
        self.errors.append(error)

    def to_dict(self) -> dict:
        return {
            "table": self.table,
            "rows_affected": self.rows_affected,
            "status": self.status,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration_seconds": self.duration_seconds,
            "errors": self.errors,
        }


@dataclass
class QueryResult:
    """쿼리 실행 결과"""

    columns: list[str]
    rows: list[tuple]
    row_count: int

    # 메타데이터
    query: str = ""
    execution_time_ms: Optional[float] = None

    def to_dataframe(self) -> "pd.DataFrame":
        """pandas DataFrame으로 변환"""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for to_dataframe(). "
                "Install with: pip install pandas"
            )
        return pd.DataFrame(self.rows, columns=self.columns)

    def to_dicts(self) -> list[dict]:
        """딕셔너리 리스트로 변환"""
        return [dict(zip(self.columns, row)) for row in self.rows]

    def __repr__(self) -> str:
        return f"QueryResult(columns={self.columns}, row_count={self.row_count})"
