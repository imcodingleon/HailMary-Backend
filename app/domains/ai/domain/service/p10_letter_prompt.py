"""P-10 박스 3 AI 답장 시스템 프롬프트 dispatcher.

캐릭터별 톤이 정반대라 builder를 분리:
- 연우: 반말·자연 비유 → `yeonwoo_p10_letter_prompt.py`
- 도윤: 존댓말·통계 어휘 + user_name 호명 → `doyoon_p10_letter_prompt.py`

이 모듈은 persona.name으로 위임. UseCase는 기존 시그니처
`build_p10_system_prompt(*, persona, ...)` 그대로 유지.
"""

from __future__ import annotations

from app.domains.ai.domain.service.doyoon_p10_letter_prompt import (
    build_doyoon_p10_system_prompt,
)
from app.domains.ai.domain.service.yeonwoo_p10_letter_prompt import (
    build_yeonwoo_p10_system_prompt,
)
from app.domains.ai.domain.value_object.character_persona import CharacterPersona


def build_p10_system_prompt(
    *,
    persona: CharacterPersona,
    ilgan: str,
    ilju: str,
    ohang_excess: str,
    ohang_lack: str,
    box1_body: str,
    box2_body: str,
    step3: str,
    emphasis: str,
    user_name: str | None = None,
) -> tuple[str, str]:
    """persona.name으로 builder 선택 후 위임.

    Args:
        user_name: 도윤일 때 필수. 연우일 때 무시됨.

    Raises:
        ValueError: persona.name이 매칭 안 되거나 도윤인데 user_name 누락.
    """
    if persona.name == "강연우":
        return build_yeonwoo_p10_system_prompt(
            persona=persona,
            ilgan=ilgan,
            ilju=ilju,
            ohang_excess=ohang_excess,
            ohang_lack=ohang_lack,
            box1_body=box1_body,
            box2_body=box2_body,
            step3=step3,
            emphasis=emphasis,
        )
    if persona.name == "한도윤":
        if not user_name:
            raise ValueError("doyoon P-10 prompt requires user_name")
        return build_doyoon_p10_system_prompt(
            persona=persona,
            user_name=user_name,
            ilgan=ilgan,
            ilju=ilju,
            ohang_excess=ohang_excess,
            ohang_lack=ohang_lack,
            box1_body=box1_body,
            box2_body=box2_body,
            step3=step3,
            emphasis=emphasis,
        )
    raise ValueError(f"unknown persona.name: {persona.name!r}")
