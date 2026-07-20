from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest, StreamEvent
import asyncio


router = APIRouter()


# 决定了 SSE 的格式
def sse(event: StreamEvent) -> str:
    return f"data: {event.model_dump_json(exclude_none=True, ensure_ascii=False)}\n\n"


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    async def event_generator():
        try:
            # 这里先做一个最小可用的流式测试：把固定文案逐字拆成 token 发给前端
            # 等后面接模型时，可以把这个 for 循环替换成真实 LLM 的逐 token 输出
            text = f"收到消息：{req.message}。这是一个流式测试回复。"
            if req.message.strip().lower() == "message":
                yield sse(
                    StreamEvent(
                        type="message",
                        content={
                            "role": "assistant",
                            "content": "这是一条结构化消息测试",
                        },
                    )
                )

            for ch in text:
                yield sse(StreamEvent(type="token", content=ch))
                await asyncio.sleep(0.05)

            # 告诉前端本次流式输出结束，页面会在收到 end 后停止 loading 状态
            yield sse(StreamEvent(type="end", content=""))
        except Exception as e:
            # yield sse(StreamEvent(type="error", content=str(e)))
            raise Exception(str(e))

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
