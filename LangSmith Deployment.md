---
title: LangSmith Deployment
language_tabs:
  - shell: Shell
  - http: HTTP
  - javascript: JavaScript
  - ruby: Ruby
  - python: Python
  - php: PHP
  - java: Java
  - go: Go
toc_footers: []
includes: []
search: true
code_clipboard: true
highlight_theme: darkula
headingLevel: 2
generator: "@tarslib/widdershins v4.0.30"

---

# LangSmith Deployment

Base URLs:

* <a href="http://127.0.0.1:2024">http://127.0.0.1:2024: http://127.0.0.1:2024</a>

# Authentication

# 完整流程

<a id="opIdcreate_thread_threads_post"></a>

## 1. POST Create Thread

POST /threads

Create a thread.

> Body 请求参数

```json
{"metadata": {}}
```

> 200 Response

```json
{
  "thread_id": "1de43264-67cb-48af-89f9-e865c375bb84",
  "created_at": "2019-08-24T14:15:22Z",
  "updated_at": "2019-08-24T14:15:22Z",
  "state_updated_at": "2019-08-24T14:15:22Z",
  "metadata": {},
  "config": {},
  "status": "idle",
  "values": {},
  "interrupts": {},
  "ttl": {
    "strategy": "delete",
    "ttl_minutes": 0,
    "expires_at": "2019-08-24T14:15:22Z"
  },
  "extracted": {}
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Success|[Thread](#schemathread)|
|409|[Conflict](https://tools.ietf.org/html/rfc7231#section-6.5.8)|Conflict|[ErrorResponse](#schemaerrorresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[ErrorResponse](#schemaerrorresponse)|

<a id="opIdstream_run_threads__thread_id__runs_stream_post"></a>

## 2.POST Create Run, Stream Output 

POST /threads/{thread_id}/runs/stream

Create a run in existing thread. Stream the output. step2, path parameters is thread_id

> Body 请求参数

```json
{
    "input": {
        "messages": [
            {
                "id": "31ca725c-3dde-4790-8c32-5431c48cfcbc", # 自己生成
                "type": "human",
                "content": [
                    {
                        "type": "text",
                        "text": "给张三打电话" # 用户请求
                    }
                ]
            }
        ]
    },
    "stream_mode": [
        "values",
        "messages-tuple",
        "custom"
    ],
    "stream_subgraphs": true,
    "stream_resumable": true,
    "assistant_id": "my_mcp_agent", # 环境变量获取
    "on_disconnect": "continue"
}
```

> 200 Response

> 404 Response


### 返回结果

|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Success|string|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Not Found|[ErrorResponse](#schemaerrorresponse)|
|409|[Conflict](https://tools.ietf.org/html/rfc7231#section-6.5.8)|Conflict|[ErrorResponse](#schemaerrorresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[ErrorResponse](#schemaerrorresponse)|

event: metadata
data: {"run_id":"019d7d41-a481-77d1-8991-a4cd2e430c58","attempt":1}
id: 1775922948771-0

event: values
data: {"messages":[{"content":[{"type":"text","text":"给张三打电话"}],"additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"31ca725c-3dde-4790-8c32-5431c48cfcbc"}]}
id: 1775922948773-0

event: messages
data: [{"content":"","additional_kwargs":{},"response_metadata":{"model_provider":"openai"},"type":"AIMessageChunk","name":null,"id":"lc_run--019d7d41-aaa6-7761-ad13-a8d65fbd1992","tool_calls":[],"invalid_tool_calls":[],"usage_metadata":null,"tool_call_chunks":[],"chunk_position":null},{"created_by":"system","graph_id":"my_mcp_agent","assistant_id":"4225f1f1-164f-585e-87aa-7518d04e786d","langgraph_auth_user_id":"","langgraph_request_id":"0ec493d5-aa64-452a-b320-36a60f83b447","run_id":"019d7d41-a481-77d1-8991-a4cd2e430c58","thread_id":"02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6","user_id":"","run_attempt":1,"langgraph_version":"1.1.6","langgraph_api_version":"0.7.99","langgraph_plan":"enterprise","langgraph_host":"self-hosted","langgraph_api_url":"http://127.0.0.1:2024","ls_integration":"langchain_chat_model","langgraph_step":1,"langgraph_node":"model","langgraph_triggers":["branch:to:model"],"langgraph_path":["__pregel_pull","model"],"langgraph_checkpoint_ns":"model:793b9d58-3113-442a-ed8e-a46d0b4544f6","checkpoint_ns":"model:793b9d58-3113-442a-ed8e-a46d0b4544f6","ls_provider":"openai","ls_model_name":"claude-sonnet-4-5-20250929-thinking","ls_model_type":"chat","ls_temperature":1.0,"ls_max_tokens":10000}]
id: 1775922951081-0

event: messages
data: [{"content":"","additional_kwargs":{},"response_metadata":{"model_provider":"openai"},"type":"AIMessageChunk","name":null,"id":"lc_run--019d7d41-aaa6-7761-ad13-a8d65fbd1992","tool_calls":[],"invalid_tool_calls":[],"usage_metadata":null,"tool_call_chunks":[],"chunk_position":null},{"created_by":"system","graph_id":"my_mcp_agent","assistant_id":"4225f1f1-164f-585e-87aa-7518d04e786d","langgraph_auth_user_id":"","langgraph_request_id":"0ec493d5-aa64-452a-b320-36a60f83b447","run_id":"019d7d41-a481-77d1-8991-a4cd2e430c58","thread_id":"02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6","user_id":"","run_attempt":1,"langgraph_version":"1.1.6","langgraph_api_version":"0.7.99","langgraph_plan":"enterprise","langgraph_host":"self-hosted","langgraph_api_url":"http://127.0.0.1:2024","ls_integration":"langchain_chat_model","langgraph_step":1,"langgraph_node":"model","langgraph_triggers":["branch:to:model"],"langgraph_path":["__pregel_pull","model"],"langgraph_checkpoint_ns":"model:793b9d58-3113-442a-ed8e-a46d0b4544f6","checkpoint_ns":"model:793b9d58-3113-442a-ed8e-a46d0b4544f6","ls_provider":"openai","ls_model_name":"claude-sonnet-4-5-20250929-thinking","ls_model_type":"chat","ls_temperature":1.0,"ls_max_tokens":10000}]
id: 1775922951082-0

event: messages
data: [{"content":"我","additional_kwargs":{},"response_metadata":{"model_provider":"openai"},"type":"AIMessageChunk","name":null,"id":"lc_run--019d7d41-aaa6-7761-ad13-a8d65fbd1992","tool_calls":[],"invalid_tool_calls":[],"usage_metadata":null,"tool_call_chunks":[],"chunk_position":null},{"created_by":"system","graph_id":"my_mcp_agent","assistant_id":"4225f1f1-164f-585e-87aa-7518d04e786d","langgraph_auth_user_id":"","langgraph_request_id":"0ec493d5-aa64-452a-b320-36a60f83b447","run_id":"019d7d41-a481-77d1-8991-a4cd2e430c58","thread_id":"02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6","user_id":"","run_attempt":1,"langgraph_version":"1.1.6","langgraph_api_version":"0.7.99","langgraph_plan":"enterprise","langgraph_host":"self-hosted","langgraph_api_url":"http://127.0.0.1:2024","ls_integration":"langchain_chat_model","langgraph_step":1,"langgraph_node":"model","langgraph_triggers":["branch:to:model"],"langgraph_path":["__pregel_pull","model"],"langgraph_checkpoint_ns":"model:793b9d58-3113-442a-ed8e-a46d0b4544f6","checkpoint_ns":"model:793b9d58-3113-442a-ed8e-a46d0b4544f6","ls_provider":"openai","ls_model_name":"claude-sonnet-4-5-20250929-thinking","ls_model_type":"chat","ls_temperature":1.0,"ls_max_tokens":10000}]
id: 1775922951083-0

event: messages
data: [{"content":"","additional_kwargs":{},"response_metadata":{"model_provider":"openai"},"type":"AIMessageChunk","name":null,"id":"lc_run--019d7d41-aaa6-7761-ad13-a8d65fbd1992","tool_calls":[{"name":"","args":{},"id":null,"type":"tool_call"}],"invalid_tool_calls":[],"usage_metadata":null,"tool_call_chunks":[{"name":null,"args":"","id":null,"index":0,"type":"tool_call_chunk"}],"chunk_position":null},{"created_by":"system","graph_id":"my_mcp_agent","assistant_id":"4225f1f1-164f-585e-87aa-7518d04e786d","langgraph_auth_user_id":"","langgraph_request_id":"0ec493d5-aa64-452a-b320-36a60f83b447","run_id":"019d7d41-a481-77d1-8991-a4cd2e430c58","thread_id":"02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6","user_id":"","run_attempt":1,"langgraph_version":"1.1.6","langgraph_api_version":"0.7.99","langgraph_plan":"enterprise","langgraph_host":"self-hosted","langgraph_api_url":"http://127.0.0.1:2024","ls_integration":"langchain_chat_model","langgraph_step":1,"langgraph_node":"model","langgraph_triggers":["branch:to:model"],"langgraph_path":["__pregel_pull","model"],"langgraph_checkpoint_ns":"model:793b9d58-3113-442a-ed8e-a46d0b4544f6","checkpoint_ns":"model:793b9d58-3113-442a-ed8e-a46d0b4544f6","ls_provider":"openai","ls_model_name":"claude-sonnet-4-5-20250929-thinking","ls_model_type":"chat","ls_temperature":1.0,"ls_max_tokens":10000}]
id: 1775922951807-0

event: messages
data: [{"content":"","additional_kwargs":{},"response_metadata":{"model_provider":"openai"},"type":"AIMessageChunk","name":null,"id":"lc_run--019d7d41-aaa6-7761-ad13-a8d65fbd1992","tool_calls":[{"name":"","args":{"name":"张三"},"id":null,"type":"tool_call"}],"invalid_tool_calls":[],"usage_metadata":null,"tool_call_chunks":[{"name":null,"args":"{\"name\": \"张三","id":null,"index":0,"type":"tool_call_chunk"}],"chunk_position":null},{"created_by":"system","graph_id":"my_mcp_agent","assistant_id":"4225f1f1-164f-585e-87aa-7518d04e786d","langgraph_auth_user_id":"","langgraph_request_id":"0ec493d5-aa64-452a-b320-36a60f83b447","run_id":"019d7d41-a481-77d1-8991-a4cd2e430c58","thread_id":"02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6","user_id":"","run_attempt":1,"langgraph_version":"1.1.6","langgraph_api_version":"0.7.99","langgraph_plan":"enterprise","langgraph_host":"self-hosted","langgraph_api_url":"http://127.0.0.1:2024","ls_integration":"langchain_chat_model","langgraph_step":1,"langgraph_node":"model","langgraph_triggers":["branch:to:model"],"langgraph_path":["__pregel_pull","model"],"langgraph_checkpoint_ns":"model:793b9d58-3113-442a-ed8e-a46d0b4544f6","checkpoint_ns":"model:793b9d58-3113-442a-ed8e-a46d0b4544f6","ls_provider":"openai","ls_model_name":"claude-sonnet-4-5-20250929-thinking","ls_model_type":"chat","ls_temperature":1.0,"ls_max_tokens":10000}]
id: 1775922952004-0

event: messages
data: [{"content":"","additional_kwargs":{},"response_metadata":{"model_provider":"openai"},"type":"AIMessageChunk","name":null,"id":"lc_run--019d7d41-aaa6-7761-ad13-a8d65fbd1992","tool_calls":[],"invalid_tool_calls":[{"name":null,"args":"\"}","id":null,"error":null,"type":"invalid_tool_call"}],"usage_metadata":null,"tool_call_chunks":[{"name":null,"args":"\"}","id":null,"index":0,"type":"tool_call_chunk"}],"chunk_position":null},{"created_by":"system","graph_id":"my_mcp_agent","assistant_id":"4225f1f1-164f-585e-87aa-7518d04e786d","langgraph_auth_user_id":"","langgraph_request_id":"0ec493d5-aa64-452a-b320-36a60f83b447","run_id":"019d7d41-a481-77d1-8991-a4cd2e430c58","thread_id":"02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6","user_id":"","run_attempt":1,"langgraph_version":"1.1.6","langgraph_api_version":"0.7.99","langgraph_plan":"enterprise","langgraph_host":"self-hosted","langgraph_api_url":"http://127.0.0.1:2024","ls_integration":"langchain_chat_model","langgraph_step":1,"langgraph_node":"model","langgraph_triggers":["branch:to:model"],"langgraph_path":["__pregel_pull","model"],"langgraph_checkpoint_ns":"model:793b9d58-3113-442a-ed8e-a46d0b4544f6","checkpoint_ns":"model:793b9d58-3113-442a-ed8e-a46d0b4544f6","ls_provider":"openai","ls_model_name":"claude-sonnet-4-5-20250929-thinking","ls_model_type":"chat","ls_temperature":1.0,"ls_max_tokens":10000}]
id: 1775922952006-0

event: messages
data: [{"content":"","additional_kwargs":{},"response_metadata":{"finish_reason":"tool_calls","model_name":"claude-sonnet-4-6","model_provider":"openai"},"type":"AIMessageChunk","name":null,"id":"lc_run--019d7d41-aaa6-7761-ad13-a8d65fbd1992","tool_calls":[],"invalid_tool_calls":[],"usage_metadata":null,"tool_call_chunks":[],"chunk_position":null},{"created_by":"system","graph_id":"my_mcp_agent","assistant_id":"4225f1f1-164f-585e-87aa-7518d04e786d","langgraph_auth_user_id":"","langgraph_request_id":"0ec493d5-aa64-452a-b320-36a60f83b447","run_id":"019d7d41-a481-77d1-8991-a4cd2e430c58","thread_id":"02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6","user_id":"","run_attempt":1,"langgraph_version":"1.1.6","langgraph_api_version":"0.7.99","langgraph_plan":"enterprise","langgraph_host":"self-hosted","langgraph_api_url":"http://127.0.0.1:2024","ls_integration":"langchain_chat_model","langgraph_step":1,"langgraph_node":"model","langgraph_triggers":["branch:to:model"],"langgraph_path":["__pregel_pull","model"],"langgraph_checkpoint_ns":"model:793b9d58-3113-442a-ed8e-a46d0b4544f6","checkpoint_ns":"model:793b9d58-3113-442a-ed8e-a46d0b4544f6","ls_provider":"openai","ls_model_name":"claude-sonnet-4-5-20250929-thinking","ls_model_type":"chat","ls_temperature":1.0,"ls_max_tokens":10000,"LANGSMITH_LANGGRAPH_API_VARIANT":"local_dev","LANGSMITH_TRACING":"true"}]
id: 1775922952099-0

event: messages
data: [{"content":"","additional_kwargs":{},"response_metadata":{},"type":"AIMessageChunk","name":null,"id":"lc_run--019d7d41-aaa6-7761-ad13-a8d65fbd1992","tool_calls":[],"invalid_tool_calls":[],"usage_metadata":null,"tool_call_chunks":[],"chunk_position":"last"},{"created_by":"system","graph_id":"my_mcp_agent","assistant_id":"4225f1f1-164f-585e-87aa-7518d04e786d","langgraph_auth_user_id":"","langgraph_request_id":"0ec493d5-aa64-452a-b320-36a60f83b447","run_id":"019d7d41-a481-77d1-8991-a4cd2e430c58","thread_id":"02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6","user_id":"","run_attempt":1,"langgraph_version":"1.1.6","langgraph_api_version":"0.7.99","langgraph_plan":"enterprise","langgraph_host":"self-hosted","langgraph_api_url":"http://127.0.0.1:2024","ls_integration":"langchain_chat_model","langgraph_step":1,"langgraph_node":"model","langgraph_triggers":["branch:to:model"],"langgraph_path":["__pregel_pull","model"],"langgraph_checkpoint_ns":"model:793b9d58-3113-442a-ed8e-a46d0b4544f6","checkpoint_ns":"model:793b9d58-3113-442a-ed8e-a46d0b4544f6","ls_provider":"openai","ls_model_name":"claude-sonnet-4-5-20250929-thinking","ls_model_type":"chat","ls_temperature":1.0,"ls_max_tokens":10000,"LANGSMITH_LANGGRAPH_API_VARIANT":"local_dev","LANGSMITH_TRACING":"true"}]
id: 1775922952100-0

event: values
data: {"messages":[{"content":[{"type":"text","text":"给张三打电话"}],"additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"31ca725c-3dde-4790-8c32-5431c48cfcbc"},{"content":"我来帮您查找张三的联系方式并拨打电话！","additional_kwargs":{},"response_metadata":{"finish_reason":"tool_calls","model_name":"claude-sonnet-4-6","model_provider":"openai"},"type":"ai","name":null,"id":"lc_run--019d7d41-aaa6-7761-ad13-a8d65fbd1992","tool_calls":[{"name":"get_contact_phone","args":{"name":"张三"},"id":"toolu_bdrk_01Nj8QBjcV6Rej9vXPq3NVyA","type":"tool_call"}],"invalid_tool_calls":[],"usage_metadata":null}]}
id: 1775922952101-0

event: values
data: {"messages":[{"content":[{"type":"text","text":"给张三打电话"}],"additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"31ca725c-3dde-4790-8c32-5431c48cfcbc"},{"content":"我来帮您查找张三的联系方式并拨打电话！","additional_kwargs":{},"response_metadata":{"finish_reason":"tool_calls","model_name":"claude-sonnet-4-6","model_provider":"openai"},"type":"ai","name":null,"id":"lc_run--019d7d41-aaa6-7761-ad13-a8d65fbd1992","tool_calls":[{"name":"get_contact_phone","args":{"name":"张三"},"id":"toolu_bdrk_01Nj8QBjcV6Rej9vXPq3NVyA","type":"tool_call"}],"invalid_tool_calls":[],"usage_metadata":null}],"__interrupt__":[{"value":{"action_requests":[{"name":"get_contact_phone","args":{"name":"张三"},"description":"🔔 需要人工确认 - 敏感操作\n\nTool: get_contact_phone\nArgs: {'name': '张三'}"}],"review_configs":[{"action_name":"get_contact_phone","allowed_decisions":["approve","edit","reject"]}]},"id":"49ad13acb083432933aa4e1afccb3b5a"}]}
id: 1775922952103-0

流式片段中，content部不为空实时处理content流式输出，最后停止连接时解析完整的工具调用片段并提示用户处理，注意检查finish_reason为tool_call说明还要继续为stop/max_token等是结束条件



## POST Get Thread History Post 

POST /threads/{thread_id}/history

Get all past states for a thread.

> Body 请求参数

```json
{
    "limit": 10
}
```



> 返回示例

> 200 Response

```json
[
    {
        "values": {
            "messages": [
                {
                    "content": [
                        {
                            "type": "text",
                            "text": "给张三打电话"
                        }
                    ],
                    "additional_kwargs": {},
                    "response_metadata": {},
                    "type": "human",
                    "name": null,
                    "id": "31ca725c-3dde-4790-8c32-5431c48cfcbc"
                },
                {
                    "content": "我来帮您查找张三的联系方式并拨打电话！",
                    "additional_kwargs": {},
                    "response_metadata": {
                        "finish_reason": "tool_calls",
                        "model_name": "claude-sonnet-4-6",
                        "model_provider": "openai"
                    },
                    "type": "ai",
                    "name": null,
                    "id": "lc_run--019d7d41-aaa6-7761-ad13-a8d65fbd1992",
                    "tool_calls": [
                        {
                            "name": "get_contact_phone",
                            "args": {
                                "name": "张三"
                            },
                            "id": "toolu_bdrk_01Nj8QBjcV6Rej9vXPq3NVyA",
                            "type": "tool_call"
                        }
                    ],
                    "invalid_tool_calls": [],
                    "usage_metadata": null
                },
                {
                    "content": [
                        {
                            "type": "text",
                            "text": "{\"name\":\"张三\",\"phone\":\"13800000001\",\"found\":true}",
                            "id": "lc_a6c48514-4325-4de8-bb09-dbee830d80e6"
                        }
                    ],
                    "additional_kwargs": {},
                    "response_metadata": {},
                    "type": "tool",
                    "name": "get_contact_phone",
                    "id": "93324f99-798d-4935-b05b-b67272323c0f",
                    "tool_call_id": "toolu_bdrk_01Nj8QBjcV6Rej9vXPq3NVyA",
                    "artifact": {
                        "structured_content": {
                            "name": "张三",
                            "phone": "13800000001",
                            "found": true
                        }
                    },
                    "status": "success"
                },
                {
                    "content": "找到张三的电话了，马上为您拨打！",
                    "additional_kwargs": {},
                    "response_metadata": {
                        "finish_reason": "tool_calls",
                        "model_name": "claude-sonnet-4-6",
                        "model_provider": "openai"
                    },
                    "type": "ai",
                    "name": null,
                    "id": "lc_run--019d7d4f-807c-7a62-9e47-997cde69b919",
                    "tool_calls": [
                        {
                            "name": "make_call",
                            "args": {
                                "phone": "13800000001",
                                "name": "张三"
                            },
                            "id": "toolu_bdrk_01M97KNLWxoHhk3UfJX3aGPt",
                            "type": "tool_call"
                        }
                    ],
                    "invalid_tool_calls": [],
                    "usage_metadata": null
                },
                {
                    "content": [
                        {
                            "type": "text",
                            "text": "{\"success\":true,\"phone\":\"13800000001\",\"name\":\"张三\",\"message\":\"正在呼叫 张三 (13800000001)...\"}",
                            "id": "lc_e3754342-da18-4b13-afe1-db5268e82391"
                        }
                    ],
                    "additional_kwargs": {},
                    "response_metadata": {},
                    "type": "tool",
                    "name": "make_call",
                    "id": "b7393059-3eb7-45e5-b379-296be569890e",
                    "tool_call_id": "toolu_bdrk_01M97KNLWxoHhk3UfJX3aGPt",
                    "artifact": {
                        "structured_content": {
                            "success": true,
                            "phone": "13800000001",
                            "name": "张三",
                            "message": "正在呼叫 张三 (13800000001)..."
                        }
                    },
                    "status": "success"
                },
                {
                    "content": "已经成功为您拨打张三（13800000001）的电话！\n\n**任务完成**：我先调用了联系人查询工具找到了张三的电话号码（13800000001），然后调用了拨号工具为您拨打了这个电话。",
                    "additional_kwargs": {},
                    "response_metadata": {
                        "finish_reason": "stop",
                        "model_name": "claude-sonnet-4-5-20250929",
                        "model_provider": "openai"
                    },
                    "type": "ai",
                    "name": null,
                    "id": "lc_run--019d7d5f-2168-75a1-b995-269ff1a9619e",
                    "tool_calls": [],
                    "invalid_tool_calls": [],
                    "usage_metadata": null
                }
            ]
        },
        "next": [],
        "tasks": [],
        "metadata": {
            "graph_id": "my_mcp_agent",
            "assistant_id": "4225f1f1-164f-585e-87aa-7518d04e786d",
            "user_id": "",
            "created_by": "system",
            "checkpoint_id": "1f135c10-71ef-6dc0-8004-250d8c7e2054",
            "checkpoint_ns": "",
            "run_id": "019d7d5f-1b9d-7660-9144-c90214251af1",
            "thread_id": "02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6",
            "run_attempt": 1,
            "langgraph_version": "1.1.6",
            "langgraph_api_version": "0.7.99",
            "langgraph_plan": "enterprise",
            "langgraph_host": "self-hosted",
            "langgraph_api_url": "http://127.0.0.1:2024",
            "source": "loop",
            "step": 8,
            "parents": {},
            "langgraph_auth_user_id": "",
            "langgraph_request_id": "b1331ad2-a196-47d5-aedf-0ae8eada0cdf"
        },
        "created_at": "2026-04-11T16:28:11.210684+00:00",
        "checkpoint": {
            "checkpoint_id": "1f135c36-e638-6594-8008-54ecc43181fd",
            "thread_id": "02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6",
            "checkpoint_ns": ""
        },
        "parent_checkpoint": {
            "checkpoint_id": "1f135c36-e632-6c8e-8007-5e632cfbd52e",
            "thread_id": "02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6",
            "checkpoint_ns": ""
        },
        "interrupts": [],
        "checkpoint_id": "1f135c36-e638-6594-8008-54ecc43181fd", # 需要这个
        "parent_checkpoint_id": "1f135c36-e632-6c8e-8007-5e632cfbd52e"
    }
]
···


## POST Create Run, Stream Output 

POST /threads/{thread_id}/runs/stream

Create a run in existing thread. Stream the output. tell agent user choice and continue generate

> Body 请求参数
{
    "input": {},
    "command": {
        "resume": {
            "decisions": [
                {
                    "type": "approve"
                }
            ]
        }
    },
    "stream_mode": [
        "messages-tuple",
        "values",
        "custom"
    ],
    "stream_resumable": false,
    "assistant_id": "my_mcp_agent",
    "checkpoint": {
        "checkpoint_id": "1f135bee-a96e-65f2-8001-bdecfbd60dd4", # 填上一轮的history中checkout_id, 注意可能有多次中断，每次中断均需要获取history最新的checkout_id并等待用户同意、拒绝或是修改
    
        "checkpoint_ns": ""
    },
    "on_disconnect": "cancel"
}



> 返回示例

> 200 Response

event: metadata
data: {"run_id":"019d7d5f-1b9d-7660-9144-c90214251af1","attempt":1}

event: values
data: {"messages":[{"content":[{"type":"text","text":"给张三打电话"}],"additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"31ca725c-3dde-4790-8c32-5431c48cfcbc"},{"content":"我来帮您查找张三的联系方式并拨打电话！","additional_kwargs":{},"response_metadata":{"finish_reason":"tool_calls","model_name":"claude-sonnet-4-6","model_provider":"openai"},"type":"ai","name":null,"id":"lc_run--019d7d41-aaa6-7761-ad13-a8d65fbd1992","tool_calls":[{"name":"get_contact_phone","args":{"name":"张三"},"id":"toolu_bdrk_01Nj8QBjcV6Rej9vXPq3NVyA","type":"tool_call"}],"invalid_tool_calls":[],"usage_metadata":null},{"content":[{"type":"text","text":"{\"name\":\"张三\",\"phone\":\"13800000001\",\"found\":true}","id":"lc_a6c48514-4325-4de8-bb09-dbee830d80e6"}],"additional_kwargs":{},"response_metadata":{},"type":"tool","name":"get_contact_phone","id":"93324f99-798d-4935-b05b-b67272323c0f","tool_call_id":"toolu_bdrk_01Nj8QBjcV6Rej9vXPq3NVyA","artifact":{"structured_content":{"name":"张三","phone":"13800000001","found":true}},"status":"success"},{"content":"找到张三的电话了，马上为您拨打！","additional_kwargs":{},"response_metadata":{"finish_reason":"tool_calls","model_name":"claude-sonnet-4-6","model_provider":"openai"},"type":"ai","name":null,"id":"lc_run--019d7d4f-807c-7a62-9e47-997cde69b919","tool_calls":[{"name":"make_call","args":{"phone":"13800000001","name":"张三"},"id":"toolu_bdrk_01M97KNLWxoHhk3UfJX3aGPt","type":"tool_call"}],"invalid_tool_calls":[],"usage_metadata":null}]}

event: values
data: {"messages":[{"content":[{"type":"text","text":"给张三打电话"}],"additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"31ca725c-3dde-4790-8c32-5431c48cfcbc"},{"content":"我来帮您查找张三的联系方式并拨打电话！","additional_kwargs":{},"response_metadata":{"finish_reason":"tool_calls","model_name":"claude-sonnet-4-6","model_provider":"openai"},"type":"ai","name":null,"id":"lc_run--019d7d41-aaa6-7761-ad13-a8d65fbd1992","tool_calls":[{"name":"get_contact_phone","args":{"name":"张三"},"id":"toolu_bdrk_01Nj8QBjcV6Rej9vXPq3NVyA","type":"tool_call"}],"invalid_tool_calls":[],"usage_metadata":null},{"content":[{"type":"text","text":"{\"name\":\"张三\",\"phone\":\"13800000001\",\"found\":true}","id":"lc_a6c48514-4325-4de8-bb09-dbee830d80e6"}],"additional_kwargs":{},"response_metadata":{},"type":"tool","name":"get_contact_phone","id":"93324f99-798d-4935-b05b-b67272323c0f","tool_call_id":"toolu_bdrk_01Nj8QBjcV6Rej9vXPq3NVyA","artifact":{"structured_content":{"name":"张三","phone":"13800000001","found":true}},"status":"success"},{"content":"找到张三的电话了，马上为您拨打！","additional_kwargs":{},"response_metadata":{"finish_reason":"tool_calls","model_name":"claude-sonnet-4-6","model_provider":"openai"},"type":"ai","name":null,"id":"lc_run--019d7d4f-807c-7a62-9e47-997cde69b919","tool_calls":[{"name":"make_call","args":{"phone":"13800000001","name":"张三"},"id":"toolu_bdrk_01M97KNLWxoHhk3UfJX3aGPt","type":"tool_call"}],"invalid_tool_calls":[],"usage_metadata":null}]}

event: messages
data: [{"content":[{"type":"text","text":"{\"success\":true,\"phone\":\"13800000001\",\"name\":\"张三\",\"message\":\"正在呼叫 张三 (13800000001)...\"}","id":"lc_e3754342-da18-4b13-afe1-db5268e82391"}],"additional_kwargs":{},"response_metadata":{},"type":"tool","name":"make_call","id":"b7393059-3eb7-45e5-b379-296be569890e","tool_call_id":"toolu_bdrk_01M97KNLWxoHhk3UfJX3aGPt","artifact":{"structured_content":{"success":true,"phone":"13800000001","name":"张三","message":"正在呼叫 张三 (13800000001)..."}},"status":"success"},{"created_by":"system","graph_id":"my_mcp_agent","assistant_id":"4225f1f1-164f-585e-87aa-7518d04e786d","checkpoint_id":"1f135c10-71ef-6dc0-8004-250d8c7e2054","checkpoint_ns":"","langgraph_auth_user_id":"","langgraph_request_id":"b1331ad2-a196-47d5-aedf-0ae8eada0cdf","run_id":"019d7d5f-1b9d-7660-9144-c90214251af1","thread_id":"02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6","user_id":"","run_attempt":1,"langgraph_version":"1.1.6","langgraph_api_version":"0.7.99","langgraph_plan":"enterprise","langgraph_host":"self-hosted","langgraph_api_url":"http://127.0.0.1:2024","ls_integration":"langgraph","langgraph_step":6,"langgraph_node":"tools","langgraph_triggers":["__pregel_push"],"langgraph_path":["__pregel_push",0,false],"langgraph_checkpoint_ns":"tools:688d5ebd-f35d-a03f-33f8-aef693d0b88c","LANGSMITH_LANGGRAPH_API_VARIANT":"local_dev","LANGSMITH_TRACING":"true"}]

event: values
data: {"messages":[{"content":[{"type":"text","text":"给张三打电话"}],"additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"31ca725c-3dde-4790-8c32-5431c48cfcbc"},{"content":"我来帮您查找张三的联系方式并拨打电话！","additional_kwargs":{},"response_metadata":{"finish_reason":"tool_calls","model_name":"claude-sonnet-4-6","model_provider":"openai"},"type":"ai","name":null,"id":"lc_run--019d7d41-aaa6-7761-ad13-a8d65fbd1992","tool_calls":[{"name":"get_contact_phone","args":{"name":"张三"},"id":"toolu_bdrk_01Nj8QBjcV6Rej9vXPq3NVyA","type":"tool_call"}],"invalid_tool_calls":[],"usage_metadata":null},{"content":[{"type":"text","text":"{\"name\":\"张三\",\"phone\":\"13800000001\",\"found\":true}","id":"lc_a6c48514-4325-4de8-bb09-dbee830d80e6"}],"additional_kwargs":{},"response_metadata":{},"type":"tool","name":"get_contact_phone","id":"93324f99-798d-4935-b05b-b67272323c0f","tool_call_id":"toolu_bdrk_01Nj8QBjcV6Rej9vXPq3NVyA","artifact":{"structured_content":{"name":"张三","phone":"13800000001","found":true}},"status":"success"},{"content":"找到张三的电话了，马上为您拨打！","additional_kwargs":{},"response_metadata":{"finish_reason":"tool_calls","model_name":"claude-sonnet-4-6","model_provider":"openai"},"type":"ai","name":null,"id":"lc_run--019d7d4f-807c-7a62-9e47-997cde69b919","tool_calls":[{"name":"make_call","args":{"phone":"13800000001","name":"张三"},"id":"toolu_bdrk_01M97KNLWxoHhk3UfJX3aGPt","type":"tool_call"}],"invalid_tool_calls":[],"usage_metadata":null},{"content":[{"type":"text","text":"{\"success\":true,\"phone\":\"13800000001\",\"name\":\"张三\",\"message\":\"正在呼叫 张三 (13800000001)...\"}","id":"lc_e3754342-da18-4b13-afe1-db5268e82391"}],"additional_kwargs":{},"response_metadata":{},"type":"tool","name":"make_call","id":"b7393059-3eb7-45e5-b379-296be569890e","tool_call_id":"toolu_bdrk_01M97KNLWxoHhk3UfJX3aGPt","artifact":{"structured_content":{"success":true,"phone":"13800000001","name":"张三","message":"正在呼叫 张三 (13800000001)..."}},"status":"success"}]}

: heartbeat

event: messages
data: [{"content":"","additional_kwargs":{},"response_metadata":{"model_provider":"openai"},"type":"AIMessageChunk","name":null,"id":"lc_run--019d7d5f-2168-75a1-b995-269ff1a9619e","tool_calls":[],"invalid_tool_calls":[],"usage_metadata":null,"tool_call_chunks":[],"chunk_position":null},{"created_by":"system","graph_id":"my_mcp_agent","assistant_id":"4225f1f1-164f-585e-87aa-7518d04e786d","checkpoint_id":"1f135c10-71ef-6dc0-8004-250d8c7e2054","checkpoint_ns":"","langgraph_auth_user_id":"","langgraph_request_id":"b1331ad2-a196-47d5-aedf-0ae8eada0cdf","run_id":"019d7d5f-1b9d-7660-9144-c90214251af1","thread_id":"02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6","user_id":"","run_attempt":1,"langgraph_version":"1.1.6","langgraph_api_version":"0.7.99","langgraph_plan":"enterprise","langgraph_host":"self-hosted","langgraph_api_url":"http://127.0.0.1:2024","ls_integration":"langchain_chat_model","langgraph_step":7,"langgraph_node":"model","langgraph_triggers":["branch:to:model"],"langgraph_path":["__pregel_pull","model"],"langgraph_checkpoint_ns":"model:d53315c8-a788-731b-2759-b772523a9467","ls_provider":"openai","ls_model_name":"claude-sonnet-4-5-20250929-thinking","ls_model_type":"chat","ls_temperature":1.0,"ls_max_tokens":10000}]

event: messages
data: [{"content":"","additional_kwargs":{},"response_metadata":{"model_provider":"openai"},"type":"AIMessageChunk","name":null,"id":"lc_run--019d7d5f-2168-75a1-b995-269ff1a9619e","tool_calls":[],"invalid_tool_calls":[],"usage_metadata":null,"tool_call_chunks":[],"chunk_position":null},{"created_by":"system","graph_id":"my_mcp_agent","assistant_id":"4225f1f1-164f-585e-87aa-7518d04e786d","checkpoint_id":"1f135c10-71ef-6dc0-8004-250d8c7e2054","checkpoint_ns":"","langgraph_auth_user_id":"","langgraph_request_id":"b1331ad2-a196-47d5-aedf-0ae8eada0cdf","run_id":"019d7d5f-1b9d-7660-9144-c90214251af1","thread_id":"02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6","user_id":"","run_attempt":1,"langgraph_version":"1.1.6","langgraph_api_version":"0.7.99","langgraph_plan":"enterprise","langgraph_host":"self-hosted","langgraph_api_url":"http://127.0.0.1:2024","ls_integration":"langchain_chat_model","langgraph_step":7,"langgraph_node":"model","langgraph_triggers":["branch:to:model"],"langgraph_path":["__pregel_pull","model"],"langgraph_checkpoint_ns":"model:d53315c8-a788-731b-2759-b772523a9467","ls_provider":"openai","ls_model_name":"claude-sonnet-4-5-20250929-thinking","ls_model_type":"chat","ls_temperature":1.0,"ls_max_tokens":10000}]

event: messages
data: [{"content":"已","additional_kwargs":{},"response_metadata":{"model_provider":"openai"},"type":"AIMessageChunk","name":null,"id":"lc_run--019d7d5f-2168-75a1-b995-269ff1a9619e","tool_calls":[],"invalid_tool_calls":[],"usage_metadata":null,"tool_call_chunks":[],"chunk_position":null},{"created_by":"system","graph_id":"my_mcp_agent","assistant_id":"4225f1f1-164f-585e-87aa-7518d04e786d","checkpoint_id":"1f135c10-71ef-6dc0-8004-250d8c7e2054","checkpoint_ns":"","langgraph_auth_user_id":"","langgraph_request_id":"b1331ad2-a196-47d5-aedf-0ae8eada0cdf","run_id":"019d7d5f-1b9d-7660-9144-c90214251af1","thread_id":"02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6","user_id":"","run_attempt":1,"langgraph_version":"1.1.6","langgraph_api_version":"0.7.99","langgraph_plan":"enterprise","langgraph_host":"self-hosted","langgraph_api_url":"http://127.0.0.1:2024","ls_integration":"langchain_chat_model","langgraph_step":7,"langgraph_node":"model","langgraph_triggers":["branch:to:model"],"langgraph_path":["__pregel_pull","model"],"langgraph_checkpoint_ns":"model:d53315c8-a788-731b-2759-b772523a9467","ls_provider":"openai","ls_model_name":"claude-sonnet-4-5-20250929-thinking","ls_model_type":"chat","ls_temperature":1.0,"ls_max_tokens":10000}]

event: messages
data: [{"content":"话。","additional_kwargs":{},"response_metadata":{"model_provider":"openai"},"type":"AIMessageChunk","name":null,"id":"lc_run--019d7d5f-2168-75a1-b995-269ff1a9619e","tool_calls":[],"invalid_tool_calls":[],"usage_metadata":null,"tool_call_chunks":[],"chunk_position":null},{"created_by":"system","graph_id":"my_mcp_agent","assistant_id":"4225f1f1-164f-585e-87aa-7518d04e786d","checkpoint_id":"1f135c10-71ef-6dc0-8004-250d8c7e2054","checkpoint_ns":"","langgraph_auth_user_id":"","langgraph_request_id":"b1331ad2-a196-47d5-aedf-0ae8eada0cdf","run_id":"019d7d5f-1b9d-7660-9144-c90214251af1","thread_id":"02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6","user_id":"","run_attempt":1,"langgraph_version":"1.1.6","langgraph_api_version":"0.7.99","langgraph_plan":"enterprise","langgraph_host":"self-hosted","langgraph_api_url":"http://127.0.0.1:2024","ls_integration":"langchain_chat_model","langgraph_step":7,"langgraph_node":"model","langgraph_triggers":["branch:to:model"],"langgraph_path":["__pregel_pull","model"],"langgraph_checkpoint_ns":"model:d53315c8-a788-731b-2759-b772523a9467","ls_provider":"openai","ls_model_name":"claude-sonnet-4-5-20250929-thinking","ls_model_type":"chat","ls_temperature":1.0,"ls_max_tokens":10000}]

event: messages
data: [{"content":"","additional_kwargs":{},"response_metadata":{"finish_reason":"stop","model_name":"claude-sonnet-4-5-20250929","model_provider":"openai"},"type":"AIMessageChunk","name":null,"id":"lc_run--019d7d5f-2168-75a1-b995-269ff1a9619e","tool_calls":[],"invalid_tool_calls":[],"usage_metadata":null,"tool_call_chunks":[],"chunk_position":null},{"created_by":"system","graph_id":"my_mcp_agent","assistant_id":"4225f1f1-164f-585e-87aa-7518d04e786d","checkpoint_id":"1f135c10-71ef-6dc0-8004-250d8c7e2054","checkpoint_ns":"","langgraph_auth_user_id":"","langgraph_request_id":"b1331ad2-a196-47d5-aedf-0ae8eada0cdf","run_id":"019d7d5f-1b9d-7660-9144-c90214251af1","thread_id":"02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6","user_id":"","run_attempt":1,"langgraph_version":"1.1.6","langgraph_api_version":"0.7.99","langgraph_plan":"enterprise","langgraph_host":"self-hosted","langgraph_api_url":"http://127.0.0.1:2024","ls_integration":"langchain_chat_model","langgraph_step":7,"langgraph_node":"model","langgraph_triggers":["branch:to:model"],"langgraph_path":["__pregel_pull","model"],"langgraph_checkpoint_ns":"model:d53315c8-a788-731b-2759-b772523a9467","ls_provider":"openai","ls_model_name":"claude-sonnet-4-5-20250929-thinking","ls_model_type":"chat","ls_temperature":1.0,"ls_max_tokens":10000}]

: heartbeat

event: messages
data: [{"content":"","additional_kwargs":{},"response_metadata":{},"type":"AIMessageChunk","name":null,"id":"lc_run--019d7d5f-2168-75a1-b995-269ff1a9619e","tool_calls":[],"invalid_tool_calls":[],"usage_metadata":null,"tool_call_chunks":[],"chunk_position":"last"},{"created_by":"system","graph_id":"my_mcp_agent","assistant_id":"4225f1f1-164f-585e-87aa-7518d04e786d","checkpoint_id":"1f135c10-71ef-6dc0-8004-250d8c7e2054","checkpoint_ns":"","langgraph_auth_user_id":"","langgraph_request_id":"b1331ad2-a196-47d5-aedf-0ae8eada0cdf","run_id":"019d7d5f-1b9d-7660-9144-c90214251af1","thread_id":"02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6","user_id":"","run_attempt":1,"langgraph_version":"1.1.6","langgraph_api_version":"0.7.99","langgraph_plan":"enterprise","langgraph_host":"self-hosted","langgraph_api_url":"http://127.0.0.1:2024","ls_integration":"langchain_chat_model","langgraph_step":7,"langgraph_node":"model","langgraph_triggers":["branch:to:model"],"langgraph_path":["__pregel_pull","model"],"langgraph_checkpoint_ns":"model:d53315c8-a788-731b-2759-b772523a9467","ls_provider":"openai","ls_model_name":"claude-sonnet-4-5-20250929-thinking","ls_model_type":"chat","ls_temperature":1.0,"ls_max_tokens":10000,"LANGSMITH_LANGGRAPH_API_VARIANT":"local_dev","LANGSMITH_TRACING":"true"}]

event: values
data: {"messages":[{"content":[{"type":"text","text":"给张三打电话"}],"additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"31ca725c-3dde-4790-8c32-5431c48cfcbc"},{"content":"我来帮您查找张三的联系方式并拨打电话！","additional_kwargs":{},"response_metadata":{"finish_reason":"tool_calls","model_name":"claude-sonnet-4-6","model_provider":"openai"},"type":"ai","name":null,"id":"lc_run--019d7d41-aaa6-7761-ad13-a8d65fbd1992","tool_calls":[{"name":"get_contact_phone","args":{"name":"张三"},"id":"toolu_bdrk_01Nj8QBjcV6Rej9vXPq3NVyA","type":"tool_call"}],"invalid_tool_calls":[],"usage_metadata":null},{"content":[{"type":"text","text":"{\"name\":\"张三\",\"phone\":\"13800000001\",\"found\":true}","id":"lc_a6c48514-4325-4de8-bb09-dbee830d80e6"}],"additional_kwargs":{},"response_metadata":{},"type":"tool","name":"get_contact_phone","id":"93324f99-798d-4935-b05b-b67272323c0f","tool_call_id":"toolu_bdrk_01Nj8QBjcV6Rej9vXPq3NVyA","artifact":{"structured_content":{"name":"张三","phone":"13800000001","found":true}},"status":"success"},{"content":"找到张三的电话了，马上为您拨打！","additional_kwargs":{},"response_metadata":{"finish_reason":"tool_calls","model_name":"claude-sonnet-4-6","model_provider":"openai"},"type":"ai","name":null,"id":"lc_run--019d7d4f-807c-7a62-9e47-997cde69b919","tool_calls":[{"name":"make_call","args":{"phone":"13800000001","name":"张三"},"id":"toolu_bdrk_01M97KNLWxoHhk3UfJX3aGPt","type":"tool_call"}],"invalid_tool_calls":[],"usage_metadata":null},{"content":[{"type":"text","text":"{\"success\":true,\"phone\":\"13800000001\",\"name\":\"张三\",\"message\":\"正在呼叫 张三 (13800000001)...\"}","id":"lc_e3754342-da18-4b13-afe1-db5268e82391"}],"additional_kwargs":{},"response_metadata":{},"type":"tool","name":"make_call","id":"b7393059-3eb7-45e5-b379-296be569890e","tool_call_id":"toolu_bdrk_01M97KNLWxoHhk3UfJX3aGPt","artifact":{"structured_content":{"success":true,"phone":"13800000001","name":"张三","message":"正在呼叫 张三 (13800000001)..."}},"status":"success"},{"content":"已经成功为您拨打张三（13800000001）的电话！\n\n**任务完成**：我先调用了联系人查询工具找到了张三的电话号码（13800000001），然后调用了拨号工具为您拨打了这个电话。","additional_kwargs":{},"response_metadata":{"finish_reason":"stop","model_name":"claude-sonnet-4-5-20250929","model_provider":"openai"},"type":"ai","name":null,"id":"lc_run--019d7d5f-2168-75a1-b995-269ff1a9619e","tool_calls":[],"invalid_tool_calls":[],"usage_metadata":null}]

event: messages
data: [{"content":"话。","additional_kwargs":{},"response_metadata":{"model_provider":"openai"},"type":"AIMessageChunk","name":null,"id":"lc_run--019d7d5f-2168-75a1-b995-269ff1a9619e","tool_calls":[],"invalid_tool_calls":[],"usage_metadata":null,"tool_call_chunks":[],"chunk_position":null},{"created_by":"system","graph_id":"my_mcp_agent","assistant_id":"4225f1f1-164f-585e-87aa-7518d04e786d","checkpoint_id":"1f135c10-71ef-6dc0-8004-250d8c7e2054","checkpoint_ns":"","langgraph_auth_user_id":"","langgraph_request_id":"b1331ad2-a196-47d5-aedf-0ae8eada0cdf","run_id":"019d7d5f-1b9d-7660-9144-c90214251af1","thread_id":"02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6","user_id":"","run_attempt":1,"langgraph_version":"1.1.6","langgraph_api_version":"0.7.99","langgraph_plan":"enterprise","langgraph_host":"self-hosted","langgraph_api_url":"http://127.0.0.1:2024","ls_integration":"langchain_chat_model","langgraph_step":7,"langgraph_node":"model","langgraph_triggers":["branch:to:model"],"langgraph_path":["__pregel_pull","model"],"langgraph_checkpoint_ns":"model:d53315c8-a788-731b-2759-b772523a9467","ls_provider":"openai","ls_model_name":"claude-sonnet-4-5-20250929-thinking","ls_model_type":"chat","ls_temperature":1.0,"ls_max_tokens":10000}]

event: messages
data: [{"content":"","additional_kwargs":{},"response_metadata":{"finish_reason":"stop","model_name":"claude-sonnet-4-5-20250929","model_provider":"openai"},"type":"AIMessageChunk","name":null,"id":"lc_run--019d7d5f-2168-75a1-b995-269ff1a9619e","tool_calls":[],"invalid_tool_calls":[],"usage_metadata":null,"tool_call_chunks":[],"chunk_position":null},{"created_by":"system","graph_id":"my_mcp_agent","assistant_id":"4225f1f1-164f-585e-87aa-7518d04e786d","checkpoint_id":"1f135c10-71ef-6dc0-8004-250d8c7e2054","checkpoint_ns":"","langgraph_auth_user_id":"","langgraph_request_id":"b1331ad2-a196-47d5-aedf-0ae8eada0cdf","run_id":"019d7d5f-1b9d-7660-9144-c90214251af1","thread_id":"02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6","user_id":"","run_attempt":1,"langgraph_version":"1.1.6","langgraph_api_version":"0.7.99","langgraph_plan":"enterprise","langgraph_host":"self-hosted","langgraph_api_url":"http://127.0.0.1:2024","ls_integration":"langchain_chat_model","langgraph_step":7,"langgraph_node":"model","langgraph_triggers":["branch:to:model"],"langgraph_path":["__pregel_pull","model"],"langgraph_checkpoint_ns":"model:d53315c8-a788-731b-2759-b772523a9467","ls_provider":"openai","ls_model_name":"claude-sonnet-4-5-20250929-thinking","ls_model_type":"chat","ls_temperature":1.0,"ls_max_tokens":10000}]

: heartbeat

event: messages
data: [{"content":"","additional_kwargs":{},"response_metadata":{},"type":"AIMessageChunk","name":null,"id":"lc_run--019d7d5f-2168-75a1-b995-269ff1a9619e","tool_calls":[],"invalid_tool_calls":[],"usage_metadata":null,"tool_call_chunks":[],"chunk_position":"last"},{"created_by":"system","graph_id":"my_mcp_agent","assistant_id":"4225f1f1-164f-585e-87aa-7518d04e786d","checkpoint_id":"1f135c10-71ef-6dc0-8004-250d8c7e2054","checkpoint_ns":"","langgraph_auth_user_id":"","langgraph_request_id":"b1331ad2-a196-47d5-aedf-0ae8eada0cdf","run_id":"019d7d5f-1b9d-7660-9144-c90214251af1","thread_id":"02a4593c-ea1a-4a9f-be8e-7340dc9c1ed6","user_id":"","run_attempt":1,"langgraph_version":"1.1.6","langgraph_api_version":"0.7.99","langgraph_plan":"enterprise","langgraph_host":"self-hosted","langgraph_api_url":"http://127.0.0.1:2024","ls_integration":"langchain_chat_model","langgraph_step":7,"langgraph_node":"model","langgraph_triggers":["branch:to:model"],"langgraph_path":["__pregel_pull","model"],"langgraph_checkpoint_ns":"model:d53315c8-a788-731b-2759-b772523a9467","ls_provider":"openai","ls_model_name":"claude-sonnet-4-5-20250929-thinking","ls_model_type":"chat","ls_temperature":1.0,"ls_max_tokens":10000,"LANGSMITH_LANGGRAPH_API_VARIANT":"local_dev","LANGSMITH_TRACING":"true"}]

event: values
data: {"messages":[{"content":[{"type":"text","text":"给张三打电话"}],"additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"31ca725c-3dde-4790-8c32-5431c48cfcbc"},{"content":"我来帮您查找张三的联系方式并拨打电话！","additional_kwargs":{},"response_metadata":{"finish_reason":"tool_calls","model_name":"claude-sonnet-4-6","model_provider":"openai"},"type":"ai","name":null,"id":"lc_run--019d7d41-aaa6-7761-ad13-a8d65fbd1992","tool_calls":[{"name":"get_contact_phone","args":{"name":"张三"},"id":"toolu_bdrk_01Nj8QBjcV6Rej9vXPq3NVyA","type":"tool_call"}],"invalid_tool_calls":[],"usage_metadata":null},{"content":[{"type":"text","text":"{\"name\":\"张三\",\"phone\":\"13800000001\",\"found\":true}","id":"lc_a6c48514-4325-4de8-bb09-dbee830d80e6"}],"additional_kwargs":{},"response_metadata":{},"type":"tool","name":"get_contact_phone","id":"93324f99-798d-4935-b05b-b67272323c0f","tool_call_id":"toolu_bdrk_01Nj8QBjcV6Rej9vXPq3NVyA","artifact":{"structured_content":{"name":"张三","phone":"13800000001","found":true}},"status":"success"},{"content":"找到张三的电话了，马上为您拨打！","additional_kwargs":{},"response_metadata":{"finish_reason":"tool_calls","model_name":"claude-sonnet-4-6","model_provider":"openai"},"type":"ai","name":null,"id":"lc_run--019d7d4f-807c-7a62-9e47-997cde69b919","tool_calls":[{"name":"make_call","args":{"phone":"13800000001","name":"张三"},"id":"toolu_bdrk_01M97KNLWxoHhk3UfJX3aGPt","type":"tool_call"}],"invalid_tool_calls":[],"usage_metadata":null},{"content":[{"type":"text","text":"{\"success\":true,\"phone\":\"13800000001\",\"name\":\"张三\",\"message\":\"正在呼叫 张三 (13800000001)...\"}","id":"lc_e3754342-da18-4b13-afe1-db5268e82391"}],"additional_kwargs":{},"response_metadata":{},"type":"tool","name":"make_call","id":"b7393059-3eb7-45e5-b379-296be569890e","tool_call_id":"toolu_bdrk_01M97KNLWxoHhk3UfJX3aGPt","artifact":{"structured_content":{"success":true,"phone":"13800000001","name":"张三","message":"正在呼叫 张三 (13800000001)..."}},"status":"success"},{"content":"已经成功为您拨打张三（13800000001）的电话！\n\n**任务完成**：我先调用了联系人查询工具找到了张三的电话号码（13800000001），然后调用了拨号工具为您拨打了这个电话。","additional_kwargs":{},"response_metadata":{"finish_reason":"stop","model_name":"claude-sonnet-4-5-20250929","model_provider":"openai"},"type":"ai","name":null,"id":"lc_run--019d7d5f-2168-75a1-b995-269ff1a9619e","tool_calls":[],"invalid_tool_calls":[],"usage_metadata":null}]}


# HITL 三个指令，均需要转为标准json
允许指令

resume={
            "decisions": [
                {
                    "type": "approve",
                }
            ]
        }
编辑指令

resume={
            "decisions": [
                {
                    "type": "edit",
                    # Edited action with tool name and args
                    "edited_action": {
                        # Tool name to call.
                        # Will usually be the same as the original action.
                        "name": "new_tool_name",
                        # Arguments to pass to the tool.
                        "args": {"key1": "new_value", "key2": "original_value"},
                    }
                }
            ]
        }
        
拒绝指令
resume={
            "decisions": [
                {
                    "type": "reject",
                    # An explanation about why the action was rejected
                    "message": "No, this is wrong because ..., instead do this ...",
                }
            ]
        }

