"""P-10 박스 3 AI 답장 생성 UseCase.

호출 시점: ComposePaidReportUseCase에서 P-0~P-9 + 박스 1·2까지 합성된 뒤,
step3가 비어있지 않을 때만 호출.

결제 검증 게이트: 이 UseCase는 결제 검증을 직접 하지 않음.
호출자가 PaidReport 존재 또는 Payment.is_active() 확인 후 호출 (CLAUDE.md Core Rule 1).
"""

from __future__ import annotations

from app.domains.ai.domain.port.ai_client_port import AIClientPort
from app.domains.ai.domain.service.p10_letter_prompt import build_p10_system_prompt


class GenerateP10LetterUseCase:
    """P-10 박스 3 가운데 AI 단락 생성 (fill-in-the-middle)."""

    def __init__(self, *, ai_client: AIClientPort) -> None:
        self._ai_client = ai_client

    async def execute(
        self,
        *,
        ilgan: str,
        ilju: str,
        ohang_excess: str,
        ohang_lack: str,
        box1_body: str,
        box2_body: str,
        step3: str,
        emphasis: str,
    ) -> str:
        """AI 호출로 박스 3 가운데 단락 생성.

        Returns:
            AI 응답 텍스트 (300~400자 도화선 톤 답장).
        """
        system_prompt, user_prompt = build_p10_system_prompt(
            ilgan=ilgan,
            ilju=ilju,
            ohang_excess=ohang_excess,
            ohang_lack=ohang_lack,
            box1_body=box1_body,
            box2_body=box2_body,
            step3=step3,
            emphasis=emphasis,
        )
        return await self._ai_client.generate_chapter(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=600,
            temperature=0.85,
        )
