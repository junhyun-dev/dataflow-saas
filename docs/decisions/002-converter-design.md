# ADR 002: Converter 설계 - Pipeline 패턴과 책임 분리

## 상태

승인됨 (2026-03-02)

## 컨텍스트

Excel 파일을 Parquet으로 변환하는 컴포넌트가 필요했다.

**회사 현황 분석**:
- 기존 V1: FileConverter 클래스가 536줄, 7가지 책임 (God Class 문제)
- V2 설계: 책임 분리, Pydantic Config 도입 예정

**문제점**:
```python
# Bad: 모든 책임이 한 클래스에
class FileConverter:
    def load_file(self): ...      # 파일 로드
    def parse_table(self): ...    # 테이블 파싱
    def find_headers(self): ...   # 헤더 찾기
    def convert_types(self): ...  # 타입 변환
    def write_output(self): ...   # 출력
    def handle_config(self): ...  # 설정 처리
    def run(self): ...            # 오케스트레이션
```

## 결정

**책임 분리 + Pipeline 패턴**을 선택했다.

```
Pipeline (오케스트레이터)
    ├── ExcelLoader (파일 로드)
    ├── TableParser (테이블 파싱)
    └── ParquetWriter (출력)
```

각 클래스는 **단일 책임**만 가진다:

| 클래스 | 책임 | 하지 않는 것 |
|--------|------|-------------|
| Pipeline | 흐름 조율, 에러 수집 | 실제 파싱, I/O |
| ExcelLoader | 파일 로드, 시트 필터 | 파싱, 저장 |
| TableParser | 행/열 파싱, 타입 변환 | 파일 I/O |
| ParquetWriter | Parquet 저장 | 파싱, 로드 |

## 근거

1. **테스트 용이성**
   - 각 클래스를 독립적으로 테스트 가능
   - Mock 대체 쉬움

2. **유지보수성**
   - 변경 범위가 좁아짐
   - 버그 위치 특정 쉬움

3. **재사용성**
   - Parser만 다른 곳에서 재사용 가능
   - 새로운 Writer (CSV, JSON) 추가 쉬움

4. **회사 V2 설계와 일치**
   - 회사 코드 이해에 도움
   - 나중에 회사 코드 개선 시 참고

## 코드 예시

```python
# Good: 책임 분리
class Pipeline:
    def run(self, file_path):
        with ExcelLoader() as loader:
            loader.load(file_path)
            for sheet in loader.sheets:
                raw_df = loader.read_sheet(sheet)
                parsed_df = self.parser.parse(raw_df)
                self.writer.write(parsed_df)
```

## 트레이드오프

**장점**:
- 코드 이해 쉬움
- 테스트 쉬움
- 확장 쉬움

**단점**:
- 파일 수 증가
- 간단한 작업에도 여러 클래스 필요
- 클래스 간 데이터 전달 오버헤드

**결론**: 학습 목적 + 실무 패턴 익히기에는 장점이 더 큼

## 결과

- transform/converter/ 구조 완성
- 테스트 5개 통과
- 확장 가능한 구조

## 면접 대비 질문

Q: "왜 이렇게 여러 클래스로 나눴나요?"
A: "단일 책임 원칙(SRP)을 적용했습니다. 기존에 하나의 클래스가 파일 로드, 파싱, 저장까지 다 하면 테스트도 어렵고, 한 부분 수정이 다른 부분에 영향을 줍니다. 분리하면 각각 독립적으로 테스트하고 수정할 수 있습니다."

Q: "오버엔지니어링 아닌가요?"
A: "간단한 스크립트라면 그렇습니다. 하지만 이 프로젝트는 확장을 고려했고, 실제로 다양한 입력 포맷(CSV, JSON)이나 출력 포맷을 추가할 수 있습니다. 또한 회사 코드도 이 방향으로 리팩토링 예정이어서 미리 익혀두는 의미가 있습니다."
