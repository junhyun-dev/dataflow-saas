"""
Warehouse 커스텀 예외

Gemini 리뷰 반영:
- DuckDB 예외를 직접 노출하지 않고 추상화된 예외로 감싸기
- 추상화 누수(Leaky Abstraction) 방지
- 향후 DB 교체 시 사용 코드 변경 불필요
"""


class WarehouseError(Exception):
    """모든 Warehouse 에러의 기본 클래스"""

    pass


class ConnectionError(WarehouseError):
    """연결 실패 시 발생"""

    pass


class QueryError(WarehouseError):
    """쿼리 실행 실패 시 발생"""

    pass


class TableCreationError(WarehouseError):
    """테이블 생성 실패 시 발생"""

    pass


class InsertionError(WarehouseError):
    """데이터 삽입 실패 시 발생"""

    pass


class SchemaError(WarehouseError):
    """스키마 관련 에러"""

    pass
