from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.domains.payment.domain.value_object.payment_status import (
    CharacterCode,
    PaymentStatus,
)
from app.infrastructure.database.session import Base


class PaymentORM(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    payment_key: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    order_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    character: Mapped[CharacterCode] = mapped_column(
        Enum(CharacterCode, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
    )
    customer_email: Mapped[str] = mapped_column(String(254), nullable=False)
    approved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
