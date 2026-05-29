"""多轮对话示例：演示如何管理对话历史和上下文。"""

import sys
sys.path.insert(0, "..")

from utils import ClaudeClient


def main():
    # 创建客户端，设置系统提示
    client = ClaudeClient(
        system="你是一个有帮助的编程助手，用简洁的中文回答问题。"
    )

    print("=== 多轮对话示例 ===")
    print("输入 'quit' 退出，'reset' 重置对话\n")

    while True:
        user_input = input("用户: ")
        if user_input.lower() == "quit":
            break
        if user_input.lower() == "reset":
            client.reset()
            print("[对话已重置]\n")
            continue

        response = client.send(user_input)
        print(f"助手: {response}\n")

        # 显示对话历史长度
        history = client.get_history()
        print(f"[历史消息数: {len(history)}]")


def demo_scripted():
    """脚本化演示，展示多轮对话的上下文保持。"""

    client = ClaudeClient(
        system="你是一个有帮助的编程助手，用简洁的中文回答问题。"
    )

    # 第一轮
    print("用户: 我叫 Alice")
    response = client.send("我叫 Alice")
    print(f"助手: {response}\n")

    # 第二轮 - 测试上下文记忆
    print("用户: 我叫什么名字？")
    response = client.send("我叫什么名字？")
    print(f"助手: {response}\n")

    # 第三轮 - 测试连续对话
    print("用户: 帮我写一个 Python 函数，计算斐波那契数列")
    response = client.send("帮我写一个 Python 函数，计算斐波那契数列")
    print(f"助手: {response}\n")

    # 第四轮 - 基于上下文的追问
    print("用户: 能否用递归实现？")
    response = client.send("能否用递归实现？")
    print(f"助手: {response}\n")

    print(f"最终历史消息数: {len(client.get_history())}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_scripted()
    else:
        main()
