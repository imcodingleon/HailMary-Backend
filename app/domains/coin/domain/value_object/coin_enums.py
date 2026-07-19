from enum import Enum


class CoinType(str, Enum):
    PAID = "PAID"
    FREE = "FREE"


class SourceReason(str, Enum):
    SIGNUP_GRANT = "SIGNUP_GRANT"
    CHARGE = "CHARGE"
    EVENT = "EVENT"


class TransactionType(str, Enum):
    GRANT = "GRANT"
    CHARGE = "CHARGE"
    SPEND = "SPEND"
    REFUND = "REFUND"
    EXPIRE = "EXPIRE"
