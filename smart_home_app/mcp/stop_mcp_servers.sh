#!/bin/bash
# -*- coding: utf-8 -*-

# MCP 서버 모두를 종료하는 스크립트
# 실행 권한 부여: chmod +x stop_mcp_servers.sh
# 실행 방법: ./stop_mcp_servers.sh

echo "===== 스마트홈 MCP 서버 종료 ====="

# 실행 중인 모든 MCP 서버 프로세스 찾기 및 종료
echo "실행 중인 MCP 서버 프로세스를 종료합니다..."

# _mcp.py로 끝나는 모든 프로세스 종료
pkill -f "_mcp.py" && echo "모든 MCP 서버가 종료되었습니다." || echo "실행 중인 MCP 서버가 없습니다."

# 개별 서버 종료 (백업 방법)
SERVER_PATTERNS=(
    "refrigerator_mcp.py"
    "induction_mcp.py"
    "microwave_mcp.py"
    "mobile_mcp.py"
    "cooking_mcp.py"
    "personalization_mcp.py"
)

for pattern in "${SERVER_PATTERNS[@]}"; do
    # 각 서버 프로세스를 개별적으로 종료 (이미 종료되었을 수 있음)
    pkill -f "$pattern" 2>/dev/null || true
done

echo "모든 MCP 서버 프로세스가 정상적으로 종료되었습니다." 