"""
GitHubCollector - GitHub API 데이터 수집

책임:
- GitHub REST API 호출
- 페이지네이션 처리
- Rate Limit 관리
- 데이터 정규화

하지 않는 것:
- 저장 형식 결정 (base에서 처리)
- 데이터 변환/분석
"""

import logging
import time
from pathlib import Path
from typing import Iterator, Optional

import requests

from ..base import BaseCollector, CollectResult
from ..config.schema import GitHubConfig, RateLimitConfig
from .github_types import (
    GitHubCommitResponse,
    GitHubIssueResponse,
    GitHubPRResponse,
    GitHubReleaseResponse,
)

logger = logging.getLogger(__name__)


class GitHubCollector(BaseCollector):
    """GitHub 데이터 수집기"""

    BASE_URL = "https://api.github.com"

    def __init__(
        self,
        config: GitHubConfig,
        output_dir: str | Path = "./output"
    ):
        super().__init__(output_dir)
        self.config = config
        self._session = self._create_session()

    @property
    def source_name(self) -> str:
        return "github"

    def _create_session(self) -> requests.Session:
        """인증된 세션 생성"""
        session = requests.Session()
        session.headers.update({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        })

        if self.config.token:
            # SecretStr에서 실제 값 추출 (로그에 노출 방지)
            session.headers["Authorization"] = f"Bearer {self.config.token.get_secret_value()}"

        return session

    def collect(self) -> list[CollectResult]:
        """설정된 모든 리소스 수집"""
        results = []
        logger.info(f"Starting collection for {self.config.repo_full_name}")

        if self.config.collect_commits:
            results.append(self.collect_resource("commits"))

        if self.config.collect_issues:
            results.append(self.collect_resource("issues"))

        if self.config.collect_pull_requests:
            results.append(self.collect_resource("pull_requests"))

        if self.config.collect_releases:
            results.append(self.collect_resource("releases"))

        success = sum(1 for r in results if r.status == "success")
        logger.info(f"Collection complete: {success}/{len(results)} succeeded")
        return results

    def collect_resource(self, resource: str) -> CollectResult:
        """특정 리소스 수집"""
        result = self._create_result(resource)
        logger.debug(f"Collecting {resource} from {self.config.repo_full_name}")

        try:
            if resource == "commits":
                data = list(self._fetch_commits())
            elif resource == "issues":
                data = list(self._fetch_issues())
            elif resource == "pull_requests":
                data = list(self._fetch_pull_requests())
            elif resource == "releases":
                data = list(self._fetch_releases())
            else:
                raise ValueError(f"Unknown resource: {resource}")

            result.total_count = len(data)
            result.collected_count = len(data)

            # 저장
            filename = f"{self.config.owner}_{self.config.repo}_{resource}"
            result.output_path = self._save_json(data, filename)

            logger.info(f"Collected {len(data)} {resource}")
            return result.finish("success")

        except Exception as e:
            logger.error(f"Failed to collect {resource}: {e}")
            result.add_error(str(e))
            return result.finish("fail")

    def _fetch_commits(self) -> Iterator[dict]:
        """커밋 수집"""
        endpoint = f"/repos/{self.config.repo_full_name}/commits"
        params = {
            "sha": self.config.branch,
            "per_page": self.config.per_page
        }

        if self.config.since:
            params["since"] = self.config.since.isoformat()
        if self.config.until:
            params["until"] = self.config.until.isoformat()

        for item in self._paginate(endpoint, params):
            yield self._normalize_commit(item)

    def _fetch_issues(self) -> Iterator[dict]:
        """이슈 수집"""
        endpoint = f"/repos/{self.config.repo_full_name}/issues"
        params = {
            "state": "all",
            "per_page": self.config.per_page
        }

        if self.config.since:
            params["since"] = self.config.since.isoformat()

        for item in self._paginate(endpoint, params):
            # PR은 제외 (pull_request 키가 있으면 PR)
            if "pull_request" not in item:
                yield self._normalize_issue(item)

    def _fetch_pull_requests(self) -> Iterator[dict]:
        """PR 수집"""
        endpoint = f"/repos/{self.config.repo_full_name}/pulls"
        params = {
            "state": "all",
            "per_page": self.config.per_page
        }

        for item in self._paginate(endpoint, params):
            yield self._normalize_pr(item)

    def _fetch_releases(self) -> Iterator[dict]:
        """릴리즈 수집"""
        endpoint = f"/repos/{self.config.repo_full_name}/releases"
        params = {"per_page": self.config.per_page}

        for item in self._paginate(endpoint, params):
            yield self._normalize_release(item)

    def _paginate(
        self,
        endpoint: str,
        params: dict
    ) -> Iterator[dict]:
        """페이지네이션 처리"""
        url = f"{self.BASE_URL}{endpoint}"
        page = 1
        rate_limit = self.config.rate_limit

        while True:
            # Max pages 체크
            if self.config.max_pages and page > self.config.max_pages:
                break

            params["page"] = page

            # Rate limit 대기
            time.sleep(1 / rate_limit.requests_per_second)

            # 요청 (재시도 포함)
            response = self._request_with_retry(
                url,
                params,
                rate_limit.retry_count,
                rate_limit.retry_delay
            )

            if response is None:
                break

            data = response.json()

            if not data:
                break

            yield from data
            page += 1

    def _request_with_retry(
        self,
        url: str,
        params: dict,
        retry_count: int,
        retry_delay: float
    ) -> Optional[requests.Response]:
        """재시도 로직 포함 요청"""
        for attempt in range(retry_count + 1):
            try:
                response = self._session.get(url, params=params, timeout=30)

                if response.status_code == 200:
                    return response

                if response.status_code == 403:
                    # Rate limit 도달
                    reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                    wait_time = max(reset_time - time.time(), 60)
                    time.sleep(wait_time)
                    continue

                if response.status_code == 404:
                    return None

                response.raise_for_status()

            except requests.RequestException as e:
                if attempt < retry_count:
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    raise

        return None

    # === 정규화 함수들 ===

    @staticmethod
    def _normalize_commit(raw: GitHubCommitResponse) -> dict:
        """커밋 데이터 정규화"""
        commit = raw.get("commit", {})
        author = commit.get("author", {})
        committer = commit.get("committer", {})
        # top-level author/committer는 GitHub user 객체 (login 포함)
        gh_author = raw.get("author") or {}
        gh_committer = raw.get("committer") or {}

        return {
            "sha": raw.get("sha"),
            "message": commit.get("message"),
            "author_name": author.get("name"),
            "author_email": author.get("email"),
            "author_login": gh_author.get("login"),
            "author_date": author.get("date"),
            "committer_name": committer.get("name"),
            "committer_email": committer.get("email"),
            "committer_login": gh_committer.get("login"),
            "committer_date": committer.get("date"),
            "url": raw.get("html_url"),
            "parents": [p.get("sha") for p in raw.get("parents", [])],
        }

    @staticmethod
    def _normalize_issue(raw: GitHubIssueResponse) -> dict:
        """이슈 데이터 정규화"""
        user = raw.get("user", {})

        return {
            "number": raw.get("number"),
            "title": raw.get("title"),
            "body": raw.get("body"),
            "state": raw.get("state"),
            "author": user.get("login"),
            "labels": [l.get("name") for l in raw.get("labels", [])],
            "created_at": raw.get("created_at"),
            "updated_at": raw.get("updated_at"),
            "closed_at": raw.get("closed_at"),
            "comments_count": raw.get("comments", 0),
            "url": raw.get("html_url"),
        }

    @staticmethod
    def _normalize_pr(raw: GitHubPRResponse) -> dict:
        """PR 데이터 정규화"""
        user = raw.get("user", {})
        head = raw.get("head", {})
        base = raw.get("base", {})

        return {
            "number": raw.get("number"),
            "title": raw.get("title"),
            "body": raw.get("body"),
            "state": raw.get("state"),
            "author": user.get("login"),
            "head_ref": head.get("ref"),
            "base_ref": base.get("ref"),
            "labels": [l.get("name") for l in raw.get("labels", [])],
            "created_at": raw.get("created_at"),
            "updated_at": raw.get("updated_at"),
            "closed_at": raw.get("closed_at"),
            "merged_at": raw.get("merged_at"),
            "url": raw.get("html_url"),
        }

    @staticmethod
    def _normalize_release(raw: GitHubReleaseResponse) -> dict:
        """릴리즈 데이터 정규화"""
        author = raw.get("author", {})

        return {
            "id": raw.get("id"),
            "tag_name": raw.get("tag_name"),
            "name": raw.get("name"),
            "body": raw.get("body"),
            "draft": raw.get("draft"),
            "prerelease": raw.get("prerelease"),
            "author": author.get("login"),
            "created_at": raw.get("created_at"),
            "published_at": raw.get("published_at"),
            "url": raw.get("html_url"),
            "assets_count": len(raw.get("assets", [])),
        }
