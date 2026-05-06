import base64
from typing import Any

import httpx

from app.domains.payment.domain.port.payment_gateway_port import (
    PaymentGatewayError,
    PaymentGatewayPort,
)


class TossPaymentsClient(PaymentGatewayPort):
    """토스페이먼츠 V1 결제 승인 클라이언트.

    인증: Authorization: Basic base64(secretKey + ':')
    엔드포인트: POST {base_url}/v1/payments/confirm
    """

    def __init__(self, secret_key: str, base_url: str) -> None:
        if not secret_key:
            raise ValueError("토스 시크릿 키가 설정되지 않았습니다.")
        token = base64.b64encode(f"{secret_key}:".encode()).decode()
        self._auth_header = f"Basic {token}"
        self._base_url = base_url.rstrip("/")

    async def confirm(
        self,
        *,
        payment_key: str,
        order_id: str,
        amount: int,
    ) -> dict[str, Any]:
        url = f"{self._base_url}/v1/payments/confirm"
        payload = {"paymentKey": payment_key, "orderId": order_id, "amount": amount}
        headers = {
            "Authorization": self._auth_header,
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:  # noqa: S501
            try:
                resp = await client.post(url, json=payload, headers=headers)
            except httpx.RequestError as e:
                raise PaymentGatewayError(f"토스 연결 실패: {e}") from e

        if resp.status_code >= 400:
            raise _map_error(resp)

        data = resp.json()
        if not isinstance(data, dict):
            raise PaymentGatewayError("토스 응답 형식 오류 (dict 아님)")
        return data


def _map_error(resp: httpx.Response) -> PaymentGatewayError:
    try:
        body = resp.json()
        code = body.get("code") if isinstance(body, dict) else None
        message = body.get("message") if isinstance(body, dict) else None
    except Exception:
        code = None
        message = None
    msg = message or resp.text or f"HTTP {resp.status_code}"
    return PaymentGatewayError(f"토스 결제 승인 실패: {msg}", code=code)
