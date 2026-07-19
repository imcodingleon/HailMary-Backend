class InsufficientCoinsError(Exception):
    """가용 잔액 < 요청 cost. 라우터에서 402로 매핑."""

    def __init__(self, *, available: int, required: int) -> None:
        super().__init__(f"insufficient coins: have {available}, need {required}")
        self.available = available
        self.required = required
