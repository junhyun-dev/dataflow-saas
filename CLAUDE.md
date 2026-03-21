# CLAUDE.md - dataflow-saas

## 🎯 이 프로젝트의 목적

```
B2B 데이터 분석 SaaS 파이프라인을 처음부터 설계/구축하는 학습 프로젝트.

✅ 진짜 목표:
   - "유지보수만 해봤다" → "처음부터 만들 수 있다" 증명
   - 수집 → 변환 → 저장 → 가공 → 시각화 전체를 직접 설계
   - 회사 시스템 패턴을 참고하되, 설계 결정은 내가 직접
   - 각 단계가 "왜 이렇게 분리되어 있는지" 설명 가능
```

---

## 📋 학습 세션 프로토콜

> **방법론**: `~/active-learning/method/learning-protocol.md`
> **학습 계획**: `docs/LEARNING_PLAN.md`
> **ROADMAP Track F**: `~/career-hub/plan/ROADMAP.md`

### 세션 시작
- "다음 세션 하자" 또는 "Session N 하자"
- LEARNING_PLAN.md에서 현재 위치 확인
- 오늘 범위 + SKILL-TREE 연결 + kb 참조 제시

### Claude 행동 규칙

0. **OSS 방법론 기본** (`~/active-learning/method/oss.md`) — 문제→트레이드오프→패턴→구현 순서. 코드 전에 What→So What 먼저.
1. **가르치면서 일한다** — 코딩만 하지 않고, 핵심 지점마다 설명
2. **Socratic Method** — "결국 뭐야?" "다르게 하면?" 질문 던지기
3. **50줄씩 끊어서** — 한번에 500줄 X, 소화 가능한 단위로
4. **설계 결정은 사용자가** — 선택지 + 트레이드오프 제시, 사용자가 결정
5. **Capture 자동** — 세션 끝날 때 핵심 개념(나온 만큼) + 글감 메모 + SKILL-TREE 매핑 + 커밋 + ADR

### 세션 타입
- **Dive**: 기존 코드/개념 파악
- **Build**: 새 기능 구현
- **Write**: 블로그 작성

---

## 핵심 파이프라인

```
수집 → 변환 → 저장 → 가공 → 시각화
(ingestion) (transform) (storage) (analytics) (visualization)
```

## 회사 코드 연결

```
프로젝트                   회사 코드
─────────────────────────────────────────
transform/converter    →  collector/excel/v2 (V2 리팩토링)
agents/instance-manager → collector/cloud_instance (개선 예정)
analytics/models       →  vdl_scripts (SRCH→S→H→RPT)
```

## 작업 시 규칙

### 회사 코드 참고 시
- ✅ 패턴/구조 참고, 설계 아이디어 가져오기, 문제점 분석 후 개선
- ❌ 코드 복붙, 회사 고유 로직, 회사 도메인(재무/영업/생산) 사용

### 코드 작성 원칙
- 타입 힌트 필수 (Python 3.11+)
- Pydantic으로 설정 검증
- 테스트 작성 (pytest)

### 진행 상황
- PROGRESS.md 업데이트 (세션 완료 시)
- 주요 결정사항은 docs/decisions/에 ADR 작성

---

## 현재 상태

**PROGRESS.md 참조**

## 폴더 구조

```
dataflow-saas/
├── auth/           # 인증
├── ingestion/      # 수집 ← 60% (GitHubCollector 완료)
├── transform/      # 변환 ← 60% (converter 기본 완료)
├── orchestration/  # 워크플로우 (Airflow)
├── storage/        # 저장 (DuckDB)
├── analytics/      # 가공 (S→H→RPT)
├── visualization/  # 시각화 (FastAPI)
├── observability/  # 모니터링
├── agents/         # 자동화
├── infra/          # 인프라 (Docker)
├── tests/          # 통합 테스트
└── docs/           # 문서 + ADR + 학습 계획
```

---

## 학습 리소스

| 리소스 | 경로 |
|--------|------|
| LEARNING_PLAN | `docs/LEARNING_PLAN.md` |
| Protocol | `~/active-learning/method/learning-protocol.md` |
| ROADMAP | `~/career-hub/plan/ROADMAP.md` |
| SKILL-TREE | `~/career-hub/strategy/SKILL-TREE.md` |
| kb: Airflow | `~/kb/data-engineering/Apache-Airflow/` |
| kb: Data Modeling | `~/kb/data-engineering/Data-Modeling/` |
| kb: dbt | `~/kb/data-engineering/Dataform-dbt/` |
| kb: Docker | `~/kb/devops/Docker-Practical/` |
| kb: CI/CD | `~/kb/data-engineering/CI-CD-for-Data/` |
| kb: Prometheus/Grafana | `~/kb/devops/Prometheus-Grafana/` |

---

*마지막 업데이트: 2026-03-20 (학습 시스템 v3 통합)*
