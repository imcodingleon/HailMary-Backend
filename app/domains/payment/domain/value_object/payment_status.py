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


class PaymentMethod(str, Enum):
    """결제수단 대분류. 토스 confirm 응답 `method`(한글) 를 도메인 enum 으로 매핑."""

    CARD = "CARD"
    EASY_PAY = "EASY_PAY"
    TRANSFER = "TRANSFER"
    VIRTUAL_ACCOUNT = "VIRTUAL_ACCOUNT"
    MOBILE_PHONE = "MOBILE_PHONE"
    OTHER = "OTHER"

    @classmethod
    def from_toss(cls, korean: str | None) -> "PaymentMethod | None":
        """토스 응답의 한글 method 값을 도메인 enum 으로 변환. 누락은 None, 미정의는 OTHER."""
        if not korean:
            return None
        mapping = {
            "카드": cls.CARD,
            "간편결제": cls.EASY_PAY,
            "계좌이체": cls.TRANSFER,
            "가상계좌": cls.VIRTUAL_ACCOUNT,
            "휴대폰": cls.MOBILE_PHONE,
        }
        return mapping.get(korean.strip(), cls.OTHER)
