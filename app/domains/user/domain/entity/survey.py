from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Survey:
    user_id: int
    survey_version: str
    step1_slugs: list[str]
    step2_slugs: list[str]
    id: int | None = None
    step3_text: str | None = None
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.step3_text is not None:
            trimmed = self.step3_text.strip()
            self.step3_text = trimmed if trimmed else None
