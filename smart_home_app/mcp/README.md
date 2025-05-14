# 스마트홈 MCP 서버

스마트홈 시스템의 API를 MCP(Model Context Protocol) 형태로 제공하는 서버 모음입니다.
이 서버들은 AI 모델이 스마트홈의 가전제품을 제어하고 정보를 조회할 수 있도록 도구(tools)를 제공합니다.

## 통신 방식

모든 MCP 서버는 SSE(Server-Sent Events) 방식으로 통신합니다. 각 서버는 다음과 같은 URL을 통해 접근할 수 있습니다:

- `http://localhost:[PORT]/mcp`

## 필요 패키지

```bash
pip install -r requirements.txt
```

## 환경 설정

`.env.example` 파일을 `.env`로 복사한 후, 필요한 설정을 수정하세요:

```bash
cp .env.example .env
```

## 포함된 MCP 서버

### 1. 냉장고 MCP 서버 (refrigerator_mcp.py) - 포트 8001
- 식재료 조회/추가
- 디스플레이 상태/내용 조회/설정 
- 요리 상태 조회

### 2. 인덕션 MCP 서버 (induction_mcp.py) - 포트 8002
- 전원 상태 조회/토글
- 조리 시작/중단

### 3. 전자레인지 MCP 서버 (microwave_mcp.py) - 포트 8003
- 전원 상태 조회/토글
- 조리 시작/중단
- 남은 시간 조회

### 4. 모바일 MCP 서버 (mobile_mcp.py) - 포트 8004
- 메시지 조회/전송/삭제
- 캘린더 일정 조회/추가/삭제

### 5. 요리 MCP 서버 (cooking_mcp.py) - 포트 8005
- 식재료 기반 요리 추천
- 레시피 조회
- 요리 시작 (냉장고 디스플레이 활용)

### 6. 선호도 관리 MCP 서버 (personalization_mcp.py) - 포트 8006
- 선호도 조회/추가/삭제
- 가전기기 목록 조회
- 선호도 분석

## 사용 방법

### 모든 서버 한번에 실행 (셸 스크립트 사용)

모든 MCP 서버를 한 번에 실행하려면 다음 셸 스크립트를 사용하세요:

```bash
# 실행 권한 부여
chmod +x run_mcp_servers.sh

# 스크립트 실행
./run_mcp_servers.sh
```

서버를 종료하려면:

```bash
# 실행 권한 부여
chmod +x stop_mcp_servers.sh

# 스크립트 실행
./stop_mcp_servers.sh
```

### 서버 실행 도움말

실행 도움말을 확인하려면:

```bash
python run_servers_help.py
```

### 개별 서버 실행

각 MCP 서버를 개별적으로 실행하려면 별도의 터미널 창에서 다음 명령어를 실행하세요:

```bash
# 냉장고 MCP 서버
python refrigerator_mcp.py

# 인덕션 MCP 서버
python induction_mcp.py

# 전자레인지 MCP 서버
python microwave_mcp.py

# 모바일 MCP 서버
python mobile_mcp.py

# 요리 MCP 서버
python cooking_mcp.py

# 선호도 관리 MCP 서버
python personalization_mcp.py
```

또는 다음과 같이 python3 명령으로 실행할 수도 있습니다:

```bash
python3 refrigerator_mcp.py
```

## API 서버 연동

모든 MCP 서버는 기본적으로 `http://localhost:8000`에서 실행 중인 API 서버와 통신합니다.
다른 URL을 사용하려면 `.env` 파일 내의 `MOCK_SERVER_URL` 변수를 수정하세요.

## 예시 질문

스마트홈 에이전트에게 다음과 같은 질문을 해볼 수 있습니다:

1. "냉장고에 있는 식재료를 알려줘"
2. "소고기로 만들 수 있는 요리를 추천해줘"
3. "인덕션 전원을 켜줘"
4. "전자레인지를 3분 동안 작동시켜줘"
5. "홍길동에게 '오늘 저녁에 만나자'라는 문자를 보내줘"
6. "내일 오전 10시에 '회의' 일정을 추가해줘"
7. "내가 좋아하는 음식은 뭐야?"
8. "냉장고 디스플레이에 '우유 사기'라고 표시해줘" 