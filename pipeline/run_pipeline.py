"""
E2E: Collect → Load → Transform 전체 파이프라인

사용법:
    python -m pipeline.run_pipeline

    # Transform만 다시 실행 (이미 데이터 있을 때)
    python -m pipeline.run_pipeline --transform-only

동작:
    1. Collect: GitHub API → JSON
    2. Load: JSON → DuckDB raw 테이블
    3. Transform: SQL 모델 실행 (staging→intermediate→mart)
    4. Verify: mart 테이블 확인
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ingestion.collector.collectors.github_collector import GitHubCollector
from ingestion.collector.config.schema import GitHubConfig
from pipeline.github_loader import GitHubLoader
from storage.warehouse import DuckDBConfig, DuckDBWarehouse
from transform.sql_runner import run_models

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# === 설정 ===
REPO_OWNER = "junhyun-dev"
REPO_NAME = "dataflow-saas"
OUTPUT_DIR = project_root / "output" / "github"
DB_PATH = project_root / "data" / "warehouse.duckdb"
MAX_PAGES = 3


def get_github_token() -> str | None:
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    try:
        result = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def step_collect() -> None:
    """Step 1: Collect"""
    logger.info("--- Step 1: Collect (GitHub API → JSON) ---")
    token = get_github_token()
    config = GitHubConfig(
        owner=REPO_OWNER,
        repo=REPO_NAME,
        token=token,
        collect_commits=True,
        collect_issues=False,
        collect_pull_requests=True,
        collect_releases=False,
        max_pages=MAX_PAGES,
    )
    collector = GitHubCollector(config=config, output_dir=OUTPUT_DIR)
    results = collector.collect()
    for r in results:
        logger.info(f"  {r.resource}: {r.status} ({r.collected_count} records)")


def step_load(warehouse: DuckDBWarehouse) -> None:
    """Step 2: Load"""
    logger.info("--- Step 2: Load (JSON → DuckDB) ---")
    loader = GitHubLoader(warehouse=warehouse, repo_owner=REPO_OWNER, repo_name=REPO_NAME)
    loader.setup_tables()
    results = loader.load_all(OUTPUT_DIR)
    for resource, result in results.items():
        logger.info(f"  {resource}: {result.rows_affected} rows")


def step_transform(warehouse: DuckDBWarehouse) -> None:
    """Step 3: Transform (SQL models)"""
    logger.info("--- Step 3: Transform (SQL models) ---")
    result = run_models(warehouse)
    if result.fail_count > 0:
        logger.error(f"Transform had {result.fail_count} failures")
        for m in result.models:
            if m.status == "fail":
                logger.error(f"  {m.name}: {m.error}")


def step_verify(warehouse: DuckDBWarehouse) -> None:
    """Step 4: Verify"""
    logger.info("--- Step 4: Verify ---")

    tables = ["raw_commits", "raw_pull_requests", "int_commit_daily", "int_pr_metrics", "mart_developer_weekly"]
    for table in tables:
        try:
            count = warehouse.query(f"SELECT COUNT(*) FROM {table}")
            logger.info(f"  {table}: {count.rows[0][0]} rows")
        except Exception:
            logger.warning(f"  {table}: NOT FOUND")

    # mart 샘플 출력
    try:
        sample = warehouse.query(
            "SELECT week_start, developer, total_commits, total_prs, merged_prs, avg_hours_to_merge "
            "FROM mart_developer_weekly ORDER BY week_start DESC LIMIT 5"
        )
        if sample.rows:
            logger.info("  mart_developer_weekly sample:")
            for row in sample.rows:
                logger.info(f"    {row[0]} | {row[1]} | commits={row[2]} prs={row[3]} merged={row[4]} merge_h={row[5]}")
        else:
            logger.info("  mart_developer_weekly: empty (expected if PR data is 0)")
    except Exception as e:
        logger.error(f"  mart query failed: {e}")


def main() -> None:
    transform_only = "--transform-only" in sys.argv

    logger.info("=" * 60)
    logger.info(f"E2E Pipeline: {'Transform only' if transform_only else 'Collect → Load → Transform'}")
    logger.info(f"Target: {REPO_OWNER}/{REPO_NAME}")
    logger.info("=" * 60)

    if not transform_only:
        step_collect()

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db_config = DuckDBConfig(db_path=DB_PATH)

    with DuckDBWarehouse(db_config) as warehouse:
        if not transform_only:
            step_load(warehouse)
        step_transform(warehouse)
        step_verify(warehouse)

    logger.info("=" * 60)
    logger.info("Pipeline DONE")
    logger.info(f"DB: {DB_PATH}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
