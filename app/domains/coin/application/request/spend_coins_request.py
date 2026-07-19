from dataclasses import dataclass


@dataclass
class SpendCoinsRequest:
    account_id: int
    cost: int
    ref: str  # 멱등 키(호출자 생성 토큰: 예 f"love:{result_id}", f"chat:{message_id}")
