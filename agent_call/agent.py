# agent.py
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage
from agent_call.mcp_config import client
from agent_call.middleware import create_hitl_middleware



# 需要把初始化的过程封装好，让 CLI 能调用
async def build_graph():    
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
        checkpointer=InMemorySaver(), # 实际部署用 PostgresSaver 等
        system_prompt="""
            你是爱帮助人的导航与设备控制助手周香同学，
            请调用合适的工具按照合适的顺序完成用户指令，
            最后简短总结你调用了哪些工具完成任务。
        """
      )
    return agent

async def main(query: str):
    agent = await build_graph()
    result = agent.invoke(
    {"messages": [HumanMessage(content=query)]},
    config={"configurable": {"thread_id": "session-1"}}
)

    print(result)


if __name__ == "__main__":
    asyncio.run(main("你是什么牛马"))
