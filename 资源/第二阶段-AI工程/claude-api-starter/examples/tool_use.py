"""Tool Use 示例：演示如何定义和使用工具。"""

import json
import math
import sys
sys.path.insert(0, "..")

from utils import ClaudeClient


# 定义工具
TOOLS = [
    {
        "name": "calculate",
        "description": "执行数学计算。支持基本运算和数学函数。",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，如 '2 + 3' 或 'sqrt(16)'",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "get_weather",
        "description": "获取指定城市的当前天气。",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，如 '北京' 或 '上海'",
                }
            },
            "required": ["city"],
        },
    },
]


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """执行工具并返回结果。"""
    if tool_name == "calculate":
        try:
            # 安全地计算表达式
            expression = tool_input["expression"]
            # 替换常见的数学函数
            safe_expr = expression.replace("sqrt", "math.sqrt")
            result = eval(safe_expr, {"math": math, "__builtins__": {}})
            return json.dumps({"result": result})
        except Exception as e:
            return json.dumps({"error": str(e)})

    elif tool_name == "get_weather":
        # 模拟天气 API
        city = tool_input["city"]
        mock_weather = {
            "北京": {"temp": 22, "condition": "晴"},
            "上海": {"temp": 25, "condition": "多云"},
            "广州": {"temp": 30, "condition": "雨"},
        }
        weather = mock_weather.get(city, {"temp": 20, "condition": "未知"})
        return json.dumps(weather, ensure_ascii=False)

    return json.dumps({"error": f"未知工具: {tool_name}"})


def main():
    client = ClaudeClient(
        system="你是一个有帮助的助手，可以使用工具来回答问题。"
    )

    print("=== Tool Use 示例 ===\n")

    # 用户请求
    user_message = "北京和上海的天气怎么样？另外帮我算一下 15 * 23 + sqrt(144)"
    print(f"用户: {user_message}\n")

    # 发送请求，带工具定义
    response = client.client.messages.create(
        model=client.model,
        max_tokens=16000,
        tools=TOOLS,
        messages=[{"role": "user", "content": user_message}],
    )

    # 处理工具调用循环
    messages = [{"role": "user", "content": user_message}]

    while response.stop_reason == "tool_use":
        # 显示 Claude 的思考过程
        for block in response.content:
            if block.type == "text":
                print(f"助手: {block.text}")

        # 执行工具调用
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"\n[调用工具: {block.name}]")
                print(f"  参数: {json.dumps(block.input, ensure_ascii=False)}")

                result = execute_tool(block.name, block.input)
                print(f"  结果: {result}")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        # 将工具结果发送回 Claude
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

        response = client.client.messages.create(
            model=client.model,
            max_tokens=16000,
            tools=TOOLS,
            messages=messages,
        )

    # 显示最终回答
    print("\n[最终回答:]")
    for block in response.content:
        if block.type == "text":
            print(f"助手: {block.text}")


if __name__ == "__main__":
    main()
