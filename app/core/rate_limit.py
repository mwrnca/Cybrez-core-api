"""
In-memory sliding-window rate limiter for CYBREZ.

IMPORTANT — Deployment note:
    This implementation stores rate-limit counters in the process's local
    memory. It is appropriate for the current single-instance beta deployment.

    A distributed production deployment running multiple API processes or
    instances (behind a load balancer) will need shared rate-limit storage,
    e.g. Redis with a INCR+EXPIRE strategy. Migrate app/core/rate_limit.py
    when horizontal scaling is introduced.
"""

import threading
import time
from collections import defaultdict, deque
from typing import Callable

from fastapi import Depends, HTTPException, Request, status

from app.config.settings import settings


class RateLimiter:
    """
    Thread-safe sliding-window rate limiter.

    Tracks the timestamps of recent calls per key.  When the number of calls
    in the last ``period_seconds`` reaches ``max_calls`` the next call is
    rejected with (False, retry_after_seconds).
    """

    def __init__(self, max_calls: int, period_seconds: int):
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self._calls: defaultdict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def is_allowed(self, key: str) -> tuple[bool, int]:
        """
        Record a call attempt for ``key``.

        Returns:
            (True, 0)  – request is within limit; the call is recorded.
            (False, N) – limit exceeded; N is the seconds to wait before
                         the oldest in-window call expires.
        """
        now = time.monotonic()
        window_start = now - self.period_seconds

        with self._lock:
            timestamps = self._calls[key]

            # Evict timestamps that have left the window
            while timestamps and timestamps[0] <= window_start:
                timestamps.popleft()

            if len(timestamps) >= self.max_calls:
                retry_after = max(1, int(timestamps[0] - window_start) + 1)
                return False, retry_after

            timestamps.append(now)
            return True, 0

    def clear(self) -> None:
        """Remove all tracked state.  Intended for test isolation only."""
        with self._lock:
            self._calls.clear()


# ---------------------------------------------------------------------------
# Registry — all active limiters so tests can reset them as a group
# ---------------------------------------------------------------------------

_registry: list[RateLimiter] = []


def _new(max_calls: int, period_seconds: int = 60) -> RateLimiter:
    limiter = RateLimiter(max_calls, period_seconds)
    _registry.append(limiter)
    return limiter


def clear_all_limiters() -> None:
    """Reset all limiter state.  Call this between test cases."""
    for limiter in _registry:
        limiter.clear()


# ---------------------------------------------------------------------------
# Named limiter instances (values driven by settings / env vars)
# ---------------------------------------------------------------------------

login_limiter = _new(settings.RATE_LIMIT_LOGIN_PER_MINUTE)
register_limiter = _new(settings.RATE_LIMIT_REGISTER_PER_MINUTE)
refresh_limiter = _new(settings.RATE_LIMIT_REFRESH_PER_MINUTE)
logout_limiter = _new(settings.RATE_LIMIT_LOGOUT_PER_MINUTE)
invite_create_limiter = _new(settings.RATE_LIMIT_INVITE_CREATE_PER_MINUTE)
invite_resend_limiter = _new(settings.RATE_LIMIT_INVITE_RESEND_PER_MINUTE)
search_limiter = _new(settings.RATE_LIMIT_SEARCH_PER_MINUTE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_client_ip(request: Request) -> str:
    """
    Extract the originating client IP address.

    Reads the leftmost address from X-Forwarded-For when the app sits behind
    a reverse proxy, otherwise falls back to request.client.host.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _reject(retry_after: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Too many requests. Please try again later.",
        headers={"Retry-After": str(retry_after)},
    )


# ---------------------------------------------------------------------------
# Dependency factories
# ---------------------------------------------------------------------------

def ip_rate_limit(limiter: RateLimiter) -> Callable:
    """
    Return a FastAPI dependency that rate-limits by client IP address.

    Usage::

        @router.post("/login", dependencies=[Depends(ip_rate_limit(login_limiter))])
        def login(...):
            ...
    """

    async def dependency(request: Request) -> None:
        key = _get_client_ip(request)
        allowed, retry_after = limiter.is_allowed(key)
        if not allowed:
            raise _reject(retry_after)

    return dependency


def user_rate_limit(limiter: RateLimiter) -> Callable:
    """
    Return a FastAPI dependency that rate-limits by authenticated user ID.

    The dependency resolves the current user internally; FastAPI will
    deduplicate the get_current_user call when the endpoint also declares
    ``current_user`` as a parameter.

    Usage::

        @router.post("/invite", dependencies=[Depends(user_rate_limit(invite_create_limiter))])
        def invite_user(current_user: User = Depends(get_current_user), ...):
            ...
    """
    # Import here to avoid circular imports at module load time.
    from app.api.dependencies import get_current_user  # noqa: PLC0415
    from app.models.user import User  # noqa: PLC0415

    async def dependency(
        current_user: User = Depends(get_current_user),
    ) -> None:
        key = str(current_user.public_id)
        allowed, retry_after = limiter.is_allowed(key)
        if not allowed:
            raise _reject(retry_after)

    return dependency
