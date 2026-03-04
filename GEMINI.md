# GEMINI.md - dataflow-saas

## 프로젝트 개요

이 프로젝트는 데이터 파이프라인 SaaS의 핵심 컴포넌트를 학습 목적으로 구현한 토이 프로젝트입니다.

- **목적**: 회사에서 배운 데이터 엔지니어링 패턴 정리 + 포트폴리오
- **구현자**: Claude Code (AI)
- **검토자**: 사용자 + Gemini (당신)

## 현재 구현 상태

### 완료된 컴포넌트

1. **transform/converter** (Excel → Parquet 변환)
   - Pipeline 패턴으로 책임 분리
   - Pydantic Config
   - 테스트 5개 통과

2. **ingestion/collector** (GitHub API 수집)
   - 추상 클래스 기반 설계
   - Rate limit, 페이지네이션 처리
   - 테스트 12개 + 통합 테스트 4개 통과

## 리뷰 요청 사항

다음 관점에서 코드 리뷰 부탁드립니다:

1. **아키텍처**: 책임 분리가 적절한가?
2. **확장성**: 새 기능 추가하기 쉬운 구조인가?
3. **Python Best Practices**: 2026년 기준 개선할 점은?
4. **보안**: 잠재적 취약점은?
5. **테스트**: 테스트 커버리지 충분한가?

## 주요 파일

```
transform/converter/
├── pipeline.py          # 오케스트레이터
├── config/schema.py     # Pydantic 설정
├── loader/excel_loader.py
├── parser/table_parser.py
├── writer/parquet_writer.py
└── tests/test_pipeline.py

ingestion/collector/
├── base.py              # 추상 클래스
├── config/schema.py     # Pydantic 설정
├── collectors/github_collector.py
├── cli.py               # CLI 엔트리포인트
└── tests/test_collector.py
```

## 설계 결정 문서

- `docs/decisions/001-project-structure.md`
- `docs/decisions/002-converter-design.md`
- `docs/decisions/003-collector-design.md`
- `docs/reviews/2026-03-03-self-review.md`
