"""
视觉理解子 Agent

使用支持 vision 的模型作为子 agent，专职处理图片理解任务。
通过 @tool 装饰器包装后，可直接注册到主 agent 的工具列表中。

遵循 LangChain 1.0 规范：
- 使用 create_agent() 创建子 agent
- 使用 @tool() 将子 agent 包装为可调用工具
"""

import os
from typing import Annotated

from dotenv import load_dotenv

load_dotenv()

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage


def _build_vision_subagent():
    """
    构建视觉理解子 agent。

    使用 vision-capable 模型（Gemini/Claude/GPT-4o 等）。
    子 agent 只接收用户消息并返回图片理解结果，无其他工具。
    """
    # 优先使用配置中指定的支持 vision 的模型
    model_provider = os.getenv("VISION_MODEL_PROVIDER", "openai")
    model_name = os.getenv("VISION_MODEL", "gpt-4o-mini")

    if model_provider == "google_genai":
        from langchain_google_genai import ChatGoogleGenerativeAI

        model = ChatGoogleGenerativeAI(
            model=model_name,
            api_key=os.getenv("GOOGLE_API_KEY"),
        )
    elif model_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        model = ChatAnthropic(
            model_name=model_name,
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )
    elif model_provider == "openai":
        from langchain_openai import ChatOpenAI

        model = ChatOpenAI(
            model=model_name,
            api_key=os.getenv("OPENAI_API_KEY") or os.getenv("MOONSHOT_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL")
            or os.getenv("MOONSHOT_BASE_URL", "https://api.openai.com/v1"),
        )
    else:
        raise ValueError(f"Unsupported VISION_MODEL_PROVIDER: {model_provider}")

    return create_agent(
        model=model,
        tools=[],
        system_prompt=(
            "你是一个专业的视觉理解助手。你的任务是对给定的图片进行详细、准确的描述和解读。"
            "请从以下角度进行分析：\n"
            "1. 图片的整体内容和大致场景\n"
            "2. 图片中的主要对象及其特征\n"
            "3. 图片中的文字、符号或特殊元素\n"
            "4. 图片的质量、风格或拍摄条件\n"
            "5. 其他值得注意的细节\n\n"
            "请用简洁但信息丰富的语言描述图片内容。"
        ),
    )


# 模块级缓存，避免每次调用 tool 都重新创建 agent
subagent = _build_vision_subagent()


@tool(
    "vision",
    description="""分析图片内容，提取图片中的文字、物体、场景等信息。

输入参数：
- image_url: 图片的网络 URL 地址，例如 https://example.com/image.jpg
- image_base64: 图片的 base64 编码字符串（可选，与 image_url 二选一）
- query: 用户想要了解的问题，例如 "这张图里有什么？" 或 "读取图片中的文字"

返回：图片的详细描述和分析结果。
""",
)
def analyze_image(
    image_url: Annotated[str | None, "图片的网络 URL"] = None,
    image_base64: Annotated[str | None, "图片的 base64 编码"] = None,
    query: Annotated[str, "用户想要了解的问题"] = "请详细描述这张图片的内容",
) -> str:
    """
    视觉理解工具——将图片 URL / base64 发送给 vision 子 agent 进行分析。

    主 agent 通过调用本工具来理解用户发送的图片内容。
    """

    # 构建发送给子 agent 的消息内容（支持多模态）
    if image_base64:
        content = [
            {"type": "text", "text": query},
            {
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{image_base64}",
            },
        ]
    elif image_url:
        content = [
            {"type": "text", "text": query},
            {
                "type": "image_url",
                "image_url": image_url,
            },
        ]
    else:
        return "错误：未提供图片 URL 或 base64 数据"

    result = subagent.invoke({"messages": [HumanMessage(content=content)]})

    # 提取子 agent 的最终回复
    final_message = result["messages"][-1]
    return final_message.content


if __name__ == "__main__":
    result = analyze_image.invoke(
        {
            "image_url": "http://88bill99.top:23050/api/device/upload/file/1234",
            "query": "请详细描述这张图片的内容，包括场景、物体、文字等所有细节",
        }
    )
    print(result)
