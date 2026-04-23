import asyncio
import contextlib
import json
import os
import sys
import uuid

import aiohttp
from dotenv import load_dotenv

load_dotenv()

from client_apis.memory_router import ThreadContext, get_memory_router

BASE_URL = os.getenv("LANGGRAPH_BASE_URL", "http://127.0.0.1:2024")
ASSISTANT_ID = os.getenv("LANGGRAPH_ASSISTANT_ID")


class LangGraphClient:
    def __init__(self):
        self.base_url = BASE_URL
        self.assistant_id = ASSISTANT_ID
        self.console_lock = asyncio.Lock()
        self._is_new_line = True
        self.memory_router = get_memory_router(
            langgraph_base_url=self.base_url,
            assistant_id=self.assistant_id,
        )
        self._last_ai_response: str = ""

    async def create_thread(self) -> str:
        """创建一个新的 Thread"""
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                f"{self.base_url}/threads", json={"metadata": {"graph_id": "my_mcp_agent"}}
            ) as resp,
        ):
            resp.raise_for_status()
            data = await resp.json()
            return data["thread_id"]

    async def search_threads(self, limit: int = 10) -> list:
        """获取历史 Thread 列表"""
        payload = {
            "metadata": {"graph_id": "my_mcp_agent"},
            "limit": limit,
            "offset": 0,
            "status": "idle",
            "sort_by": "updated_at",
            "sort_order": "desc",
        }
        async with (
            aiohttp.ClientSession() as session,
            session.post(f"{self.base_url}/threads/search", json=payload) as resp,
        ):
            resp.raise_for_status()
            return await resp.json()

    async def get_latest_checkpoint(self, thread_id: str) -> str:
        """获取某个 Thread 最新的 checkpoint_id"""
        payload = {"limit": 1}
        async with (
            aiohttp.ClientSession() as session,
            session.post(f"{self.base_url}/threads/{thread_id}/history", json=payload) as resp,
        ):
            resp.raise_for_status()
            history = await resp.json()
            if history:
                return history[0].get("checkpoint_id")
            return None

    # ==========================================
    # 流式渲染
    # ==========================================
    async def _handle_ai_chunk(self, content: str):
        if not content:
            return
        async with self.console_lock:
            if self._is_new_line:
                sys.stdout.write("AI: ")
                self._is_new_line = False
            sys.stdout.write(content)
            sys.stdout.flush()
        self._last_ai_response += content

    async def _handle_tool_table(self, tool_name: str, args: dict, result: str):
        display_result = result
        try:
            if isinstance(result, str):
                parsed = json.loads(result)
                display_result = parsed
            elif (
                isinstance(result, list)
                and len(result) > 0
                and isinstance(result[0], dict)
                and "text" in result[0]
            ):
                display_result = result[0]["text"]
                with contextlib.suppress(Exception):
                    display_result = json.loads(display_result)
            if isinstance(display_result, (dict, list)):
                display_result = json.dumps(display_result, ensure_ascii=False)
            else:
                display_result = str(display_result)
        except Exception:
            display_result = str(result)

        display_result = display_result.replace("\n", " ")
        if len(display_result) > 55:
            display_result = display_result[:52] + "..."

        args_str = json.dumps(args, ensure_ascii=False)
        if len(args_str) > 30:
            args_str = args_str[:27] + "..."

        table = (
            f"\n\n{'=' * 60}\n"
            f"工具执行完成: {tool_name}\n"
            f"{'-' * 60}\n"
            f"{'输入参数 (Args)':<32} | {'执行结果 (Result)'}\n"
            f"{'-' * 60}\n"
            f"{args_str:<32} | {display_result}\n"
            f"{'=' * 60}\n\n"
        )

        async with self.console_lock:
            if not self._is_new_line:
                sys.stdout.write("\n")
            sys.stdout.write(table)
            sys.stdout.flush()
            self._is_new_line = True

    # ==========================================
    # 核心流式请求
    # ==========================================
    async def stream_run(
        self,
        thread_id: str,
        input_msg: str | None = None,
        command: dict | None = None,
        checkpoint_id: str | None = None,
        injected_messages: list | None = None,
    ):
        """
        发起一次 runs/stream 请求。

        Args:
            thread_id: LangGraph thread ID
            input_msg: 当前用户消息
            command: HITL resume 命令
            checkpoint_id: 从指定 checkpoint 恢复
            injected_messages: 历史上下文消息（来自 MemoryRouter），
                              作为 input.messages 的前缀注入
        """
        url = f"{self.base_url}/threads/{thread_id}/runs/stream"

        messages = []
        if injected_messages:
            messages.extend(injected_messages)
        if input_msg:
            messages.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "human",
                    "content": [{"type": "text", "text": input_msg}],
                }
            )

        payload = {
            "stream_mode": ["messages-tuple", "values", "custom"],
            "stream_subgraphs": True,
            "assistant_id": self.assistant_id,
            "on_disconnect": "cancel",
        }

        if messages:
            payload["input"] = {"messages": messages}
            payload["stream_resumable"] = True
        else:
            payload["input"] = {}
            payload["stream_resumable"] = False

        if command:
            payload["command"] = command
            payload["stream_resumable"] = False

        if checkpoint_id:
            payload["checkpoint"] = {"checkpoint_id": checkpoint_id, "checkpoint_ns": ""}

        pending_tool_calls = {}
        pending_tasks: list[asyncio.Task] = []
        interrupt_data = None
        self._is_new_line = True
        self._last_ai_response = ""

        sys.stdout.write("\n")

        async with aiohttp.ClientSession() as session, session.post(url, json=payload) as resp:
            if resp.status != 200:
                error_detail = await resp.text()
                print(f"\n请求失败, 状态码: {resp.status}")
                print(f"后端报错详情: {error_detail}")
                return

            current_event = None
            async for line_bytes in resp.content:
                line = line_bytes.decode("utf-8").strip()
                if not line:
                    continue

                if line.startswith("event:"):
                    current_event = line.split(":", 1)[1].strip()
                elif line.startswith("data:") and current_event:
                    data_str = line.split(":", 1)[1].strip()
                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    if current_event == "messages":
                        for msg_item in data:
                            if isinstance(msg_item, dict) and "type" in msg_item:
                                msg_type = msg_item.get("type")

                                if msg_type == "AIMessageChunk":
                                    content = msg_item.get("content", "")
                                    pending_tasks.append(
                                        asyncio.create_task(self._handle_ai_chunk(content))
                                    )

                                    for tc in msg_item.get("tool_calls", []):
                                        pending_tool_calls[tc["id"]] = {
                                            "name": tc["name"],
                                            "args": tc.get("args", {}),
                                        }

                                elif msg_type == "tool":
                                    tc_id = msg_item.get("tool_call_id")
                                    tool_result = msg_item.get("content", "")
                                    if tc_id in pending_tool_calls:
                                        tc_info = pending_tool_calls.pop(tc_id)
                                        pending_tasks.append(
                                            asyncio.create_task(
                                                self._handle_tool_table(
                                                    tc_info["name"], tc_info["args"], tool_result
                                                )
                                            )
                                        )

                    elif current_event == "values":
                        if "__interrupt__" in data and len(data["__interrupt__"]) > 0:
                            interrupt_data = data["__interrupt__"][0].get("value", {})
                            break

        # Wait for all pending tasks to complete
        if pending_tasks:
            await asyncio.gather(*pending_tasks)

        print()

        if interrupt_data:
            action_requests = interrupt_data.get("action_requests", [])
            if not action_requests:
                print(f"\n收到未知格式的中断数据: {interrupt_data}")
                return

            decisions = []
            for action in action_requests:
                print("\n" + "=" * 40)
                print("触发敏感操作，需要人工确认！")
                print(f"工具名称: {action.get('name')}")
                print(f"工具参数: {json.dumps(action.get('args', {}), ensure_ascii=False)}")
                print(f"中断说明: {action.get('description', '无')}")
                print("=" * 40)

                while True:
                    choice = input("\n[1] Approve  [2] Reject  [3] Edit: ").strip()
                    if choice == "1":
                        decisions.append({"type": "approve"})
                        break
                    elif choice == "2":
                        reason = input("请输入拒绝原因: ")
                        decisions.append({"type": "reject", "message": reason})
                        break
                    elif choice == "3":
                        new_args_str = input("请输入新的参数 (JSON): ")
                        try:
                            new_args = json.loads(new_args_str)
                            decisions.append(
                                {
                                    "type": "edit",
                                    "edited_action": {"name": action.get("name"), "args": new_args},
                                }
                            )
                            break
                        except json.JSONDecodeError:
                            print("JSON 格式错误，请重新输入。")
                            continue
                    else:
                        print("无效输入。")

            latest_checkpoint = await self.get_latest_checkpoint(thread_id)
            await self.stream_run(
                thread_id,
                command={"resume": {"decisions": decisions}},
                checkpoint_id=latest_checkpoint,
            )

    # ==========================================
    # 主交互循环
    # ==========================================
    async def run(self):
        print("=" * 40)
        print("欢迎使用 LangGraph 终端代理")
        print("1. 自动关联历史对话（推荐）")
        print("2. 查看并继续历史对话")
        print("3. 强制开启新 session")
        print("=" * 40)

        mode = input("请选择操作 (1/2/3): ").strip()

        thread_id: str | None = None
        inject_context = True

        if mode == "2":
            threads = await self.search_threads(limit=10)
            if not threads:
                print("暂无历史记录，将开启新对话。")
                thread_id = await self.create_thread()
                inject_context = True
            else:
                for idx, t in enumerate(threads):
                    updated = t.get("updated_at", "")[:19].replace("T", " ")
                    status = t.get("status", "unknown")
                    print(f"[{idx}] {t['thread_id'][:8]}... | 状态: {status} | 更新时间: {updated}")

                t_idx = int(input("\n请输入要继续的序号: ").strip())
                thread_id = threads[t_idx]["thread_id"]
                print(f"已选择 thread: {thread_id[:8]}...")
                inject_context = True

        elif mode == "3":
            # 直接创建新 thread，不注入任何历史上下文
            thread_id = await self.create_thread()
            inject_context = False
            print(f"已创建新 session: {thread_id[:8]}...")

        else:
            # 模式 1：自动关联历史
            # 创建新 thread，第一次询问时从最新 thread 找关联上下文注入
            thread_id = await self.create_thread()
            inject_context = True
            print("将自动判断是否关联历史。")

        print("\n提示: 输入 'quit' 退出，'new' 强制开启新 session。\n")

        while True:
            user_input = input("提问: ").strip()
            if user_input.lower() in ("quit", "exit", "q"):
                break
            if user_input.lower() == "new":
                # 强制新 session：创建 thread，不注入上下文
                self.memory_router.invalidate_cache()
                thread_id = await self.create_thread()
                inject_context = False
                print(f"已开启新 session: {thread_id[:8]}...")
                continue
            if not user_input:
                continue

            injected: list = []

            if inject_context:
                self.memory_router.invalidate_cache()
                ctx: ThreadContext = await self.memory_router.route(
                    query=user_input,
                    force_thread_id=None,
                    own_thread_id=thread_id,
                )
                injected = self.memory_router.build_injected_messages(ctx)
                if injected:
                    print("[关联历史，注入上下文]")
                # 后续消息不再关联
                inject_context = False

            # 调用 LangGraph
            await self.stream_run(
                thread_id=thread_id,
                input_msg=user_input,
                injected_messages=injected if injected else None,
            )


async def main():
    client = LangGraphClient()
    await client.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n已退出。")
