from __future__ import annotations

from datetime import date, time

from pydantic import BaseModel, field_validator

from app.domains.user.domain.value_object.calendar_type import CalendarType
from app.domains.user.domain.value_object.character_type import CharacterType
from app.domains.user.domain.value_object.gender import Gender


class SubmitUserInfoRequest(BaseModel):
    birth: str                       # "YYYY-MM-DD"
    calendar: CalendarType
    gender: Gender
    name: str
    time: str | None = None          # "HH:MM" 또는 null(모름)
    character_id: CharacterType | None = None  # 어떤 캐릭터의 설문인지 (yeonwoo / doyoon)

    @field_validator("birth")
    @classmethod
    def validate_birth(cls, v: str) -> str:
        date.fromisoformat(v)
        return v

    @field_validator("time")
    @classmethod
    def validate_time(cls, v: str | None) -> str | None:
        if v is None or v == "unknown":
            return None
        time.fromisoformat(v)
        return v

    def birth_date(self) -> date:
        return date.fromisoformat(self.birth)

    def birth_time(self) -> time | None:
        if self.time is None:
            return None
        return time.fromisoformat(self.time)
