# Study Guide - 코드 학습 가이드

## 이 문서의 목적

이 프로젝트는 Claude가 구현했지만, **네가 이해하고 설명할 수 있어야** 한다.
면접에서 "이거 직접 만드셨어요?"라고 물으면 "네, 제가 설계하고 구현했습니다"라고 말할 수 있어야 함.

---

## Part 1: Converter 학습

### 1.1 먼저 읽어볼 것

```
순서:
1. docs/decisions/002-converter-design.md (왜 이렇게 설계했는지)
2. transform/converter/config/schema.py (설정 구조)
3. transform/converter/pipeline.py (전체 흐름)
4. 나머지 (loader, parser, writer)
```

### 1.2 핵심 개념

#### Pipeline 패턴

```
질문: Pipeline 클래스가 뭘 하는지 한 문장으로?
정답: "Loader, Parser, Writer를 연결하고 에러를 수집하는 오케스트레이터"
```

**직접 해보기**:
1. `pipeline.py`의 `run()` 메서드 읽기
2. 각 단계가 뭘 하는지 주석 달아보기
3. 에러가 나면 어떻게 처리되는지 추적

#### Pydantic Config

```python
# 이 코드가 뭘 하는지 설명해봐
class TableConfig(BaseModel):
    name: str
    sheet_pattern: str = ".*"
    columns: Optional[list[str]] = None
```

**이해 확인 질문**:
- `Field(default=...)`와 `= ...`의 차이는?
- `Optional[list[str]]`이 뭔 뜻이야?
- 왜 Pydantic을 쓰지, 그냥 dict 쓰면 안 돼?

### 1.3 코드 트레이싱 연습

**문제**: "sample.xlsx" 파일을 Parquet으로 변환할 때 코드 흐름을 따라가봐

```python
Pipeline.simple_run("sample.xlsx", "output/")
```

**추적해볼 것**:
1. `simple_run`이 뭘 호출해?
2. `ExcelLoader.load()`가 뭘 반환해?
3. `TableParser.parse()`에서 헤더는 어떻게 처리돼?
4. 최종 Parquet 파일은 어디에 저장돼?

### 1.4 직접 수정해보기

**미션 1**: CSV 출력 추가
- `writer/csv_writer.py` 만들어보기
- Pipeline에서 출력 포맷 선택 가능하게

**미션 2**: 머지셀 처리
- `parser/table_parser.py`에 머지셀 감지 로직 추가

---

## Part 2: Collector 학습

### 2.1 먼저 읽어볼 것

```
순서:
1. docs/decisions/003-collector-design.md (왜 추상 클래스)
2. ingestion/collector/base.py (추상 클래스)
3. ingestion/collector/config/schema.py (설정)
4. ingestion/collector/collectors/github_collector.py (구현)
```

### 2.2 핵심 개념

#### 추상 클래스

```python
class BaseCollector(ABC):
    @abstractmethod
    def collect(self) -> list[CollectResult]: ...
```

**이해 확인 질문**:
- `ABC`가 뭐야?
- `@abstractmethod`를 빼면 어떻게 돼?
- `GitHubCollector`가 `collect()`를 구현 안 하면?

#### Rate Limiting

```python
# 이 코드가 왜 필요한지 설명해봐
time.sleep(1 / rate_limit.requests_per_second)
```

**이해 확인 질문**:
- GitHub API Rate Limit가 뭐야?
- 403 응답이 오면 어떻게 처리해?
- 토큰 있을 때/없을 때 차이는?

#### 데이터 정규화

```python
def _normalize_commit(self, raw: dict) -> dict:
    return {
        "sha": raw.get("sha"),
        "message": raw["commit"]["message"],
        ...
    }
```

**이해 확인 질문**:
- 왜 API 응답 그대로 저장 안 해?
- `raw.get("sha")` vs `raw["sha"]` 차이는?
- 어떤 필드를 선택했고, 왜?

### 2.3 코드 트레이싱 연습

**문제**: `anthropics/claude-code` 저장소의 commits를 수집할 때

```python
config = GitHubConfig(owner="anthropics", repo="claude-code")
collector = GitHubCollector(config, "./output")
results = collector.collect()
```

**추적해볼 것**:
1. `_create_session()`에서 어떤 헤더를 설정해?
2. `_paginate()`가 어떻게 동작해?
3. 결과 JSON 파일 구조는?

### 2.4 직접 수정해보기

**미션 1**: 새 리소스 추가
- `contributors` 수집 추가
- API: `GET /repos/{owner}/{repo}/contributors`

**미션 2**: Jira Collector
- `JiraCollector` 클래스 만들어보기
- `BaseCollector` 상속

---

## Part 3: 통합 이해

### 3.1 전체 아키텍처 그려보기

종이에 직접 그려봐:
```
수집 → 변환 → 저장 → 분석 → 시각화
```

각 단계에서:
- 어떤 컴포넌트가 담당?
- 입력/출력이 뭐야?
- 실패하면 어떻게 돼?

### 3.2 설계 결정 설명 연습

**면접관 역할놀이**:

Q1: "왜 이렇게 여러 파일로 나눴어요?"
→ 네 답변 작성해봐

Q2: "Pydantic을 왜 사용했나요?"
→ 네 답변 작성해봐

Q3: "async를 안 쓴 이유가 있나요?"
→ 네 답변 작성해봐

Q4: "테스트는 어떻게 작성했나요?"
→ 네 답변 작성해봐

### 3.3 개선점 분석

`docs/reviews/2026-03-03-self-review.md` 읽고:

1. 왜 이게 개선점인지 이해했어?
2. 어떻게 개선할 건지 설명할 수 있어?
3. 직접 개선해볼 수 있어?

---

## Part 4: 학습 체크리스트

### Converter

- [ ] Pipeline 패턴이 뭔지 설명 가능
- [ ] 책임 분리가 왜 중요한지 설명 가능
- [ ] Pydantic Config의 장점 설명 가능
- [ ] 코드 없이 전체 흐름 그릴 수 있음
- [ ] 테스트 코드 읽고 이해 가능
- [ ] 새 기능 추가할 수 있음 (예: CSV Writer)

### Collector

- [ ] 추상 클래스 패턴 설명 가능
- [ ] Rate Limiting이 왜 필요한지 설명 가능
- [ ] 데이터 정규화가 왜 필요한지 설명 가능
- [ ] 페이지네이션 처리 방법 설명 가능
- [ ] 새 Collector 추가할 수 있음

### 통합

- [ ] 전체 데이터 흐름 설명 가능
- [ ] 각 설계 결정의 근거 설명 가능
- [ ] 개선점이 뭔지, 왜 개선해야 하는지 설명 가능
- [ ] 비슷한 시스템을 처음부터 설계할 수 있음

---

## Part 5: 실습 과제

### Level 1: 코드 이해

1. 모든 테스트 실행하고 결과 이해하기
   ```bash
   cd dataflow-saas
   pytest -v
   ```

2. 각 테스트가 뭘 검증하는지 주석 달기

### Level 2: 작은 수정

1. Converter에 진행률 출력 추가
2. Collector에 `--dry-run` 옵션 추가

### Level 3: 새 기능

1. `SlackCollector` 구현
2. `CSVWriter` 구현
3. CLI 통합 (converter + collector를 하나의 명령으로)

### Level 4: 리팩토링

1. async 지원 추가 (httpx)
2. structlog로 로깅 개선
3. Sink 추상화 (JSON, Parquet, DB)

---

## 학습 팁

1. **코드 읽기 전에 ADR 먼저**
   - "왜"를 알면 "어떻게"가 이해됨

2. **손으로 그려보기**
   - 클래스 다이어그램
   - 시퀀스 다이어그램
   - 데이터 흐름도

3. **테스트 코드 읽기**
   - 테스트는 "사용 예시"
   - 어떻게 쓰는지 빠르게 파악

4. **직접 수정해보기**
   - 읽기만 하면 잊어버림
   - 작은 것이라도 직접 수정

5. **설명해보기**
   - 혼잣말로라도 설명
   - 글로 정리
   - 누군가에게 가르친다고 생각
