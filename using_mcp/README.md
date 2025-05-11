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
├── generate_scenario_using_mcp_server.py         # 하드코딩된 도구 정보 사용 버전
├── generate_scenario_using_mcp_server_get_tool.py # 동적 도구 정보 사용 버전
├── react_using_mcp.py        # ReAct 패턴 구현 버전
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

## 핵심 파일 분석

이 프로젝트에는 세 가지 핵심 구현 파일이 있으며, 각각 다른 접근 방식을 보여줍니다:

### 1. generate_scenario_using_mcp_server.py

**기능**: DevOps 플래닝 에이전트 (하드코딩 방식)
- Google Vertex AI의 Gemini 모델을 사용하여 계획 생성
- 도구 정보가 코드 내에 하드코딩되어 있음 (`get_tools_info()` 함수)
- 실제 도구 호출 없이 사용자 요청에 따른 작업 계획만 생성
- 비동기 방식으로 LLM API 호출

**한계점**:
- 새로운 도구가 추가될 때마다 코드 수정 필요
- 도구 정보의 동적 업데이트 불가능
- 코드 중복 이슈 존재

### 2. generate_scenario_using_mcp_server_get_tool.py

**기능**: 동적 도구 정보 기반 DevOps 플래닝 에이전트
- MCP 서버에서 도구 정보를 동적으로 가져와 사용
- SSE(Server-Sent Events) 통신으로 외부 서버와 연동
- 향상된 오류 처리 및 리소스 관리 기능 구현

**주요 개선사항**:
- `init_mcp_client()` / `close_mcp_client()`: MCP 서버 연결/종료 안전하게 관리
- `get_mcp_tools()`: 서버에서 도구 정보 동적 수집
- `convert_mcp_tools_to_info()`: 도구 정보를 프롬프트용 형식으로 변환
- 도구 정보 캐싱을 통한 성능 최적화
- 신호 처리기를 통한 안전한 프로그램 종료
- 비동기 컨텍스트 관리자를 활용한 리소스 관리

### 3. react_using_mcp.py

**기능**: ReAct 패턴 기반 지능형 DevOps 에이전트
- 사고(Thought)-행동(Action)-관찰(Observation) 주기로 복잡한 작업 처리
- 단순 계획 생성이 아닌 실제 도구 호출 및 실행 가능
- 대화 이력 유지를 통한 맥락 이해
- Google Vertex AI의 Gemini 2.0 Flash 모델 활용

**핵심 구성 요소**:
- `create_devops_agent()`: LangGraph의 ReAct 에이전트 생성
- `run_conversation_async()`: 대화형 인터페이스 구현
- `run_single_query_async()`: 단일 쿼리 처리
- 상세한 시스템 프롬프트를 통한 에이전트 역할 및 행동 지정

## 구현 파일 비교 표

| 특성 | generate_scenario_using_mcp_server.py | generate_scenario_using_mcp_server_get_tool.py | react_using_mcp.py |
|------|--------------------------------------|----------------------------------------------|-------------------|
| 도구 정보 | 하드코딩 | 동적 수집 | 동적 수집 |
| 에러 처리 | 기본적 | 강화됨 | 강화됨 |
| 패턴 | 단순 계획 생성 | 단순 계획 생성 | ReAct 패턴 |
| 도구 실행 | 계획만 생성 | 계획만 생성 | 실제 도구 실행 |
| 컨텍스트 | 없음 | 없음 | 대화 이력 유지 |
| 리소스 관리 | 기본적 | 안전한 종료 구현 | 안전한 종료 구현 |
| 모델 통합 | 단순 API 호출 | 단순 API 호출 | LangGraph 통합 |

## 파일별 발전 과정

세 파일은 DevOps 자동화 에이전트 개발의 발전 과정을 잘 보여줍니다:

1. **1단계(generate_scenario_using_mcp_server.py)**: 가장 기본적인 구현으로, 하드코딩된 도구 정보를 사용하고 계획만 생성합니다.

2. **2단계(generate_scenario_using_mcp_server_get_tool.py)**: MCP 서버에서 도구 정보를 동적으로 수집하여 유연성을 높이고, 향상된 오류 처리와 리소스 관리를 구현했습니다.

3. **3단계(react_using_mcp.py)**: ReAct 패턴을 적용하여 더 지능적인 에이전트를 구현했으며, 실제 도구 호출과 결과를 활용할 수 있습니다.

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

# 하드코딩 도구 정보 버전 실행
python generate_scenario_using_mcp_server.py

# 동적 도구 정보 버전 실행
python generate_scenario_using_mcp_server_get_tool.py

# ReAct 패턴 버전 실행
python react_using_mcp.py

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

## 기술적 과제 및 해결책

### 1. SSE 연결 관리
- **문제**: generate_scenario_using_mcp_server_get_tool.py에서 SSE 연결이 제대로 종료되지 않아 에러 발생
- **해결책**: 
  - `close_mcp_client()` 함수 추가
  - 신호 처리기를 통한 안전한 종료
  - try/finally 블록에서 리소스 정리

### 2. 비동기 작업 관리
- **문제**: 비동기 컨텍스트에서 예외 처리와 리소스 관리의 복잡성
- **해결책**:
  - 컨텍스트 매니저 활용
  - 캐싱을 통한 반복 요청 최소화
  - 오류 발생 시에도 적절한 응답 제공

### 3. LLM 응답 처리
- **문제**: LLM이 도구 호출 형식을 정확히 따르지 않을 수 있음
- **해결책**:
  - 상세한 시스템 프롬프트 제공
  - ReAct 패턴 구현으로 단계별 처리
  - 자세한 예외 처리 및 오류 메시지

## 라이선스

MIT 