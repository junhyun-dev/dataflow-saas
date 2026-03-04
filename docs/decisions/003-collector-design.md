# ADR 003: Collector 설계 - 추상 클래스 기반 패턴

## 상태

승인됨 (2026-03-03)

## 컨텍스트

외부 API에서 데이터를 수집하는 컴포넌트가 필요했다. 첫 번째 구현은 GitHub API지만, 나중에 Jira, Slack 등 다른 소스도 추가할 계획.

**고려한 옵션들**:

1. **소스별 독립 스크립트**
   ```python
   # github_collector.py
   def collect_github(): ...

   # jira_collector.py
   def collect_jira(): ...
   ```
   - 장점: 간단
   - 단점: 공통 로직 중복, 일관성 없음

2. **추상 클래스 기반 (선택)**
   ```python
   class BaseCollector(ABC):
       @abstractmethod
       def collect(self): ...

   class GitHubCollector(BaseCollector): ...
   class JiraCollector(BaseCollector): ...
   ```
   - 장점: 일관된 인터페이스, 공통 로직 재사용
   - 단점: 초기 설계 비용

3. **함수형 스타일**
   ```python
   def collect(source: str, config: dict): ...
   ```
   - 장점: 유연
   - 단점: 타입 안전성 부족

## 결정

**추상 클래스 기반 패턴**을 선택했다.

```python
class BaseCollector(ABC):
    """공통 인터페이스 + 헬퍼 메서드"""

    @abstractmethod
    def source_name(self) -> str: ...

    @abstractmethod
    def collect(self) -> list[CollectResult]: ...

    # 공통 헬퍼
    def _save_json(self, data, filename): ...
    def _save_parquet(self, data, filename): ...


class GitHubCollector(BaseCollector):
    """GitHub 구현"""

    def source_name(self) -> str:
        return "github"

    def collect(self) -> list[CollectResult]:
        # GitHub 전용 로직
```

## 근거

1. **일관된 인터페이스**
   - 모든 Collector가 같은 방식으로 사용됨
   - CLI, 테스트 코드 재사용 가능

2. **공통 로직 재사용**
   - 저장 로직 (`_save_json`, `_save_parquet`)
   - 결과 객체 생성 (`_create_result`)

3. **타입 안전성**
   - `CollectResult` 데이터클래스로 결과 구조 명확
   - IDE 자동완성, 타입 체크 가능

4. **확장 용이**
   - 새 소스 추가 시 `BaseCollector` 상속만 하면 됨
   - 기존 코드 수정 불필요

## 핵심 설계 요소

### 1. CollectResult 데이터클래스

```python
@dataclass
class CollectResult:
    source: str      # "github"
    resource: str    # "commits"
    status: str      # "success" | "fail"
    total_count: int
    collected_count: int
    output_path: Path
    errors: list[str]
```

**왜 dataclass인가?**
- 불변 데이터 구조
- `to_dict()` 쉽게 구현
- 타입 힌트 자동

### 2. Pydantic Config

```python
class GitHubConfig(BaseModel):
    owner: str
    repo: str
    token: Optional[str]
    collect_commits: bool = True
    rate_limit: RateLimitConfig
```

**왜 Pydantic인가?**
- 런타임 검증 (잘못된 설정 빠르게 발견)
- 타입 변환 자동
- JSON/YAML 직렬화

### 3. 데이터 정규화

```python
def _normalize_commit(self, raw: dict) -> dict:
    """GitHub API 응답 → 표준 포맷"""
    return {
        "sha": raw.get("sha"),
        "message": raw["commit"]["message"],
        "author_name": raw["commit"]["author"]["name"],
        ...
    }
```

**왜 정규화하는가?**
- API 응답 구조가 복잡함 (중첩, 불필요한 필드)
- 저장/분석에 필요한 것만 추출
- 포맷 일관성 보장

## 트레이드오프

| 측면 | 장점 | 단점 |
|------|------|------|
| 초기 비용 | - | 설계/구현 시간 |
| 확장성 | 새 소스 추가 쉬움 | - |
| 일관성 | 모든 소스 같은 인터페이스 | - |
| 유연성 | - | 공통 인터페이스에 맞춰야 함 |

## 결과

- ingestion/collector/ 구조 완성
- 테스트 12개 통과
- 통합 테스트 (실제 GitHub API) 통과

## 면접 대비 질문

Q: "왜 추상 클래스를 사용했나요?"
A: "여러 데이터 소스(GitHub, Jira, Slack 등)를 지원할 계획이었습니다. 추상 클래스로 공통 인터페이스를 정의하면, 새 소스를 추가할 때 기존 코드를 수정할 필요 없이 새 클래스만 만들면 됩니다. Open-Closed Principle이죠."

Q: "인터페이스(Protocol)가 아닌 추상 클래스인 이유는?"
A: "공통 헬퍼 메서드(_save_json, _save_parquet)가 있어서입니다. 인터페이스는 메서드 시그니처만 정의하고, 추상 클래스는 구현도 제공할 수 있습니다. 공통 로직 재사용이 필요해서 추상 클래스를 선택했습니다."

Q: "동기 requests 대신 async를 안 쓴 이유는?"
A: "MVP 단계에서 단순함을 우선했습니다. 현재 사용량에서는 동기로 충분하고, async 추가 시 복잡도가 증가합니다. 다만 2026 best practices 리뷰에서 async 지원을 개선점으로 식별했고, 다음 이터레이션에서 httpx AsyncClient로 전환할 계획입니다."
