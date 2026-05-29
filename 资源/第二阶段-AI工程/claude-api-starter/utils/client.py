"""Claude API 客户端封装，支持多轮对话和流式输出。"""

import os
from typing import Optional
from dotenv import load_dotenv
import anthropic

load_dotenv()


class ClaudeClient:
    """Claude API 客户端，封装常用功能。"""

    def __init__(
        self,
        model: str = "claude-opus-4-7",
        max_tokens: int = 16000,
        system: Optional[str] = None,
    ):
        self.client = anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens
        self.system = system
        self.messages: list[dict] = []

    def send(self, user_message: str, **kwargs) -> str:
        """发送消息并获取回复。"""
        self.messages.append({"role": "user", "content": user_message})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            system=self.system,
            messages=self.messages,
            **{k: v for k, v in kwargs.items() if k != "max_tokens"},
        )

        assistant_message = next(
            (b.text for b in response.content if b.type == "text"), ""
        )
        self.messages.append({"role": "assistant", "content": assistant_message})

        return assistant_message

    def stream(self, user_message: str, **kwargs):
        """流式发送消息，返回事件流。"""
        self.messages.append({"role": "user", "content": user_message})

        stream = self.client.messages.stream(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            system=self.system,
            messages=self.messages,
            **{k: v for k, v in kwargs.items() if k != "max_tokens"},
        )

        return stream

    def reset(self):
        """重置对话历史。"""
        self.messages = []

    def get_history(self) -> list[dict]:
        """获取对话历史。"""
        return self.messages.copy()
