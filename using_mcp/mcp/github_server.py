#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GitHub MCP 서버
PR 목록 조회 및 PR 승인 기능을 제공합니다.
"""

import random
import time
from typing import Dict, Any, List
from mcp.server.fastmcp import FastMCP

# MCP 서버 인스턴스 생성
mcp = FastMCP(
    "GitHub",  # MCP 서버 이름
    instructions="GitHub 코드 관리 도구를 제어하는 서버입니다. PR 목록 조회 및 PR 승인 기능을 제공합니다.",
    host="0.0.0.0",  # 모든 IP에서 접속 허용
    port=10004,  # 포트 번호
)

# 시뮬레이션에 사용할 GitHub PR 데이터
github_prs = [
    {
        "id": 101,
        "title": "사용자 인증 기능 개선",
        "author": "developer1",
        "branch": "feature/auth-improvement",
        "status": "open",
        "created_at": "2023-05-10T09:30:00Z",
        "updated_at": "2023-05-10T14:20:00Z",
        "comments": 5,
        "approved": False
    },
    {
        "id": 102,
        "title": "주문 서비스 성능 최적화",
        "author": "developer2",
        "branch": "perf/order-service",
        "status": "open",
        "created_at": "2023-05-11T10:15:00Z",
        "updated_at": "2023-05-11T16:45:00Z",
        "comments": 8,
        "approved": False
    },
    {
        "id": 103,
        "title": "레스토랑 검색 API 추가",
        "author": "developer3",
        "branch": "feature/restaurant-search",
        "status": "open",
        "created_at": "2023-05-12T08:20:00Z",
        "updated_at": "2023-05-12T13:10:00Z",
        "comments": 3,
        "approved": False
    }
]

@mcp.tool()
def list_github_prs() -> Dict[str, Any]:
    """
    GitHub Pull Request 목록을 조회합니다.
    현재 열린 PR의 ID, 제목, 작성자, 브랜치, 상태 등의 정보를 반환합니다.
    """
    print("====== [도구 호출] list_github_prs 도구가 호출되었습니다. ======")
    
    # PR 목록에서 필요한 정보만 추출
    prs_info = []
    for pr in github_prs:
        # 이미 승인된 PR은 목록에서 제외
        if pr["approved"]:
            continue
            
        prs_info.append({
            "id": pr["id"],
            "title": pr["title"],
            "author": pr["author"],
            "branch": pr["branch"],
            "status": pr["status"],
            "created_at": pr["created_at"],
            "comments": pr["comments"]
        })
    
    return {
        "success": True,
        "pull_requests": prs_info
    }

@mcp.tool()
def approve_github_pr(pr_id: int) -> Dict[str, Any]:
    """
    GitHub Pull Request를 승인합니다.
    
    Args:
        pr_id: 승인할 PR ID
    """
    print(f"====== [도구 호출] approve_github_pr 도구가 호출되었습니다. PR ID: {pr_id} ======")
    
    # PR ID 유효성 검사
    found_pr = None
    for pr in github_prs:
        if pr["id"] == pr_id:
            found_pr = pr
            break
    
    if not found_pr:
        return {"error": f"PR ID '{pr_id}'을(를) 찾을 수 없습니다."}
    
    # 이미 승인된 PR인지 확인
    if found_pr["approved"]:
        return {
            "success": False,
            "message": f"PR #{pr_id}는 이미 승인되었습니다."
        }
    
    # PR 승인 처리
    found_pr["approved"] = True
    found_pr["status"] = "approved"
    found_pr["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    return {
        "success": True,
        "message": f"PR #{pr_id}가 성공적으로 승인되었습니다.",
        "pull_request": {
            "id": found_pr["id"],
            "title": found_pr["title"],
            "status": found_pr["status"],
            "approved_at": found_pr["updated_at"]
        }
    }

if __name__ == "__main__":
    print("GitHub MCP 서버를 시작합니다. (포트: 10004)")
    # SSE 전송 방식으로 MCP 서버 실행
    mcp.run(transport="sse") 