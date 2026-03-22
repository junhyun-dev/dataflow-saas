"""
Chart API — mart 테이블을 차트 데이터로 서빙

E2E 파이프라인의 마지막 단계: Collect → Load → Transform → Serve(여기)

사용법:
    # 프로젝트 루트에서
    python -m uvicorn visualization.chart-api.app:app --reload --port 8000

    # 또는
    python -m visualization.chart-api.app
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from storage.warehouse import DuckDBConfig, DuckDBWarehouse

app = FastAPI(
    title="DataFlow SaaS - Chart API",
    description="Developer Productivity Dashboard 데이터 서빙",
    version="0.1.0",
)

DB_PATH = project_root / "data" / "warehouse.duckdb"


def get_warehouse() -> DuckDBWarehouse:
    """DuckDB 연결 (read-only)"""
    config = DuckDBConfig(db_path=DB_PATH, read_only=True)
    return DuckDBWarehouse(config)


@app.get("/")
def root():
    return {"service": "DataFlow Chart API", "status": "ok"}


@app.get("/api/v1/developer/weekly")
def developer_weekly(
    repo_owner: str = Query(default=None, description="Filter by repo owner"),
    repo_name: str = Query(default=None, description="Filter by repo name"),
    limit: int = Query(default=50, ge=1, le=500, description="Max rows"),
):
    """주간 개발자 생산성 KPI"""
    sql = "SELECT * FROM mart_developer_weekly WHERE 1=1"
    params = []

    if repo_owner:
        sql += " AND repo_owner = ?"
        params.append(repo_owner)
    if repo_name:
        sql += " AND repo_name = ?"
        params.append(repo_name)

    sql += " ORDER BY week_start DESC, developer"
    sql += f" LIMIT {limit}"

    with get_warehouse() as warehouse:
        result = warehouse.query(sql)

    rows = []
    for row in result.rows:
        rows.append(dict(zip(result.columns, row)))

    return {
        "data": rows,
        "count": len(rows),
        "query": {
            "repo_owner": repo_owner,
            "repo_name": repo_name,
            "limit": limit,
        },
    }


@app.get("/api/v1/tables")
def list_tables():
    """사용 가능한 테이블 목록 + 행 수"""
    tables = [
        "raw_commits",
        "raw_pull_requests",
        "int_commit_daily",
        "int_pr_metrics",
        "mart_developer_weekly",
    ]
    result = {}

    with get_warehouse() as warehouse:
        for table in tables:
            try:
                count = warehouse.query(f"SELECT COUNT(*) FROM {table}")
                result[table] = count.rows[0][0]
            except Exception:
                result[table] = None

    return {"tables": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
