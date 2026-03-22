"""
SQL Model Runner — SQL 파일을 의존성 순서대로 실행

책임:
- models/ 디렉토리의 SQL 파일을 레이어 순서대로 실행
- staging(View) → intermediate(Table) → mart(Table)
- 실행 결과 로깅

하지 않는 것:
- 의존성 자동 파싱 (하드코딩 순서, Session 8에서 config-driven으로)
- 테이블 변경 감지 (Session 5에서 멱등성과 함께)
"""

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

from storage.warehouse import DuckDBWarehouse

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).parent / "models"

# 실행 순서 (의존성 순서 — 하드코딩)
MODEL_ORDER = [
    # staging: View (raw 테이블 의존)
    "staging/stg_commits.sql",
    "staging/stg_pull_requests.sql",
    # intermediate: Table (staging View 의존)
    "intermediate/int_commit_daily.sql",
    "intermediate/int_pr_metrics.sql",
    # mart: Table (intermediate 의존)
    "mart/mart_developer_weekly.sql",
]


@dataclass
class ModelResult:
    """모델 실행 결과"""
    name: str
    status: str  # "success" | "fail"
    duration_ms: float = 0.0
    error: str | None = None


@dataclass
class TransformResult:
    """전체 Transform 실행 결과"""
    models: list[ModelResult] = field(default_factory=list)

    @property
    def success_count(self) -> int:
        return sum(1 for m in self.models if m.status == "success")

    @property
    def fail_count(self) -> int:
        return sum(1 for m in self.models if m.status == "fail")


def run_models(warehouse: DuckDBWarehouse) -> TransformResult:
    """모든 SQL 모델을 순서대로 실행"""
    result = TransformResult()

    for model_path in MODEL_ORDER:
        full_path = MODELS_DIR / model_path
        model_name = model_path.replace(".sql", "").replace("/", ".")

        if not full_path.exists():
            mr = ModelResult(name=model_name, status="fail", error=f"File not found: {full_path}")
            result.models.append(mr)
            logger.error(f"  FAIL {model_name}: file not found")
            continue

        sql = full_path.read_text(encoding="utf-8")

        start = time.time()
        try:
            warehouse.execute(sql)
            duration_ms = (time.time() - start) * 1000
            mr = ModelResult(name=model_name, status="success", duration_ms=duration_ms)
            result.models.append(mr)
            logger.info(f"  OK   {model_name} ({duration_ms:.0f}ms)")
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            mr = ModelResult(name=model_name, status="fail", duration_ms=duration_ms, error=str(e))
            result.models.append(mr)
            logger.error(f"  FAIL {model_name}: {e}")

    logger.info(f"Transform complete: {result.success_count}/{len(result.models)} models succeeded")
    return result
