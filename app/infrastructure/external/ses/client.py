"""AWS SES v2 비동기 이메일 발송 클라이언트.

boto3는 동기 SDK라 asyncio.to_thread로 wrap.
SES 샌드박스 모드에선 검증된 발송자/수신자만 발송 가능.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


class SESEmailError(Exception):
    """SES 발송 실패."""


class SESClient:
    """AWS SES v2 클라이언트.

    Args:
        region: AWS region (예: "ap-northeast-2")
        sender: 검증된 발송자 이메일 (SES 콘솔에서 verify 필수)
        access_key_id / secret_access_key: 명시 주입 시 사용. None이면 EC2 IAM role 자동.

    예외 정책:
        BotoCoreError / ClientError → SESEmailError로 변환. 호출자가 swallow.
    """

    def __init__(
        self,
        *,
        region: str,
        sender: str,
        access_key_id: str | None = None,
        secret_access_key: str | None = None,
    ) -> None:
        kwargs: dict[str, Any] = {"region_name": region}
        if access_key_id and secret_access_key:
            kwargs["aws_access_key_id"] = access_key_id
            kwargs["aws_secret_access_key"] = secret_access_key
        self._client = boto3.client("sesv2", **kwargs)
        self._sender = sender

    async def send_email(
        self,
        *,
        to: str,
        subject: str,
        html_body: str,
        text_body: str,
    ) -> None:
        """이메일 1통 발송. boto3 동기 호출을 asyncio.to_thread로 비동기 wrap.

        실패 시 SESEmailError 발생. 호출자가 fire-and-forget으로 swallow 권장.
        """
        try:
            await asyncio.to_thread(
                self._client.send_email,
                FromEmailAddress=self._sender,
                Destination={"ToAddresses": [to]},
                Content={
                    "Simple": {
                        "Subject": {"Data": subject, "Charset": "UTF-8"},
                        "Body": {
                            "Html": {"Data": html_body, "Charset": "UTF-8"},
                            "Text": {"Data": text_body, "Charset": "UTF-8"},
                        },
                    }
                },
            )
        except (BotoCoreError, ClientError) as e:
            logger.exception("SES send_email failed (to=%s)", to)
            raise SESEmailError(str(e)) from e
