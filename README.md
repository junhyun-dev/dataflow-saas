# dataflow-saas

B2B 데이터 분석 SaaS 플랫폼 (토이 프로젝트)

## 개요

다양한 데이터 소스를 수집, 변환, 가공하여 시각화하는 멀티테넌트 분석 플랫폼.

```
수집 → 변환 → 저장 → 가공 → 시각화
```

## 구조

```
dataflow-saas/
├── auth/                  # 인증/권한 (Keycloak, API Gateway)
├── ingestion/             # 데이터 수집 (Collector, Crawler)
├── transform/             # 데이터 변환 (Converter, Tagger, LLM)
├── orchestration/         # 워크플로우 (Airflow DAG, Scheduler)
├── storage/               # 데이터 저장 (Warehouse, Sync, Catalog)
├── analytics/             # 데이터 가공/모델링 (S→H→RPT)
├── visualization/         # 시각화 API (Chart API, Dashboard)
├── observability/         # 모니터링 (Monitoring, Notification)
├── agents/                # 자동화 (AI Agent, Instance Manager)
├── infra/                 # 인프라 (Terraform, Docker)
└── docs/                  # 문서
```

## 데이터 소스 (예정)

- [ ] GitHub API (개발팀 메트릭) - 첫 번째
- [ ] 이커머스 CSV
- [ ] 로그 파일
- [ ] IoT 센서

## 시작하기

TBD

## 관련 문서

- [Architecture](docs/architecture.md)
- [Decisions](docs/decisions/)
