"""
스키마 정의

Gemini 리뷰 반영:
- dtype에 Literal 타입 사용하여 오타 방지
- 코드 기반 스키마 관리 (타입 안전성, IDE 지원)
"""

from dataclasses import dataclass, field
from typing import Literal

# DuckDB 주요 데이터 타입 (Gemini 제안)
DuckDBType = Literal[
    "VARCHAR",
    "INTEGER",
    "BIGINT",
    "DOUBLE",
    "BOOLEAN",
    "DATE",
    "TIMESTAMP",
    "BLOB",
    "JSON",
]


@dataclass
class Column:
    """컬럼 정의"""

    name: str
    dtype: DuckDBType
    nullable: bool = True
    primary_key: bool = False

    def to_ddl(self) -> str:
        """컬럼 DDL 생성"""
        parts = [self.name, self.dtype]
        if self.primary_key:
            parts.append("PRIMARY KEY")
        elif not self.nullable:
            parts.append("NOT NULL")
        return " ".join(parts)


@dataclass
class TableSchema:
    """테이블 스키마 정의"""

    name: str
    columns: list[Column] = field(default_factory=list)

    def to_ddl(self) -> str:
        """CREATE TABLE DDL 생성"""
        cols_ddl = ", ".join(col.to_ddl() for col in self.columns)
        return f"CREATE TABLE IF NOT EXISTS {self.name} ({cols_ddl})"

    def column_names(self) -> list[str]:
        """컬럼 이름 리스트"""
        return [col.name for col in self.columns]


# === Raw Layer 스키마 ===
# GitHubCollector._normalize_*() 출력과 1:1 매칭
# 날짜: TIMESTAMP으로 즉시 변환 (ADR 005 DON'T #4)
# 리스트 필드: JSON 타입 (parents, labels)
# 메타데이터: repo_owner, repo_name, loaded_at

RAW_COMMITS_SCHEMA = TableSchema(
    name="raw_commits",
    columns=[
        # Collector 출력 필드
        Column("sha", "VARCHAR", primary_key=True),
        Column("message", "VARCHAR"),
        Column("author_name", "VARCHAR"),
        Column("author_email", "VARCHAR"),
        Column("author_date", "TIMESTAMP"),
        Column("committer_name", "VARCHAR"),
        Column("committer_email", "VARCHAR"),
        Column("committer_date", "TIMESTAMP"),
        Column("url", "VARCHAR"),
        Column("parents", "JSON"),  # ["sha1", "sha2"]
        # 메타데이터
        Column("repo_owner", "VARCHAR", nullable=False),
        Column("repo_name", "VARCHAR", nullable=False),
        Column("loaded_at", "TIMESTAMP", nullable=False),
    ],
)

RAW_PULL_REQUESTS_SCHEMA = TableSchema(
    name="raw_pull_requests",
    columns=[
        # Collector 출력 필드
        Column("number", "INTEGER", primary_key=True),
        Column("title", "VARCHAR"),
        Column("body", "VARCHAR"),
        Column("state", "VARCHAR"),
        Column("author", "VARCHAR"),
        Column("head_ref", "VARCHAR"),
        Column("base_ref", "VARCHAR"),
        Column("labels", "JSON"),  # ["bug", "feature"]
        Column("created_at", "TIMESTAMP"),
        Column("updated_at", "TIMESTAMP"),
        Column("closed_at", "TIMESTAMP"),
        Column("merged_at", "TIMESTAMP"),
        Column("url", "VARCHAR"),
        # 메타데이터
        Column("repo_owner", "VARCHAR", nullable=False),
        Column("repo_name", "VARCHAR", nullable=False),
        Column("loaded_at", "TIMESTAMP", nullable=False),
    ],
)
