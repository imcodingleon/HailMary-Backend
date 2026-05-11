"""FortuneTeller Lambda Function URL 호출 클라이언트.

Lambda Function URL이 AuthType=AWS_IAM 인 경우 SigV4 서명 필요. boto3 의 SigV4
서명을 httpx 요청에 적용하여 EC2 IAM Instance Profile 자격증명으로 호출한다.

자격증명 우선순위 (botocore 기본):
1. 환경변수 (AWS_ACCESS_KEY_ID 등)
2. ~/.aws/credentials
3. **EC2 Instance Metadata Service** ← 프로덕션 경로 (hailmary-backend-role)

자격증명이 없으면 unsigned 호출 (개발 환경 fallback). AuthType=NONE 인 Function URL
은 서명 유무 상관없이 동작하므로 마이그레이션 순서 안전.
"""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlparse

import botocore.session
import httpx
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest


class FortuneTellerError(Exception):
    pass


def _sigv4_headers(
    method: str, url: str, body: bytes, region: str
) -> dict[str, str]:
    """boto3 자격증명 체인으로 SigV4 서명 헤더 생성.

    자격증명 미발견 시 빈 dict 반환 (unsigned 호출 — AuthType=NONE 개발 환경 대응).
    """
    session = botocore.session.Session()
    credentials = session.get_credentials()
    if credentials is None:
        return {}
    request = AWSRequest(method=method, url=url, data=body)
    SigV4Auth(credentials, "lambda", region).add_auth(request)
    return dict(request.headers.items())


class FortuneTellerClient:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")
        parsed = urlparse(self._base_url)
        # Function URL 도메인 형태: https://<id>.lambda-url.<region>.on.aws
        if parsed.hostname and ".lambda-url." in parsed.hostname:
            self._region = parsed.hostname.split(".lambda-url.")[1].split(".")[0]
        else:
            self._region = "ap-northeast-2"

    async def analyze(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self._base_url}/api/saju/free"
        body = json.dumps(payload).encode()
        sig_headers = _sigv4_headers("POST", url, body, self._region)
        headers = {"Content-Type": "application/json", **sig_headers}
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:  # noqa: S501 # Windows Python 3.14 SSL DLL 충돌 우회
            try:
                resp = await client.post(url, content=body, headers=headers)
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                raise FortuneTellerError(
                    f"FortuneTeller 오류 {e.response.status_code}"
                ) from e
            except httpx.RequestError as e:
                raise FortuneTellerError(f"FortuneTeller 연결 실패: {e}") from e
            return dict(resp.json())
