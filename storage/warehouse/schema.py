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


# 미리 정의된 스키마 (GitHub 데이터용)
GITHUB_COMMITS_SCHEMA = TableSchema(
    name="github_commits",
    columns=[
        Column("sha", "VARCHAR", primary_key=True),
        Column("message", "VARCHAR"),
        Column("author_name", "VARCHAR"),
        Column("author_email", "VARCHAR"),
        Column("committed_at", "TIMESTAMP"),
        Column("repo_owner", "VARCHAR"),
        Column("repo_name", "VARCHAR"),
    ],
)

GITHUB_ISSUES_SCHEMA = TableSchema(
    name="github_issues",
    columns=[
        Column("id", "BIGINT", primary_key=True),
        Column("number", "INTEGER"),
        Column("title", "VARCHAR"),
        Column("state", "VARCHAR"),
        Column("user_login", "VARCHAR"),
        Column("created_at", "TIMESTAMP"),
        Column("updated_at", "TIMESTAMP"),
        Column("closed_at", "TIMESTAMP"),
        Column("repo_owner", "VARCHAR"),
        Column("repo_name", "VARCHAR"),
    ],
)

GITHUB_PULL_REQUESTS_SCHEMA = TableSchema(
    name="github_pull_requests",
    columns=[
        Column("id", "BIGINT", primary_key=True),
        Column("number", "INTEGER"),
        Column("title", "VARCHAR"),
        Column("state", "VARCHAR"),
        Column("user_login", "VARCHAR"),
        Column("created_at", "TIMESTAMP"),
        Column("updated_at", "TIMESTAMP"),
        Column("merged_at", "TIMESTAMP"),
        Column("closed_at", "TIMESTAMP"),
        Column("repo_owner", "VARCHAR"),
        Column("repo_name", "VARCHAR"),
    ],
)
