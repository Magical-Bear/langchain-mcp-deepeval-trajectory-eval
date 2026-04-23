"""
LangChain MCP Agent - 周香同学

构建 LangGraph agent，连接 MCP tools，支持 HITL。
build_graph() 是 langgraph dev 的入口点（langgraph.json 指向此处）。

跨 Session 记忆注入方式：
  客户端在调用 /threads/{id}/runs/stream 时，通过 input.messages 的第一条 HumanMessage
  注入【相关历史上下文】。LangGraph 的 InMemorySaver 会自动 checkpoint 住所有 messages，
  模型每次调用都能看到完整上下文，无需在 agent 端做任何特殊处理。
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from agent_call.mcp_config import client
from agent_call.middleware import create_hitl_middleware


SYSTEM_PROMPT = (
    "你是爱帮助人的导航与设备控制助手周香同学，"
    "请调用合适的工具按照合适的顺序完成用户指令，"
    "最后简短总结你调用了哪些工具完成任务。"
)


async def build_graph():
    """
    LangGraph agent 入口，供 langgraph dev 使用。
    返回编译后的 agent graph。
    """
    tools = await client.get_tools()

    model = ChatOpenAI(
        model=os.getenv("MOONSHOT_MODEL", "kimi-k2-5"),
        temperature=1,
        max_tokens=10000,
        timeout=30,
        api_key=os.getenv("MOONSHOT_API_KEY"),
        base_url=os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1")
    )

    agent = create_agent(
        model=model,
        tools=tools,
        middleware=[create_hitl_middleware()],
        checkpointer=InMemorySaver(),
        system_prompt=SYSTEM_PROMPT,
    )
    return agent


async def main(query: str):
    from langchain_core.messages import HumanMessage

    agent = await build_graph()
    result = agent.invoke(
        {"messages": [HumanMessage(content=query)]},
        config={"configurable": {"thread_id": "session-1"}}
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main("你是什么牛马"))
