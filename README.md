# LangChain MCP Agent 项目

基于 LangChain 和 LangGraph 构建的 MCP (Model Context Protocol) Agent，集成高德地图导航和自定义工具服务，支持 Human-in-the-loop 人机交互确认。

## 功能特性

- **多 MCP 服务集成**：同时连接高德地图 MCP 和自定义 MCP 服务
- **Human-in-the-loop**：敏感操作需要人工确认（GPS获取、拨打电话、读取联系人）
- **LangGraph 支持**：使用 LangGraph 编排 Agent 工作流
- **Streamable HTTP**：使用 HTTP 流式传输与 MCP 服务通信

## 快速启动

### 1. 安装依赖

```bash
# 使用 uv 安装依赖
uv sync
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
vim .env
```

### 3. 启动服务

**直接运行自定义 MCP 服务器，不可中断**

```bash
# 启动自定义 MCP 服务器（提供 GPS、联系人、拨号等功能）
uv run python -m agent_call.custom_mcp_server
```

**方式一：使用 LangGraph CLI（推荐）**

```bash
# 启动 LangGraph 开发服务器
uv run langgraph dev
```


**方式二：运行 Agent 脚本测试**

```bash
# 直接运行 Agent 测试
uv run python -m agent_call.agent
```

## 项目文件结构

```
.
├── README.md                       # 本文件
├── pyproject.toml                  # Python 项目配置和依赖
├── langgraph.json                  # LangGraph CLI 配置文件
├── uv.lock                         # uv 依赖锁定文件
├── .env.example                    # 环境变量示例
├── main.py                         # 项目入口文件
└── agent_call/                     # Agent 核心代码包
    ├── __init__.py                 # 包初始化文件
    ├── agent.py                    # Agent 主逻辑和构建函数
    ├── mcp_config.py               # MCP 客户端配置
    ├── custom_mcp_server.py        # 自定义 MCP 服务器实现
    └── middleware.py               # Human-in-the-loop 中间件配置
```
## 启动客户端
### uv run client_apis/agent_client.py
### [客户端接口说明文件](readme_hitl.md) - http接口和python改造、sse 帧格式、前端接入指南

## 各文件作用详解

### [langgraph.json](langgraph.json) - LangGraph CLI 配置

LangGraph CLI 的配置文件，定义了图的入口点。

```json
{
  "dependencies": ["."],
  "graphs": {
    "my_mcp_agent": "agent_call/agent.py:build_graph"
  },
  "env": ".env"
}
```

- `graphs`: 定义可用的图，键是图名称，值是 `模块路径:函数名`
- `env`: 指定环境变量文件路径
- **修改建议**：如需添加新的图，在 `graphs` 中添加新的键值对

### [agent_call/agent.py](agent_call/agent.py) - Agent 主逻辑

核心 Agent 实现文件，包含 `build_graph()` 函数用于构建 Agent。

**主要功能**：
- 加载环境变量
- 初始化 MCP 客户端获取工具
- 配置 Kimi/Moonshot 大模型
- 创建带有人机交互中间件的 Agent
- 实现记忆功能（InMemorySaver）

**修改建议**：
- 修改系统提示词：编辑 `system_prompt` 变量
- 更换大模型：修改 `ChatOpenAI` 的参数
- 更换记忆存储：将 `InMemorySaver` 替换为 `PostgresSaver`

### [agent_call/mcp_config.py](agent_call/mcp_config.py) - MCP 配置

配置 MCP 客户端连接的服务列表。

**当前配置的服务**：
- `Phone-use`: 自定义 MCP 服务器（本地 8000 端口）
- `Amap`: 高德地图 MCP 服务器

**修改建议**：
```python
# 添加新的 MCP 服务
client = MultiServerMCPClient(
    {
        "新服务名": {
            "url": "http://your-mcp-server/mcp",
            "transport": "http",
        },
        # ... 现有服务
    }
)
```

### [agent_call/custom_mcp_server.py](agent_call/custom_mcp_server.py) - 自定义 MCP 服务器

实现自定义工具的 MCP 服务器，提供三个核心工具：

| 工具名 | 功能 | 说明 |
|--------|------|------|
| `get_gps` | 获取 GPS 位置 | 返回固定坐标（模拟成都位置） |
| `get_contact_phone` | 获取联系人电话 | 支持张三、李四、王五 |
| `make_call` | 拨打电话 | 模拟拨号功能 |
| `send_sms` | 发送短信 | 模拟短信发送（随机成功/失败） |

**修改建议**：
- 添加新工具：使用 `@mcp.tool()` 装饰器定义新函数
- 修改端口：设置 `CUSTOM_MCP_PORT` 环境变量
- 扩展联系人：修改 `CONTACTS` 字典

### [agent_call/middleware.py](agent_call/middleware.py) - 人机交互中间件

配置 Human-in-the-loop 中间件，定义哪些工具需要人工确认。

**当前配置**：
```python
interrupt_on={
    "get_gps": {"allowed_decisions": ["approve", "reject"]},
    "get_contact_phone": True,  # 允许编辑、批准、拒绝
    "send_sms": True,
    "make_call": {"allowed_decisions": ["approve", "reject"]},
}
```

**修改建议**：
- `True`: 允许所有操作（批准、拒绝、编辑）
- `{"allowed_decisions": ["approve", "reject"]}`: 只允许批准或拒绝

### [pyproject.toml](pyproject.toml) - 项目配置

Python 项目配置文件，包含：
- 项目名称、版本、描述
- Python 版本要求 (>=3.11)
- 依赖包列表

**主要依赖**：
- `langchain>=1.2.15` - LangChain 框架
- `langchain-mcp-adapters>=0.2.2` - MCP 适配器
- `langchain-openai>=1.1.12` - OpenAI/Kimi 模型支持
- `langgraph-cli[inmem]>=0.4.21` - LangGraph CLI
- `fastmcp>=3.2.3` - MCP 服务器开发

## 环境变量配置

复制 `.env.example` 为 `.env` 并填写以下配置：

### Moonshot/Kimi API 配置
```bash
MOONSHOT_API_KEY=your_moonshot_api_key_here
MOONSHOT_BASE_URL=https://api.moonshot.cn/v1
MOONSHOT_MODEL=kimi-k2.5
```

获取地址：[https://platform.moonshot.cn/](https://platform.moonshot.cn/)

### 高德 MCP 配置
```bash
AMAP_MCP_KEY=your_amap_mcp_key_here
AMAP_MCP_URL=https://mcp.amap.com/mcp?key=${AMAP_MCP_KEY}
```

获取地址：[https://mcp.amap.com/](https://mcp.amap.com/)

### 自定义 MCP 配置
```bash
CUSTOM_MCP_URL=http://localhost:8000/mcp
CUSTOM_MCP_PORT=8000
```

### LangSmith 配置（可选）
```bash
LANGSMITH_API_KEY=your_langsmith_api_key
```

## 使用示例

启动服务后，可以通过 LangGraph Studio 或 API 与 Agent 交互：

**示例对话**：
```
用户: 我要导航到天府广场
Agent: [调用高德地图规划路线工具]
Agent: 已为您规划路线，距离 XX 公里，预计用时 XX 分钟

用户: 给张三打电话
Agent: [触发 Human-in-the-loop 确认]
Agent: 正在呼叫张三 (13800000001)...

用户: 我在哪里
Agent: [调用 get_gps 获取位置]
Agent: 您当前位于东经104.095278°, 北纬30.686667°
```

## 开发指南

### 添加新工具

1. 在 `custom_mcp_server.py` 中添加工具函数：
```python
@mcp.tool()
async def my_new_tool(param: str) -> dict:
    """工具描述"""
    return {"result": f"处理结果: {param}"}
```

2. 如需人机确认，在 `middleware.py` 中配置：
```python
interrupt_on={
    "my_new_tool": True,
    # ... 其他配置
}
```

### 添加新的 MCP 服务

1. 在 `mcp_config.py` 中添加服务配置
2. 在 `.env` 中添加对应的环境变量

## 参考资源

### 官方文档与仓库

| 链接 | 说明 | 查找资源 |
|------|------|----------|
| [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters) | MCP 适配器官方仓库 | `MultiServerMCPClient` 用法示例、HTTP/SSE 传输配置、连接多个 MCP 服务器的最佳实践 |
| [LangChain Middleware 文档](https://docs.langchain.com/oss/python/langchain/middleware/overview) | 中间件系统概述 | 中间件的概念、执行顺序、如何创建自定义中间件、与其他组件的交互方式 |
| [Human-in-the-loop 文档](https://docs.langchain.com/oss/python/langchain/human-in-the-loop) | 人机交互官方文档 | `HumanInTheLoopMiddleware` 配置参数、`interrupt_on` 用法、批准/拒绝/编辑决策类型 |
| [LangChain Agents 文档](https://docs.langchain.com/oss/python/langchain/agents) | Agent 框架文档 | `create_agent` 函数用法、工具绑定、记忆配置、系统提示词设置 |
| [Human-in-the-loop 视频教程](https://www.youtube.com/watch?v=SpfT6-YAVPk) | YouTube 官方教程 | `interrupt_on` 参数详解、中间件配置实战、人机交互流程演示 |

### 快速导航

- **MCP 配置问题** → 查看 [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters) 仓库示例代码
- **人机交互配置** → 参考 [Human-in-the-loop 文档](https://docs.langchain.com/oss/python/langchain/human-in-the-loop) 和 [视频教程](https://www.youtube.com/watch?v=SpfT6-YAVPk)
- **Agent 构建问题** → 查看 [LangChain Agents 文档](https://docs.langchain.com/oss/python/langchain/agents)
- **中间件开发** → 参考 [Middleware 文档](https://docs.langchain.com/oss/python/langchain/middleware/overview)

## 技术栈

- **LangChain 1.x**: Agent 框架
- **LangGraph**: 工作流编排
- **FastMCP**: MCP 服务器开发
- **Moonshot/Kimi**: 大语言模型
- **UV**: Python 包管理

## 许可证

MIT License
