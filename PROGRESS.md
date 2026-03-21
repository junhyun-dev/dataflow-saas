# Progress Tracker

## Quick View

```
┌─────────────────────────────────────────────────────────────┐
│  🎯 현재 단계: Part 1 - E2E 하드코딩                        │
│  📍 현재 위치: Session 1 완료 (아키텍처 재설계)               │
│  📊 전체 진행률: Part 1: 1/5, Part 2: 0/5, Part 3: 0/3     │
│                                                             │
│  Part 1 ██░░░░░░░░░░░░░░░░░░ 20%  (E2E 하드코딩)           │
│  Part 2 ░░░░░░░░░░░░░░░░░░░░ 0%   (Airflow + 확장)         │
│  Part 3 ░░░░░░░░░░░░░░░░░░░░ 0%   (운영 품질)              │
│                                                             │
│  다음 할 일: Session 2 — Collect → Load 연결                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 파이프라인 설계 (ADR 005)

```
4단계로 시작, 진화형 아키텍처:

Collect → Load → Transform(SQL) → Serve(API)
  ✅       🔲       🔲              🔲

구현 순서:
1. E2E 하드코딩 (commits → DuckDB → mart → API)  ← 지금 여기
2. Airflow DAG 오케스트레이션
3. SQL 모델 추가 (issues, PRs)
4. 멱등성 구현
5. Config-driven 리팩토링 (2번째 소스 추가 시)
```

---

## 기존 컴포넌트 상태

| 컴포넌트 | 상태 | 비고 |
|---------|------|------|
| ingestion/collector | ✅ 동작 | GitHubCollector, 테스트 12개 |
| transform/converter | ✅ 동작 | Excel→Parquet, 테스트 5개 |
| storage/warehouse | ✅ 동작 | DuckDB, Context Manager |

---

## 학습 세션 진행

| Session | 주제 | 상태 |
|---------|------|------|
| **S1** | 전체 아키텍처 + 기존 코드 리뷰 | ✅ 완료 (2026-03-21) |
| **S2** | E2E: Collect → Load | ⬜ 다음 |
| S3 | E2E: Transform (SQL 모델) | ⬜ |
| S4 | E2E: Serve (FastAPI) | ⬜ |
| S5 | E2E 수동 실행 → 문제 발견 | ⬜ |
| S6-7 | Airflow DAG | ⬜ |
| S8 | Config-driven 리팩토링 | ⬜ |
| S9-10 | SQL 모델 확장 + 증분 처리 | ⬜ |
| S11 | Data Quality | ⬜ |
| S12 | 모니터링 | ⬜ |
| S13 | CI/CD + Docker | ⬜ |

상세: `docs/LEARNING_PLAN.md`

---

## 주간 기록

### Week 1 (2026-03-02 ~)

**완료:**
- [x] 프로젝트 구조 생성 + README + architecture.md
- [x] transform/converter 기본 구조 (Pipeline→Loader→Parser→Writer, 테스트 5개)
- [x] ingestion/collector 기본 구조 (BaseCollector→GitHubCollector, 테스트 12개)
- [x] storage/warehouse (DuckDBWarehouse, Context Manager, Gemini 리뷰 반영)
- [x] 통합 테스트 (GitHub API, 4개 통과)
- [x] 셀프 리뷰 + ADR 4개

### Week 3 (2026-03-21)

**완료:**
- [x] Session 1: 전체 아키텍처 재설계
  - 회사 시스템 7단계 분석 (PROMPT_hyperlounge_system_analysis.md)
  - Medallion Architecture + dbt 패턴 웹 리서치
  - Gemini 리뷰 → 셀프 리뷰 2 (주도적 판단)
  - 4단계 파이프라인 확정 (ADR 005)
  - 회사 DO/DON'T 정리 (EAV 안티패턴, Config 과잉 유연성 등)
  - LEARNING_PLAN 세션 구조 재편 (14→13세션)

**핵심 결정:**
- 9단계(Gemini 권장) → 4단계(Claude 판단)로 축소
- "만들면서 필요할 때 분리" 진화형 아키텍처 채택
- 회사 EAV 패턴 대신 소스별 명시적 스키마

---

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-03-02 | 프로젝트 초기 구조 생성 |
| 2026-03-02 | transform/converter 기본 완료 |
| 2026-03-03 | ingestion/collector 기본 완료, 통합 테스트, ADR 3개 |
| 2026-03-21 | Session 1 완료: 아키텍처 재설계 (ADR 005), LEARNING_PLAN 재편 |
