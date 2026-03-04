"""
BaseCollector - 추상 기본 클래스

책임:
- Collector 공통 인터페이스 정의
- 결과 집계 구조
- 에러 핸들링 기본 패턴

하지 않는 것:
- 실제 API 호출
- 특정 소스 로직
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class CollectResult:
    """수집 결과"""
    source: str  # "github", "api", etc.
    resource: str  # "commits", "issues", etc.
    status: str  # "success" | "partial" | "fail"

    # 통계
    total_count: int = 0
    collected_count: int = 0

    # 출력
    output_path: Optional[Path] = None

    # 메타데이터
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None
    errors: list[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None

    def finish(self, status: str = "success") -> "CollectResult":
        """수집 완료 처리"""
        self.finished_at = datetime.now()
        self.status = status
        return self

    def add_error(self, error: str) -> None:
        self.errors.append(error)

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "resource": self.resource,
            "status": self.status,
            "total_count": self.total_count,
            "collected_count": self.collected_count,
            "output_path": str(self.output_path) if self.output_path else None,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration_seconds": self.duration_seconds,
            "errors": self.errors
        }


class BaseCollector(ABC):
    """Collector 추상 기본 클래스"""

    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @property
    @abstractmethod
    def source_name(self) -> str:
        """소스 이름 (예: "github", "jira")"""
        pass

    @abstractmethod
    def collect(self) -> list[CollectResult]:
        """
        데이터 수집 실행

        Returns:
            수집 결과 리스트 (리소스별)
        """
        pass

    @abstractmethod
    def collect_resource(self, resource: str) -> CollectResult:
        """
        특정 리소스만 수집

        Args:
            resource: 리소스 이름 (예: "commits", "issues")

        Returns:
            수집 결과
        """
        pass

    def _create_result(self, resource: str) -> CollectResult:
        """결과 객체 생성 헬퍼"""
        return CollectResult(
            source=self.source_name,
            resource=resource,
            status="pending"
        )

    def _save_json(self, data: list[dict], filename: str) -> Path:
        """JSON 저장 헬퍼"""
        import json

        output_path = self.output_dir / f"{filename}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        logger.debug(f"Saved {len(data)} records to {output_path}")
        return output_path

    def _save_parquet(self, data: list[dict], filename: str) -> Path:
        """Parquet 저장 헬퍼"""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for parquet output. Install with: pip install pandas pyarrow")

        output_path = self.output_dir / f"{filename}.parquet"
        df = pd.DataFrame(data)
        df.to_parquet(output_path, index=False, compression="zstd")
        logger.debug(f"Saved {len(data)} records to {output_path}")
        return output_path
