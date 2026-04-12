import os
import json
import uuid
import sys
import asyncio
import aiohttp
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

BASE_URL = os.getenv("LANGGRAPH_BASE_URL", "http://127.0.0.1:2024")
ASSISTANT_ID = os.getenv("LANGGRAPH_ASSISTANT_ID")

class LangGraphClient:
    def __init__(self):
        self.base_url = BASE_URL
        self.assistant_id = ASSISTANT_ID
        self.console_lock = asyncio.Lock()  # 用于保证终端打印不串行交错
        self._is_new_line = True  # 追踪当前终端是否在行首，决定是否打印 "AI: "

    async def create_thread(self) -> str:
        """创建一个新的 Thread"""
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/threads", json={"metadata": {}}) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data["thread_id"]

    async def search_threads(self, limit: int = 10) -> list:
        """获取历史 Thread 列表"""
        payload = {
            "limit": limit,
            "status": "idle",
            "sort_by": "updated_at",
            "sort_order": "desc"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/threads/search", json=payload) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def get_latest_checkpoint(self, thread_id: str) -> str:
        """获取某个 Thread 最新的 checkpoint_id"""
        payload = {"limit": 1}
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/threads/{thread_id}/history", json=payload) as resp:
                resp.raise_for_status()
                history = await resp.json()
                if history and len(history) > 0:
                    return history[0].get("checkpoint_id")
                return None

    # ==========================================
    # 独立的流式渲染与工具表格处理函数
    # ==========================================
    async def _handle_ai_chunk(self, content: str):
        """处理增量流式文本输出"""
        if not content: return
        
        async with self.console_lock:
            if self._is_new_line:
                sys.stdout.write("AI: ")
                self._is_new_line = False
            sys.stdout.write(content)
            sys.stdout.flush()

    async def _handle_tool_table(self, tool_name: str, args: dict, result: str):
        """处理并打印工具调用结果表格"""
        # 尝试美化 result（因为 LangGraph 经常返回含 JSON 字符串的 List/Dict）
        display_result = result
        try:
            if isinstance(result, str):
                parsed = json.loads(result)
                display_result = parsed
            elif isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict) and 'text' in result[0]:
                display_result = result[0]['text']
                # 尝试进一步解析嵌套 JSON
                try:
                    display_result = json.loads(display_result)
                except Exception:
                    pass
            
            # 将清洗后的结果转为紧凑字符串
            if isinstance(display_result, (dict, list)):
                display_result = json.dumps(display_result, ensure_ascii=False)
            else:
                display_result = str(display_result)
        except Exception:
            display_result = str(result)

        # 清理换行符，限制长度防止刷屏
        display_result = display_result.replace("\n", " ")
        if len(display_result) > 55:
            display_result = display_result[:52] + "..."

        args_str = json.dumps(args, ensure_ascii=False)
        if len(args_str) > 30:
             args_str = args_str[:27] + "..."

        table = (
            f"\n\n{'='*60}\n"
            f"🔧 工具执行完成: {tool_name}\n"
            f"{'-'*60}\n"
            f"{'输入参数 (Args)':<32} | {'执行结果 (Result)'}\n"
            f"{'-'*60}\n"
            f"{args_str:<32} | {display_result}\n"
            f"{'='*60}\n\n"
        )

        async with self.console_lock:
            # 如果此时 AI 正在同一行说话，先换行，防止打断
            if not self._is_new_line:
                sys.stdout.write("\n")
            
            sys.stdout.write(table)
            sys.stdout.flush()
            
            # 打印完表格后，下一次 AI 说话需要重新加上 "AI: " 前缀
            self._is_new_line = True

    # ==========================================
    # 核心流式请求与主循环
    # ==========================================
    # ==========================================
    # 核心流式请求与主循环
    # ==========================================
    async def stream_run(self, thread_id: str, input_msg: str = None, command: dict = None, checkpoint_id: str = None):
        url = f"{self.base_url}/threads/{thread_id}/runs/stream"
        
        payload = {
            "stream_mode": ["messages-tuple", "values", "custom"],
            "stream_subgraphs": True,
            "assistant_id": self.assistant_id,
            "on_disconnect": "cancel" 
        }

        if input_msg:
            payload["input"] = {
                "messages": [{
                    "id": str(uuid.uuid4()),
                    "type": "human",
                    "content": [{"type": "text", "text": input_msg}]
                }]
            }
        else:
            payload["input"] = {}

        if command:
            payload["command"] = command
            payload["stream_resumable"] = False
        else:
            payload["stream_resumable"] = True

        if checkpoint_id:
            payload["checkpoint"] = {"checkpoint_id": checkpoint_id, "checkpoint_ns": ""}

        pending_tool_calls = {}
        interrupt_data = None
        self._is_new_line = True # 新的一轮请求，重置新行状态

        sys.stdout.write("\n") # 请求开始前给个空行留白

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    error_detail = await resp.text()
                    print(f"\n❌ 请求失败，状态码: {resp.status}")
                    print(f"🕵️ 后端报错详情: {error_detail}")
                    return

                current_event = None
                async for line_bytes in resp.content:
                    line = line_bytes.decode('utf-8').strip()
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
                                    
                                    # 处理文本流
                                    if msg_type == "AIMessageChunk":
                                        content = msg_item.get("content", "")
                                        asyncio.create_task(self._handle_ai_chunk(content))
                                        
                                        for tc in msg_item.get("tool_calls", []):
                                            pending_tool_calls[tc["id"]] = {"name": tc["name"], "args": tc.get("args", {})}

                                    # 处理工具返回
                                    elif msg_type == "tool":
                                        tc_id = msg_item.get("tool_call_id")
                                        tool_result = msg_item.get("content", "")
                                        if tc_id in pending_tool_calls:
                                            tc_info = pending_tool_calls.pop(tc_id)
                                            asyncio.create_task(self._handle_tool_table(
                                                tc_info["name"], tc_info["args"], tool_result
                                            ))

                        elif current_event == "values":
                            if "__interrupt__" in data and len(data["__interrupt__"]) > 0:
                                interrupt_data = data["__interrupt__"][0].get("value", {})
                                break

        print() # 流结束收尾换行

        # 处理中断情况
        if interrupt_data:
            action_requests = interrupt_data.get("action_requests", [])
            
            if not action_requests:
                print(f"\n⚠️ 收到未知格式的中断数据: {interrupt_data}")
                return

            decisions = []
            
            for i, action in enumerate(action_requests):
                print("\n" + "⚠️ "*25)
                print(f"🛑 触发敏感操作，需要人工确认！ ({i+1}/{len(action_requests)})")
                print(f"工具名称: {action.get('name')}")
                print(f"工具参数: {json.dumps(action.get('args', {}), ensure_ascii=False)}")
                print(f"中断说明: {action.get('description', '无')}")
                print("⚠️ "*25)

                while True:
                    choice = input("\n请选择操作 [1] Approve (同意)  [2] Reject (拒绝)  [3] Edit (修改参数): ").strip()
                    
                    if choice == "1":
                        decisions.append({"type": "approve"})
                        break
                    elif choice == "2":
                        reason = input("请输入拒绝原因: ")
                        decisions.append({
                            "type": "reject",
                            "message": reason
                        })
                        break
                    elif choice == "3":
                        new_args_str = input("请输入新的参数 (JSON格式): ")
                        try:
                            new_args = json.loads(new_args_str)
                            decisions.append({
                                "type": "edit",
                                "edited_action": {
                                    "name": action.get('name'), 
                                    "args": new_args
                                }
                            })
                            break
                        except json.JSONDecodeError:
                            print("❌ JSON 格式错误，请重新输入。")
                            continue
                    else:
                        print("无效输入，请重试。")
                        continue

            latest_checkpoint = await self.get_latest_checkpoint(thread_id)
            resume_cmd = {"resume": {"decisions": decisions}}
            
            print("\n正在提交您的决策...")
            await self.stream_run(thread_id, command=resume_cmd, checkpoint_id=latest_checkpoint)
            
            # 👇 极度关键：阻断栈回退。确保内部流执行完后，本层不再执行任何多余代码直接退出
            return

async def main():
    client = LangGraphClient()
    
    print("="*40)
    print("🤖 欢迎使用 LangGraph 终端代理")
    print("1. 开启新对话")
    print("2. 查看并继续历史对话")
    print("="*40)
    
    mode = input("请选择操作 (1/2): ").strip()
    thread_id = None
    
    if mode == "2":
        print("\n获取最近的历史记录...")
        threads = await client.search_threads(limit=10)
        if not threads:
            print("暂无历史记录，将开启新对话。")
            thread_id = await client.create_thread()
        else:
            for idx, t in enumerate(threads):
                updated = t.get("updated_at", "")[:19].replace("T", " ")
                status = t.get("status", "unknown")
                print(f"[{idx}] 线程ID: {t['thread_id']} | 状态: {status} | 更新时间: {updated}")
            
            t_idx = int(input("\n请输入要继续的序号: ").strip())
            thread_id = threads[t_idx]["thread_id"]
    else:
        thread_id = await client.create_thread()
        print(f"\n已创建新对话，线程 ID: {thread_id}")

    print("\n💡 提示: 输入 'quit' 退出对话。\n")
    
    while True:
        user_input = input("🧑 提问: ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        if not user_input:
            continue
            
        await client.stream_run(thread_id, input_msg=user_input)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n已退出。")