from pydantic import BaseModel, Field
from typing import Literal, Any


class ChatRequest(BaseModel):
    """
    前端发给后端的聊天请求。
    这是今天最核心的协议。
    """

    thread_id: str = Field(
        ...,
        description="会话 ID，用来区分不同聊天线程",
        examples=["thread_123"],
    )
    role: Literal["user", "assistant", "system"] = Field(
        default="user",
        description="消息角色，通常前端发过来的是 user",
        examples=["user"],
    )
    message: str = Field(
        ...,
        description="用户输入的文本",
        examples=["你好，帮我查一下这个信息"],
    )
    agent_id: str = Field(
        ...,
        description="Agent ID，用来区分不同 Agent",
        examples=["default-agent"],
    )
    agent_config: dict[str, Any] = Field(
        default_factory=dict,
        description="可选的 Agent 扩展配置",
        examples=[{"temperature": 0.7}],
    )


class StreamEvent(BaseModel):
    """
    后端通过 SSE 返回给前端的同意事件格式。
    """

    type: Literal["token", "message", "end", "error"] = Field(
        ...,
        description="流式事件类型",
        examples=["token"],
    )
    content: Any | None = Field(
        default=None,
        description="事件内容，不同type下含义不同",
    )


class ChatMessage(BaseModel):
    """
    聊天消息结构。
    这个结构主要用于后续message事件，先把格式固定下来。
    """

    role: Literal["user", "ai", "system", "tool"] = Field(
        ...,
        description="消息角色",
        examples=["user"],
    )
    content: str = Field(
        ...,
        description="消息内容",
        examples=["你好，帮我查一下这个信息"],
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="可选的元数据",
        examples=[{"timestamp": "2026-07-20 10:00:00"}],
    )
