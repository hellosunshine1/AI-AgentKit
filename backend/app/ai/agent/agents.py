from pydoc import describe
from pydantic import BaseModel, Field
from dataclasses import dataclass
from langgraph.graph.state import CompiledStateGraph

DEFAULT_AGENT = "oa-assistant"


class AgentInfo(BaseModel):
    """
    前端 Agent 选择器展示用的Agent 元信息
    """

    key: str = Field(..., description="Agent 唯一标识", example=["oa-assistant"])
    description: str = Field(..., description="Agent 描述", example="公司 OA 助手")


@dataclass
class Agent:
    description: str
    graph: CompiledStateGraph  # 编译后的Agent 状态图
