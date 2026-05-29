"""重试机制，处理 API 限流和临时错误。"""

import time
import random
from functools import wraps
from typing import TypeVar, Callable, Any
import anthropic

T = TypeVar("T")


def with_retry(
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
) -> Callable:
    """装饰器：为 API 调用添加指数退避重试。"""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except anthropic.RateLimitError as e:
                    last_exception = e
                except anthropic.APIStatusError as e:
                    if e.status_code >= 500:
                        last_exception = e
                    else:
                        raise

                delay = min(
                    base_delay * (2**attempt) + random.uniform(0, 1),
                    max_delay,
                )
                print(f"重试 {attempt + 1}/{max_retries}，等待 {delay:.1f}s")
                time.sleep(delay)

            raise last_exception

        return wrapper

    return decorator


def call_with_retry(
    client: anthropic.Anthropic,
    max_retries: int = 5,
    **kwargs,
) -> Any:
    """直接调用 API，带重试机制。"""

    @with_retry(max_retries=max_retries)
    def _call():
        return client.messages.create(**kwargs)

    return _call()
