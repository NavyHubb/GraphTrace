# GraphTrace 시작하기 (Getting Started)

이 문서는 GraphTrace 프로젝트를 로컬 개발 환경 및 운영 환경에서 실행하기 위한 구동 가이드입니다.

## 📦 사전 요구사항 (Prerequisites)
- **Python 3.12+** (패키지 매니저로 `uv` 권장)
- **Node.js 18+** (Frontend 실행용)
- **Neo4j Database** (데이터 저장소)

## 🚀 프로젝트 설정 (Configuration)
이 프로젝트는 로컬 개발환경(dev)과 운영 환경(prd)을 구분하여 설정 파일을 관리합니다.

### 환경 설정 파일 준비
프로젝트 루트에 다음 두 파일을 생성해야 합니다.

**1) 로컬 개발용 (.env.dev)**
개인 로컬 Neo4j 및 OpenAI 설정을 입력하세요.
```ini
# .env.dev
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

OPENAI_API_KEY=your_openai_api_key_here
LANGSMITH_API_KEY=your_langsmith_api_key_here # Optional
```

**2) 운영/클라우드용 (.env.prd)**
팀원들과 공유된 클라우드 Neo4j 설정을 입력하세요.
```ini
# .env.prd
NEO4J_URI=bolt://<cloud-neo4j-uri>:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<secure-password>
```

---

## 🏃‍♂️ 구동 방법 (Running the Application)

### 1. 데이터베이스 준비 (Neo4j)
Neo4j 인스턴스가 실행 중이어야 합니다.

### 2. 백엔드 실행 (Backend)
FastAPI 서버를 실행합니다.

```bash
# 1. 의존성 및 가상환경 동기화 (최초 1회 실행)
uv sync

# 2. 서버 실행
# 개발 환경 (로컬 DB 사용, 기본값)
APP_ENV=dev uv run uvicorn api.main:app --reload

# 운영 환경 (클라우드 DB 사용)
APP_ENV=prd uv run uvicorn api.main:app --reload
```
> **Tip**: `APP_ENV` 변수를 생략하면 기본적으로 `dev` 환경으로 실행됩니다.
- Swagger UI 문서: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. 프론트엔드 실행 (Frontend)
Next.js 웹 애플리케이션을 실행합니다.

```bash
cd frontend
npm install
npm run dev
```

### 4. LangGraph Studio 실행 (AI Agent Debugger)
에이전트의 사고 과정과 그래프 시각화를 위해 LangGraph Studio 명령어를 사용할 수 있습니다.

```bash
# 1. LangGraph CLI 설치 (최초 1회)
uv add --dev "langgraph-cli[inmem]"

# 2. LangGraph 개발 서버 실행 (.env.dev 사용)
uv run langgraph dev
```
- 실행 후 로그에 출력되는 **Studio UI** URL로 접속하여 에이전트 로직을 인터랙티브하게 테스트할 수 있습니다.
- 사전에 저장된 `.env.dev`의 OpenAI 및 LangSmith 설정을 자동으로 참조합니다.

## ✅ 에이전트 로직 검증 (Verification)

에이전트의 복잡한 순환 구조와 자가 보정 로직이 정상적으로 작동하는지 확인하기 위해 실제 LLM 비용을 발생시키지 않고 Mock 데이터를 사용하여 흐름을 검증하는 독립적인 스크립트를 제공합니다.

### 검증 스크립트 실행
```bash
uv run python scripts/test_integration_loop.py
```

### 주요 검증 항목
- **자가 보정 루프**: 시나리오 생성 실패 시 피드백을 수집하여 다시 생성 단계로 진입하는지 확인합니다.
- **최대 반복 제한**: 지속적인 결함 발생 시 `max_iterations` 설정값에 따라 루프가 안전하게 종료되는지 확인합니다.
- **상태 전파**: 노드 간에 `impact_groups`, `contexts`, `scenarios` 등의 상태 데이터가 누락 없이 전달되는지 검증합니다.
