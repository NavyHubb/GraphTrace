# GraphTrace: AI-Powered Code Traceability & Testing

**GraphTrace**는 자바 소스 코드의 복잡한 호출 구조와 의존성을 Neo4j 그래프 데이터베이스로 시각화하고,  
AI 에이전트(LangGraph)를 통해 코드 변경에 따른 영향 분석 및 맞춤형 통합 테스트 시나리오 생성을 지원하는 **지능형 개발 가이드 시스템**입니다.

👉 **설치 및 프로젝트 구동 방법은 [구동 가이드(GETTING_STARTED.md)](docs/GETTING_STARTED.md)를 참고해 주세요.**

## 🔍 프로젝트 비전 및 주요 기능 (Features)

최신 소프트웨어 개발 환경에서는 비즈니스 로직이 방대해짐에 따라 코드 변경이 어떤 부수 효과(Side Effect)를 가져올지 예측하기 어렵습니다. GraphTrace는 이러한 문제를 해결하기 위해 소스 코드를 그래프의 형태로 해석하고 AI를 결합하여 개발 과정을 보조합니다.

- **Java 소스 코드 구조화**: `.zip` 파일 업로드 시 구조를 자동 분석(AST 파싱)하여 Graph DB에 적재
- **증분 분석 (Incremental Update)**: 파일 해시 기반으로 변경 사항을 감지하여 `NEW`(신규), `MODIFIED`(수정), `DELETED`(삭제) 상태 추적
- **호출 흐름 시각화 (Call Graph)**: 메서드 간 호출 관계 및 API 엔드포인트부터 하위 로직까지 이어지는 전체 연결 시각화
- **AI 테스트 에이전트**: 변경된 코드가 영향을 미치는 범위를 역추적하여, 영향을 받는 API에 대한 맞춤형 통합 테스트 시나리오 자동 생성

---

## 🏗 핵심 아키텍처 1: Graph DB (Neo4j) 구조

이 시스템의 첫 번째 핵심은 코드를 구조화하여 파악할 수 있도록 돕는 그래프 데이터베이스입니다. 코드의 정적 정보와 실행 흐름을 효과적으로 모델링하기 위해 다음과 같은 노드와 엣지로 구성됩니다.

### 🟢 노드 (Nodes) 구성

| 노드 | 설명 | 역할 |
| :--- | :---------------------------------- | :-------------------------------------------------------------------------------- |
| `FILE` | 물리적 소스 코드 파일 | 파일 해시값을 보유하여 코드 변경 감지의 기준점이 됨 |
| `TYPE` | 클래스(Class) 또는 인터페이스 | 객체 지향의 데이터 타입 및 추상화 단위를 표현 |
| `FIELD` | 클래스 내부 멤버 변수 | 클래스 상태를 정의하는 변수 정보 저장 |
| `METHOD` | 함수 / 메서드 | 실제 실행 가능한 최소 단위. 시그니처, 부여된 API 엔드포인트(`@GetMapping` 등) 보관 |
| `PARAMETER` | 메서드 입력 파라미터 | 메서드 호출 인수의 이름 및 타입 정보 보유 |
| `RETURN_VALUE` | 메서드 반환 값 | 메서드 실행 결과의 반환 타입 정보 보유 |

### 🔗 엣지 (Edges) 구성 및 설계 이유

| 관계 유형 | 엣지 방향의 형태 | 설계 목적 및 활용 방식 |
| :-------- | :---------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------- |
| **구조적 계층** | `(FILE)` ➔ `[:CONTAINS]` ➔ `(TYPE)` ➔ `[:CONTAINS]` ➔ `(METHOD)` | 코드의 포함 관계를 명확히 하여, 특정 파일 변경 시 영향을 받는 클래스와 메서드를 신속히 식별 |
| **상세 구조** | `(TYPE)` ➔ `[:HAS_FIELD]` ➔ `(FIELD)`<br>`(METHOD)` ➔ `[:HAS_PARAMETER]` ➔ `(PARAMETER)`<br>`(METHOD)` ➔ `[:HAS_RETURN]` ➔ `(RETURN_VALUE)` | 클래스나 메서드 내부의 상세 요소들을 계층상으로 연결, 변경 분석 시 정교한 문맥 정보 확보 |
| **타입 의존성** | `(FIELD)` ➔ `[:OF_TYPE]` ➔ `(TYPE)`<br>`(PARAMETER)` ➔ `[:OF_TYPE]` ➔ `(TYPE)`<br>`(METHOD)` ➔ `[:RETURNS]` ➔ `(TYPE)` | DTO 등 특정 요소가 의존하는 외부 클래스(타입)를 파악하고, 데이터의 흐름과 형태를 추적 |
| **실행 의존성** | `(METHOD)` ➔ `[:CALLS]` ➔ `(METHOD)` | 순차적·논리적 실행 흐름 연결. 최종 엔드포인트 역추적(Upstream Analysis) 및 세부 실행 흐름 추적(Downstream Analysis) 기능 제공 |

---

## 🤖 핵심 아키텍처 2: LangGraph 기반 AI 에이전트

두 번째 핵심은 Graph DB에 구축된 정밀한 문맥 정보(Context)를 바탕으로 지능적 추론을 수행하는 순환 구조(Cyclic Graph)의 AI 에이전트입니다. 단순한 단방향 텍스트 생성을 넘어, 결과를 스스로 검증하고 보정하는 자가 보정(Self-Correction) 메커니즘을 갖추고 있습니다.

<img width="332" height="783" alt="Image" src="https://github.com/user-attachments/assets/be38b1b1-92f4-4ded-902c-2dd01aa75e65" />

<details>
<summary>📊 Mermaid 다이어그램 코드 보기</summary>

```mermaid
graph TD
    Entry([시작]) --> Planner[Planner: 영향 범위 분석 및 엔드포인트 그룹화]
    Planner --> Retriever[Retriever: 코드 문맥 및 DTO 구조 수집]
    Retriever --> Generator[Generator: 테스트 시나리오 생성]
    Generator --> Validator{Validator: 품질 검증}
    Validator -- "결함 발견 (Fail)" --> Generator
    Validator -- "검증 통과 (Pass) / Max Iterations 도달" --> End([종료])

    style Generator fill:#f9f,stroke:#333,stroke-width:2px
    style Validator fill:#bbf,stroke:#333,stroke-width:2px
```

</details>

### 각 단계 노드의 상세 역할

| 에이전트 노드명 | 입력 (Input) | 주요 역할 및 논리 |
| :--- | :--- | :--- |
| **Planner Node** | 변경된 메서드 목록 | 시작점에서 `CALLS` 역방향 엣지를 타고 상위 호출을 추적하여 최종적으로 연관된 API 엔드포인트들을 탐색 및 그룹화 |
| **Retriever Node** | 영향받는 엔드포인트 정보 | 시나리오 생성에 필수적인 코드 문맥(원본 소스코드, DTO 필드, 하위 흐름 등)을 Graph DB에서 추출 |
| **Generator Node** | 코드 문맥 및 이전 단계 피드백 | 수집된 정보와 과거 비판 피드백을 수용하여, 마크다운 형식의 테스트 시나리오 및 최적화된 리퀘스트/리스폰스 JSON 생성 |
| **Validator Node** | 생성된 시나리오와 페이로드 | 결과물의 JSON 유효성, 비즈니스 흐름 정합성 및 포맷을 검증. 결함 발생 시 구체적인 보완 피드백(Feedback Loop)을 재전송 |

> [!TIP]
> **자가 보정 루프**는 최대 3회(`max_iterations`)까지 실행되도록 설정되어 있어, 잘못된 형식이나 모순된 결과를 생성하는 LLM의 할루시네이션(Hallucination) 위험을 줄이고 반복 개선을 통해 고품질의 완성된 테스트 시나리오를 보장합니다.