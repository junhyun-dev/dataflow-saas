"""
Config Schema - Pydantic 모델로 설정 검증

회사 V2 설계 참고하되, 단순화해서 시작
"""

from typing import Literal, Optional, Union
from pydantic import BaseModel, Field

# 지원하는 컬럼 타입
ColumnType = Literal["int", "float", "datetime", "str"]


class RowsConfig(BaseModel):
    """행 범위 설정"""

    # 시작 행: 숫자 또는 패턴
    start: Union[int, str] = Field(
        default=0,
        description="시작 행 (0-based index 또는 regex 패턴)"
    )

    # 종료 행: 숫자 또는 패턴 또는 None(끝까지)
    end: Optional[Union[int, str]] = Field(
        default=None,
        description="종료 행 (None이면 끝까지)"
    )

    # 헤더 행 수
    header_rows: int = Field(
        default=1,
        description="헤더 행 수"
    )


class TableConfig(BaseModel):
    """테이블 설정"""

    name: str = Field(
        description="테이블 이름"
    )

    # 시트 이름 패턴 (regex)
    sheet_pattern: str = Field(
        default=".*",
        description="대상 시트 이름 패턴 (regex)"
    )

    # 행 범위
    rows: RowsConfig = Field(
        default_factory=RowsConfig
    )

    # 컬럼 필터 (포함할 컬럼 목록, None이면 전체)
    columns: Optional[list[str]] = Field(
        default=None,
        description="포함할 컬럼 목록 (None이면 전체)"
    )

    # 컬럼 타입 지정
    column_types: dict[str, ColumnType] = Field(
        default_factory=dict,
        description="컬럼별 타입: 'int', 'float', 'datetime', 'str'"
    )


class ConvertConfig(BaseModel):
    """전체 변환 설정"""

    # 테이블 설정 목록
    tables: list[TableConfig] = Field(
        default_factory=list,
        description="변환할 테이블 설정 목록"
    )

    # 기본 시트 패턴 (tables에 없으면 이걸 사용)
    default_sheet_pattern: str = Field(
        default=".*",
        description="기본 시트 패턴"
    )

    # 빈 행 제거
    drop_empty_rows: bool = Field(
        default=True,
        description="빈 행 제거 여부"
    )

    # 빈 컬럼 제거
    drop_empty_columns: bool = Field(
        default=True,
        description="빈 컬럼 제거 여부"
    )

    @classmethod
    def simple(cls, table_name: str = "default") -> "ConvertConfig":
        """간단한 설정 생성 (테스트용)"""
        return cls(
            tables=[TableConfig(name=table_name)]
        )
