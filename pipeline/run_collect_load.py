"""
E2E: Collect → Load 실행 스크립트

사용법:
    # 프로젝트 루트에서 실행
    python -m pipeline.run_collect_load

    # 환경변수로 토큰 전달 (선택)
    GITHUB_TOKEN=ghp_xxx python -m pipeline.run_collect_load

동작:
    1. GitHub API에서 commits, PRs 수집 → JSON 저장
    2. JSON → DuckDB raw_commits, raw_pull_requests 테이블 적재
    3. 적재 결과 출력
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ingestion.collector.collectors.github_collector import GitHubCollector
from ingestion.collector.config.schema import GitHubConfig
from pipeline.github_loader import GitHubLoader
from storage.warehouse import DuckDBConfig, DuckDBWarehouse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# === 설정 (하드코딩 — Session 8에서 Config-driven으로 리팩토링) ===
REPO_OWNER = "junhyun-dev"
REPO_NAME = "dataflow-saas"
OUTPUT_DIR = project_root / "output" / "github"
DB_PATH = project_root / "data" / "warehouse.duckdb"
MAX_PAGES = 3  # 테스트용: 최대 3페이지 (300건)


def get_github_token() -> str | None:
    """GitHub 토큰 가져오기 (환경변수 → gh CLI 순서)"""
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token

    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None


def main() -> None:
    logger.info("=" * 60)
    logger.info("E2E: Collect → Load")
    logger.info(f"Target: {REPO_OWNER}/{REPO_NAME}")
    logger.info("=" * 60)

    # 1. Collect
    logger.info("--- Step 1: Collect (GitHub API → JSON) ---")

    token = get_github_token()
    if token:
        logger.info("GitHub token found")
    else:
        logger.warning("No GitHub token — using unauthenticated (60 req/hour limit)")

    config = GitHubConfig(
        owner=REPO_OWNER,
        repo=REPO_NAME,
        token=token,
        collect_commits=True,
        collect_issues=False,  # Session 2에서는 commits + PRs만
        collect_pull_requests=True,
        collect_releases=False,
        max_pages=MAX_PAGES,
    )

    collector = GitHubCollector(config=config, output_dir=OUTPUT_DIR)
    collect_results = collector.collect()

    for r in collect_results:
        logger.info(f"  {r.resource}: {r.status} ({r.collected_count} records → {r.output_path})")

    failed = [r for r in collect_results if r.status != "success"]
    if failed:
        logger.error(f"Collection failed for: {[r.resource for r in failed]}")
        sys.exit(1)

    # 2. Load
    logger.info("--- Step 2: Load (JSON → DuckDB) ---")

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db_config = DuckDBConfig(db_path=DB_PATH)

    with DuckDBWarehouse(db_config) as warehouse:
        loader = GitHubLoader(
            warehouse=warehouse,
            repo_owner=REPO_OWNER,
            repo_name=REPO_NAME,
        )

        # 테이블 생성
        loader.setup_tables()

        # JSON → DuckDB
        load_results = loader.load_all(OUTPUT_DIR)

        for resource, result in load_results.items():
            logger.info(f"  {resource}: {result.status} ({result.rows_affected} rows)")

        # 3. 검증
        logger.info("--- Step 3: Verify ---")

        commits_count = warehouse.query("SELECT COUNT(*) FROM raw_commits")
        prs_count = warehouse.query("SELECT COUNT(*) FROM raw_pull_requests")

        logger.info(f"  raw_commits: {commits_count.rows[0][0]} rows")
        logger.info(f"  raw_pull_requests: {prs_count.rows[0][0]} rows")

        # 샘플 데이터 확인
        sample = warehouse.query(
            "SELECT sha, author_name, author_date, message "
            "FROM raw_commits ORDER BY author_date DESC LIMIT 3"
        )
        logger.info("  Latest commits:")
        for row in sample.rows:
            sha_short = row[0][:7] if row[0] else "???"
            logger.info(f"    {sha_short} | {row[1]} | {row[2]} | {row[3][:50]}")

    logger.info("=" * 60)
    logger.info("E2E Collect → Load DONE")
    logger.info(f"DB: {DB_PATH}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
