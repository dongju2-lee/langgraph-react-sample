#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
k6 MCP 서버
성능 테스트 실행 및 결과 비교 기능을 제공합니다.
"""

import random
import time
import uuid
from typing import Dict, Any, List
from mcp.server.fastmcp import FastMCP

# MCP 서버 인스턴스 생성
mcp = FastMCP(
    "k6",  # MCP 서버 이름
    instructions="k6 성능 테스트 도구를 제어하는 서버입니다. 서비스 성능 테스트 실행 및 결과 비교 기능을 제공합니다.",
    host="0.0.0.0",  # 모든 IP에서 접속 허용
    port=10003,  # 포트 번호
)

# 테스트 결과 저장을 위한 딕셔너리
test_results = {}

@mcp.tool()
def run_k6_performance_test(service_name: str, virtual_users: int = 10, duration: str = "30s") -> Dict[str, Any]:
    """
    k6를 사용하여 서비스 성능 테스트를 실행합니다.
    
    Args:
        service_name: 테스트할 서비스 이름 (예: "order-service")
        virtual_users: 가상 사용자 수
        duration: 테스트 지속 시간 (예: "30s", "1m", "5m")
    """
    print(f"====== [도구 호출] run_k6_performance_test 도구가 호출되었습니다. 서비스: {service_name}, VUs: {virtual_users}, 지속시간: {duration} ======")
    
    # 입력값 검증
    if not service_name:
        return {"error": "서비스 이름은 필수 입력값입니다."}
    
    if virtual_users < 1:
        return {"error": "가상 사용자 수는 1 이상이어야 합니다."}
    
    # 지속 시간 형식 검증 (간단히 's', 'm', 'h'로 끝나는지만 확인)
    if not duration.endswith(('s', 'm', 'h')):
        return {"error": "지속 시간은 's', 'm', 'h' 단위로 입력해야 합니다. (예: '30s', '1m', '5m')"}
    
    # 테스트 ID 생성
    test_id = str(uuid.uuid4())
    
    # 테스트 실행 중 메시지
    print(f"{service_name}에 대한 성능 테스트를 실행 중입니다... (VUs: {virtual_users}, 지속시간: {duration})")
    
    # 테스트 실행 시뮬레이션 (실제로는 k6 명령어 실행)
    # 여기서는 간단히 시간 지연으로 시뮬레이션
    start_time = time.time()
    
    # 시뮬레이션된 테스트 결과 생성
    avg_response_time = random.uniform(50, 500)  # 50ms~500ms
    p95_response_time = avg_response_time * random.uniform(1.5, 2.5)
    requests_per_second = random.uniform(50, 2000)
    error_rate = random.uniform(0, 15)
    
    # 테스트 결과 저장
    result = {
        "test_id": test_id,
        "service_name": service_name,
        "config": {
            "virtual_users": virtual_users,
            "duration": duration
        },
        "results": {
            "avg_response_time_ms": round(avg_response_time, 2),
            "p95_response_time_ms": round(p95_response_time, 2),
            "requests_per_second": round(requests_per_second, 2),
            "error_rate_percentage": round(error_rate, 2),
            "http_200": round(random.uniform(80, 100), 2),
            "http_4xx": round(random.uniform(0, 10), 2),
            "http_5xx": round(random.uniform(0, 10), 2)
        },
        "status": "성공" if error_rate < 5 else "주의 필요",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    }
    
    # 결과 저장
    test_results[test_id] = result
    
    return {
        "success": True,
        "message": f"{service_name}에 대한 성능 테스트가 완료되었습니다.",
        "test_id": test_id,
        "results": result
    }

@mcp.tool()
def compare_k6_tests(test_id1: str, test_id2: str) -> Dict[str, Any]:
    """
    두 개의 성능 테스트 결과를 비교합니다.
    
    Args:
        test_id1: 첫 번째 테스트 ID
        test_id2: 두 번째 테스트 ID
    """
    print(f"====== [도구 호출] compare_k6_tests 도구가 호출되었습니다. 테스트 ID: {test_id1}, {test_id2} ======")
    
    # 두 테스트 결과가 모두 존재하는지 확인
    if test_id1 not in test_results:
        return {"error": f"테스트 ID '{test_id1}'을(를) 찾을 수 없습니다."}
    
    if test_id2 not in test_results:
        return {"error": f"테스트 ID '{test_id2}'을(를) 찾을 수 없습니다."}
    
    test1 = test_results[test_id1]
    test2 = test_results[test_id2]
    
    # 비교 결과 계산
    avg_response_time_diff = test2["results"]["avg_response_time_ms"] - test1["results"]["avg_response_time_ms"]
    avg_response_time_diff_percent = (avg_response_time_diff / test1["results"]["avg_response_time_ms"]) * 100
    
    p95_response_time_diff = test2["results"]["p95_response_time_ms"] - test1["results"]["p95_response_time_ms"]
    p95_response_time_diff_percent = (p95_response_time_diff / test1["results"]["p95_response_time_ms"]) * 100
    
    rps_diff = test2["results"]["requests_per_second"] - test1["results"]["requests_per_second"]
    rps_diff_percent = (rps_diff / test1["results"]["requests_per_second"]) * 100
    
    error_rate_diff = test2["results"]["error_rate_percentage"] - test1["results"]["error_rate_percentage"]
    
    # 성능 변화 요약
    performance_change = "향상" if avg_response_time_diff < 0 and rps_diff > 0 else "저하" if avg_response_time_diff > 0 and rps_diff < 0 else "혼합"
    
    # 응답 생성
    comparison = {
        "test1": {
            "test_id": test_id1,
            "service_name": test1["service_name"],
            "config": test1["config"]
        },
        "test2": {
            "test_id": test_id2,
            "service_name": test2["service_name"],
            "config": test2["config"]
        },
        "comparison": {
            "avg_response_time_diff_ms": round(avg_response_time_diff, 2),
            "avg_response_time_diff_percent": round(avg_response_time_diff_percent, 2),
            "p95_response_time_diff_ms": round(p95_response_time_diff, 2),
            "p95_response_time_diff_percent": round(p95_response_time_diff_percent, 2),
            "requests_per_second_diff": round(rps_diff, 2),
            "requests_per_second_diff_percent": round(rps_diff_percent, 2),
            "error_rate_diff_percentage": round(error_rate_diff, 2)
        },
        "summary": {
            "performance_change": performance_change,
            "highlights": []
        }
    }
    
    # 주목할만한 변화를 하이라이트에 추가
    if abs(avg_response_time_diff_percent) > 10:
        comparison["summary"]["highlights"].append(
            f"평균 응답 시간이 {abs(round(avg_response_time_diff_percent, 2))}% {'감소' if avg_response_time_diff < 0 else '증가'}했습니다."
        )
    
    if abs(rps_diff_percent) > 10:
        comparison["summary"]["highlights"].append(
            f"초당 요청 처리량이 {abs(round(rps_diff_percent, 2))}% {'증가' if rps_diff > 0 else '감소'}했습니다."
        )
    
    if abs(error_rate_diff) > 1:
        comparison["summary"]["highlights"].append(
            f"오류율이 {abs(round(error_rate_diff, 2))}% {'감소' if error_rate_diff < 0 else '증가'}했습니다."
        )
    
    return {
        "success": True,
        "message": f"{test1['service_name']}에 대한 두 테스트 결과를 비교했습니다.",
        "comparison": comparison
    }

if __name__ == "__main__":
    print("k6 MCP 서버를 시작합니다. (포트: 10003)")
    # SSE 전송 방식으로 MCP 서버 실행
    mcp.run(transport="sse") 