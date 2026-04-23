"""
跨 Session 记忆路由

- 查询 /threads/search 获取历史 thread 和 messages
- kimi-k2-turbo-preview 二分类判断关联性
- kimi-k2-0905-preview 在超长历史时压缩上下文
- 返回 (thread_id, context_messages) 给调用方

核心设计：所有 agent_call 代码由 LangGraph server 托管，对外提供 HTTP 服务。
客户端（client_apis）通过 HTTP 与 server 交互，MemoryRouter 是客户端的路由逻辑，
不依赖任何 agent_call 模块。
"""

import os
import uuid
from dataclasses import dataclass, field

import aiohttp
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


@dataclass
class ConversationTurn:
    """一轮完整的对话：user 提问 + ai 回复"""

    user: str
    ai: str


@dataclass
class ThreadContext:
    """一个 thread 的上下文，供注入用"""

    thread_id: str
    # 最后 3 轮完整对话（不压缩时）
    turns: list[ConversationTurn] = field(default_factory=list)
    # 压缩后的摘要（历史超过 3 轮时）
    compressed_history: str | None = None


class MemoryRouter:
    def __init__(self, langgraph_base_url: str, assistant_id: str):
        self.base_url = langgraph_base_url.rstrip("/")
        self.assistant_id = assistant_id
        self._classifier = ChatOpenAI(
            model=os.getenv("CLASSIFIER_MODEL", "kimi-k2-turbo-preview"),
            temperature=1,
            api_key=os.getenv("MOONSHOT_API_KEY"),
            base_url=os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1"),
        )
        self._compressor = ChatOpenAI(
            model=os.getenv("COMPRESSOR_MODEL", "kimi-k2-0905-preview"),
            temperature=1,
            api_key=os.getenv("MOONSHOT_API_KEY"),
            base_url=os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1"),
        )
        # 缓存最近的 /threads/search 结果，避免同一次交互中重复调用
        self._threads_cache: list[dict] | None = None

    # ---- 对话级别 API ----

    async def route(
        self,
        query: str,
        force_thread_id: str | None = None,
        own_thread_id: str | None = None,
    ) -> ThreadContext:
        """
        路由决策。

        - force_thread_id: 直接使用该 thread_id，注入其历史上下文
        - own_thread_id: 客户端已持有自己的 thread，只从关联 thread 取上下文，
                         返回的 thread_id 仍用 own_thread_id
        - None + 无关联: 返回新的 ThreadContext（thread_id 由内部创建）
        """
        # 强制复用
        if force_thread_id:
            return await self._build_context_for_thread(force_thread_id)

        # 遍历最近 threads，找关联的
        threads = await self._get_cached_threads()
        for thread in threads:
            thread_id = thread["thread_id"]
            if await self._is_related(query, thread):
                ctx = await self._build_context_for_thread(thread_id)
                # 用客户端自己的 thread_id，不切换到旧 thread
                if own_thread_id:
                    ctx.thread_id = own_thread_id
                return ctx

        # 无关联 → 新 thread（客户端有 own_thread_id 时优先用）
        if own_thread_id:
            return ThreadContext(thread_id=own_thread_id)
        new_id = await self._create_thread()
        return ThreadContext(thread_id=new_id)

    # ---- 内部方法 ----

    async def _get_cached_threads(self) -> list[dict]:
        """获取最近的 threads（带缓存，TTL 30s）"""
        if self._threads_cache is not None:
            return self._threads_cache
        self._threads_cache = await self._search_recent_threads(limit=10)
        return self._threads_cache

    def invalidate_cache(self):
        """清除 threads 缓存，在需要获取最新状态时调用"""
        self._threads_cache = None

    async def _search_recent_threads(self, limit: int = 10) -> list[dict]:
        """调用 POST /threads/search，获取最近的 threads 和最新 state"""
        payload = {
            "metadata": {"graph_id": "my_mcp_agent"},
            "limit": limit,
            "offset": 0,
            "status": "idle",
        }
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                f"{self.base_url}/threads/search",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp,
        ):
            resp.raise_for_status()
            return await resp.json()

    async def _create_thread(self) -> str:
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                f"{self.base_url}/threads",
                json={"metadata": {"graph_id": "my_mcp_agent"}},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp,
        ):
            resp.raise_for_status()
            data = await resp.json()
            return data["thread_id"]

    def _extract_turns(self, messages: list[dict], n: int = 3) -> list[ConversationTurn]:
        """
        从 LangChain message list 中提取最后 n 轮完整对话。
        每轮 = 1 个 human message + 1 个 ai message。
        """
        human_msgs = []
        ai_msgs = []

        for msg in messages:
            msg_type = msg.get("type", "")
            text = self._extract_text(msg)
            if not text:
                continue
            if msg_type == "human":
                human_msgs.append(text)
            elif msg_type == "ai":
                ai_msgs.append(text)

        # 从后往前配对，最后一个 ai 和最后一个 human 配对
        pairs = list(zip(reversed(human_msgs), reversed(ai_msgs), strict=True))
        turns = []
        for user, ai in pairs[:n]:
            turns.insert(0, ConversationTurn(user=user, ai=ai))
        return turns

    def _extract_text(self, msg: dict) -> str:
        """从 LangChain message dict 中提取纯文本"""
        content = msg.get("content", [])
        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    return part["text"]
        elif isinstance(content, str):
            return content
        return ""

    def _format_full_turns_for_classifier(self, turns: list[ConversationTurn]) -> str:
        """把完整 turns 格式化为分类器的输入文本，包含 user 和 ai"""
        lines = []
        for turn in turns:
            lines.append(f"用户: {turn.user}")
            lines.append(f"助手: {turn.ai}")
        return "\n".join(lines) if lines else "(无历史)"

    async def _is_related(self, query: str, thread: dict) -> bool:
        """调用 kimi-k2-turbo-preview 判断当前消息是否与该 thread 关联"""
        values = thread.get("values") or {}
        messages = values.get("messages", [])
        turns = self._extract_turns(messages, n=3)
        history_text = self._format_full_turns_for_classifier(turns)

        prompt = (
            "判断以下两个对话片段是否属于同一话题/任务。\n"
            f"片段A (当前用户消息): {query}\n"
            f"片段B (最近 3 轮完整对话):\n{history_text}\n"
            "如果属于同一话题/任务，回复'y'，否则回复'n'。只输出一个字。"
        )
        try:
            resp = self._classifier.invoke(prompt)
            return resp.content.strip().lower() == "y"
        except Exception:
            return False

    async def _compress_history(self, turns: list[ConversationTurn]) -> str:
        """调用 kimi-k2-0905-preview 将完整对话压缩为摘要"""
        history_lines = []
        for turn in turns:
            history_lines.append(f"用户: {turn.user}")
            history_lines.append(f"助手: {turn.ai}")
        history_text = "\n".join(history_lines)

        prompt = (
            "你是一个对话摘要助手。请将以下对话压缩为 2-3 句简洁的摘要，"
            "保留关键信息（地点、人物、任务、决策结果等）。\n"
            "对话内容:\n" + history_text + "\n"
            "请输出摘要:"
        )
        try:
            resp = self._compressor.invoke(prompt)
            return resp.content.strip()
        except Exception:
            return history_text

    async def _build_context_for_thread(self, thread_id: str) -> ThreadContext:
        """
        为指定 thread 构建上下文。
        从 /threads/search 的 values.messages 中提取最后 3 轮完整对话。
        如果历史超过 3 轮，调用压缩器。
        """
        threads = await self._get_cached_threads()
        target = None
        for t in threads:
            if t["thread_id"] == thread_id:
                target = t
                break

        if not target:
            return ThreadContext(thread_id=thread_id)

        messages = (target.get("values") or {}).get("messages", [])

        # 提取所有轮次用于压缩判断
        all_turns = self._extract_turns(messages, n=100)
        recent_turns = all_turns[-3:]

        if len(all_turns) > 3:
            compressed = await self._compress_history(all_turns)
            return ThreadContext(
                thread_id=thread_id,
                turns=recent_turns,
                compressed_history=compressed,
            )

        return ThreadContext(thread_id=thread_id, turns=recent_turns)

    def build_injected_messages(self, ctx: ThreadContext) -> list[dict]:
        """
        将 ThreadContext 转换为 LangGraph HTTP API 接受的 messages 格式。
        返回的列表会作为 input.messages 的前缀注入。
        """
        messages = []

        if ctx.compressed_history:
            messages.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "human",
                    "content": [
                        {
                            "type": "text",
                            "text": f"【相关历史上下文（摘要）】\n{ctx.compressed_history}",
                        }
                    ],
                }
            )
        elif ctx.turns:
            parts = []
            for turn in ctx.turns:
                parts.append(f"用户: {turn.user}")
                parts.append(f"助手: {turn.ai}")
            messages.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "human",
                    "content": [
                        {"type": "text", "text": "【相关历史上下文】\n" + "\n".join(parts)}
                    ],
                }
            )

        return messages


# 全局单例（进程级别）
_memory_router: MemoryRouter | None = None


def get_memory_router(
    langgraph_base_url: str | None = None,
    assistant_id: str | None = None,
) -> MemoryRouter:
    global _memory_router
    if _memory_router is None:
        _memory_router = MemoryRouter(
            langgraph_base_url=langgraph_base_url
            or os.getenv("LANGGRAPH_BASE_URL", "http://localhost:2024"),
            assistant_id=assistant_id or os.getenv("LANGGRAPH_ASSISTANT_ID", "my_mcp_agent"),
        )
    return _memory_router
