"""
BaseWarehouse - 추상 기본 클래스

Gemini 리뷰 반영:
- Context Manager 패턴 적용 (__enter__/__exit__)
- 리소스 해제 보장

책임:
- Warehouse 공통 인터페이스 정의
- Context Manager 프로토콜

하지 않는 것:
- 실제 DB 연결
- 특정 DB 로직
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .results import InsertResult, QueryResult
    from .schema import TableSchema


class BaseWarehouse(ABC):
    """Warehouse 추상 기본 클래스 (Context Manager 지원)"""

    # Context Manager 프로토콜
    @abstractmethod
    def __enter__(self) -> BaseWarehouse:
        """연결 및 self 반환"""
        pass

    @abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """연결 종료 (예외 발생 시에도 호출됨)"""
        pass

    # 테이블 관리
    @abstractmethod
    def create_table(self, schema: "TableSchema") -> None:
        """
        테이블 생성

        Args:
            schema: 테이블 스키마

        Raises:
            TableCreationError: 테이블 생성 실패 시
        """
        pass

    @abstractmethod
    def drop_table(self, table: str, if_exists: bool = True) -> None:
        """
        테이블 삭제

        Args:
            table: 테이블 이름
            if_exists: True면 존재하지 않아도 에러 안 남
        """
        pass

    @abstractmethod
    def table_exists(self, table: str) -> bool:
        """테이블 존재 여부 확인"""
        pass

    # 데이터 조작
    @abstractmethod
    def insert(self, table: str, data: list[dict]) -> "InsertResult":
        """
        데이터 삽입

        Args:
            table: 테이블 이름
            data: 삽입할 데이터 (딕셔너리 리스트)

        Returns:
            삽입 결과

        Raises:
            InsertionError: 삽입 실패 시
        """
        pass

    @abstractmethod
    def load_parquet(self, table: str, path: Path) -> "InsertResult":
        """
        Parquet 파일을 테이블에 로드

        Args:
            table: 테이블 이름
            path: Parquet 파일 경로

        Returns:
            로드 결과

        Raises:
            InsertionError: 로드 실패 시
        """
        pass

    # 쿼리
    @abstractmethod
    def query(self, sql: str) -> "QueryResult":
        """
        SQL 쿼리 실행

        Args:
            sql: SQL 쿼리문

        Returns:
            쿼리 결과

        Raises:
            QueryError: 쿼리 실패 시
        """
        pass

    @abstractmethod
    def execute(self, sql: str) -> None:
        """
        SQL 실행 (결과 없음)

        Args:
            sql: SQL 문

        Raises:
            QueryError: 실행 실패 시
        """
        pass
