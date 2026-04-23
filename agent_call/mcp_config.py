"""
MCP 客户端配置
配置两个 MCP 服务：
1. 高德导航 MCP (amap-mcp)
2. 自定义 MCP (custom-mcp)

都使用 streamable-http 传输方式
"""

import os

from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "Phone-use": {
            # Make sure you start your weather server on port 8000
            "url": os.getenv("CUSTOM_MCP_URL"),
            "transport": "http",
        },
        "Amap": {
            # Make sure you start your weather server on port 8000
            "url": os.getenv("AMAP_MCP_URL"),
            "transport": "http",
        },
    }
)


async def main():
    tools = await client.get_tools()
    print(tools)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
