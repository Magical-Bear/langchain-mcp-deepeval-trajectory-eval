"""
LangChain 1.0 MCP Agent with Human-in-the-loop

基于 LangChain 1.0 实现的 MCP 工具调用系统：
- Kimi K2.5 模型支持
- 高德导航 MCP 集成
- 自定义 MCP 工具（GPS、联系人、打电话）
- Vision 子 Agent 图片理解（支持本地图片 base64 / URL）
- Human-in-the-loop 人工确认机制
"""

__version__ = "0.1.0"
