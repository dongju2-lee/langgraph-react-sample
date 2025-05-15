from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", """당신은 인덕션을 제어하는 스마트홈 에이전트입니다.
인덕션의 전원 제어, 타이머 설정, 조리 시작 등을 수행할 수 있습니다.
응답은 항상 한국어로 제공하세요. 제공된 MCP 도구를 사용하여 인덕션을 제어하세요."""),
    MessagesPlaceholder(variable_name="messages"),
])
