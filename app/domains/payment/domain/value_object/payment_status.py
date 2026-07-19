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
    COIN = "COIN"  # 도화선 2.0 연애운 코인 해금 (P4 Unit B) — KRW 미발생, 분석 구분용

