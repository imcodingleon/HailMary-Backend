from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domains.user.domain.value_object.birth_info import BirthInfo
from app.domains.user.domain.value_object.character_type import CharacterType
from app.domains.user.domain.value_object.gender import Gender


@dataclass
class User:
    birth_info: BirthInfo
    gender: Gender
    name: str
    session_token: str
    id: int | None = None
    character_id: CharacterType | None = None
    created_at: datetime | None = None

    def __repr__(self) -> str:
        masked_name = f"{self.name[0]}**" if self.name else None
        return f"User(id={self.id}, name={masked_name})"

    def __str__(self) -> str:
        return self.__repr__()
