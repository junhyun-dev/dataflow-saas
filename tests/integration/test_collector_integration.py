"""
통합 테스트 - Collector

실제 GitHub API를 호출해서 데이터 수집 테스트
(인터넷 연결 필요, rate limit 주의)
"""

import json
import os
from pathlib import Path

import pytest

from ingestion.collector.config.schema import GitHubConfig, RateLimitConfig
from ingestion.collector.collectors.github_collector import GitHubCollector


# 테스트용 공개 저장소 (작은 저장소 사용)
TEST_OWNER = "octocat"
TEST_REPO = "Hello-World"


@pytest.fixture
def output_dir(tmp_path):
    """임시 출력 디렉토리"""
    out = tmp_path / "github_data"
    out.mkdir()
    return out


@pytest.fixture
def github_config():
    """GitHub 설정 (토큰 없이, 낮은 rate limit)"""
    return GitHubConfig(
        owner=TEST_OWNER,
        repo=TEST_REPO,
        token=os.environ.get("GITHUB_TOKEN"),  # 있으면 사용
        collect_commits=True,
        collect_issues=True,
        collect_pull_requests=True,
        collect_releases=False,
        max_pages=1,  # 테스트용으로 1페이지만
        per_page=10,  # 적은 수만
        rate_limit=RateLimitConfig(
            requests_per_second=1.0,
            retry_count=2
        )
    )


class TestGitHubCollectorIntegration:
    """GitHub Collector 통합 테스트"""

    @pytest.mark.integration
    def test_collect_commits(self, github_config, output_dir):
        """커밋 수집 테스트"""
        config = github_config.model_copy(update={
            "collect_issues": False,
            "collect_pull_requests": False
        })

        collector = GitHubCollector(config, output_dir)
        results = collector.collect()

        assert len(results) == 1
        result = results[0]

        print(f"\n커밋 수집 결과:")
        print(f"  - 상태: {result.status}")
        print(f"  - 수집 건수: {result.collected_count}")
        print(f"  - 소요 시간: {result.duration_seconds:.2f}초")

        if result.status == "success":
            assert result.output_path.exists()

            # 데이터 확인
            with open(result.output_path) as f:
                commits = json.load(f)

            print(f"  - 파일: {result.output_path}")
            if commits:
                print(f"  - 첫 번째 커밋: {commits[0].get('message', '')[:50]}...")

            assert isinstance(commits, list)

    @pytest.mark.integration
    def test_collect_all_resources(self, github_config, output_dir):
        """전체 리소스 수집 테스트"""
        collector = GitHubCollector(github_config, output_dir)
        results = collector.collect()

        print(f"\n전체 수집 결과:")
        print("-" * 40)

        success_count = 0
        for result in results:
            status_icon = "✅" if result.status == "success" else "❌"
            print(f"{status_icon} {result.resource}: {result.collected_count}건 ({result.duration_seconds:.2f}초)")

            if result.status == "success":
                success_count += 1

        print("-" * 40)
        print(f"성공: {success_count}/{len(results)}")

        # 최소 1개는 성공해야 함
        assert success_count >= 1

    @pytest.mark.integration
    def test_output_file_structure(self, github_config, output_dir):
        """출력 파일 구조 확인"""
        config = github_config.model_copy(update={
            "collect_commits": True,
            "collect_issues": False,
            "collect_pull_requests": False
        })

        collector = GitHubCollector(config, output_dir)
        results = collector.collect()

        # 출력 파일 확인
        json_files = list(output_dir.glob("*.json"))
        print(f"\n생성된 파일: {[f.name for f in json_files]}")

        assert len(json_files) >= 1

        # JSON 구조 확인
        for json_file in json_files:
            with open(json_file) as f:
                data = json.load(f)

            if data:
                print(f"\n{json_file.name} 필드:")
                print(f"  {list(data[0].keys())}")


@pytest.mark.integration
def test_cli_dry_run():
    """CLI 임포트 테스트"""
    from ingestion.collector.cli import main
    assert callable(main)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration", "-s"])
