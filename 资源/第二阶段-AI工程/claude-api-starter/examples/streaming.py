"""流式输出示例：演示如何实时显示生成内容。"""

import sys
sys.path.insert(0, "..")

from utils import ClaudeClient


def main():
    client = ClaudeClient(
        system="你是一个有帮助的编程助手。"
    )

    print("=== 流式输出示例 ===\n")

    # 基本流式输出
    print("用户: 用 Python 写一个快速排序算法")
    print("助手: ", end="", flush=True)

    full_response = ""
    with client.stream("用 Python 写一个快速排序算法") as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print("\n")

    # 获取完整响应和 token 使用量
    final_message = stream.get_final_message()
    print(f"输出 tokens: {final_message.usage.output_tokens}")
    print(f"停止原因: {final_message.stop_reason}")


def demo_with_thinking():
    """演示带思考过程的流式输出。"""

    import anthropic

    client = anthropic.Anthropic()

    print("=== 带思考过程的流式输出 ===\n")
    print("用户: 解释一下为什么天空是蓝色的")
    print()

    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": "解释一下为什么天空是蓝色的"}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_start":
                if event.content_block.type == "thinking":
                    print("[思考中...]")
                elif event.content_block.type == "text":
                    print("[回答:]")

            elif event.type == "content_block_delta":
                if event.delta.type == "thinking_delta":
                    print(event.delta.thinking, end="", flush=True)
                elif event.delta.type == "text_delta":
                    print(event.delta.text, end="", flush=True)

    print("\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--thinking":
        demo_with_thinking()
    else:
        main()
