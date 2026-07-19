from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio


router = APIRouter()

class ChatStreamRequest(BaseModel):
  thread_id: str
  role: str
  message: str
  agent_id: str

def sse(data: dict) -> str:
  return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/chat/stream")
async def chat_stream(req: ChatStreamRequest):
    async def event_generator():
        text = f"收到消息：{req.message}。这是一个流式测试回复。"
        for ch in text:
            yield sse({
                "type": "token",
                "content": ch
            })
            await asyncio.sleep(0.05)
        yield sse({
            "type": "end",
            "content": ""
        })
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )