"""
DuckDBWarehouse 테스트

Gemini 리뷰 반영:
- in-memory DB로 단위 테스트 (빠름, 격리)
- 파일 기반 DB로 통합 테스트 (실제 환경 검증)
"""

import tempfile
from pathlib import Path

import pytest

from storage.warehouse import (
    Column,
    ConnectionError,
    DuckDBConfig,
    DuckDBWarehouse,
    InsertResult,
    QueryError,
    QueryResult,
    TableCreationError,
    TableSchema,
)


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def in_memory_config():
    """In-memory DuckDB 설정"""
    return DuckDBConfig(db_path=None)


@pytest.fixture
def sample_schema():
    """테스트용 스키마"""
    return TableSchema(
        name="test_users",
        columns=[
            Column("id", "INTEGER", primary_key=True),
            Column("name", "VARCHAR"),
            Column("email", "VARCHAR"),
            Column("created_at", "TIMESTAMP"),
        ],
    )


@pytest.fixture
def sample_data():
    """테스트용 데이터"""
    return [
        {"id": 1, "name": "Alice", "email": "alice@test.com", "created_at": "2026-01-01 10:00:00"},
        {"id": 2, "name": "Bob", "email": "bob@test.com", "created_at": "2026-01-02 11:00:00"},
        {"id": 3, "name": "Charlie", "email": "charlie@test.com", "created_at": "2026-01-03 12:00:00"},
    ]


# ============================================================
# Context Manager 테스트
# ============================================================


class TestContextManager:
    """Context Manager 동작 테스트"""

    def test_with_statement_connects(self, in_memory_config):
        """with 문으로 연결됨"""
        with DuckDBWarehouse(in_memory_config) as warehouse:
            assert warehouse._conn is not None

    def test_with_statement_closes(self, in_memory_config):
        """with 문 종료 시 연결 해제"""
        warehouse = DuckDBWarehouse(in_memory_config)
        with warehouse:
            pass
        assert warehouse._conn is None

    def test_connection_error_without_context(self, in_memory_config):
        """context manager 없이 접근 시 에러"""
        warehouse = DuckDBWarehouse(in_memory_config)
        with pytest.raises(ConnectionError):
            _ = warehouse.conn

    def test_exception_still_closes(self, in_memory_config):
        """예외 발생해도 연결 해제됨"""
        warehouse = DuckDBWarehouse(in_memory_config)
        try:
            with warehouse:
                raise ValueError("Test error")
        except ValueError:
            pass
        assert warehouse._conn is None


# ============================================================
# 테이블 관리 테스트
# ============================================================


class TestTableManagement:
    """테이블 생성/삭제/확인 테스트"""

    def test_create_table(self, in_memory_config, sample_schema):
        """테이블 생성"""
        with DuckDBWarehouse(in_memory_config) as warehouse:
            warehouse.create_table(sample_schema)
            assert warehouse.table_exists("test_users")

    def test_table_exists_false(self, in_memory_config):
        """존재하지 않는 테이블"""
        with DuckDBWarehouse(in_memory_config) as warehouse:
            assert not warehouse.table_exists("nonexistent_table")

    def test_drop_table(self, in_memory_config, sample_schema):
        """테이블 삭제"""
        with DuckDBWarehouse(in_memory_config) as warehouse:
            warehouse.create_table(sample_schema)
            warehouse.drop_table("test_users")
            assert not warehouse.table_exists("test_users")

    def test_drop_table_if_exists(self, in_memory_config):
        """존재하지 않는 테이블 삭제 (if_exists=True)"""
        with DuckDBWarehouse(in_memory_config) as warehouse:
            # 에러 없이 통과해야 함
            warehouse.drop_table("nonexistent", if_exists=True)


# ============================================================
# 데이터 조작 테스트
# ============================================================


class TestDataOperations:
    """데이터 삽입/조회 테스트"""

    def test_insert_data(self, in_memory_config, sample_schema, sample_data):
        """데이터 삽입"""
        with DuckDBWarehouse(in_memory_config) as warehouse:
            warehouse.create_table(sample_schema)
            result = warehouse.insert("test_users", sample_data)

            assert isinstance(result, InsertResult)
            assert result.status == "success"
            assert result.rows_affected == 3

    def test_insert_empty_data(self, in_memory_config, sample_schema):
        """빈 데이터 삽입"""
        with DuckDBWarehouse(in_memory_config) as warehouse:
            warehouse.create_table(sample_schema)
            result = warehouse.insert("test_users", [])

            assert result.status == "success"
            assert result.rows_affected == 0

    def test_query_data(self, in_memory_config, sample_schema, sample_data):
        """데이터 조회"""
        with DuckDBWarehouse(in_memory_config) as warehouse:
            warehouse.create_table(sample_schema)
            warehouse.insert("test_users", sample_data)

            result = warehouse.query("SELECT * FROM test_users ORDER BY id")

            assert isinstance(result, QueryResult)
            assert result.row_count == 3
            assert "id" in result.columns
            assert "name" in result.columns

    def test_query_with_filter(self, in_memory_config, sample_schema, sample_data):
        """필터링 쿼리"""
        with DuckDBWarehouse(in_memory_config) as warehouse:
            warehouse.create_table(sample_schema)
            warehouse.insert("test_users", sample_data)

            result = warehouse.query("SELECT name FROM test_users WHERE id = 1")

            assert result.row_count == 1
            assert result.rows[0][0] == "Alice"

    def test_query_result_to_dicts(self, in_memory_config, sample_schema, sample_data):
        """QueryResult를 딕셔너리로 변환"""
        with DuckDBWarehouse(in_memory_config) as warehouse:
            warehouse.create_table(sample_schema)
            warehouse.insert("test_users", sample_data)

            result = warehouse.query("SELECT id, name FROM test_users ORDER BY id LIMIT 1")
            dicts = result.to_dicts()

            assert len(dicts) == 1
            assert dicts[0]["id"] == 1
            assert dicts[0]["name"] == "Alice"


# ============================================================
# 예외 처리 테스트
# ============================================================


class TestExceptionHandling:
    """커스텀 예외 테스트"""

    def test_query_error_invalid_sql(self, in_memory_config):
        """잘못된 SQL 쿼리 시 QueryError"""
        with DuckDBWarehouse(in_memory_config) as warehouse:
            with pytest.raises(QueryError):
                warehouse.query("INVALID SQL SYNTAX")

    def test_table_creation_error_invalid_schema(self, in_memory_config):
        """잘못된 스키마로 테이블 생성 시 에러"""
        invalid_schema = TableSchema(
            name="test",
            columns=[Column("col1", "INVALID_TYPE")],  # type: ignore
        )
        with DuckDBWarehouse(in_memory_config) as warehouse:
            with pytest.raises(TableCreationError):
                warehouse.create_table(invalid_schema)


# ============================================================
# 스키마 테스트
# ============================================================


class TestSchema:
    """스키마 관련 테스트"""

    def test_column_to_ddl(self):
        """Column DDL 생성"""
        col = Column("id", "INTEGER", primary_key=True)
        assert col.to_ddl() == "id INTEGER PRIMARY KEY"

    def test_column_nullable(self):
        """NOT NULL 컬럼"""
        col = Column("name", "VARCHAR", nullable=False)
        assert col.to_ddl() == "name VARCHAR NOT NULL"

    def test_table_schema_to_ddl(self, sample_schema):
        """TableSchema DDL 생성"""
        ddl = sample_schema.to_ddl()
        assert "CREATE TABLE IF NOT EXISTS test_users" in ddl
        assert "id INTEGER PRIMARY KEY" in ddl
        assert "name VARCHAR" in ddl


# ============================================================
# 파일 기반 통합 테스트 (Gemini 권장)
# ============================================================


class TestFileBasedIntegration:
    """파일 기반 DB 통합 테스트"""

    def test_persistent_storage(self, sample_schema, sample_data):
        """파일에 저장하고 다시 읽기"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.duckdb"
            config = DuckDBConfig(db_path=db_path)

            # 데이터 저장
            with DuckDBWarehouse(config) as warehouse:
                warehouse.create_table(sample_schema)
                warehouse.insert("test_users", sample_data)

            # 새 연결로 데이터 확인
            with DuckDBWarehouse(config) as warehouse:
                result = warehouse.query("SELECT COUNT(*) FROM test_users")
                assert result.rows[0][0] == 3

    def test_db_file_created(self, sample_schema):
        """DB 파일 생성 확인"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.duckdb"
            config = DuckDBConfig(db_path=db_path)

            with DuckDBWarehouse(config) as warehouse:
                warehouse.create_table(sample_schema)

            assert db_path.exists()


# ============================================================
# Parquet 로드 테스트
# ============================================================


class TestParquetLoading:
    """Parquet 파일 로드 테스트"""

    def test_load_parquet(self, in_memory_config, sample_schema, sample_data):
        """Parquet 파일 로드"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Parquet 파일 생성
            parquet_path = Path(tmpdir) / "test.parquet"

            import pandas as pd
            df = pd.DataFrame(sample_data)
            df.to_parquet(parquet_path)

            # DuckDB에 로드
            with DuckDBWarehouse(in_memory_config) as warehouse:
                warehouse.create_table(sample_schema)
                result = warehouse.load_parquet("test_users", parquet_path)

                assert result.status == "success"

                # 데이터 확인
                query_result = warehouse.query("SELECT COUNT(*) FROM test_users")
                assert query_result.rows[0][0] == 3

    def test_query_parquet_directly(self, in_memory_config, sample_data):
        """Parquet 파일 직접 쿼리 (테이블 없이)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            parquet_path = Path(tmpdir) / "test.parquet"

            import pandas as pd
            df = pd.DataFrame(sample_data)
            df.to_parquet(parquet_path)

            with DuckDBWarehouse(in_memory_config) as warehouse:
                result = warehouse.query_parquet(parquet_path)
                assert result.row_count == 3
