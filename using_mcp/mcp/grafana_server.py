#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Grafana MCP 서버
대시보드 검색, 대시보드 메트릭 조회, 데이터 소스 조회 기능을 제공합니다.
"""

import random
from typing import Dict, Any, List
from mcp.server.fastmcp import FastMCP

# MCP 서버 인스턴스 생성
mcp = FastMCP(
    "Grafana",  # MCP 서버 이름
    instructions="Grafana 모니터링 도구를 제어하는 서버입니다. 대시보드 검색, 메트릭 조회, 데이터소스 조회 기능을 제공합니다.",
    host="0.0.0.0",  # 모든 IP에서 접속 허용
    port=10001,  # 포트 번호
)

# 시뮬레이션에 사용할 대시보드 데이터
grafana_dashboards = ["cpu-usage-dashboard", "memory-usage-dashboard", "pod-count-dashboard"]
grafana_datasources = ["Prometheus", "Loki", "Tempo"]

@mcp.tool()
def search_grafana_dashboards() -> Dict[str, Any]:
    """
    Grafana 대시보드 목록을 검색합니다.
    CPU 사용량, 메모리 사용량, 파드 수 등의 대시보드를 반환합니다.
    """
    print("====== [도구 호출] search_grafana_dashboards 도구가 호출되었습니다. ======")
    
    return {
        "success": True,
        "dashboards": grafana_dashboards
    }

@mcp.tool()
def get_dashboard_metrics(dashboard_name: str) -> Dict[str, Any]:
    """
    Grafana 대시보드의 메트릭을 조회합니다.
    대시보드 이름을 입력하면 해당 대시보드의 메트릭을 반환합니다.
    
    Args:
        dashboard_name: 메트릭을 조회할 대시보드 이름
    """
    print(f"====== [도구 호출] get_dashboard_metrics 도구가 호출되었습니다. 대시보드: {dashboard_name} ======")
    
    if dashboard_name not in grafana_dashboards and dashboard_name.lower() not in [d.lower() for d in grafana_dashboards]:
        return {"error": f"대시보드 '{dashboard_name}'을(를) 찾을 수 없습니다."}
    
    metrics = {}
    
    if dashboard_name.lower() == "cpu-usage-dashboard" or dashboard_name.lower() == "cpu-usage":
        cpu_usage = random.randint(20, 100)
        metrics = {
            "title": "CPU 사용량 대시보드",
            "metrics": {
                "current_usage": f"{cpu_usage}%",
                "average_usage_1h": f"{random.randint(20, cpu_usage)}%",
                "peak_usage_24h": f"{random.randint(cpu_usage, 100)}%",
                "threshold": "80%",
                "status": "정상" if cpu_usage < 80 else "경고"
            },
            "services": {
                "user-service": f"{random.randint(20, 60)}%",
                "restaurant-service": f"{random.randint(20, 60)}%",
                "order-service": f"{random.randint(20, 60)}%"
            }
        }
    elif dashboard_name.lower() == "memory-usage-dashboard" or dashboard_name.lower() == "memory-usage":
        memory_usage = random.randint(20, 100)
        metrics = {
            "title": "메모리 사용량 대시보드",
            "metrics": {
                "current_usage": f"{memory_usage}%",
                "average_usage_1h": f"{random.randint(20, memory_usage)}%",
                "peak_usage_24h": f"{random.randint(memory_usage, 100)}%",
                "threshold": "85%",
                "status": "정상" if memory_usage < 85 else "경고"
            },
            "services": {
                "user-service": f"{random.randint(20, 70)}%",
                "restaurant-service": f"{random.randint(20, 70)}%",
                "order-service": f"{random.randint(20, 70)}%"
            }
        }
    elif dashboard_name.lower() == "pod-count-dashboard" or dashboard_name.lower() == "pod-count":
        pod_count = random.randint(15, 30)
        metrics = {
            "title": "파드 수 대시보드",
            "metrics": {
                "total_pods": pod_count,
                "running_pods": random.randint(pod_count - 5, pod_count),
                "pending_pods": random.randint(0, 3),
                "failed_pods": random.randint(0, 2)
            },
            "services": {
                "user-service": random.randint(3, 8),
                "restaurant-service": random.randint(4, 10),
                "order-service": random.randint(5, 12)
            }
        }
    
    return {
        "success": True,
        "dashboard_name": dashboard_name,
        "data": metrics
    }

@mcp.tool()
def get_grafana_datasources() -> Dict[str, Any]:
    """
    Grafana에 연결된 데이터 소스 목록을 조회합니다.
    Prometheus, Loki, Tempo 등의 데이터 소스를 반환합니다.
    """
    print("====== [도구 호출] get_grafana_datasources 도구가 호출되었습니다. ======")
    
    return {
        "success": True,
        "datasources": [
            {
                "name": "Prometheus",
                "type": "prometheus",
                "url": "http://prometheus:9090",
                "status": "활성"
            },
            {
                "name": "Loki",
                "type": "loki",
                "url": "http://loki:3100",
                "status": "활성"
            },
            {
                "name": "Tempo",
                "type": "tempo",
                "url": "http://tempo:3200",
                "status": "활성"
            }
        ]
    }

if __name__ == "__main__":
    print("Grafana MCP 서버를 시작합니다. (포트: 10001)")
    # SSE 전송 방식으로 MCP 서버 실행
    mcp.run(transport="sse") 