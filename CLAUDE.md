# CLAUDE.md - dataflow-saas

## 프로젝트 개요

B2B 데이터 분석 SaaS 플랫폼 토이 프로젝트.
회사(hyperloungescripts) 패턴을 학습하고, 새로운 설계를 테스트하는 실험장.

## 핵심 파이프라인

```
수집 → 변환 → 저장 → 가공 → 시각화
(ingestion) (transform) (storage) (analytics) (visualization)
```

## 회사 코드 연결

```
토이 프로젝트              회사 코드
─────────────────────────────────────────
transform/converter    →  collector/excel/v2 (V2 리팩토링)
agents/instance-manager → collector/cloud_instance (개선 예정)
analytics/models       →  vdl_scripts (SRCH→S→H→RPT)
```

## 작업 시 규칙

### 1. 진행 상황 업데이트 필수!

**작업 완료 후 반드시:**
```
1. PROGRESS.md 업데이트
   - Quick View 진행률
   - Phase별 상태
   - 상세 체크리스트
   - 변경 이력

2. 주요 결정사항은 docs/decisions/에 ADR 작성
```

### 2. 회사 코드 참고 시

```
✅ DO:
- 패턴/구조 참고
- 설계 아이디어 가져오기
- 문제점 분석 후 개선된 버전 구현

❌ DON'T:
- 코드 복붙
- 회사 고유 로직 그대로 가져오기
- 회사 도메인(재무/영업/생산) 사용
```

### 3. 코드 작성 원칙

```
- 타입 힌트 필수 (Python 3.11+)
- Pydantic으로 설정 검증
- 테스트 작성 (pytest)
- 문서화 (docstring)
```

## 폴더 구조

```
dataflow-saas/
├── auth/           # 인증
├── ingestion/      # 수집
├── transform/      # 변환 ← 현재 진행
├── orchestration/  # 워크플로우
├── storage/        # 저장
├── analytics/      # 가공
├── visualization/  # 시각화
├── observability/  # 모니터링
├── agents/         # 자동화
├── infra/          # 인프라
└── docs/           # 문서
```

## 현재 상태

**PROGRESS.md 참조** - 항상 최신 상태 유지

## 자주 하는 작업

### 1. "converter 작업하자"
→ transform/converter/ 작업
→ 회사 collector/excel/v2 참고

### 2. "instance-manager 작업하자"
→ agents/instance-manager/ 작업
→ 회사 collector/cloud_instance 참고

### 3. "진행 상황 보여줘"
→ PROGRESS.md 읽고 요약

### 4. "다음 뭐 해야 해?"
→ PROGRESS.md의 Quick View에서 "다음 할 일" 확인
