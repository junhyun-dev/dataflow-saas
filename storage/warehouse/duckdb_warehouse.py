"""
DuckDBWarehouse - DuckDB 구현

Gemini 리뷰 반영:
- Context Manager 패턴 적용
- 커스텀 예외로 DuckDB 예외 감싸기
- 리소스 관리 보장
"""

import logging
import time
from pathlib import Path
from types import TracebackType
from typing import Optional

import duckdb

from .base import BaseWarehouse
from .config import DuckDBConfig
from .exceptions import (
    ConnectionError,
    InsertionError,
    QueryError,
    TableCreationError,
)
from .results import InsertResult, QueryResult
from .schema import TableSchema

logger = logging.getLogger(__name__)


class DuckDBWarehouse(BaseWarehouse):
    """DuckDB 기반 로컬 데이터 웨어하우스"""

    def __init__(self, config: DuckDBConfig):
        """
        Args:
            config: DuckDB 설정
        """
        self.config = config
        self._conn: Optional[duckdb.DuckDBPyConnection] = None

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        """연결 객체 (연결 안 됐으면 에러)"""
        if self._conn is None:
            raise ConnectionError(
                "Not connected. Use 'with DuckDBWarehouse(config) as warehouse:'"
            )
        return self._conn

    # Context Manager
    def __enter__(self) -> "DuckDBWarehouse":
        try:
            self._conn = duckdb.connect(
                self.config.connection_string,
                read_only=self.config.read_only,
            )

            # 옵션 설정
            if self.config.threads > 0:
                self._conn.execute(f"SET threads TO {self.config.threads}")
            if self.config.memory_limit:
                self._conn.execute(f"SET memory_limit = '{self.config.memory_limit}'")

            logger.info(f"Connected to DuckDB: {self.config.connection_string}")
            return self

        except duckdb.Error as e:
            raise ConnectionError(f"Failed to connect to DuckDB: {e}") from e

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.info("DuckDB connection closed")

    # 테이블 관리
    def create_table(self, schema: TableSchema) -> None:
        try:
            ddl = schema.to_ddl()
            self.conn.execute(ddl)
            logger.info(f"Created table: {schema.name}")
        except duckdb.Error as e:
            raise TableCreationError(
                f"Failed to create table '{schema.name}': {e}"
            ) from e

    def drop_table(self, table: str, if_exists: bool = True) -> None:
        try:
            sql = f"DROP TABLE {'IF EXISTS ' if if_exists else ''}{table}"
            self.conn.execute(sql)
            logger.info(f"Dropped table: {table}")
        except duckdb.Error as e:
            raise QueryError(f"Failed to drop table '{table}': {e}") from e

    def table_exists(self, table: str) -> bool:
        try:
            result = self.conn.execute(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = ?",
                [table],
            ).fetchone()
            return result[0] > 0 if result else False
        except duckdb.Error as e:
            raise QueryError(f"Failed to check table existence: {e}") from e

    # 데이터 조작
    def insert(self, table: str, data: list[dict]) -> InsertResult:
        result = InsertResult(table=table, rows_affected=0, status="pending")

        if not data:
            return result.finish("success")

        try:
            # 첫 번째 행에서 컬럼 추출
            columns = list(data[0].keys())
            placeholders = ", ".join(["?"] * len(columns))
            cols_str = ", ".join(columns)

            sql = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})"

            # 배치 삽입
            for row in data:
                values = [row.get(col) for col in columns]
                self.conn.execute(sql, values)

            result.rows_affected = len(data)
            logger.info(f"Inserted {len(data)} rows into {table}")
            return result.finish("success")

        except duckdb.Error as e:
            result.add_error(str(e))
            result.finish("fail")
            raise InsertionError(f"Failed to insert into '{table}': {e}") from e

    def insert_or_ignore(self, table: str, data: list[dict]) -> InsertResult:
        """PK 중복 시 무시하고 삽입 (멱등성)"""
        result = InsertResult(table=table, rows_affected=0, status="pending")

        if not data:
            return result.finish("success")

        try:
            columns = list(data[0].keys())
            placeholders = ", ".join(["?"] * len(columns))
            cols_str = ", ".join(columns)

            sql = f"INSERT OR IGNORE INTO {table} ({cols_str}) VALUES ({placeholders})"

            before_count = self.conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            for row in data:
                values = [row.get(col) for col in columns]
                self.conn.execute(sql, values)

            after_count = self.conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            result.rows_affected = after_count - before_count
            skipped = len(data) - result.rows_affected
            if skipped > 0:
                logger.info(f"Inserted {result.rows_affected}, skipped {skipped} duplicates into {table}")
            else:
                logger.info(f"Inserted {result.rows_affected} rows into {table}")
            return result.finish("success")

        except duckdb.Error as e:
            result.add_error(str(e))
            result.finish("fail")
            raise InsertionError(f"Failed to insert into '{table}': {e}") from e

    def load_parquet(self, table: str, path: Path) -> InsertResult:
        result = InsertResult(table=table, rows_affected=0, status="pending")

        if not path.exists():
            result.add_error(f"File not found: {path}")
            result.finish("fail")
            raise InsertionError(f"Parquet file not found: {path}")

        try:
            # Parquet 파일에서 직접 로드
            sql = f"INSERT INTO {table} SELECT * FROM read_parquet('{path}')"
            self.conn.execute(sql)

            # 삽입된 행 수 확인
            count_result = self.conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()
            result.rows_affected = count_result[0] if count_result else 0

            logger.info(f"Loaded {result.rows_affected} rows from {path} into {table}")
            return result.finish("success")

        except duckdb.Error as e:
            result.add_error(str(e))
            result.finish("fail")
            raise InsertionError(f"Failed to load parquet into '{table}': {e}") from e

    # 쿼리
    def query(self, sql: str) -> QueryResult:
        try:
            start_time = time.time()
            cursor = self.conn.execute(sql)

            # 결과 가져오기
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()

            execution_time_ms = (time.time() - start_time) * 1000

            return QueryResult(
                columns=columns,
                rows=rows,
                row_count=len(rows),
                query=sql,
                execution_time_ms=execution_time_ms,
            )

        except duckdb.Error as e:
            raise QueryError(f"Query failed: {e}\nSQL: {sql}") from e

    def execute(self, sql: str) -> None:
        try:
            self.conn.execute(sql)
        except duckdb.Error as e:
            raise QueryError(f"Execute failed: {e}\nSQL: {sql}") from e

    # 추가 유틸리티
    def query_parquet(self, path: Path, sql: str | None = None) -> QueryResult:
        """
        Parquet 파일 직접 쿼리 (테이블 생성 없이)

        Args:
            path: Parquet 파일 경로
            sql: SQL 쿼리 (None이면 SELECT * FROM)

        Returns:
            쿼리 결과
        """
        if sql is None:
            sql = f"SELECT * FROM read_parquet('{path}')"
        else:
            # {path} 플레이스홀더 치환
            sql = sql.replace("{path}", f"read_parquet('{path}')")

        return self.query(sql)

    def get_table_info(self, table: str) -> QueryResult:
        """테이블 스키마 정보 조회"""
        return self.query(f"DESCRIBE {table}")
