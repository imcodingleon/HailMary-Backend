"""QA 토큰 검증 미들웨어 — APP_ENV=test 일 때만 등록.

모든 /api/* 요청에서 X-QA-Token 헤더 검증.
예외 경로 (인증 없이 접근 가능):
  - /api/qa/login (로그인 자체)
  - /api/payments/feedback (PayApp webhook — PayApp 서버가 호출, 헤더 못 박음)
  - /api/payments/return (PayApp returnurl POST — 사용자 브라우저가 도달, BE가 FE로 redirect)
  - /api/payments/status (FE 폴링 — QA 토큰 없는 success 페이지에서 호출 가능해야 함)
  - /health (헬스 체크)

운영 환경(APP_ENV != "test")에선 main.py에서 미들웨어 등록 안 함.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# 토큰 없이 접근 가능한 경로 prefix
_EXEMPT_PREFIXES: tuple[str, ...] = (
    "/api/qa/login",
    "/api/payments/feedback",  # PayApp webhook
    "/api/payments/return",    # PayApp returnurl POST → BE redirect
    "/api/payments/status",    # FE polling (success 페이지에서 호출)
    "/health",
    "/docs",
    "/openapi.json",
)


class QaAuthMiddleware(BaseHTTPMiddleware):
    """X-QA-Token 헤더 검증. 미일치 시 401 반환.

    settings.qa_access_token이 None이면 미들웨어 자체가 동작 안 함 (안전 모드).
    """

    def __init__(self, app, *, expected_token: str) -> None:
        super().__init__(app)
        self._expected_token = expected_token

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        path = request.url.path
        # /api/* 외 경로는 통과 (정적 파일, 헬스 등)
        if not path.startswith("/api/"):
            return await call_next(request)
        # 예외 경로 통과
        for prefix in _EXEMPT_PREFIXES:
            if path.startswith(prefix):
                return await call_next(request)
        # 토큰 검증
        token = request.headers.get("X-QA-Token", "")
        if token != self._expected_token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "QA token required"},
            )
        return await call_next(request)
