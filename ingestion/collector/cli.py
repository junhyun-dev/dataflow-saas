"""
Collector CLI

사용법:
    python -m ingestion.collector.cli github owner/repo
    python -m ingestion.collector.cli github owner/repo --token $GITHUB_TOKEN
    python -m ingestion.collector.cli github owner/repo --resource commits
"""

import argparse
import json
import os
import sys
from pathlib import Path

from .config.schema import GitHubConfig, CollectorConfig
from .collectors.github_collector import GitHubCollector


def main():
    parser = argparse.ArgumentParser(
        description="데이터 수집기 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
    # 기본 사용 (commits, issues, PRs 수집)
    python -m ingestion.collector.cli github anthropics/claude-code

    # 토큰 사용 (rate limit 완화)
    python -m ingestion.collector.cli github anthropics/claude-code --token $GITHUB_TOKEN

    # 특정 리소스만 수집
    python -m ingestion.collector.cli github anthropics/claude-code --resource commits

    # 출력 디렉토리 지정
    python -m ingestion.collector.cli github anthropics/claude-code -o ./data
        """
    )

    subparsers = parser.add_subparsers(dest="source", help="데이터 소스")

    # GitHub 서브커맨드
    github_parser = subparsers.add_parser("github", help="GitHub 저장소 수집")
    github_parser.add_argument(
        "repo",
        help="저장소 (owner/repo 형식)"
    )
    github_parser.add_argument(
        "--token", "-t",
        default=os.environ.get("GITHUB_TOKEN"),
        help="GitHub Personal Access Token (기본: $GITHUB_TOKEN)"
    )
    github_parser.add_argument(
        "--resource", "-r",
        choices=["commits", "issues", "pull_requests", "releases", "all"],
        default="all",
        help="수집할 리소스 (기본: all)"
    )
    github_parser.add_argument(
        "--output", "-o",
        default="./output",
        help="출력 디렉토리 (기본: ./output)"
    )
    github_parser.add_argument(
        "--branch", "-b",
        default="main",
        help="대상 브랜치 (기본: main)"
    )
    github_parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="최대 페이지 수 (기본: 제한 없음)"
    )
    github_parser.add_argument(
        "--json",
        action="store_true",
        help="결과를 JSON으로 출력"
    )

    args = parser.parse_args()

    if not args.source:
        parser.print_help()
        sys.exit(1)

    if args.source == "github":
        run_github_collector(args)


def run_github_collector(args):
    """GitHub 수집 실행"""
    # repo 파싱
    if "/" not in args.repo:
        print(f"오류: 저장소 형식이 잘못됐습니다. 'owner/repo' 형식 필요: {args.repo}")
        sys.exit(1)

    owner, repo = args.repo.split("/", 1)

    # Config 생성
    config = GitHubConfig(
        owner=owner,
        repo=repo,
        token=args.token,
        branch=args.branch,
        max_pages=args.max_pages,
        # 리소스 선택
        collect_commits=args.resource in ("all", "commits"),
        collect_issues=args.resource in ("all", "issues"),
        collect_pull_requests=args.resource in ("all", "pull_requests"),
        collect_releases=args.resource in ("all", "releases"),
    )

    # 실행
    collector = GitHubCollector(config, args.output)

    if not args.json:
        print(f"수집 시작: {config.repo_full_name}")
        print(f"출력 디렉토리: {args.output}")
        print("-" * 40)

    results = collector.collect()

    # 결과 출력
    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2, default=str))
    else:
        for result in results:
            status_icon = "✅" if result.status == "success" else "❌"
            print(
                f"{status_icon} {result.resource}: "
                f"{result.collected_count}건 수집 "
                f"({result.duration_seconds:.1f}초)"
            )
            if result.errors:
                for error in result.errors:
                    print(f"   └─ 오류: {error}")

        print("-" * 40)
        success = sum(1 for r in results if r.status == "success")
        print(f"완료: {success}/{len(results)} 성공")


if __name__ == "__main__":
    main()
