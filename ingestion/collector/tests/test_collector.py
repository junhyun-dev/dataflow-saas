"""
Collector 테스트
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ..base import BaseCollector, CollectResult
from ..config.schema import GitHubConfig, CollectorConfig, RateLimitConfig
from ..collectors.github_collector import GitHubCollector


class TestCollectResult:
    """CollectResult 테스트"""

    def test_create_result(self):
        """결과 생성"""
        result = CollectResult(
            source="github",
            resource="commits",
            status="pending"
        )
        assert result.source == "github"
        assert result.resource == "commits"
        assert result.status == "pending"

    def test_finish(self):
        """완료 처리"""
        result = CollectResult(
            source="test",
            resource="test",
            status="pending"
        )
        result.finish("success")

        assert result.status == "success"
        assert result.finished_at is not None
        assert result.duration_seconds is not None

    def test_to_dict(self):
        """딕셔너리 변환"""
        result = CollectResult(
            source="github",
            resource="commits",
            status="success",
            total_count=100,
            collected_count=100
        )
        result.finish()

        d = result.to_dict()
        assert d["source"] == "github"
        assert d["total_count"] == 100


class TestGitHubConfig:
    """GitHubConfig 테스트"""

    def test_simple_config(self):
        """간단한 설정"""
        config = GitHubConfig(
            owner="anthropics",
            repo="claude-code"
        )
        assert config.owner == "anthropics"
        assert config.repo == "claude-code"
        assert config.repo_full_name == "anthropics/claude-code"

    def test_config_defaults(self):
        """기본값 확인"""
        config = GitHubConfig(owner="test", repo="test")

        assert config.token is None
        assert config.collect_commits is True
        assert config.collect_issues is True
        assert config.collect_pull_requests is True
        assert config.collect_releases is False
        assert config.branch == "main"
        assert config.per_page == 100

    def test_rate_limit_config(self):
        """Rate limit 설정"""
        rate_limit = RateLimitConfig(
            requests_per_second=2.0,
            retry_count=5
        )
        assert rate_limit.requests_per_second == 2.0
        assert rate_limit.retry_count == 5


class TestCollectorConfig:
    """CollectorConfig 테스트"""

    def test_for_github(self):
        """GitHub용 간편 생성"""
        config = CollectorConfig.for_github(
            owner="anthropics",
            repo="claude-code",
            output_dir="./data"
        )
        assert config.github is not None
        assert config.github.owner == "anthropics"
        assert config.output_dir == "./data"


class TestGitHubCollector:
    """GitHubCollector 테스트"""

    @pytest.fixture
    def config(self):
        """테스트용 설정"""
        return GitHubConfig(
            owner="test",
            repo="test-repo",
            collect_commits=True,
            collect_issues=False,
            collect_pull_requests=False,
            collect_releases=False,
            max_pages=1,
            rate_limit=RateLimitConfig(
                requests_per_second=100,  # 테스트에서는 빠르게
                retry_count=1
            )
        )

    @pytest.fixture
    def collector(self, config, tmp_path):
        """테스트용 collector"""
        return GitHubCollector(config, tmp_path)

    def test_source_name(self, collector):
        """소스 이름"""
        assert collector.source_name == "github"

    def test_normalize_commit(self, collector):
        """커밋 정규화"""
        raw = {
            "sha": "abc123",
            "commit": {
                "message": "test commit",
                "author": {
                    "name": "Test",
                    "email": "test@test.com",
                    "date": "2024-01-01T00:00:00Z"
                },
                "committer": {
                    "name": "Test",
                    "email": "test@test.com",
                    "date": "2024-01-01T00:00:00Z"
                }
            },
            "html_url": "https://github.com/test/test/commit/abc123",
            "parents": [{"sha": "parent1"}]
        }

        normalized = collector._normalize_commit(raw)

        assert normalized["sha"] == "abc123"
        assert normalized["message"] == "test commit"
        assert normalized["author_name"] == "Test"
        assert normalized["parents"] == ["parent1"]

    def test_normalize_issue(self, collector):
        """이슈 정규화"""
        raw = {
            "number": 1,
            "title": "Test issue",
            "body": "Description",
            "state": "open",
            "user": {"login": "testuser"},
            "labels": [{"name": "bug"}],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "closed_at": None,
            "comments": 5,
            "html_url": "https://github.com/test/test/issues/1"
        }

        normalized = collector._normalize_issue(raw)

        assert normalized["number"] == 1
        assert normalized["title"] == "Test issue"
        assert normalized["author"] == "testuser"
        assert normalized["labels"] == ["bug"]

    @patch.object(GitHubCollector, '_paginate')
    def test_collect_commits(self, mock_paginate, collector, tmp_path):
        """커밋 수집 테스트 (mock)"""
        mock_paginate.return_value = iter([
            {
                "sha": "abc123",
                "commit": {
                    "message": "test",
                    "author": {"name": "A", "email": "a@a.com", "date": "2024-01-01"},
                    "committer": {"name": "A", "email": "a@a.com", "date": "2024-01-01"}
                },
                "html_url": "https://github.com/test/test/commit/abc",
                "parents": []
            }
        ])

        result = collector.collect_resource("commits")

        assert result.status == "success"
        assert result.collected_count == 1
        assert result.output_path is not None
        assert result.output_path.exists()

    def test_save_json(self, collector, tmp_path):
        """JSON 저장 테스트"""
        data = [{"id": 1, "name": "test"}]
        output_path = collector._save_json(data, "test")

        assert output_path.exists()

        with open(output_path) as f:
            loaded = json.load(f)
        assert loaded == data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
