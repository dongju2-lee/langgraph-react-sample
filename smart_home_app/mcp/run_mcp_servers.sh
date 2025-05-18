#!/bin/bash
# -*- coding: utf-8 -*-

# MCP 서버 모두를 한 번에 실행하는 스크립트
# 실행 권한 부여: chmod +x run_mcp_servers.sh
# 실행 방법: ./run_mcp_servers.sh

echo "===== 스마트홈 MCP 서버 시작 ====="
echo "모든 MCP 서버를 백그라운드에서 실행합니다."
echo "종료하려면 CTRL+C를 누르세요."

# 현재 스크립트 디렉토리 가져오기
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 서버 목록과 포트 설정
SERVERS=(
    "refrigerator_mcp.py:8001"
    "induction_mcp.py:8002"
    "microwave_mcp.py:8003"
    "mobile_mcp.py:8004"
    "cooking_mcp.py:8005"
    "personalization_mcp.py:8006"
    "tv_mcp.py:10006"
    "audio_mcp.py:10007"
    "light_mcp.py:10008"
    "curtain_mcp.py:10009"
)

# 이미 실행 중인 프로세스 확인 및 종료
for server in "${SERVERS[@]}"; do
    IFS=':' read -r server_name port <<< "$server"
    echo "이전 $server_name 프로세스 확인 중..."
    pkill -f "$server_name" || true
done

echo "모든 이전 MCP 서버 프로세스가 종료되었습니다."
sleep 1

# 각 서버 실행
for server in "${SERVERS[@]}"; do
    IFS=':' read -r server_name port <<< "$server"
    echo "시작: $server_name (포트: $port)"
    # 환경 변수 설정 후 파이썬 스크립트 실행
    MCP_PORT=$port python3 "$server_name" &
    sleep 1  # 서버가 시작할 시간을 주기 위해 약간의 지연
done

# 서버 상태 확인
echo -e "\n모든 MCP 서버가 시작되었습니다."
echo "실행 중인 MCP 서버 확인:"
for server in "${SERVERS[@]}"; do
    IFS=':' read -r server_name port <<< "$server"
    if pgrep -f "$server_name" > /dev/null; then
        echo "- $server_name: 실행 중 (포트: $port)"
    else
        echo "- $server_name: 실패 (포트: $port)"
    fi
done

echo -e "\n모든 서버는 백그라운드에서 실행 중입니다."
echo "각 서버는 다음 URL로 접근할 수 있습니다: http://localhost:[PORT]/mcp"
echo "서버를 종료하려면 다음 명령을 실행하세요: pkill -f '_mcp.py'"

# 로그 확인을 위한 대기
echo -e "\n서버 로그를 확인합니다. 종료하려면 CTRL+C를 누르세요."
tail -f /dev/null 