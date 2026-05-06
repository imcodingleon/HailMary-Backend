from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, Enum, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domains.user.domain.value_object.calendar_type import CalendarType
from app.domains.user.domain.value_object.character_type import CharacterType
from app.domains.user.domain.value_object.gender import Gender
from app.infrastructure.database.session import Base


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    gender: Mapped[Gender] = mapped_column(Enum(Gender, values_callable=lambda e: [x.value for x in e]))
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    calendar_type: Mapped[CalendarType] = mapped_column(
        Enum(CalendarType, values_callable=lambda e: [x.value for x in e])
    )
    birth_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    birth_time_unknown: Mapped[bool] = mapped_column(Boolean, default=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    session_token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    character_id: Mapped[CharacterType | None] = mapped_column(
        Enum(CharacterType, values_callable=lambda e: [x.value for x in e]),
        nullable=True,
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, server_default=func.now()
    )
