# Self Review - 2026-03-03

## 검토 범위

- `ingestion/collector/` - GitHub API Collector
- `transform/converter/` - Excel → Parquet Converter

---

## 1. 코드 품질 이슈

### Critical (즉시 수정)

| 위치 | 문제 | 해결 방안 |
|------|------|----------|
| `github_collector.py:19` | `urlencode` import 안 씀 | 삭제 |
| `github_collector.py:17` | `datetime` import 안 씀 | 삭제 |
| `base.py:18` | `Iterator` import 안 씀 | 삭제 |

### High (다음 스프린트)

| 위치 | 문제 | 해결 방안 |
|------|------|----------|
| `github_collector.py` | 로깅 없음 | structlog/loguru 도입 |
| `github_collector.py` | 동기 requests만 지원 | async httpx 지원 추가 |
| `base.py:123-130` | `_save_parquet`에서 pandas 런타임 import | 의존성 체크 추가 |

### Medium (나중에)

| 위치 | 문제 | 해결 방안 |
|------|------|----------|
| `github_collector.py:58-74` | `collect()` if문 반복 | dict 매핑으로 리팩토링 |
| `converter/config/schema.py` | `column_types` 값 검증 없음 | Literal type 또는 validator 추가 |

---

## 2. 2026 Best Practices 적용 필요

### ETL 파이프라인

> "An idempotent pipeline produces the same result whether it runs once or ten times"
> — [OneUptime ETL Best Practices](https://oneuptime.com/blog/post/2026-02-13-etl-best-practices/view)

**현재 상태:** 멱등성 미보장 (같은 파일 중복 저장)

**필요한 작업:**
- [ ] 출력 파일 덮어쓰기 전 확인 옵션
- [ ] 체크섬 기반 중복 방지
- [ ] 증분 수집 (last_sync timestamp)

### Pydantic v2

> "Pydantic v2 is 5-50x faster than v1, use TypeAdapter for just validation"
> — [Pydantic Performance](https://docs.pydantic.dev/latest/concepts/performance/)

**현재 상태:** 기본 Pydantic 사용

**필요한 작업:**
- [ ] Annotated 타입 활용 (재사용 가능한 검증 로직)
- [ ] `column_types`에 Literal 타입 적용
- [ ] 복잡한 검증에 `@field_validator` 사용

### Async HTTP Client

> "HTTPX supports HTTP/2, AIOHTTP is better for high-concurrency"
> — [Oxylabs Comparison](https://oxylabs.io/blog/httpx-vs-requests-vs-aiohttp)

**현재 상태:** 동기 requests 사용

**필요한 작업:**
- [ ] httpx AsyncClient 지원 추가
- [ ] 연결 풀링 (세션 재사용)
- [ ] HTTP/2 활용

### Logging

> "Use structlog for production JSON logs, loguru for simple projects"
> — [Better Stack Logging Guide](https://betterstack.com/community/guides/logging/best-python-logging-libraries/)

**현재 상태:** print 또는 로깅 없음

**필요한 작업:**
- [ ] structlog 또는 loguru 도입
- [ ] JSON 형식 로깅 (프로덕션)
- [ ] 로그 레벨 환경변수 지원

---

## 3. 아키텍처 개선점

### Collector 패턴

```
현재:
┌──────────────┐
│ GitHubCollector │──→ JSON 파일
└──────────────┘

개선:
┌──────────────┐     ┌─────────┐     ┌──────────┐
│ GitHubCollector │──→│ Sink    │──→ │ Storage  │
└──────────────┘     │ Interface│    │ (JSON/   │
                     └─────────┘     │  Parquet/│
                                     │  DuckDB) │
                                     └──────────┘
```

**필요한 작업:**
- [ ] Sink 추상화 (JSON, Parquet, DB)
- [ ] 스트리밍 지원 (메모리 효율)

### Converter 패턴

```
현재: 동기 처리 (파일 하나씩)

개선:
- 병렬 처리 (multiprocessing)
- 스트리밍 (대용량 파일)
```

---

## 4. 테스트 개선점

| 항목 | 현재 | 목표 |
|------|------|------|
| Unit Tests | 17개 | 30개+ |
| Integration Tests | 4개 | 10개+ |
| Coverage | 측정 안 함 | 80%+ |
| Mock 사용 | 일부 | 완전한 API mock |

**필요한 작업:**
- [ ] pytest-cov 추가
- [ ] responses 라이브러리로 완전한 API mock
- [ ] 에러 케이스 테스트 추가

---

## 5. 우선순위 정리

### 즉시 (이번 세션)

1. ~~사용하지 않는 import 정리~~
2. 로깅 기본 도입 (loguru)

### 단기 (이번 주)

1. async 지원 (httpx)
2. Sink 추상화
3. 테스트 커버리지 측정

### 중기 (다음 주)

1. 멱등성 보장
2. 증분 수집
3. DuckDB 저장소 연동

---

## Sources

- [Integrate.io - Building ETL Pipeline in Python 2026](https://www.integrate.io/blog/building-an-etl-pipeline-in-python/)
- [OneUptime - ETL Best Practices](https://oneuptime.com/blog/post/2026-02-13-etl-best-practices/view)
- [Airbyte - Python ETL Tools 2026](https://airbyte.com/top-etl-tools-for-sources/python-etl-tools)
- [Pydantic Performance Guide](https://docs.pydantic.dev/latest/concepts/performance/)
- [OneUptime - Pydantic v2 Validation](https://oneuptime.com/blog/post/2026-01-21-python-pydantic-v2-validation/view)
- [Oxylabs - HTTPX vs Requests vs AIOHTTP](https://oxylabs.io/blog/httpx-vs-requests-vs-aiohttp)
- [Better Stack - Python Logging Libraries](https://betterstack.com/community/guides/logging/best-python-logging-libraries/)
- [structlog Documentation](https://www.structlog.org/)
