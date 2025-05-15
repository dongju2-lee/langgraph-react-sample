from .supervisor import build_supervisor_graph

def build_main_graph():
    """
    전체 스마트홈 그래프를 생성합니다.
    인자 없이 바로 그래프를 반환합니다.
    """
    graph = build_supervisor_graph()
    return graph
