# LangChain MCP Agent 项目

基于 LangChain 和 LangGraph 构建的 MCP (Model Context Protocol) Agent，集成高德地图导航和自定义工具服务，支持 Human-in-the-loop 人机交互确认。

## 功能特性

- **多 MCP 服务集成**：同时连接高德地图 MCP 和自定义 MCP 服务
- **Human-in-the-loop**：敏感操作需要人工确认（GPS获取、拨打电话、读取联系人）
- **LangGraph 支持**：使用 LangGraph 编排 Agent 工作流
- **Streamable HTTP**：使用 HTTP 流式传输与 MCP 服务通信
- **多模态 Sub-Agent**：支持视觉理解等专用多模态模型作为子 Agent 接入

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
├── client_apis/                    # 客户端 API 服务
│   ├── __init__.py
│   ├── agent_client.py           # LangGraph HTTP 客户端（交互入口）
│   └── memory_router.py          # 跨 Session 记忆路由（客户端专用）
├── agent_call/                    # Agent 核心代码包（LangGraph 服务端）
│   ├── __init__.py                # 包初始化文件
│   ├── agent.py                   # Agent 主逻辑和构建函数
│   ├── mcp_config.py              # MCP 客户端配置
│   ├── custom_mcp_server.py       # 自定义 MCP 服务器实现
│   ├── middleware.py               # Human-in-the-loop 中间件配置
│   └── vision_agent.py            # 视觉理解 Sub-Agent（多模态模型）
└── readme_hitl.md                 # HITL 客户端接口详细说明
```
## 启动客户端
### uv run python -m client_apis.agent_client
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
- **集成视觉理解 Sub-Agent**

**修改建议**：
- 修改系统提示词：编辑 `system_prompt` 变量
- 更换大模型：修改 `ChatOpenAI` 的参数
- 更换记忆存储：将 `InMemorySaver` 替换为 `PostgresSaver`

### [agent_call/vision_agent.py](agent_call/vision_agent.py) - 视觉理解 Sub-Agent

多模态视觉理解子 Agent，支持多种视觉模型（GPT-4o、Gemini、Claude Vision）。

**核心设计**：
- 使用 `create_agent()` 创建专用视觉子 Agent
- 使用 `@tool` 装饰器包装为工具
- 支持 image_url 和 base64 两种图片输入方式
- 支持 OpenAI/Google GenAI/Anthropic 多种提供商

**环境配置**：
```bash
VISION_MODEL_PROVIDER=openai       # openai / google_genai / anthropic
VISION_MODEL=openai/gpt-4o-mini    # 视觉模型名称
OPENAI_API_KEY=xxx                 # API Key
GOOGLE_API_KEY=xxx                 # 若使用 Google
ANTHROPIC_API_KEY=xxx              # 若使用 Anthropic
```

**使用示例**：
```python
from agent_call.vision_agent import analyze_image

# 使用图片 URL
result = analyze_image.invoke({
    "image_url": "https://example.com/image.jpg",
    "query": "这张图片里有什么？"
})

# 使用 base64
result = analyze_image.invoke({
    "image_base64": base64_string,
    "query": "请读取图片中的文字"
})
```

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

### [client_apis/agent_client.py](client_apis/agent_client.py) - LangGraph HTTP 客户端

与 LangGraph 服务器交互的客户端，提供终端交互界面。

**核心功能**：
- `LangGraphClient` 类：封装所有与 LangGraph API 的交互
- `create_thread()`: 创建新的对话线程
- `search_threads()`: 搜索历史线程
- `stream_run()`: 流式执行对话，支持 SSE 事件处理
- `run()`: 交互式终端主循环

**交互流程**：
```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraphClient.run()                     │
├─────────────────────────────────────────────────────────────┤
│  1. 选择模式: 自动关联历史 / 查看历史 / 强制新session         │
│  2. 创建/选择 thread_id                                     │
│  3. 调用 memory_router.route() 获取历史上下文                │
│  4. 调用 stream_run() 执行流式对话                          │
│     ├─ SSE 事件: messages → 流式输出 AI 回复                │
│     ├─ SSE 事件: tool → 显示工具执行结果                    │
│     └─ SSE 事件: values.__interrupt__ → 触发 HITL 确认     │
│  5. 若有中断: 等待用户输入 (approve/reject/edit)             │
│  6. 递归调用 stream_run() 恢复执行                           │
└─────────────────────────────────────────────────────────────┘
```

**核心方法详解**：

| 方法 | 功能 | 关键参数 |
|------|------|----------|
| `create_thread()` | 创建新线程 | `metadata.graph_id` |
| `stream_run()` | 流式执行请求 | `thread_id`, `input_msg`, `injected_messages`, `command` |
| `_handle_ai_chunk()` | 流式渲染 AI 回复 | 实时输出到终端 |
| `_handle_tool_table()` | 格式化工具执行结果 | 显示工具名、参数、结果 |

**HITL 中断处理**：
```python
# 触发敏感操作时，stream_run() 会返回 interrupt_data
# 客户端等待用户输入:
# - [1] Approve: 批准操作
# - [2] Reject: 拒绝操作（需输入原因）
# - [3] Edit: 编辑参数后重试
# 然后用 command={"resume": {"decisions": [...] }} 恢复执行
```

**启动方式**：
```bash
uv run client_apis/agent_client.py
```

### [client_apis/memory_router.py](client_apis/memory_router.py) - 跨 Session 记忆路由

智能判断当前对话是否需要关联历史上下文，避免重复提供背景信息。

**核心问题**：如何让 Agent "记起"之前的对话？

**解决方案**：MemoryRouter 三步走：
```
┌─────────────────────────────────────────────────────────────┐
│                  MemoryRouter.route()                        │
├─────────────────────────────────────────────────────────────┤
│  Step 1: 获取候选历史                                        │
│  ├─ 从 LangGraph 获取最新的 thread                          │
│  └─ 排除当前 own_thread_id                                  │
│                                                             │
│  Step 2: 语义相关性判断                                      │
│  ├─ 用分类器模型判断当前 query 是否与历史相关                │
│  └─ 相关 → 进入 Step 3，不相关 → 返回空上下文               │
│                                                             │
│  Step 3: 构建注入消息                                        │
│  ├─ 获取历史消息（超过3轮则压缩为摘要）                     │
│  └─ 返回 ThreadContext（包含注入消息列表）                  │
└─────────────────────────────────────────────────────────────┘
```

**核心组件**：

| 组件 | 类型 | 功能 |
|------|------|------|
| `_memory_router` | 单例 | 全局内存路由器实例 |
| `ThreadContext` | 数据类 | 封装上下文消息和元数据 |
| `route()` | 方法 | 核心路由逻辑 |
| `build_injected_messages()` | 方法 | 将 ThreadContext 转为 LangGraph 消息格式 |

**环境配置**：
```bash
# 分类器模型：判断是否关联历史 (y/n 二分类)
CLASSIFIER_MODEL=kimi-k2-turbo-preview

# 上下文压缩模型：历史超过 3 轮时压缩为摘要
COMPRESSOR_MODEL=kimi-k2-0905-preview
```

**使用流程**：
```python
# 1. 初始化
router = get_memory_router(langgraph_base_url=..., assistant_id=...)

# 2. 路由判断（第一次对话时调用）
ctx = await router.route(
    query="用户输入",
    force_thread_id=None,      # 强制关联某个历史 thread
    own_thread_id="当前thread", # 排除自己
)

# 3. 构建注入消息
injected = router.build_injected_messages(ctx)
# → [{"id": "...", "type": "human", "content": [...]}, ...]

# 4. 传给 stream_run
await client.stream_run(thread_id, injected_messages=injected)
```

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

### 视觉理解 Sub-Agent 配置（多模态）
```bash
# 模型提供者：openai（默认）/ google_genai / anthropic
VISION_MODEL_PROVIDER=openai

# 视觉模型（必须支持 vision）
# OpenRouter: openai/gpt-4o-mini, anthropic/claude-3.5-sonnet, google/gemini-1.5-flash
# Google: gemini-1.5-pro, gemini-1.5-flash
# Anthropic: claude-3.5-sonnet-20241022
VISION_MODEL=openai/gpt-4o-mini

# OpenAI/OpenRouter API（VISION_MODEL_PROVIDER=openai 时）
OPENAI_API_KEY=your_openrouter_api_key
OPENAI_BASE_URL=https://openrouter.ai/api/v1

# Google API（VISION_MODEL_PROVIDER=google_genai 时）
GOOGLE_API_KEY=your_google_api_key

# Anthropic API（VISION_MODEL_PROVIDER=anthropic 时）
ANTHROPIC_API_KEY=your_anthropic_api_key
```

获取 OpenRouter API：[https://openrouter.ai/keys](https://openrouter.ai/keys)
获取 Google API：[https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
获取 Anthropic API：[https://console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)

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

## 多模态 Sub-Agent 接入指南

本项目支持将多模态模型（如 GPT-4o、Gemini、Claude Vision）作为 **Sub-Agent** 接入主 Agent，作为专用工具使用。

### 核心设计理念

传统的多模态方案是将视觉模型直接作为 LLM 的一个能力（如 GPT-4V），但这存在几个问题：
- **成本高昂**：每次对话都需要为视觉能力付费
- **模型选择受限**：主模型必须同时支持文本和视觉
- **职责不清晰**：一个模型既要处理对话又要分析图片

本项目采用 **Sub-Agent 模式**：主 Agent 使用轻量级文本模型（如 Kimi K2.5），视觉理解交给专门的视觉模型 Agent 处理。

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    主 Agent (Kimi K2.5)                      │
│                         │                                    │
│            ┌───────────┴───────────┐                        │
│            ▼                       ▼                        │
│   ┌─────────────────┐    ┌─────────────────┐               │
│   │   MCP Tools     │    │  Vision Tool    │               │
│   │  (高德地图等)    │    │  (analyze_image)│               │
│   └─────────────────┘    └────────┬────────┘               │
│                                    │                         │
│                                    ▼                         │
│                         ┌─────────────────┐                 │
│                         │  Vision Sub-    │                 │
│                         │  Agent (GPT-4o) │                 │
│                         └─────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### 快速开始

#### 1. 配置环境变量

在 `.env` 文件中配置视觉模型：

```bash
# 选择视觉模型提供者：openai / google_genai / anthropic
VISION_MODEL_PROVIDER=openai

# 视觉模型名称（必须支持 vision）
VISION_MODEL=openai/gpt-4o-mini

# OpenAI API 配置（OpenRouter 或 OpenAI）
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://openrouter.ai/api/v1  # 使用 OpenRouter

# 或使用 Google
# GOOGLE_API_KEY=your_google_api_key

# 或使用 Anthropic
# ANTHROPIC_API_KEY=your_anthropic_api_key
```

#### 2. 使用方式

Vision Sub-Agent 已经集成到主 Agent 中，可以直接使用：

**方式一：通过 LangGraph 交互**
```python
# 用户发送图片并询问
result = agent.invoke({
    "messages": [
        HumanMessage(content=[
            {"type": "text", "text": "这张图片里有什么？"},
            {"type": "image_url", "image_url": "https://example.com/image.jpg"}
        ])
    ]
})
```

**方式二：直接调用 Vision 工具**
```python
from agent_call.vision_agent import analyze_image

result = analyze_image.invoke({
    "image_url": "https://example.com/image.jpg",
    "query": "请详细描述这张图片的内容"
})
```

**方式三：使用本地图片**
```python
import base64

# 读取本地图片
with open("demo/images/1.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode("utf-8")

result = analyze_image.invoke({
    "image_base64": image_base64,
    "query": "请描述这张图片"
})
```

### 核心代码解析

#### 1. 构建 Sub-Agent

`agent_call/vision_agent.py` 实现了视觉理解子 Agent：

```python
def _build_vision_subagent():
    """
    使用支持 vision 的模型创建子 agent。
    子 agent 只处理图片理解，无其他工具。
    """
    model_provider = os.getenv("VISION_MODEL_PROVIDER", "openai")
    model_name = os.getenv("VISION_MODEL", "gpt-4o-mini")
    
    if model_provider == "google_genai":
        from langchain_google_genai import ChatGoogleGenerativeAI
        model = ChatGoogleGenerativeAI(model=model_name, ...)
    elif model_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        model = ChatAnthropic(model_name=model_name, ...)
    else:  # openai
        from langchain_openai import ChatOpenAI
        model = ChatOpenAI(model=model_name, ...)
    
    return create_agent(
        model=model,
        tools=[],  # 无需其他工具
        system_prompt="你是专业的视觉理解助手..."
    )
```

#### 2. 包装为工具

使用 `@tool` 装饰器将子 Agent 包装为主 Agent 可调用的工具：

```python
@tool("vision", description="分析图片内容，提取文字、物体、场景等信息")
def analyze_image(
    image_url: str = None,
    image_base64: str = None,
    query: str = "请详细描述这张图片的内容",
) -> str:
    # 构建多模态消息
    content = [
        {"type": "text", "text": query},
        {"type": "image_url", "image_url": image_url}
    ]
    
    # 调用视觉子 agent
    result = subagent.invoke({"messages": [HumanMessage(content=content)]})
    return result["messages"][-1].content
```

#### 3. 集成到主 Agent

在 `agent_call/agent.py` 中注册工具：

```python
async def build_graph():
    # 获取 MCP 工具
    tools = await client.get_tools()
    
    # 追加视觉工具
    tools.append(analyze_image)
    
    # 创建主 Agent
    agent = create_agent(
        model=model,
        tools=tools,  # 包含视觉工具
        middleware=[create_hitl_middleware()],
        ...
    )
    return agent
```

### 支持的多模态模型

| 提供商 | 模型 | 配置示例 |
|--------|------|----------|
| OpenRouter | GPT-4o-mini, Claude-3.5-Sonnet | `VISION_MODEL=openai/gpt-4o-mini` |
| Google | Gemini-1.5-Flash, Gemini-1.5-Pro | `VISION_MODEL_PROVIDER=google_genai` |
| Anthropic | Claude-3.5-Sonnet | `VISION_MODEL_PROVIDER=anthropic` |

### 添加新的多模态 Sub-Agent

如果要添加其他类型的 Sub-Agent（如语音转文字、文档解析等），可参考以下模板：

```python
from langchain.tools import tool
from langchain.agents import create_agent

def _build_my_subagent():
    """构建专用子 Agent"""
    model = ChatOpenAI(model="gpt-4o", ...)
    return create_agent(
        model=model,
        tools=[],
        system_prompt="你的专属系统提示词..."
    )

subagent = _build_my_subagent()

@tool("my_tool", description="工具描述")
def my_tool(input: str) -> str:
    result = subagent.invoke({"messages": [HumanMessage(content=input)]})
    return result["messages"][-1].content
```

### 最佳实践

1. **模型选择**：
   - 主 Agent：使用性价比高的文本模型（如 Kimi K2.5）
   - 视觉 Sub-Agent：使用专门的视觉模型（如 GPT-4o-mini）

2. **错误处理**：
   ```python
   try:
       result = analyze_image.invoke({"image_url": url, "query": query})
   except Exception as e:
       return f"图片分析失败: {str(e)}"
   ```

3. **异步调用**：
   ```python
   # 如果需要异步调用
   async def async_analyze():
       result = await analyze_image.ainvoke({
           "image_url": url,
           "query": query
       })
       return result
   ```

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
- **Moonshot/Kimi**: 主 Agent 大语言模型
- **GPT-4o/Gemini/Claude Vision**: 视觉理解 Sub-Agent
- **UV**: Python 包管理

## 许可证

MIT License
