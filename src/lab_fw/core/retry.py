"""Retry helpers for lab_fw."""

from __future__ import annotations

import logging
import random
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")
logger = logging.getLogger("lab_fw.core.retry")


def retry_call(
    fn: Callable[[], T],
    *,
    attempts: int = 3,
    delay_s: float = 0.1,
    backoff: float = 2.0,
    jitter: float = 0.2,
    retry_on: tuple[type[BaseException], ...] = (Exception,),
) -> T:
    """Call fn until success or attempts are exhausted."""
    if attempts < 1:
        raise ValueError("attempts must be >= 1")

    last_exc: BaseException | None = None

    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except retry_on as exc:
            last_exc = exc
            if attempt >= attempts:
                break
            pause = delay_s * (backoff ** (attempt - 1))
            if jitter:
                pause *= 1 + random.uniform(-jitter, jitter)
            pause = max(pause, 0.0)
            logger.warning(
                "attempt %s/%s failed: %s; retry in %.3fs",
                attempt,
                attempts,
                exc,
                pause,
            )
            time.sleep(pause)

    assert last_exc is not None
    raise last_exc