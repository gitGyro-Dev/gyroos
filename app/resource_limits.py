from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable

from fastapi import Request
from fastapi.responses import JSONResponse, Response

from .settings import RuntimeSettings, settings


class FixedWindowRateLimiter:
    def __init__(self, *, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def allow(self, key: str, *, now: float | None = None) -> tuple[bool, int]:
        current = time.monotonic() if now is None else now
        cutoff = current - self.window_seconds
        async with self._lock:
            bucket = self._requests[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= self.max_requests:
                retry_after = max(1, int(self.window_seconds - (current - bucket[0])))
                return False, retry_after
            bucket.append(current)
            return True, 0


class ResourceLimitMiddleware:
    def __init__(
        self,
        app,
        *,
        runtime_settings: RuntimeSettings = settings,
    ) -> None:
        self.app = app
        self.settings = runtime_settings
        self.rate_limiter = FixedWindowRateLimiter(
            max_requests=runtime_settings.rate_limit_requests,
            window_seconds=runtime_settings.rate_limit_window_seconds,
        )
        self.concurrent_gate = asyncio.Semaphore(runtime_settings.max_concurrent_requests)

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http" or scope.get("path") == "/health":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                body_size = int(content_length)
            except ValueError:
                body_size = self.settings.max_request_body_bytes + 1
            if body_size > self.settings.max_request_body_bytes:
                response = JSONResponse(
                    status_code=413,
                    content={
                        "error_code": "GYRO_API_REQUEST_TOO_LARGE",
                        "category": "RESOURCE_LIMIT",
                        "phase": "REQUEST_ADMISSION",
                        "message": "Request body exceeds configured limit.",
                    },
                )
                await response(scope, receive, send)
                return

        client_host = request.client.host if request.client else "unknown"
        allowed, retry_after = await self.rate_limiter.allow(client_host)
        if not allowed:
            response = JSONResponse(
                status_code=429,
                content={
                    "error_code": "GYRO_API_RATE_LIMITED",
                    "category": "RESOURCE_LIMIT",
                    "phase": "REQUEST_ADMISSION",
                    "message": "Request rate exceeds configured limit.",
                },
                headers={"Retry-After": str(retry_after)},
            )
            await response(scope, receive, send)
            return

        try:
            await asyncio.wait_for(self.concurrent_gate.acquire(), timeout=0.001)
        except TimeoutError:
            response = JSONResponse(
                status_code=503,
                content={
                    "error_code": "GYRO_API_CONCURRENCY_LIMIT",
                    "category": "RESOURCE_LIMIT",
                    "phase": "REQUEST_ADMISSION",
                    "message": "Concurrent request capacity is exhausted.",
                },
                headers={"Retry-After": "1"},
            )
            await response(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)
        finally:
            self.concurrent_gate.release()
