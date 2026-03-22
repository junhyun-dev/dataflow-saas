"""
GitHubLoader — Collect 출력을 DuckDB raw 테이블로 적재

책임:
- JSON 파일 읽기 (GitHubCollector 출력)
- 메타데이터 추가 (repo_owner, repo_name, loaded_at)
- 리스트 필드 → JSON 문자열 변환
- DuckDB raw 테이블에 INSERT

하지 않는 것:
- API 호출 (Collect 단계 책임)
- 데이터 변환/집계 (Transform 단계 책임)
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from storage.warehouse import (
    DuckDBWarehouse,
    RAW_COMMITS_SCHEMA,
    RAW_PULL_REQUESTS_SCHEMA,
    InsertResult,
)

logger = logging.getLogger(__name__)


class GitHubLoader:
    """GitHub 데이터를 DuckDB raw 테이블로 적재"""

    def __init__(
        self,
        warehouse: DuckDBWarehouse,
        repo_owner: str,
        repo_name: str,
    ):
        self.warehouse = warehouse
        self.repo_owner = repo_owner
        self.repo_name = repo_name

    def setup_tables(self) -> None:
        """raw 테이블 생성 (없으면)"""
        self.warehouse.create_table(RAW_COMMITS_SCHEMA)
        self.warehouse.create_table(RAW_PULL_REQUESTS_SCHEMA)
        logger.info("Raw tables ready")

    def load_commits(self, json_path: Path) -> InsertResult:
        """커밋 JSON → raw_commits 테이블"""
        records = self._read_json(json_path)
        enriched = [self._enrich_commit(r) for r in records]
        result = self.warehouse.insert("raw_commits", enriched)
        logger.info(f"Loaded {result.rows_affected} commits")
        return result

    def load_pull_requests(self, json_path: Path) -> InsertResult:
        """PR JSON → raw_pull_requests 테이블"""
        records = self._read_json(json_path)
        enriched = [self._enrich_pr(r) for r in records]
        result = self.warehouse.insert("raw_pull_requests", enriched)
        logger.info(f"Loaded {result.rows_affected} pull requests")
        return result

    def load_all(self, output_dir: Path) -> dict[str, InsertResult]:
        """output 디렉토리에서 commits, PRs JSON을 찾아서 전부 적재"""
        results = {}
        pattern = f"{self.repo_owner}_{self.repo_name}"

        commits_path = output_dir / f"{pattern}_commits.json"
        if commits_path.exists():
            results["commits"] = self.load_commits(commits_path)

        prs_path = output_dir / f"{pattern}_pull_requests.json"
        if prs_path.exists():
            results["pull_requests"] = self.load_pull_requests(prs_path)

        if not results:
            logger.warning(f"No JSON files found in {output_dir} for {pattern}")

        return results

    def _enrich_commit(self, record: dict[str, Any]) -> dict[str, Any]:
        """커밋 레코드에 메타데이터 추가 + 리스트→JSON 변환"""
        record["repo_owner"] = self.repo_owner
        record["repo_name"] = self.repo_name
        record["loaded_at"] = datetime.now().isoformat()
        # parents: list → JSON string
        if isinstance(record.get("parents"), list):
            record["parents"] = json.dumps(record["parents"])
        return record

    def _enrich_pr(self, record: dict[str, Any]) -> dict[str, Any]:
        """PR 레코드에 메타데이터 추가 + 리스트→JSON 변환"""
        record["repo_owner"] = self.repo_owner
        record["repo_name"] = self.repo_name
        record["loaded_at"] = datetime.now().isoformat()
        # labels: list → JSON string
        if isinstance(record.get("labels"), list):
            record["labels"] = json.dumps(record["labels"])
        return record

    @staticmethod
    def _read_json(path: Path) -> list[dict]:
        """JSON 파일 읽기"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.debug(f"Read {len(data)} records from {path}")
        return data
