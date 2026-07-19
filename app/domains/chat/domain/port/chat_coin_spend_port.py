from typing import Protocol


class ChatCoinSpendPort(Protocol):
    """채팅 턴당 코인 소진 포트 — chat 도메인은 coin 도메인을 직접 모른다.

    구현은 coin 도메인 어댑터(ChatCoinSpendAdapter)가 제공, main.py가 주입한다.
    """

    async def spend(self, account_id: int, cost: int, ref: str) -> int:
        """cost 만큼 소진하고 소진 후 잔액을 반환. 부족 시 InsufficientCoinsError."""
        ...
