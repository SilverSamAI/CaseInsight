from __future__ import annotations
import functools
import time
from typing import Callable, TypeVar

T = TypeVar("T")


def with_retry(
    max_attempts: int = 4,
    base_delay: float = 2.0,
    retry_on: tuple[type[Exception], ...] = (Exception,),
) -> Callable:
    """Retry a function with exponential backoff (2s, 4s, 8s, 16s).

    Re-raises the last exception once attempts are exhausted.
    """

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs) -> T:
            last_exc: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except retry_on as exc:
                    last_exc = exc
                    if attempt == max_attempts - 1:
                        break
                    time.sleep(base_delay * (2 ** attempt))
            assert last_exc is not None
            raise last_exc

        return wrapper

    return decorator
