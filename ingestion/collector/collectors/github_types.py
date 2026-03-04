"""
GitHub API 응답 타입 정의

TypedDict로 API 응답 구조를 명시하여 타입 안정성 확보
"""

from typing import TypedDict, Optional


class GitHubUser(TypedDict):
    """GitHub 사용자 정보"""
    login: str
    id: int
    avatar_url: str
    html_url: str


class GitHubCommitAuthor(TypedDict):
    """커밋 작성자 정보"""
    name: str
    email: str
    date: str


class GitHubCommitData(TypedDict):
    """커밋 내부 데이터"""
    message: str
    author: GitHubCommitAuthor
    committer: GitHubCommitAuthor


class GitHubParent(TypedDict):
    """부모 커밋 참조"""
    sha: str
    url: str


class GitHubCommitResponse(TypedDict):
    """GitHub Commits API 응답"""
    sha: str
    commit: GitHubCommitData
    html_url: str
    parents: list[GitHubParent]
    author: Optional[GitHubUser]
    committer: Optional[GitHubUser]


class GitHubLabel(TypedDict):
    """이슈/PR 라벨"""
    id: int
    name: str
    color: str


class GitHubIssueResponse(TypedDict):
    """GitHub Issues API 응답"""
    number: int
    title: str
    body: Optional[str]
    state: str
    user: GitHubUser
    labels: list[GitHubLabel]
    created_at: str
    updated_at: str
    closed_at: Optional[str]
    comments: int
    html_url: str


class GitHubBranch(TypedDict):
    """PR 브랜치 정보"""
    ref: str
    sha: str


class GitHubPRResponse(TypedDict):
    """GitHub Pull Requests API 응답"""
    number: int
    title: str
    body: Optional[str]
    state: str
    user: GitHubUser
    head: GitHubBranch
    base: GitHubBranch
    labels: list[GitHubLabel]
    created_at: str
    updated_at: str
    closed_at: Optional[str]
    merged_at: Optional[str]
    html_url: str


class GitHubAsset(TypedDict):
    """릴리즈 에셋"""
    id: int
    name: str
    size: int
    download_count: int


class GitHubReleaseResponse(TypedDict):
    """GitHub Releases API 응답"""
    id: int
    tag_name: str
    name: Optional[str]
    body: Optional[str]
    draft: bool
    prerelease: bool
    author: GitHubUser
    created_at: str
    published_at: Optional[str]
    html_url: str
    assets: list[GitHubAsset]
