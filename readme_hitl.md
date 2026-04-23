# LangGraph HITL 终端交互指南

本文档介绍如何通过 `client_apis/agent_client.py` 与 LangGraph Server 进行流式交互。

---

## 1. 启动顺序

```bash
# Terminal 1: MCP 工具服务（必须先启动）
uv run python -m agent_call.custom_mcp_server

# Terminal 2: LangGraph Dev Server
uv run langgraph dev

# Terminal 3: 终端对话客户端
uv run python -m client_apis.agent_client
```

---

## 2. 三种会话模式

启动客户端后，输入数字选择：

### 模式 1 — 自动关联历史对话（推荐）

1. 客户端新建一个 `thread`
2. 用户输入第一条消息
3. `MemoryRouter` 查询 `/threads/search`，获取最近的历史 thread
4. 用 **kimi-k2-turbo-preview** 判断新消息是否与历史 thread 关联（二分类：y/n）
5. 如果关联：从历史 thread 提取最后 3 轮对话，格式化为一条 `HumanMessage` 注入到新 thread
6. 如果历史超过 3 轮：用 **kimi-k2-0905-preview** 先压缩为摘要
7. 注入后 `inject_context = False`，后续消息不再做关联查询，直接发送到此 thread
8. LangGraph `InMemorySaver` checkpoint 住所有消息，后续消息自然看到历史

### 模式 2 — 查看并继续历史对话

1. 客户端展示最近 10 个 idle thread（按更新时间倒序）
2. 用户选择序号，直接复用该 thread_id
3. 第一条消息同样走模式 1 的关联逻辑（后续不再关联）

### 模式 3 — 强制开启新 session

1. 直接 `POST /threads` 创建新 thread
2. `inject_context = False`，完全不注入任何历史上下文
3. 干净的全新对话

---

## 3. 核心 API 调用链

### 创建 Thread
```
POST /threads
Body: {"metadata": {"graph_id": "my_mcp_agent"}}
→ {"thread_id": "..."}
```

### 搜索历史 Thread
```
POST /threads/search
Body: {
  "metadata": {"graph_id": "my_mcp_agent"},
  "limit": 10,
  "status": "idle",
  "sort_by": "updated_at",
  "sort_order": "desc"
}
→ [thread, ...]
```
每个 thread 包含 `thread_id`、`updated_at`、`values.messages`（最新状态快照）。

### 获取最新 Checkpoint（用于 HITL 恢复）
```
POST /threads/{thread_id}/history
Body: {"limit": 1}
→ [{"checkpoint_id": "...", "values": {...}}]
```

### 发起流式对话
```
POST /threads/{thread_id}/runs/stream
Body: {
  "input": {"messages": [...]},
  "stream_mode": ["messages-tuple", "values", "custom"],
  "stream_subgraphs": true,
  "stream_resumable": true,
  "assistant_id": "...",
  "on_disconnect": "cancel"
}
```

> **注意**：`input.messages[0].id` 必须是由客户端生成的 UUID，不能省略或使用占位符。

---

## 4. SSE 事件流解析

客户端通过 SSE（Server-Sent Events）接收流式响应，每条消息以 `event:` 和 `data:` 开头。

### Event: `messages`

包含 AI 文本输出和工具调用。

**`type: AIMessageChunk`**：
- `content`：增量文本片段，直接追加到输出
- `tool_calls`：工具调用数组（含 `id`、`name`、`args`），缓存等待结果

**`type: tool`**：
- `tool_call_id`：匹配之前缓存的调用 ID
- `content`：工具执行结果

### Event: `values`

反映图的完整状态快照。当包含 `__interrupt__` 字段且非空时，代表 HITL 中断触发。

```json
{
  "__interrupt__": [{
    "value": {
      "action_requests": [{
        "name": "get_gps",
        "args": {"target": "春熙路"},
        "description": "🔔 需要人工确认 - 敏感操作..."
      }]
    }
  }]
}
```

---

## 5. HITL 中断与恢复

### 捕获中断

在 SSE 的 `values` 事件中检测到 `__interrupt__` 后，立即中断流读取，冻结输出，展示待确认的 `name` 和 `args`。

### 用户决策

| 选项 | 操作 |
|------|------|
| `1` Approve | 直接同意执行 |
| `2` Reject | 拒绝执行，输入拒绝原因 |
| `3` Edit | 修改参数（输入 JSON）|

### 恢复执行（Resume）

恢复前**必须**先调用 `/threads/{thread_id}/history` 获取最新的 `checkpoint_id`。

```
POST /threads/{thread_id}/runs/stream
Body: {
  "stream_mode": ["messages-tuple", "values", "custom"],
  "stream_resumable": false,
  "checkpoint": {
    "checkpoint_id": "最新_checkpoint_id",
    "checkpoint_ns": ""
  },
  "command": {
    "resume": {
      "decisions": [
        {"type": "approve"},
        {"type": "reject", "message": "..."},
        {"type": "edit", "edited_action": {"name": "...", "args": {...}}}
      ]
    }
  }
}
```

---

## 6. 终端渲染规范

### 并发锁（Asyncio Lock）

AI 文本是增量流式返回，工具结果是块状返回。若不加锁会导致输出交错。

```python
self.console_lock = asyncio.Lock()

async def _handle_ai_chunk(self, content: str):
    async with self.console_lock:
        sys.stdout.write(content)
        sys.stdout.flush()
```

维护 `_is_new_line` 状态：AI 开始说话时打印 `AI: ` 前缀，工具表格打印后重置。

### 工具结果表格化

LangGraph 工具返回经常是嵌套序列化的 JSON（list → dict → JSON 字符串）。需要深度解包：

```python
if isinstance(result, str):
    display_result = json.loads(result)
elif isinstance(result, list) and result and 'text' in result[0]:
    display_result = json.loads(result[0]['text'])
```

超长字符串截断至 55 字符，参数截断至 30 字符，格式化为 ASCII 表格：

```
============================================================
工具执行完成: get_gps
------------------------------------------------------------
输入参数 (Args)                  | 执行结果 (Result)
------------------------------------------------------------
{"target": "春熙路"}              | {"lat": 30.65, "lng": 104.08}
============================================================
```

---

## 7. MemoryRouter 内部逻辑

### 相关性判断（`route`）

```
query + 历史 thread 的最后 3 轮对话
  → kimi-k2-turbo-preview
  → y（关联）或 n（不关联）
```

- `force_thread_id` 参数：直接使用该 thread，注入其上下文（用于模式 2 选择旧 thread 后）
- `own_thread_id` 参数：客户端已持有自己的 thread，只取上下文内容，thread_id 不切换

### 上下文构建（`_build_context_for_thread`）

1. 从 thread 的 `values.messages` 提取所有对话轮次
2. 若超过 3 轮，调用 `kimi-k2-0905-preview` 压缩为摘要
3. 返回 `ThreadContext(turns, compressed_history)`

### 上下文注入（`build_injected_messages`）

将 `ThreadContext` 格式化为 LangGraph API 的 `messages` 格式：

- 有摘要：`【相关历史上下文（摘要）】\n<摘要文本>`
- 无摘要：`【相关历史上下文】\n用户: ...\n助手: ...\n...`

作为 `input.messages` 的**第一条**注入，后续消息自然通过 checkpoint 延续。

### 缓存策略

`/threads/search` 结果缓存在 `MemoryRouter._threads_cache` 中（单次交互内），每次发送新消息前调用 `invalidate_cache()` 获取最新状态。

---

## 8. 跨 Session 记忆注入流程（完整链路）

```
用户输入第一条消息（inject_context=True）
  │
  ▼
MemoryRouter.route(own_thread_id=新thread)
  │
  ▼
_is_related(query, thread)
  → kimi-k2-turbo-preview 二分类
  │
  ├─ y → _build_context_for_thread
  │          ├─ turn ≤ 3 → 直接提取
  │          └─ turn > 3 → kimi-k2-0905 压缩摘要
  │          └─ build_injected_messages → [{HumanMessage}]
  │
  └─ n → build_injected_messages → []
          └─ 返回空列表，无上下文注入
  │
  ▼
stream_run(thread_id, injected_messages=[...])
  │
  ▼
LangGraph: InMemorySaver checkpoint 住所有 messages
          模型每次调用都能看到完整上下文
          （后续消息无需再注入）
```
