# Gemini 코드 리뷰 프롬프트

## 사용법

```bash
cd ~/projects/A_data-engineering/dataflow-saas
gemini
```

그리고 아래 프롬프트를 복사해서 붙여넣기:

---

## 프롬프트 1: 전체 아키텍처 리뷰

```
이 프로젝트의 전체 구조를 분석해줘.

먼저 GEMINI.md 파일을 읽고, 그 다음 주요 파일들을 확인해줘:
- transform/converter/pipeline.py
- transform/converter/config/schema.py
- ingestion/collector/base.py
- ingestion/collector/collectors/github_collector.py

다음 관점에서 시니어 개발자로서 리뷰해줘:

1. **아키텍처 평가**
   - 책임 분리가 적절한가?
   - SOLID 원칙을 잘 따르고 있나?

2. **확장성**
   - 새로운 Collector(Jira, Slack)를 추가하려면 얼마나 쉬운가?
   - 새로운 Writer(CSV, JSON)를 추가하려면?

3. **개선점**
   - 2026년 Python best practices 관점에서 부족한 점은?
   - 리팩토링이 필요한 부분은?

구체적인 코드 위치와 함께 피드백해줘.
```

---

## 프롬프트 2: Converter 상세 리뷰

```
transform/converter/ 폴더의 코드를 상세히 리뷰해줘.

특히:
1. pipeline.py의 _process_sheet 메서드 - 에러 처리가 적절한가?
2. table_parser.py의 타입 변환 로직 - 개선할 점은?
3. Pydantic Config 사용법 - 2026년 best practices에 맞나?

코드를 직접 읽고 구체적인 라인 번호와 함께 피드백해줘.
```

---

## 프롬프트 3: Collector 상세 리뷰

```
ingestion/collector/ 폴더의 코드를 상세히 리뷰해줘.

특히:
1. 추상 클래스(base.py) 설계가 적절한가?
2. github_collector.py의 Rate Limit 처리가 production-ready한가?
3. 동기 requests 대신 async httpx로 바꾸면 어떤 점이 좋아지나?

코드를 직접 읽고 구체적인 개선 코드 예시와 함께 피드백해줘.
```

---

## 프롬프트 4: 테스트 리뷰

```
테스트 코드를 리뷰해줘:
- transform/converter/tests/test_pipeline.py
- ingestion/collector/tests/test_collector.py
- tests/integration/test_collector_integration.py

다음 관점에서:
1. 테스트 커버리지가 충분한가?
2. 빠진 테스트 케이스는?
3. mock 사용이 적절한가?
4. 테스트 구조/네이밍이 좋은가?
```

---

## 프롬프트 5: 종합 평가 + 점수

```
이 프로젝트를 종합 평가해줘.

다음 기준으로 10점 만점에 점수를 매기고 근거를 설명해줘:

1. 코드 품질 (가독성, 일관성): ?/10
2. 아키텍처 (확장성, 유지보수성): ?/10
3. 테스트 (커버리지, 품질): ?/10
4. 문서화 (README, ADR, 주석): ?/10
5. Python Best Practices: ?/10

그리고 "주니어 개발자가 포트폴리오로 쓴다면" 관점에서:
- 강점 3가지
- 개선 필요한 점 3가지
- 면접에서 이 코드로 어필할 수 있는 포인트

마지막으로, 다음에 추가하면 좋을 기능 우선순위 3개를 추천해줘.
```
