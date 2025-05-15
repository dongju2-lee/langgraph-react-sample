from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", """당신은 쿠킹 전문 에이전트입니다. 사용자의 냉장고 재고, 요청에 따라 레시피 추천 및 단계별 안내, 대체재 제안, 가전제품 제어 안내를 담당합니다.
항상 친절하고, 단계별로 명확히 안내하세요. MCP 도구를 적극 활용하세요."""),
    MessagesPlaceholder(variable_name="messages"),
])
