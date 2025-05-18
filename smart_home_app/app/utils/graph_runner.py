import asyncio
import logging
from langfuse.callback import CallbackHandler
from graph.main_graph import build_main_graph
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import HumanMessage
import logging

logger = logging.getLogger("runner")
logging.basicConfig(level=logging.INFO)
memory= MemorySaver()

class GraphRunner:
    def __init__(self) -> None:
        
        self._graph = build_main_graph().compile(checkpointer=memory)
        self._lock = asyncio.Lock()
        self.langfuse_handler =  CallbackHandler(
            public_key="",
            secret_key="",
            host=""
        )
    async def ask(self, *, session_id: str, user_input: str) -> str:
        logger.info(
            f"GraphRunner received user input: {user_input} "
            f"for session: {session_id}"
        )
        state = {
            "messages": [],
            "system_mode": "normal",
            "recipe": None,
            "current_step": None
         }

        callbacks = []

        async with self._lock:
            try:
                state["messages"].append(HumanMessage(content=user_input))
                final_state = await self._graph.ainvoke(input=state, config={"callbacks": [self.langfuse_handler],"configurable": {"thread_id": session_id}})
              
            except Exception as e:
                logger.error(f"Graph execution error: {e}")
                raise

        

        response = final_state["messages"][-1].content
        logger.info(f"response: { response}")

        return response