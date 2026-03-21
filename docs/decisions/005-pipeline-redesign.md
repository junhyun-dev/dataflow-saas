# ADR 005: 파이프라인 재설계 — 4단계 시작, 진화형 아키텍처

## 상태

승인됨 (2026-03-21)

## 컨텍스트

Session 1에서 전체 아키텍처를 리뷰했다. 회사 시스템(7단계), Medallion Architecture, dbt 패턴을 조사하고, Gemini 리뷰를 거쳤다.

**핵심 발견:**
- 회사 시스템은 Convert→Tag→TagPrep→Load→SRCH→S→H→RPT 8단계
- 업계 표준은 Bronze→Silver→Gold (Medallion) 또는 staging→intermediate→mart (dbt)
- Gemini는 "8-9단계 유지/강화"를 권장했으나, 학습 프로젝트 특성상 부적절

**문제:**
- 처음부터 9단계를 설계하면 "왜 나누는지" 체감 못 함
- 구현만 하게 되고, 면접에서 자기 경험으로 설명 불가

## 결정

**4단계로 시작하고, 만들면서 필요할 때 분리한다.**

```
Collect → Load → Transform(SQL) → Serve(API)
```

### 각 단계 책임

| 단계 | 엔진 | 책임 | 기존 코드 |
|------|------|------|----------|
| Collect | Python | 외부 API → JSON | GitHubCollector ✅ |
| Load | Python | JSON → DuckDB (flatten, 타입 변환, 메타데이터) | DuckDBWarehouse ✅ |
| Transform | SQL | staging(View) → intermediate → mart(Table) → report(Table) | 새로 구현 |
| Serve | FastAPI | report 테이블 → 차트 API | 새로 구현 |

### Transform 내부 레이어 (dbt 패턴)

```sql
stg_*    -- View: 컬럼 추출, 타입 캐스팅
int_*    -- View/Table: 필터, 집계, JOIN
mart_*   -- Table: KPI 계산, 크로스 테이블
rpt_*    -- Table: 차트 포맷 (FastAPI가 읽는 대상)
```

### 복잡성 추가 시점 (진화 계획)

| 시점 | 문제 | 분리되는 것 |
|------|------|-----------|
| DAG 재실행 시 데이터 중복 | 멱등성 없음 | Upsert/Partition Swap |
| 2번째 소스 추가 | Load 코드 소스별 다름 | Normalize 분리 + Config-driven |
| SQL 모델 10개 초과 | 파일 관리 어려움 | SQL runner 모듈 |
| DQ 이슈 발생 | 잘못된 데이터가 mart까지 감 | Quality Gate |
| 메타데이터 추적 필요 | 데이터 출처 불명 | Enrich 단계 분리 |

## 구현 순서

1. E2E 하드코딩 (commits → DuckDB → 1개 mart → 1개 API 엔드포인트)
2. Airflow DAG 오케스트레이션
3. SQL 모델 추가 (issues, PRs)
4. 멱등성 구현
5. Config-driven 리팩토링

## 회사 패턴 DO/DON'T

### DO (가져갈 것)
- 3단계 모델링: staging → intermediate/mart → report
- 역추적 가능 구조: report → mart → staging → raw 추적
- status 체계: 지표별 상태 관리
- 날짜 컬럼 필수: 모든 모델에 day/month

### DON'T (피할 것)
- EAV 패턴: 소스별 명시적 스테이징 테이블 사용
- Config 과잉 유연성: 어댑터 패턴, config은 간단하게
- 태깅 3단계 분리: Load에서 메타데이터 한번에
- 날짜 정규화 지연: Load 시점에 즉시 DATE 변환

## 근거

- 학습 목적: "왜 나누는지"를 만들면서 체감하는 게 가치
- 회사 반면교사: EAV, 과잉 config 같은 실제 문제점 회피
- 면접 대응: "이렇게 시작했는데 이런 문제가 생겨서 나눴다"로 설명 가능
- Gemini 리뷰 결과: 9단계 권장 → 반론 후 4단계 채택 (주도적 판단)

## 참고 자료

- Medallion Architecture (Bronze→Silver→Gold)
- dbt staging→intermediate→mart 패턴
- 회사 시스템 분석: `PROMPT_hyperlounge_system_analysis.md`
- Gemini 리뷰: `.ai_gemini_response.md` (2026-03-20)
