"""
自定义 MCP 服务器
实现三个工具：
1. get_gps - 获取 GPS 位置
2. get_contact_phone - 根据姓名获取联系人电话
3. make_call - 拨打电话（模拟）

启动方式: python -m agent_call.custom_mcp_server
"""

import os
from typing import Any
from fastmcp import FastMCP
from dotenv import load_dotenv
from random import choice

# 加载环境变量
load_dotenv()

# 创建 MCP 服务器实例
mcp = FastMCP("custom_tools")


# mock 联系人数据库
CONTACTS = {
    "张三": "13800000001",
    "李四": "13800000002",
    "王五": "13800000003",
}


@mcp.tool()
async def get_gps() -> dict[str, Any]:
    """
    获取当前 GPS 位置信息

    Returns:
        dict: 包含经纬度信息的字典，格式遵循高德规范
        {
            "longitude": float,  # 经度，单位度
            "latitude": float,   # 纬度，单位度
            "formatted": str     # 格式化后的坐标字符串
        }
    """
    # 30度41'12'' = 30 + 41/60 + 12/3600 = 30.686667
    # 东经104度5'43'' = 104 + 5/60 + 43/3600 = 104.095278
    latitude = 30 + 41 / 60 + 12 / 3600
    longitude = 104 + 5 / 60 + 43 / 3600

    return {
        "longitude": round(longitude, 6),
        "latitude": round(latitude, 6),
        "formatted": f"东经{longitude:.6f}°, 北纬{latitude:.6f}°"
    }


@mcp.tool()
async def get_contact_phone(name: str) -> dict[str, Any]:
    """
    根据姓名获取联系人电话号码

    Args:
        name: 联系人姓名

    Returns:
        dict: 包含联系人信息的字典
        {
            "name": str,      # 联系人姓名
            "phone": str,     # 电话号码
            "found": bool     # 是否找到
        }
    """
    phone = CONTACTS.get(name)
    if phone:
        return {
            "name": name,
            "phone": phone,
            "found": True
        }
    return {
        "name": name,
        "phone": "",
        "found": False,
        "message": f"未找到联系人 '{name}'，可用联系人：{', '.join(CONTACTS.keys())}"
    }


@mcp.tool()
async def make_call(phone: str, name: str = "") -> dict[str, Any]:
    """
    拨打指定电话号码

    Args:
        phone: 要拨打的电话号码
        name: 联系人姓名（可选）

    Returns:
        dict: 拨号结果
        {
            "success": bool,   # 是否成功
            "phone": str,      # 拨打的电话号码
            "name": str,       # 联系人姓名
            "message": str     # 结果信息
        }
    """
    # 模拟拨打电话，实际项目中这里集成真实的电话 SDK
    display_name = name if name else phone
    return {
        "success": True,
        "phone": phone,
        "name": name,
        "message": f"正在呼叫 {display_name} ({phone})..."
    }

@mcp.tool()
async def send_sms(phone: str, message: str):
    """
    给号码发短信

    Args:
        phone: 要拨打的电话号码
        message: 发送的信息内容

    Returns:
        dict: 发送结果
        {
            "success": bool,   # 是否成功
            "message": str     # 结果信息
        }
    """
    result = choice([True, False])
    if result:
        return {
            "success": result,   # 是否成功
            "message": "发送成功"     # 结果信息
        }
    else:
        return {
            "success": result,   # 是否成功
            "message": "手机欠费了"   # 结果信息
        }

if __name__ == "__main__":
    # 从环境变量获取端口，默认 8000
    port = int(os.getenv("CUSTOM_MCP_PORT", "8000"))
    host = "127.0.0.1"

    print(f"🚀 启动自定义 MCP 服务器...")
    print(f"   地址: http://{host}:{port}/mcp")
    print(f"   模式: streamable-http")

    # 启动 MCP 服务器（streamable-http 模式）
    mcp.run(transport="streamable-http", host=host, port=port)
