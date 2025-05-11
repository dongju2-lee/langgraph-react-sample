# DevOps MCP 에이전트

이 프로젝트는 LangChain과 LangGraph를 사용하여 모델 컨텍스트 프로토콜(MCP) 기반의 DevOps 자동화 에이전트를 구현합니다. 이 에이전트는 Grafana, ArgoCD, k6, GitHub 등의 도구를 통합하여 시스템 모니터링, 애플리케이션 배포, 성능 테스트 및 코드 리뷰 작업을 자동화합니다.

## 프로젝트 구조

```
using_mcp/
├── mcp/                      # MCP 서버 구현
│   ├── grafana_server.py     # Grafana 모니터링 도구
│   ├── argocd_server.py      # ArgoCD 배포 도구
│   ├── k6_server.py          # k6 성능 테스트 도구
│   ├── github_server.py      # GitHub 코드 리뷰 도구
│   ├── run_all_servers.sh    # 모든 MCP 서버를 시작하는 스크립트
│   └── stop_servers.sh       # 모든 MCP 서버를 종료하는 스크립트
├── mcp_client_react.py       # OpenAI 기반 ReAct 패턴 MCP 클라이언트
├── mcp_client_gemini.py      # Vertex AI Gemini 기반 ReAct 패턴 MCP 클라이언트
└── README.md                 # 프로젝트 설명
```

## 주요 기능

### 1. Grafana 모니터링
- 대시보드 목록 검색
- 대시보드 메트릭 조회
- 데이터 소스 목록 조회

### 2. ArgoCD 배포
- 애플리케이션 목록 조회
- 애플리케이션 배포
- 배포 상태 확인

### 3. k6 성능 테스트
- 성능 테스트 실행
- 테스트 결과 비교

### 4. GitHub 코드 리뷰
- Pull Request 목록 조회
- Pull Request 승인

## 설치 및 실행 방법

### 사전 요구사항
- Python 3.8 이상
- LangChain, LangGraph 설치
- MCP 라이브러리 설치
- 선택적으로 OpenAI API 키 또는 Google Cloud 인증 설정

### 설치

```bash
# 필요한 패키지 설치
pip install langchain langgraph langchain-openai langchain-google-vertexai mcp


# Google Cloud 인증 설정 (Google Vertex AI 기반 에이전트용)
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
```

### 실행

```bash
# 모든 MCP 서버 실행 (백그라운드에서 실행됨)
cd mcp
./run_all_servers.sh

# OpenAI 기반 MCP 클라이언트 실행
python mcp_client_react.py

# 또는 Google Vertex AI Gemini 기반 MCP 클라이언트 실행
python mcp_client_gemini.py

# 모든 MCP 서버 종료
cd mcp
./stop_servers.sh
```

## 사용 예시

에이전트를 실행한 후 다음과 같은 질문을 할 수 있습니다:

1. "Grafana 대시보드 목록을 보여줘"
2. "CPU 사용량 대시보드의 메트릭을 조회해줘"
3. "사용 가능한 애플리케이션 목록을 알려줘"
4. "order-service를 배포하고 배포 상태를 확인해줘"
5. "user-service에 대해 50명의 가상 사용자로 30초 동안 성능 테스트를 실행해줘"
6. "GitHub PR 목록을 보여주고 첫 번째 PR을 승인해줘"

## 구현 모델 비교

### OpenAI 기반 에이전트 (mcp_client_react.py)
- OpenAI의 GPT-4o 모델 사용
- 복잡한 작업을 단계별로 처리하는 ReAct 패턴 구현
- 상태 관리를 위한 AgentState 클래스 및 워크플로우 그래프 구현

### Google Vertex AI 기반 에이전트 (mcp_client_gemini.py)
- Google Vertex AI의 Gemini 2.0 Flash 모델 사용
- LangGraph의 create_react_agent 함수를 통한 ReAct 패턴 구현
- 간결한 코드로 DevOps 작업 자동화

## 확장 방법

1. 새로운 도구 추가하기:
   - `mcp` 디렉토리에 새로운 MCP 서버 파일 생성
   - 도구 함수 구현 및 MCP 서버에 등록
   - `mcp_client_gemini.py` 또는 `mcp_client_react.py`의 도구 목록 업데이트

2. 에이전트 프롬프트 수정하기:
   - `mcp_client_gemini.py`의 `PROMPT` 변수 또는 `mcp_client_react.py`의 프롬프트 변수 수정

## 라이선스

MIT 