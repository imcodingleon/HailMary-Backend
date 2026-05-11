"""Amplitude HTTP API V2 클라이언트.

엔드포인트: POST {base_url}/2/httpapi
인증: payload.api_key 평문 (헤더 인증 없음)
멱등: insert_id로 같은 이벤트 재전송 시 dedupe.

설계 원칙:
- 호출 측이 fire-and-forget로 부르므로, 본 클라이언트는 예외를 던지지 않는다.
- 모든 실패는 로그만 남기고 None 반환.
- 타임아웃 5초로 비정상 지연 방지.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class AmplitudeClient:
    def __init__(self, *, api_key: str | None, base_url: str) -> None:
        self._api_key = api_key
        self._url = f"{base_url.rstrip('/')}/2/httpapi"

    @property
    def enabled(self) -> bool:
        return bool(self._api_key)

    async def send_event(self, event: dict[str, Any]) -> None:
        """단일 이벤트 발화. 실패 시 로그만 남기고 swallow."""
        if not self._api_key:
            logger.info("amplitude.skip: api_key not configured")
            return
        payload = {"api_key": self._api_key, "events": [event]}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    self._url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
            if resp.status_code >= 400:
                logger.warning(
                    "amplitude.failed status=%s body=%s",
                    resp.status_code,
                    resp.text[:500],
                )
            else:
                logger.info(
                    "amplitude.sent event_type=%s insert_id=%s",
                    event.get("event_type"),
                    event.get("insert_id"),
                )
        except Exception as e:  # noqa: BLE001
            # 결제 응답을 막으면 안 되므로 모든 예외 swallow
            logger.warning("amplitude.exception: %s", e)
