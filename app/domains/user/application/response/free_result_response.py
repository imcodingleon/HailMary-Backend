from typing import Any

from pydantic import BaseModel


class FreeResultResponse(BaseModel):
    sajuRequestId: int
    sajuData: dict[str, Any]
