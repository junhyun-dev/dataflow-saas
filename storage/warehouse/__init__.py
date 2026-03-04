"""
Warehouse - DuckDB 기반 로컬 데이터 웨어하우스

사용법:
    from storage.warehouse import DuckDBWarehouse, DuckDBConfig

    config = DuckDBConfig(db_path="./data/warehouse.duckdb")
    with DuckDBWarehouse(config) as warehouse:
        warehouse.create_table("commits", schema)
        warehouse.load_parquet("commits", Path("./output/commits.parquet"))
        result = warehouse.query("SELECT * FROM commits")
"""

from .config import DuckDBConfig
from .duckdb_warehouse import DuckDBWarehouse
from .exceptions import (
    WarehouseError,
    ConnectionError,
    QueryError,
    TableCreationError,
    InsertionError,
)
from .schema import Column, TableSchema, DuckDBType
from .results import InsertResult, QueryResult

__all__ = [
    # Main classes
    "DuckDBWarehouse",
    "DuckDBConfig",
    # Schema
    "Column",
    "TableSchema",
    "DuckDBType",
    # Results
    "InsertResult",
    "QueryResult",
    # Exceptions
    "WarehouseError",
    "ConnectionError",
    "QueryError",
    "TableCreationError",
    "InsertionError",
]
