"""
Collector Config Schema

Pydantic 모델로 설정 검증
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, SecretStr


class RateLimitConfig(BaseModel):
    """Rate Limit 설정"""
    requests_per_second: float = Field(default=1.0, ge=0.1, le=100)
    retry_count: int = Field(default=3, ge=0, le=10)
    retry_delay: float = Field(default=1.0, ge=0.1)


class GitHubConfig(BaseModel):
    """GitHub Collector 설정"""
    token: Optional[SecretStr] = Field(default=None, description="GitHub Personal Access Token")
    owner: str = Field(..., description="Repository owner (user or org)")
    repo: str = Field(..., description="Repository name")

    # 수집 대상
    collect_commits: bool = Field(default=True)
    collect_issues: bool = Field(default=True)
    collect_pull_requests: bool = Field(default=True)
    collect_releases: bool = Field(default=False)

    # 필터
    since: Optional[datetime] = Field(default=None, description="수집 시작 시점")
    until: Optional[datetime] = Field(default=None, description="수집 종료 시점")
    branch: str = Field(default="main", description="대상 브랜치")

    # 페이징
    per_page: int = Field(default=100, ge=1, le=100)
    max_pages: Optional[int] = Field(default=None, description="최대 페이지 수 (None=전체)")

    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)

    @property
    def repo_full_name(self) -> str:
        return f"{self.owner}/{self.repo}"


class CollectorConfig(BaseModel):
    """Collector 공통 설정"""
    output_dir: str = Field(default="./output")
    output_format: Literal["json", "parquet", "csv"] = Field(default="json")

    # GitHub 설정 (다른 collector 추가 시 확장)
    github: Optional[GitHubConfig] = Field(default=None)

    @classmethod
    def for_github(
        cls,
        owner: str,
        repo: str,
        token: Optional[str] = None,
        output_dir: str = "./output"
    ) -> "CollectorConfig":
        """GitHub 수집용 간편 생성"""
        return cls(
            output_dir=output_dir,
            github=GitHubConfig(
                owner=owner,
                repo=repo,
                token=token
            )
        )
