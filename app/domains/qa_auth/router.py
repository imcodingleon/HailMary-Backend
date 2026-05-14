"""QA 로그인 라우터 — POST /api/qa/login.

요청: { username, password }
응답: { access_token } (settings.qa_access_token 그대로 반환)

ID/PW 매칭 실패 시 401. APP_ENV != "test" 일 때는 라우터 등록 자체가 안 됨 (main.py).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.infrastructure.config.settings import get_settings

router = APIRouter(prefix="/api/qa", tags=["qa-auth"])


class QaLoginRequest(BaseModel):
    username: str
    password: str


class QaLoginResponse(BaseModel):
    access_token: str


@router.post(
    "/login",
    response_model=QaLoginResponse,
    status_code=status.HTTP_200_OK,
)
async def qa_login(body: QaLoginRequest) -> QaLoginResponse:
    """QA 로그인 — ID/PW 매칭 시 단일 토큰 반환."""
    settings = get_settings()
    if not settings.qa_username or not settings.qa_password or not settings.qa_access_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="QA login not configured",
        )
    if body.username != settings.qa_username or body.password != settings.qa_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return QaLoginResponse(access_token=settings.qa_access_token)
