from app.ai.tools.oa_tools import get_user_info, get_user_department
from langchain.globals import set_verbose, set_debug  # pyright: ignore[reportMissingImports]

from langgraph.graph import MessagesState, StateGraph, END
from langchain_core.runnables import RunnableSerializable, RunnableConfig
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode
from ai.llm import get_model, settings
from langgraph.checkpoint.memory import MemorySaver
import logging
from typing import Literal

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(filename)s[line:%(lineno)d] - %(funcName)s() - %(message)s",
)


set_debug(True)
set_verbose(False)


class AgentState(MessagesState):
    """
    Agent 在图中流转的状态
    MessagesState 已内置 messages 字段：存放整段对话历史
    （HumanMessage / AIMessage / ToolMessage 等）。
    每个节点读这个状态，也可往 messages 里追加新消息。
    """

    pass


instructions = """
    你是公司 OA 系统的助手，任务是帮助用户查询公司内部的行政与人事相关信息。
    请根据用户的问题，使用工具从数据库和知识库中查询相关信息，再返回给用户。
    不允许随意伪造公司相关制度或规定，以免凭空误导用户。
    需要回答用户的问题，并确保答案准确、完整。
    请紧扣用户的问题作答，避免回答用户并不关心的内容。
    当前时间是：{current_time}
"""

tools = [get_user_info, get_user_department]


async def call_model(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    调用模型节点，返回模型响应。
    Args:
        state: 当前图状态，包含消息历史。
        config: 运行配置，包含模型选择等参数。
    Returns:
        AgentState: 本轮模型响应。
    """
    # 优先按配置里的模型名取，没有就用默认模型
    m = get_model(config["configurable"].get("model", settings.DEFAULT_MODEL))
    # 把刚拿到的裸模型 m，包装成一条可直接使用的执行链。
    model_runnable = wrap_model(m)
    # 异步调用包装好的模型链，把当前状态和配置喂进去，等它跑完，把结果存到 response
    response = await model_runnable.ainvoke(state, config)
    return {"messages": [response]}


def wrap_model(model: BaseChatModel) -> RunnableSerializable:
    """
    将基础聊天模型包装为可直接接入 LangGraph 的可执行链。
    Args:
        model: 尚未绑定工具的聊天模型实例，例如 DeepSeek 或 OpenAI 的聊天模型。
    Returns:
        RunnableSerializable: 一个可执行的处理链，先注入系统提示词，再将消息交给模型处理，
        最终输出模型响应。
    """
    # 给模型先“装上”一组它可以调用的工具。
    model = model.bind_tools(tools)

    preprocessor = RunnableLambda(
        # 先注入系统提示词，再把当前对话消息传给模型，确保模型始终带着 OA 角色和规则作答。
        lambda state: [SystemMessage(content=instructions)] + state["messages"]
    )
    return preprocessor | model


def pending_tool_calls(state: AgentState) -> Literal["tools", "done"]:
    """
    根据模型最后一条消息是否包含工具调用，决定图的下一跳。
    Args:
        state: 当前图状态，最后一条消息应为模型刚返回的消息。
    Returns:
        Literal["tools", "done"]:
        - "tools" 表示进入工具节点
        - "done" 表示结束当前轮对话
    Raises:
        TypeError: 当最后一条消息不是 AIMessage 时抛出。
    """
    # 拿最后一条消息
    last_message = state["messages"][-1]
    # 判断 last_message 这个对象，是否属于 AIMessage 这个类
    if not isinstance(last_message, AIMessage):
        raise TypeError(f"最后一条消息不是 AIMessage,got {type(last_message)}")
    # tool_calls 列表里有工具调用请求，就返回 "tools"；否则返回 "done"。
    if last_message.tool_calls:
        return "tools"
    else:
        return "done"


# 创建一个以 AgentState 为状态结构的 LangGraph 状态图
agent = StateGraph(AgentState)
# 添加一个模型节点，并绑定 call_model 函数
agent.add_node("model", call_model)
# 这个节点专门负责执行工具调用
agent.add_node("tools", ToolNode(tools=tools))

# 从 model 这个节点开始执行。
agent.set_entry_point("model")


# 模型节点执行完以后，先看模型有没有发起工具调用；有的话就走 tools，没有的话就结束
agent.add_conditional_edges(
    "model", pending_tool_calls, {"tools": "tools", "done": END}
)
# 当前节点是tools 下一步可以直接走到 model
agent.add_edge("tools", "model")


oa_assistant = agent.compile(checkpointer=MemorySaver())

oa_assistant.name = "oa_assistant"

# print(oa_assistant.get_graph().draw_mermaid())
