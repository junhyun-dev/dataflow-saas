# Dataflow SaaS 학습 계획

> "처음부터 만들어보는" SaaS 데이터 파이프라인
> 방법론: ~/active-learning/method/learning-protocol.md

---

## Part 1: 기존 코드 파악 + 저장소 완성 (Dive + Build)

> 목표: 이미 만든 converter/collector를 내 것으로 만들고, storage 레이어 완성

### Session 1: 전체 아키텍처 + 기존 코드 리뷰 ✅
- **타입**: Dive
- **범위**: architecture.md, 전체 폴더 구조, ADR 4개 리뷰 + 회사 시스템 분석
- **SKILL-TREE**: 파이프라인 설계
- **산출물**: ADR 005 (파이프라인 재설계), Gemini 리뷰 완료
- **핵심 결정**: 4단계(Collect→Load→Transform→Serve)로 시작, 진화형 아키텍처
- **학습 포인트**: Medallion Architecture, dbt 패턴, 회사 DO/DON'T 분석
- [x] 완료 (2026-03-21)

### Session 2: E2E 하드코딩 — Collect → Load
- **타입**: Build
- **범위**: GitHubCollector 출력 → DuckDB raw 테이블 적재
- **SKILL-TREE**: ETL/ELT 설계, 스키마 설계
- **핵심 질문**: "JSON을 어떻게 flatten해서 테이블로 넣을까? 메타데이터는?"
- **산출물**: `raw_commits`, `raw_issues`, `raw_prs` 테이블 생성 + 데이터 적재 코드
- **회사 DON'T**: EAV 안 씀 — 소스별 명시적 스키마
- [ ] 완료

### Session 3: E2E 하드코딩 — Transform (SQL 모델)
- **타입**: Build
- **범위**: DuckDB 위에 staging → intermediate → mart → report SQL 모델
- **SKILL-TREE**: ★ Data Modeling, Medallion Architecture
- **kb**: Data-Modeling Ch7 (Medallion), Ch8 (dbt 패턴)
- **핵심 질문**: "stg→int→mart→rpt 각 레이어가 왜 필요한지 직접 체감했나?"
- **산출물**: SQL 모델 파일들 + `mart_developer_kpi`, `rpt_team_dashboard`
- [ ] 완료

### Session 4: E2E 하드코딩 — Serve (FastAPI)
- **타입**: Build
- **범위**: report 테이블 → FastAPI 엔드포인트 → 차트 데이터 응답
- **SKILL-TREE**: API 설계
- **핵심 질문**: "API가 DuckDB를 직접 찌르는 구조의 트레이드오프는?"
- **산출물**: FastAPI 엔드포인트 + E2E 파이프라인 최초 관통 🎉
- [ ] 완료

### Session 5: E2E 수동 실행 → 문제 발견
- **타입**: Dive + Build
- **범위**: 전체 파이프라인 수동 실행, 문제점 기록, 개선
- **SKILL-TREE**: 디버깅, 파이프라인 운영
- **핵심 질문**: "재실행하면 데이터 중복되나? 날짜 처리는 맞나?"
- **산출물**: 문제점 목록 + 멱등성 1차 구현 + ADR
- [ ] 완료

---

## Part 2: 오케스트레이션 + 확장 (Build)

> 목표: Airflow로 자동화 + 2번째 소스 추가하면서 Config-driven 리팩토링

### Session 6-7: Airflow DAG 설계 + 구현
- **타입**: Build
- **범위**: orchestration/ (Collect → Load → Transform DAG)
- **SKILL-TREE**: ★ 오케스트레이션, ★ 멱등성 & Backfill, DAG 설계
- **kb**: Airflow Ch7 (Scheduling), Ch9 (Executors)
- **핵심 질문**: "태스크 단위를 어떻게 나눌까? 실패하면?"
- **산출물**: Airflow DAG + Docker Compose + ADR
- [ ] 완료

### Session 8: 2번째 소스 추가 → Config-driven 리팩토링
- **타입**: Build
- **범위**: 새 소스(CSV or API) 추가, Load 코드 리팩토링
- **SKILL-TREE**: Pydantic, 설정 기반 파이프라인, 어댑터 패턴
- **핵심 질문**: "소스 추가할 때 코드 복붙 vs 설정 추가 — 어디서 경계를 긋나?"
- **산출물**: Config-driven Load + 어댑터 패턴 + ADR
- **회사 DON'T**: config 과잉 유연성 피함 — 어댑터 패턴으로
- [ ] 완료

### Session 9-10: SQL 모델 확장 + 증분 처리
- **타입**: Build
- **범위**: 2번째 소스 SQL 모델 추가, mart 확장, 증분 처리 도입
- **SKILL-TREE**: ★ Medallion Architecture, ★ Data Modeling
- **kb**: Data-Modeling Ch7 (Medallion), Ch8 (dbt 패턴)
- **핵심 질문**: "전체 재계산 vs 증분 — 언제 어떤 걸 쓰나?"
- **산출물**: 확장된 SQL 모델 + 증분 처리 + ADR
- [ ] 완료

---

## Part 3: 운영 품질 (Build)

> 목표: DQ + 모니터링 + CI/CD로 "운영 가능한" 파이프라인

### Session 11: 데이터 품질 체크
- **타입**: Build
- **범위**: Quality Gate (Load 후 + Transform 후 검증)
- **SKILL-TREE**: ★ Data Quality, DQ 게이트
- **kb**: Great-Expectations Ch1-3
- **산출물**: DQ 모듈 + Airflow 연동
- [ ] 완료

### Session 12: 모니터링 + 알림
- **타입**: Build
- **범위**: observability/ (파이프라인 메트릭, status 체계, 알림)
- **SKILL-TREE**: Prometheus, Grafana
- **kb**: Prometheus-Grafana Ch2-3
- **회사 참고**: blind_history, status_code 체계, 4레벨 모니터링
- **산출물**: 대시보드 + 알림 설정
- [ ] 완료

### Session 13: CI/CD + Docker
- **타입**: Build
- **범위**: GitHub Actions + Docker Compose 배포
- **SKILL-TREE**: ★ CI, ★ Docker
- **kb**: CI-CD Ch6-7, Docker-Practical Ch3-4
- **산출물**: CI 워크플로우 + Docker 배포
- [ ] 완료

---

## 진행 상태

| Part | 세션 | 상태 |
|------|------|------|
| Part 1 | 1/5 완료 | 🔄 진행 중 |
| Part 2 | 0/5 완료 | ⬜ 대기 |
| Part 3 | 0/3 완료 | ⬜ 대기 |

---

## SKILL-TREE 학습 추적

| SKILL-TREE 항목 | 학습 세션 | 수준 | 블로그 |
|----------------|----------|:----:|:-----:|
| 파이프라인 설계 | Session 1 | 💬 | |
| Medallion Architecture | Session 1 | 💬 | |
| dbt staging/mart 패턴 | Session 1 | 👀 | |

> 수준: 👀 노출 → 💬 설명가능 → 🔧 구현가능 → 🎤 면접답변가능

---

## 글감 축적소 + 블로그 추적

| # | 글감 제목 | 유형 | 출처 세션 | 상태 | 파일 |
|---|----------|------|----------|:----:|------|
| 1 | 회사 파이프라인 패턴을 일반화한 과정 (DO/DON'T) | 설계 | S1 | 📝 | |
| 2 | Gemini 의견에 끌려가지 않고 주도적으로 설계한 이야기 | 회고 | S1 | 📝 | |

> 상태: 📝 글감 → ✍️ 작성중 → ✅ 발행

---

*작성: 2026-03-20*
*업데이트: 2026-03-21 (Session 1 완료, 세션 구조 재편)*
