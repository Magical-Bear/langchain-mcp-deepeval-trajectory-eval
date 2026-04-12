# LangGraph HITL (Human-in-the-loop) 终端与流式交互权威指南

本文档全面梳理了与 LangGraph Server 进行流式交互的完整生命周期。涵盖了从基础的会话管理、极其严格的 API Payload 规范，到工具结果的深度嵌套解析，再到前端 Vue3/TS 的现代流式接入方案。

---

## 1. LangGraph API 完整交互与参数实例 (以“导航”为例)

在带有 HITL（人工干预）的 LangGraph 流程中，整个状态机是靠 `thread_id` 和 `checkpoint_id` 驱动的。以下是每一步的完整输入输出实例。

### 1.1 初始化：创建新对话或检索历史
**场景 A：创建新对话**
* **API**: `POST /threads`
* **Request Body**: `{"metadata": {}}`
* **Response (提取 thread_id)**:
    ```json
    {
      "thread_id": "526978a2-f567-4f7d-8926-cc911ab89790",
      "created_at": "2024-05-20T...",
      "status": "idle"
      // ...其他字段
    }
    ```

**场景 B：搜索历史对话**
* **API**: `POST /threads/search`
* **Request Body**: `{"limit": 10, "status": "idle"}`
* **Response**: 返回一个包含多个 Thread 对象的数组，供用户选择。

### 1.2 关键前置动作：获取最新的 Checkpoint ID
**无论是继续历史对话，还是在中断（HITL）后提交决策恢复运行，都必须获取当前 Thread 的最新状态节点！**
* **API**: `POST /threads/{thread_id}/history`
* **Request Body**: `{"limit": 1}`
* **Response**: 返回一个状态数组。**注意：最新的 checkpoint_id 位于数组第 0 项的根节点。**
    ```json
    [
      {
        "values": { /* 历史消息列表 */ },
        "metadata": { "step": 8, "run_id": "..." },
        "checkpoint_id": "1f135c36-e638-6594-8008-54ecc43181fd", // 👈 必须提取这个字段！
        "parent_checkpoint_id": "..."
      }
    ]
    ```

### 1.3 核心流式对话：发起请求与结构要求
* **API**: `POST /threads/{thread_id}/runs/stream`
* **注意暗坑**：`input.messages[0].id` 必须是客户端生成的标准 UUID，否则必定报 `422 Unprocessable Entity`。
* **Request Payload (首次提问)**:
    ```json
    {
        "input": {
            "messages": [
                {
                    "id": "e858dbbd-1133-4f22-8356-59b36d0b674b", 
                    "type": "human",
                    "content": [{"type": "text", "text": "导航到春熙路"}]
                }
            ]
        },
        "stream_mode": ["messages-tuple", "values", "custom"],
        "stream_resumable": true,
        "assistant_id": "你的_assistant_id",
        "on_disconnect": "cancel"
    }
    ```

### 1.4 中断 (HITL) 的拦截与恢复提交
当模型决议调用敏感工具（如 `get_gps`）时，服务端在 SSE 流中下发 `values` 事件，并携带 `__interrupt__`：
```json
// SSE 截获到的数据结构
{
  "__interrupt__": [
    {
      "value": {
        "action_requests": [
          {
            "name": "get_gps",
            "args": {},
            "description": "🔔 需要人工确认 - 敏感操作..."
          }
        ]
      }
    }
  ]
}
```

---
## 2. Python 客户端深度解析与高阶复用
### 2.1 终极嵌套解包器 (Tool Result Unwrapper)

LangGraph 工具返回的结果经常是多层嵌套的序列化字符串（如 list 包 dict 包 JSON 字符串）。直接打印会导致反人类的阅读体验。以下是项目中使用的递归解析器：

```Python

import json

def parse_nested_tool_result(result: any) -> any:
    """
    递归剥离 LangGraph 工具返回的嵌套外衣，直到拿到最里层的干净字典/列表。
    针对场景: [{"type": "text", "text": "{\"name\":\"张三\",\"phone\":\"1380...\"}"}]
    """
    # 1. 如果是字符串，尝试反序列化
    if isinstance(result, str):
        try:
            parsed = json.loads(result)
            return parse_nested_tool_result(parsed) # 递归继续往下探
        except json.JSONDecodeError:
            return result # 真的是纯文本，直接返回
    
    # 2. 如果是列表，且只有一个元素，尝试剥离列表
    elif isinstance(result, list):
        if len(result) == 1:
            return parse_nested_tool_result(result[0])
        else:
            return [parse_nested_tool_result(item) for item in result]
            
    # 3. 如果是字典，检查是否是 LangGraph 包装格式 {"type": "text", "text": "..."}
    elif isinstance(result, dict):
        if len(result) == 2 and "type" in result and "text" in result:
            return parse_nested_tool_result(result["text"])
        else:
            # 正常的字典，遍历解析其 value
            return {k: parse_nested_tool_result(v) for k, v in result.items()}
            
    return result

# 使用示例 (在 _handle_tool_table 函数中):
# clean_result = parse_nested_tool_result(tool_result)
# 然后使用 json.dumps(clean_result, indent=2, ensure_ascii=False) 打印表格
```

### 2.2 语音与全自动化场景适配点

若要将代码改造为全自动语音交互（ASR + TTS），只需替换三个核心钩子 (Hooks)：

输入源 (ASR)：
将 user_input = input("🧑 提问: ") 替换为 user_input = await asr_service.listen()。

流式播报 (TTS)：
在 _handle_ai_chunk(self, content) 中，除了 sys.stdout.write，可以累积到出现标点符号（如 。、！、？）时，推送到 TTS 引擎进行流式合成播报。

中断拦截播报：
在处理 interrupt_data 时，停止当前所有 TTS 播报，通过 TTS 发出警报：“系统请求执行动作：XXX，是否同意？”。然后启动特定语境的 ASR 监听用户的“同意”或“拒绝”指令。

---

## 3. 前端 (Vue 3 + TS) 生产级接入指南

在浏览器端，原生 EventSource 不支持 POST/Body，而 Axios 处理流式数据异常痛苦。我们必须使用 Fetch API 及其高级封装。

### 3.1 核心依赖选型

请求库: @microsoft/fetch-event-source (完美支持 POST + Body + 重连机制)。

Markdown 渲染: 弃用传统的 v-html + markdown-it。强烈建议使用 @chizukicn/vue-stream-markdown 或类似基于 VDOM 优化的流式渲染库，彻底消除光标闪烁和表格重绘跳动问题。

### 3.2 SSE 解析器与 TS 数据接口

你需要定义严格的接口来承载状态流转：
```TS
// types.ts
export interface ToolCall {
  id: string;
  name: string;
  args: Record<string, any>;
  result?: any;
}

export interface HitlRequest {
  tool_name: string;
  args: Record<string, any>;
  description: string;
}

export interface ChatMessage {
  role: 'human' | 'ai';
  content: string;
  toolCalls: ToolCall[]; // 关联的工具调用，用于渲染 UI 卡片
}
```

### 3.3 Fetch Event Source 核心代码骨架

不要在组件里直接写 fetch，抽取到一个单独的 useLangGraphStream.ts Composable 中：
```TS
import { fetchEventSource } from '@microsoft/fetch-event-source';
import { ref } from 'vue';

export function useLangGraphStream(threadId: string, assistantId: string) {
  const currentText = ref('');
  const pendingHitl = ref<HitlRequest | null>(null);

  const startStream = async (payload: any) => {
    // 重置状态
    pendingHitl.value = null;
    
    await fetchEventSource(`http://127.0.0.1:2024/threads/${threadId}/runs/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      async onmessage(ev) {
        const data = JSON.parse(ev.data);

        // 1. 处理流式消息与工具调用
        if (ev.event === 'messages') {
          for (const msg of data) {
            if (msg.type === 'AIMessageChunk') {
              // 文本流追加给 Markdown 渲染器
              if (msg.content) currentText.value += msg.content;
              
              // TODO: 提取 msg.tool_calls 并存入组件状态
            } else if (msg.type === 'tool') {
              // TODO: 使用前文提到的递归解包逻辑清洗 msg.content
              // 将结果注入对应的 tool_call 卡片状态中，触发视图更新
            }
          }
        }
        
        // 2. 捕获中断
        else if (ev.event === 'values') {
          if (data.__interrupt__?.length > 0) {
            const action = data.__interrupt__[0].value.action_requests[0];
            // 触发弹窗
            pendingHitl.value = {
              tool_name: action.name,
              args: action.args,
              description: action.description || '需要人工确认'
            };
            // 抛出特定的异常主动断开流，等待用户操作
            throw new Error('HITL_INTERRUPT'); 
          }
        }
      },
      onclose() {
        console.log('Stream normal close');
      },
      onerror(err) {
        if (err.message === 'HITL_INTERRUPT') {
          return; // 预期的中断，不抛错
        }
        throw err; // 抛出真实网络错误 (如 422)
      }
    });
  };

  return { currentText, pendingHitl, startStream };
}
```

### 3.4 Vue 3 HITL 交互弹窗规范 (UI 层)

当 pendingHitl 有值时，页面应立刻锁定对话框并弹出 Modal。

遮罩层: <div class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50">，强调当前进程挂起。

内容呈现:

标题: 带警告图标的醒目标题。

代码块: 使用 vue-json-pretty 或类似组件高亮显示拦截到的 args。

决策操作流:

[Approve 按钮]: 绿色。点击后静默调用 /history 拿 Checkpoint，发 resume: approve，关闭弹窗。

[Reject 按钮]: 红色。点击不直接发请求，而是将 Modal 内容切换为一个输入框，要求输入拒绝原因（必填），确认后再发 resume: reject。

[Edit 按钮]: 灰色。点击后，原只读的 JSON 展示区变为一个 Monaco Editor，允许用户手动修改参数后发 resume: edit。