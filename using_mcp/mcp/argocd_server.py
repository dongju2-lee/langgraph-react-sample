#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ArgoCD MCP 서버
애플리케이션 목록 조회, 애플리케이션 배포 등의 기능을 제공합니다.
"""

import random
import time
from typing import Dict, Any, List
from mcp.server.fastmcp import FastMCP

# MCP 서버 인스턴스 생성
mcp = FastMCP(
    "ArgoCD",  # MCP 서버 이름
    instructions="ArgoCD 배포 도구를 제어하는 서버입니다. 애플리케이션 목록 조회, 애플리케이션 배포 기능을 제공합니다.",
    host="0.0.0.0",  # 모든 IP에서 접속 허용
    port=10002,  # 포트 번호
)

# 시뮬레이션에 사용할 ArgoCD 애플리케이션 데이터
argocd_applications = [
    {"name": "user-service", "status": "Healthy"},
    {"name": "restaurant-service", "status": "Healthy"},
    {"name": "order-service", "status": "Healthy"},
    {"name": "payment-service", "status": "Healthy"},
    {"name": "delivery-service", "status": "Healthy"},
    {"name": "notification-service", "status": "Healthy"}
]

@mcp.tool()
def list_argocd_applications() -> Dict[str, Any]:
    """
    ArgoCD 애플리케이션 목록을 조회합니다.
    현재 배포된 모든 마이크로서비스 목록과 상태를 반환합니다.
    """
    print("====== [도구 호출] list_argocd_applications 도구가 호출되었습니다. ======")
    
    response_apps = []
    
    for app in argocd_applications:
        response_apps.append({
            "name": app["name"],
            "status": app["status"],
            "namespace": "default",
            "cluster": "in-cluster",
            "sync_status": "Synced" if app["status"] == "Healthy" else "OutOfSync"
        })
    
    return {
        "success": True,
        "applications": response_apps
    }

@mcp.tool()
def deploy_application(app_name: str) -> Dict[str, Any]:
    """
    ArgoCD를 통해 특정 애플리케이션을 배포합니다.
    
    Args:
        app_name: 배포할 애플리케이션 이름
    """
    print(f"====== [도구 호출] deploy_application 도구가 호출되었습니다. 앱: {app_name} ======")
    
    found_app = None
    
    for app in argocd_applications:
        if app["name"].lower() == app_name.lower():
            found_app = app
            break
    
    if not found_app:
        return {"error": f"애플리케이션 '{app_name}'을(를) 찾을 수 없습니다."}
    
    # 배포 진행 상황 시뮬레이션
    print(f"애플리케이션 {app_name}를 배포 중입니다...")
    
    # 배포 시작 응답
    deploy_result = {
        "success": True,
        "message": f"애플리케이션 {app_name} 배포를 시작했습니다.",
        "application": {
            "name": app_name,
            "previous_status": found_app["status"],
            "current_status": "Progressing",
            "deployment_started": True
        }
    }
    
    # 실제로는 배포가 완료되지만, 시뮬레이션 상에서는 Progressing 상태를 반환
    # (실제 환경에서는 비동기로 처리하며, 상태 확인은 별도 API 호출을 통해 이루어짐)
    
    return deploy_result

# 배포 상태 확인 도구 추가
@mcp.tool()
def check_deployment_status(app_name: str) -> Dict[str, Any]:
    """
    배포 중인 애플리케이션의 현재 상태를 확인합니다.
    
    Args:
        app_name: 상태를 확인할 애플리케이션 이름
    """
    print(f"====== [도구 호출] check_deployment_status 도구가 호출되었습니다. 앱: {app_name} ======")
    
    found_app = None
    
    for app in argocd_applications:
        if app["name"].lower() == app_name.lower():
            found_app = app
            break
    
    if not found_app:
        return {"error": f"애플리케이션 '{app_name}'을(를) 찾을 수 없습니다."}
    
    # 실제 환경에서는 배포 상태를 확인하지만, 여기서는 랜덤으로 성공/진행 중 상태를 반환
    status_options = ["Progressing", "Healthy"]
    deployment_status = status_options[random.randint(0, len(status_options)-1)]
    
    # 80%의 확률로 Healthy 상태 반환 (배포 성공)
    if random.random() < 0.8:
        deployment_status = "Healthy"
    
    return {
        "success": True,
        "application": {
            "name": app_name,
            "status": deployment_status,
            "health_status": deployment_status,
            "sync_status": "Synced" if deployment_status == "Healthy" else "Progressing",
            "message": f"애플리케이션이 {'성공적으로 배포되었습니다' if deployment_status == 'Healthy' else '아직 배포 중입니다'}"
        }
    }

if __name__ == "__main__":
    print("ArgoCD MCP 서버를 시작합니다. (포트: 10002)")
    # SSE 전송 방식으로 MCP 서버 실행
    mcp.run(transport="sse") 