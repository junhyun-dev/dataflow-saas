# Development Roadmap

## 목표

**최종 목표**: 데이터 파이프라인 SaaS의 핵심 컴포넌트를 직접 구현하면서 학습

**학습 목표**:
1. 데이터 엔지니어링 패턴 체득
2. 회사 코드 이해도 향상
3. 포트폴리오용 프로젝트 완성

---

## Phase 1: 핵심 파이프라인 (현재)

### 1.1 ✅ Converter (완료)

**뭘 만들었나**: Excel → Parquet 변환기

**왜 이게 먼저인가**:
- 회사 V2 설계가 이미 있어서 참고 가능
- 데이터 파이프라인의 가장 기본 (파일 변환)
- 단순하지만 중요한 패턴 학습: 책임 분리

**학습 포인트**:
- Pipeline 패턴 (오케스트레이터)
- Loader/Parser/Writer 분리
- Pydantic Config

### 1.2 ✅ Collector (완료)

**뭘 만들었나**: GitHub API 데이터 수집기

**왜 이게 두 번째인가**:
- API 수집은 데이터 엔지니어링 필수 스킬
- 외부 API → 내부 포맷 변환 패턴
- Rate limit, 페이지네이션 같은 실무 문제

**학습 포인트**:
- 추상 클래스 기반 설계
- API 클라이언트 패턴
- 데이터 정규화

### 1.3 🔜 Storage/Warehouse (다음)

**뭘 만들 건가**: DuckDB 기반 로컬 데이터 웨어하우스

**왜 이게 필요한가**:
- 수집/변환한 데이터를 저장할 곳 필요
- SQL로 데이터 조회/분석
- 실제 분석 쿼리 연습

**예상 구조**:
```
storage/warehouse/
├── schema/          # 테이블 스키마 정의
├── loader/          # 데이터 로드
├── query/           # 쿼리 유틸리티
└── migrations/      # 스키마 변경 관리
```

**학습 포인트**:
- DuckDB 활용
- 스키마 설계
- 데이터 모델링 기초

### 1.4 🔜 End-to-End Pipeline

**뭘 만들 건가**: Collector → Storage → Query 전체 흐름

**왜 이게 필요한가**:
- 개별 컴포넌트를 연결하는 경험
- 실제 데이터 흐름 이해
- 에러 처리, 재시도 로직

---

## Phase 2: 확장 기능

### 2.1 Analytics/Models

**뭘 만들 건가**: S → H → RPT 데이터 모델

**왜 필요한가**:
- 회사 vdl_scripts 패턴 학습
- 차트용 데이터 가공 이해
- 분석 쿼리 작성 연습

### 2.2 Visualization/Chart-API

**뭘 만들 건가**: FastAPI 기반 차트 데이터 API

**왜 필요한가**:
- 백엔드 API 설계 경험
- 데이터 시각화 파이프라인 완성
- REST API 패턴

### 2.3 Orchestration/Scheduler

**뭘 만들 건가**: 간단한 작업 스케줄러

**왜 필요한가**:
- 자동화된 데이터 파이프라인
- Airflow 없이 스케줄링 이해
- DAG 개념 학습

---

## Phase 3: 운영 기능

### 3.1 Monitoring

- 파이프라인 상태 모니터링
- 실행 로그, 메트릭 수집

### 3.2 Notification

- 실패 알림 (Slack, Email)
- 완료 알림

---

## Phase 4: 고급 기능

### 4.1 AI Agent

- LLM 기반 데이터 분석
- 자연어 → SQL 변환

### 4.2 Instance Manager

- 회사 cloud_instance 개선 버전
- 클라우드 리소스 관리

---

## 진행 방식

### 각 컴포넌트별 사이클

```
1. 설계 문서 작성 (ADR)
   └─ 왜 이렇게 하는지 기록

2. 기본 구현
   └─ 최소 동작하는 버전

3. 테스트 작성
   └─ 단위 + 통합

4. 리뷰 + 개선
   └─ best practices 검색
   └─ 코드 개선

5. 학습 정리
   └─ 내가 이해한 것 문서화
   └─ 면접 대비 설명 준비
```

### 학습 체크리스트 (컴포넌트별)

각 컴포넌트 완료 후 스스로 체크:

- [ ] 이 컴포넌트가 왜 필요한지 설명할 수 있나?
- [ ] 전체 아키텍처에서 어떤 역할인지 아나?
- [ ] 핵심 클래스/함수를 설명할 수 있나?
- [ ] 왜 이렇게 설계했는지 근거를 댈 수 있나?
- [ ] 더 나은 방법이 있다면 뭔지 아나?
- [ ] 비슷한 걸 처음부터 만들 수 있나?

---

## 다음 단계 상세 계획

### Step 1: DuckDB Warehouse (이번 주)

**Day 1-2: 설계**
- [ ] ADR 작성: 왜 DuckDB인가?
- [ ] 스키마 설계: GitHub 데이터용 테이블
- [ ] 인터페이스 설계

**Day 3-4: 구현**
- [ ] 기본 구조 (schema, loader)
- [ ] Collector 연동
- [ ] 테스트

**Day 5: 리뷰**
- [ ] 코드 리뷰
- [ ] 학습 정리

### Step 2: E2E Pipeline (다음 주)

- GitHub 수집 → DuckDB 저장 → SQL 분석
- CLI로 전체 파이프라인 실행

### Step 3: Analytics Models

- S → H → RPT 모델 구현
- 차트용 데이터 생성

---

## 예상 일정

| 주차 | 목표 | 산출물 |
|------|------|--------|
| Week 1 | Converter + Collector | ✅ 완료 |
| Week 2 | DuckDB + E2E | Warehouse, 통합 파이프라인 |
| Week 3 | Analytics | S→H→RPT 모델 |
| Week 4 | Chart API | FastAPI 엔드포인트 |
| Week 5 | Scheduler | 자동화 파이프라인 |
| Week 6+ | 고도화 | async, 모니터링, 등 |

---

## 왜 이 순서인가?

```
수집 → 변환 → 저장 → 가공 → 시각화
  ↑       ↑      ↑      ↑       ↑
Week1  Week1  Week2  Week3   Week4
```

**데이터 흐름 순서대로** 만들어야:
1. 각 단계가 이전 단계 결과물 사용
2. 점진적으로 파이프라인 완성
3. 매주 동작하는 결과물 확인 가능
