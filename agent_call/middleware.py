"""
Human-in-the-loop 配置
使用 LangChain 1.0 官方的 HumanInTheLoopMiddleware

需要人工确认的工具：
- get_gps: 获取 GPS 位置（可编辑、批准、拒绝）
- get_contact_phone: 读取联系人（可批准、拒绝）
- make_call: 拨打电话（可批准、拒绝）
"""

from langchain.agents.middleware import HumanInTheLoopMiddleware


def create_hitl_middleware() -> HumanInTheLoopMiddleware:
    """
    创建 Human-in-the-loop 中间件

    Returns:
        HumanInTheLoopMiddleware: 配置好的中间件实例
    """
    return HumanInTheLoopMiddleware(
        interrupt_on={
            # GPS 获取：允许批准、拒绝
            "get_gps": {"allowed_decisions": ["approve", "reject"]},
            # 读取联系人：允许批准或拒绝，编辑
            "get_contact_phone": True,
            "send_sms": True,
            # 拨打电话：只允许批准或拒绝，不能编辑
            "make_call": {"allowed_decisions": ["approve", "reject"]},
        },
        description_prefix="🔔 需要人工确认 - 敏感操作",
    )
