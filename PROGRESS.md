# Progress Tracker

## Quick View

```
┌─────────────────────────────────────────────────────────────┐
│  🎯 현재 단계: Phase 1 - 핵심 파이프라인                     │
│  📍 현재 위치: 통합 테스트 + 셀프 리뷰 완료!                 │
│  📊 전체 진행률: 40%                                        │
│                                                             │
│  Phase 1 ████████░░░░░░░░░░░░ 40%  (핵심 파이프라인)        │
│  Phase 2 ░░░░░░░░░░░░░░░░░░░░ 0%   (확장 기능)              │
│  Phase 3 ░░░░░░░░░░░░░░░░░░░░ 0%   (운영 기능)              │
│  Phase 4 ░░░░░░░░░░░░░░░░░░░░ 0%   (고급 기능)              │
│                                                             │
│  다음 할 일: storage/warehouse (DuckDB) 또는 통합 테스트     │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase별 진행 상황

### Phase 1: 핵심 파이프라인 (Tier 1)

| 컴포넌트 | 상태 | 진행률 | 비고 |
|---------|------|--------|------|
| 프로젝트 구조 | ✅ 완료 | 100% | 폴더, README, architecture.md |
| transform/converter | ✅ 기본 완료 | 60% | Pipeline, Loader, Parser, Writer |
| ingestion/collector | ✅ 기본 완료 | 60% | BaseCollector, GitHubCollector, CLI |
| storage/warehouse | 🔲 예정 | 0% | DuckDB |

### Phase 2: 확장 기능 (Tier 2)

| 컴포넌트 | 상태 | 진행률 | 비고 |
|---------|------|--------|------|
| analytics/models | 🔲 예정 | 0% | S→H→RPT 모델 |
| visualization/chart-api | 🔲 예정 | 0% | FastAPI |
| orchestration/scheduler | 🔲 예정 | 0% | 간단한 스케줄러 |
| auth/api-gateway | 🔲 예정 | 0% | JWT |

### Phase 3: 운영 기능 (Tier 3)

| 컴포넌트 | 상태 | 진행률 | 비고 |
|---------|------|--------|------|
| observability/monitoring | 🔲 예정 | 0% | |
| observability/notification | 🔲 예정 | 0% | |
| storage/sync | 🔲 예정 | 0% | |

### Phase 4: 고급 기능 (Tier 4)

| 컴포넌트 | 상태 | 진행률 | 비고 |
|---------|------|--------|------|
| agents/ai-agent | 🔲 예정 | 0% | |
| agents/instance-manager | 🔲 예정 | 0% | 회사 개선 사항 반영 |
| transform/llm-transform | 🔲 예정 | 0% | |

---

## 상세 체크리스트

### transform/converter (기본 완료!)

- [x] 기본 구조 잡기
  - [x] Pipeline 클래스
  - [x] ExcelLoader 클래스
  - [x] TableParser 클래스
  - [x] ParquetWriter 클래스
- [x] Config 스키마 (Pydantic)
- [x] 테스트 작성 (5개 통과)
- [ ] 고도화 (나중에)
  - [ ] 머지셀 처리
  - [ ] 멀티 헤더 개선
  - [ ] 에러 처리 강화

### ingestion/collector (기본 완료!)

- [x] BaseCollector 추상 클래스
- [x] GitHubCollector 구현
  - commits, issues, PRs, releases 수집
  - Rate limit 처리
  - 페이지네이션
  - 데이터 정규화
- [x] CLI 엔트리포인트
- [x] 테스트 작성 (12개 통과)
- [x] 통합 테스트 (실제 GitHub API 호출, 4개 통과)
- [x] 로깅 추가 (logging 모듈)
- [ ] 고도화 (나중에)
  - [ ] async 지원 (httpx)
  - [ ] 다른 Collector 추가 (Jira, Slack 등)
  - [ ] Webhook 수신
  - [ ] 증분 수집 (last_sync 기반)

---

## 주간 기록

### Week 1 (2026-03-02 ~)

**완료:**
- [x] 프로젝트 구조 생성
- [x] README.md 작성
- [x] docs/architecture.md 작성
- [x] PROGRESS.md, CLAUDE.md 작성
- [x] transform/converter 기본 구조
  - config/schema.py (Pydantic)
  - loader/excel_loader.py
  - parser/table_parser.py
  - writer/parquet_writer.py
  - pipeline.py
- [x] converter 테스트 5개 통과
- [x] ingestion/collector 기본 구조
  - BaseCollector 추상 클래스
  - GitHubCollector (commits, issues, PRs, releases)
  - CLI 엔트리포인트
  - Pydantic Config
- [x] collector 테스트 12개 통과
- [x] 통합 테스트 (실제 GitHub API, 4개 통과)
- [x] 셀프 리뷰 + 2026 best practices 조사
- [x] 리뷰 문서 작성 (docs/reviews/2026-03-03-self-review.md)
- [x] 코드 개선 (unused imports 정리, logging 추가)

**배운 것:**
- 전체 SaaS 아키텍처 설계
- 회사 V2 설계 분석
- 책임 분리 패턴 (Pipeline → Loader → Parser → Writer)
- GitHub API 페이지네이션, Rate Limit 처리
- 추상 클래스 기반 Collector 패턴
- 2026 Python ETL best practices (멱등성, async, structlog)
- Pydantic v2 성능 최적화 팁

**다음 목표:**
- storage/warehouse (DuckDB) 또는 async 지원 추가

---

## 회사 코드 연결

| 토이 컴포넌트 | 회사 코드 | 상태 |
|--------------|----------|------|
| transform/converter | collector/excel/v2 | 기본 구조 동일하게 구현 완료 |
| agents/instance-manager | collector/cloud_instance | 회사 개선 예정 |
| ingestion/collector | collector/ | 참고만 |

---

## 마일스톤

| 마일스톤 | 목표 | 상태 |
|---------|------|------|
| MVP (converter + collector) | - | 🔄 진행 중 |
| 첫 번째 데이터 파이프라인 | - | 🔲 예정 |
| 차트 API 완성 | - | 🔲 예정 |
| 전체 통합 | - | 🔲 예정 |

---

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-03-02 | 프로젝트 초기 구조 생성, PROGRESS.md 작성 |
| 2026-03-02 | transform/converter 기본 구조 완료 (테스트 5개 통과) |
| 2026-03-03 | ingestion/collector 기본 구조 완료 (테스트 12개 통과) |
| 2026-03-03 | 통합 테스트 완료, 셀프 리뷰 + 2026 best practices 조사 |
| 2026-03-03 | ROADMAP, ADR 3개, STUDY-GUIDE 작성 |
