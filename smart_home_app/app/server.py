import uuid
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from utils.graph_runner import GraphRunner

import logging
logger = logging.getLogger("server")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Async Cooking Assistant")
runner = GraphRunner()


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    response: str


@app.post(
    "/chat", response_model=ChatResponse, summary="Process chat messages"
)
async def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message is empty")

    session = req.session_id or str(uuid.uuid4())
    try:
        answer = await runner.ask(session_id=session, user_input=req.message)
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    return ChatResponse(session_id=session, response=answer)


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run("server:app", host="0.0.0.0", port=8999, reload=True)