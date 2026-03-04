# ADR 004: Storage 설계 - DuckDB 기반 로컬 데이터 웨어하우스

## 상태

검토 중 (Gemini 리뷰 대기)

## 컨텍스트

수집된 데이터(Collector)와 변환된 데이터(Converter)를 저장하고 쿼리할 수 있는 스토리지 레이어가 필요하다.

**현재 상황**:
- ingestion/collector → JSON/Parquet 파일 출력
- transform/converter → Parquet 파일 출력
- 파일은 있지만, 쿼리/분석이 불편함

**요구사항**:
1. Parquet 파일을 쉽게 쿼리
2. 스키마 관리 (테이블 정의)
3. 간단한 ETL (Insert/Upsert)
4. 로컬 환경에서 동작 (클라우드 의존성 없음)

## 고려한 옵션들

### 1. SQLite
```python
# 전통적인 경량 DB
conn = sqlite3.connect("data.db")
cursor.execute("SELECT * FROM commits")
```
- 장점: 익숙함, 안정성
- 단점: 분석 쿼리 느림, Parquet 직접 지원 안 함

### 2. DuckDB (선택)
```python
# 분석 특화 임베디드 DB
conn = duckdb.connect("warehouse.duckdb")
conn.execute("SELECT * FROM 'data/*.parquet'")
```
- 장점: Parquet 네이티브, 분석 쿼리 빠름, SQL 표준
- 단점: 상대적으로 새로움 (2019~)

### 3. Polars + 파일 기반
```python
# DataFrame 라이브러리
df = pl.scan_parquet("data/*.parquet")
df.filter(pl.col("status") == "merged").collect()
```
- 장점: 빠름, Rust 기반
- 단점: SQL 아님, 스키마 관리 어려움

## 결정

**DuckDB**를 선택한다.

### 아키텍처

```
storage/
├── warehouse/
│   ├── __init__.py
│   ├── base.py              # BaseWarehouse 추상 클래스
│   ├── duckdb_warehouse.py  # DuckDB 구현
│   ├── config.py            # Pydantic 설정
│   └── schema.py            # 테이블 스키마 정의
└── tests/
    └── test_warehouse.py
```

### 핵심 컴포넌트

#### 1. BaseWarehouse (추상 클래스)

```python
class BaseWarehouse(ABC):
    """Warehouse 공통 인터페이스"""

    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def create_table(self, name: str, schema: TableSchema) -> None: ...

    @abstractmethod
    def insert(self, table: str, data: list[dict]) -> InsertResult: ...

    @abstractmethod
    def query(self, sql: str) -> QueryResult: ...

    @abstractmethod
    def load_parquet(self, table: str, path: Path) -> InsertResult: ...
```

**왜 추상 클래스인가?**
- Collector와 동일한 패턴 유지
- 향후 다른 DB 지원 가능 (PostgreSQL, BigQuery 등)

#### 2. DuckDBWarehouse

```python
class DuckDBWarehouse(BaseWarehouse):
    """DuckDB 구현"""

    def __init__(self, config: DuckDBConfig):
        self.config = config
        self.conn: Optional[duckdb.DuckDBPyConnection] = None

    def connect(self) -> None:
        self.conn = duckdb.connect(str(self.config.db_path))

    def load_parquet(self, table: str, path: Path) -> InsertResult:
        """Parquet 파일을 테이블에 로드"""
        self.conn.execute(f"""
            INSERT INTO {table}
            SELECT * FROM read_parquet('{path}')
        """)
```

#### 3. 스키마 정의

```python
@dataclass
class Column:
    name: str
    dtype: str  # "VARCHAR", "INTEGER", "TIMESTAMP", etc.
    nullable: bool = True
    primary_key: bool = False

@dataclass
class TableSchema:
    name: str
    columns: list[Column]

    def to_ddl(self) -> str:
        """CREATE TABLE DDL 생성"""
        cols = ", ".join(
            f"{c.name} {c.dtype}" + (" PRIMARY KEY" if c.primary_key else "")
            for c in self.columns
        )
        return f"CREATE TABLE IF NOT EXISTS {self.name} ({cols})"
```

#### 4. 결과 객체

```python
@dataclass
class InsertResult:
    table: str
    rows_affected: int
    status: str  # "success" | "fail"
    errors: list[str] = field(default_factory=list)

@dataclass
class QueryResult:
    columns: list[str]
    rows: list[tuple]
    row_count: int

    def to_dataframe(self) -> "pd.DataFrame":
        import pandas as pd
        return pd.DataFrame(self.rows, columns=self.columns)
```

### 사용 예시

```python
# 초기화
config = DuckDBConfig(db_path="./data/warehouse.duckdb")
warehouse = DuckDBWarehouse(config)
warehouse.connect()

# 스키마 생성
commits_schema = TableSchema(
    name="github_commits",
    columns=[
        Column("sha", "VARCHAR", primary_key=True),
        Column("message", "VARCHAR"),
        Column("author_name", "VARCHAR"),
        Column("committed_at", "TIMESTAMP"),
    ]
)
warehouse.create_table("github_commits", commits_schema)

# Parquet 로드
result = warehouse.load_parquet("github_commits", Path("./output/commits.parquet"))
print(f"Loaded {result.rows_affected} rows")

# 쿼리
result = warehouse.query("SELECT author_name, COUNT(*) FROM github_commits GROUP BY 1")
print(result.to_dataframe())
```

## 근거

1. **Parquet 네이티브 지원**
   - `read_parquet()` 함수로 직접 쿼리
   - 파일 → 테이블 로드 한 줄로 가능

2. **분석 쿼리 최적화**
   - 컬럼 지향 처리
   - 벡터화 연산
   - 대용량 데이터에서 SQLite 대비 10~100배 빠름

3. **SQL 표준**
   - 익숙한 SQL 문법
   - Window 함수, CTE 등 고급 기능 지원

4. **제로 의존성**
   - 서버 불필요 (임베디드)
   - 단일 파일 (`warehouse.duckdb`)
   - pip install duckdb 하나로 끝

5. **패턴 일관성**
   - Collector와 동일한 추상 클래스 패턴
   - 팀 내 코드 스타일 통일

## 트레이드오프

| 측면 | 장점 | 단점 |
|------|------|------|
| 성능 | 분석 쿼리 빠름 | OLTP(빈번한 write) 느림 |
| 호환성 | SQL 표준 | PostgreSQL과 100% 호환 아님 |
| 성숙도 | 빠르게 발전 중 | SQLite만큼 battle-tested 아님 |
| 확장성 | 로컬에서 충분 | 분산 처리는 미지원 |

## E2E 파이프라인 비전

```
[GitHub API] → [Collector] → [Parquet 파일]
                                   ↓
                            [DuckDB Warehouse]
                                   ↓
                            [SQL 분석/대시보드]
```

```python
# 향후 통합 코드
collector = GitHubCollector(config)
results = collector.collect()

warehouse = DuckDBWarehouse(warehouse_config)
for result in results:
    warehouse.load_parquet(result.resource, result.output_path)

# 분석
warehouse.query("""
    SELECT DATE(committed_at), COUNT(*)
    FROM github_commits
    GROUP BY 1
    ORDER BY 1
""")
```

## 질문 (Gemini 리뷰 요청)

1. **추상 클래스 설계**: `connect()/close()` 대신 context manager (`__enter__/__exit__`)가 더 나을까?

2. **스키마 관리**: TableSchema를 코드로 정의하는 것 vs SQL 파일로 관리하는 것, 어떤 게 더 나을까?

3. **에러 핸들링**: DuckDB 예외를 그대로 노출할지, 커스텀 예외로 감쌀지?

4. **테스트 전략**: in-memory DuckDB (`:memory:`)로 테스트하면 충분할까?

## 면접 대비 질문

Q: "왜 DuckDB를 선택했나요?"
A: "분석 워크로드에 최적화된 임베디드 DB이기 때문입니다. Parquet 파일을 네이티브로 지원해서 데이터 파이프라인과 자연스럽게 연결되고, SQL 표준을 지원해서 학습 곡선이 낮습니다. PostgreSQL 같은 서버 기반 DB는 오버킬이고, SQLite는 분석 쿼리에 느립니다."

Q: "DuckDB의 한계는?"
A: "OLTP 워크로드에는 적합하지 않습니다. 빈번한 INSERT/UPDATE가 필요하면 PostgreSQL이 나을 수 있어요. 또한 분산 처리를 지원하지 않아서 단일 머신 규모를 넘어서면 BigQuery 같은 클라우드 솔루션을 고려해야 합니다."
