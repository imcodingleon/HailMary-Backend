"""PayApp 결제 게이트웨이 클라이언트.

엔드포인트: POST https://api.payapp.kr/oapi/apiLoad.html
Content-Type: application/x-www-form-urlencoded
응답: URL-encoded KEY=VALUE  (state=1 성공 / state=0 실패 + errorCode/errorMessage)

PayApp 가맹점 인증은 호출별로 form-data에 동봉 (userid + linkkey + linkval).
"""

from __future__ import annotations

from typing import Any
from urllib.parse import parse_qs

import httpx

from app.domains.payment.domain.port.payapp_payment_port import (
    PayAppGatewayError,
    PayAppPaymentPort,
    PayAppRequestResult,
)

_PAYAPP_API_PATH = "/oapi/apiLoad.html"


class PayAppClient(PayAppPaymentPort):
    def __init__(
        self,
        *,
        userid: str,
        linkkey: str,
        linkval: str,
        base_url: str,
        feedback_url: str,
        return_url: str,
    ) -> None:
        if not userid or not linkkey or not linkval:
            raise ValueError(
                "PayApp 인증 정보(userid/linkkey/linkval)가 설정되지 않았습니다."
            )
        self._userid = userid
        self._linkkey = linkkey
        self._linkval = linkval
        self._base_url = base_url.rstrip("/")
        self._feedback_url = feedback_url
        self._return_url = return_url

    @property
    def url(self) -> str:
        return f"{self._base_url}{_PAYAPP_API_PATH}"

    async def request_payment(
        self,
        *,
        order_id: str,
        amount: int,
        goods_name: str,
        recv_phone: str,
        recv_email: str | None = None,
    ) -> PayAppRequestResult:
        payload: dict[str, str | int] = {
            "cmd": "payrequest",
            "userid": self._userid,
            "goodname": goods_name,
            "price": amount,
            "recvphone": recv_phone,
            "var1": order_id,
            "feedbackurl": self._feedback_url,
            "returnurl": self._return_url,
            "smsuse": "n",         # 카카오톡 결제링크 발송 X (FE에서 payurl로 직접 리다이렉트)
            "skip_cstpage": "y",   # 매출전표 페이지 스킵 → returnurl로 바로 이동
            "checkretry": "y",     # feedback SUCCESS 아니면 최대 10회 재시도
        }
        if recv_email:
            payload["recvemail"] = recv_email

        data = await self._post(payload)
        mul_no = data.get("mul_no")
        payurl = data.get("payurl")
        if not mul_no or not payurl:
            raise PayAppGatewayError(
                f"PayApp payrequest 응답 누락 (mul_no={mul_no}, payurl={payurl})"
            )
        return PayAppRequestResult(mul_no=str(mul_no), payurl=str(payurl))

    async def cancel_payment(
        self,
        *,
        mul_no: str,
        cancel_memo: str | None = None,
    ) -> None:
        payload: dict[str, str] = {
            "cmd": "paycancel",
            "userid": self._userid,
            "linkkey": self._linkkey,
            "mul_no": mul_no,
        }
        if cancel_memo:
            payload["cancelmemo"] = cancel_memo
        await self._post(payload)

    async def _post(self, payload: dict[str, Any]) -> dict[str, str]:
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:  # noqa: S501
            try:
                resp = await client.post(self.url, data=payload)
            except httpx.RequestError as e:
                raise PayAppGatewayError(f"PayApp 연결 실패: {e}") from e

        # PayApp은 항상 200 OK + 본문 state=0/1 로 결과 알림
        parsed = parse_qs(resp.text, keep_blank_values=True)
        # parse_qs는 값을 list로 반환 — 첫 값만 취함
        flat: dict[str, str] = {k: v[0] for k, v in parsed.items() if v}

        state = flat.get("state")
        if state != "1":
            error_message = flat.get("errorMessage") or resp.text or "알 수 없는 오류"
            error_code = flat.get("errorCode") or flat.get("errno")
            raise PayAppGatewayError(
                f"PayApp 호출 실패: {error_message}", code=error_code
            )
        return flat
