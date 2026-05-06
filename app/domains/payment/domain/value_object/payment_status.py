from enum import Enum


class PaymentStatus(str, Enum):
    """결제 상태. 토스페이먼츠 표준 status 값과 정렬."""

    DONE = "DONE"
    CANCELED = "CANCELED"
    PARTIAL_CANCELED = "PARTIAL_CANCELED"
    ABORTED = "ABORTED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"
    READY = "READY"
    WAITING_FOR_DEPOSIT = "WAITING_FOR_DEPOSIT"


class CharacterCode(str, Enum):
    YEONWOO = "yeonwoo"
    DOYOON = "doyoon"
