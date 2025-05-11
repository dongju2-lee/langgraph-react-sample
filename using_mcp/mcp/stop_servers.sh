#!/bin/bash
# -*- coding: utf-8 -*-

# MCP 서버를 모두 종료하는 스크립트
# 실행 권한 부여: chmod +x stop_servers.sh
# 실행 방법: ./stop_servers.sh

echo "===== MCP 서버 종료 ====="

# 종료할 서버 목록
SERVERS=(
    "grafana_server.py"
    "argocd_server.py"
    "k6_server.py"
    "github_server.py"
)

# 각 서버 프로세스 종료
for server in "${SERVERS[@]}"; do
    echo "종료 중: $server"
    pid=$(pgrep -f "$server")
    if [ -n "$pid" ]; then
        pkill -f "$server"
        echo "- $server (PID: $pid) 종료됨"
    else
        echo "- $server 실행 중이 아님"
    fi
done

# 모든 서버가 종료되었는지 확인
sleep 2
echo -e "\n서버 상태 확인:"
for server in "${SERVERS[@]}"; do
    if pgrep -f "$server" > /dev/null; then
        echo "- $server: 아직 실행 중 (강제 종료 시도)"
        pkill -9 -f "$server" || true
    else
        echo "- $server: 종료됨"
    fi
done

echo -e "\n모든 MCP 서버가 종료되었습니다." 