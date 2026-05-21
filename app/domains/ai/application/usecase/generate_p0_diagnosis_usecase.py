"""도윤 P-0 0-5 분석 진입 요약 AI 호출 UseCase.

호출 시점: CreatePaidReportUseCase (결제 검증 후) → ComposePaidReportUseCase 안의
character == "doyoon" 분기에서 `ai_intro` 값을 받기 위해 사용.

흐름:
    1. doyoon_p0_intro.get_doyoon_p0_facts() — 사실값 12개 + 룰 텍스트 추출
    2. doyoon_p0_diagnosis_prompt.build_p0_diagnosis_prompt() — system/user 구성
    3. ai_client.generate_chapter(model=haiku) — Claude API 호출
    4. validate_p0_diagnosis() — 9단계 검증
    5. 실패/예외 시 → 룰 합성 결과(`rule_text`) fallback

CLAUDE.md 규칙:
- 결제 검증 게이트는 호출자(CreatePaidReportUseCase)가 담당. 본 UseCase는 호출 자체로
  결제 검증을 하지 않음 (Core Rule 1 — 호출자가 보장).
- 개인정보 마스킹: 로깅 시 user_name은 평문 X (name[0]+"**").
"""

from __future__ import annotations

import logging

from app.domains.ai.domain.port.ai_client_port import (
    AIClientError,
    AIClientPort,
)
from app.domains.ai.domain.service.doyoon_p0_diagnosis_prompt import (
    build_p0_diagnosis_prompt,
    validate_p0_diagnosis,
)
from app.domains.ai.domain.templates.doyoon_p0_intro import (
    get_doyoon_p0_facts,
)

logger = logging.getLogger(__name__)

# Sonnet 4.6 — P-10 letter와 동일 모델. 톤 일관성 + 페르소나 정합성 위해 선택.
# Haiku 대비 회당 +7원이지만 도윤 100건/일 기준 월 2만원 차이로 첫인상 품질 확보.
DOYOON_P0_MODEL = "claude-sonnet-4-6"

# AI 호출 파라미터
_MAX_TOKENS = 600       # 한국어 4단락 340자 ≈ 출력 토큰 ~500 + 안전 마진
_TEMPERATURE = 0.85     # 표현 다양화. 사실값은 prompt에서 강제 보존.


def _mask_user_name(name: str) -> str:
    """CLAUDE.md 마스킹 룰. 로그용."""
    if not name:
        return ""
    return name[0] + "**"


class GenerateP0DiagnosisUseCase:
    """P-0 ai_intro 박스 AI 생성 + 룰 fallback orchestrator."""

    def __init__(self, *, ai_client: AIClientPort) -> None:
        self._ai_client = ai_client

    async def execute(
        self,
        *,
        user_name: str,
        ilgan: str,
        ohang_excess: str,
        ohang_lack: str,
    ) -> str:
        """ai_intro 텍스트 반환. AI 실패 시 룰 합성으로 자동 폴백.

        Args:
            user_name: User.name. 빈 문자열이면 ValueError.
            ilgan: 일간 한글 (갑목/.../계수). 미등록 키면 KeyError.
            ohang_excess: 과다 오행 (목/화/토/금/수).
            ohang_lack: 부족 오행.

        Returns:
            도윤 톤 4단락 텍스트. AI 성공 시 AI 결과, 실패·검증 실패 시 룰 텍스트.

        Raises:
            ValueError / KeyError: facts 추출 시점에 입력 가드 실패 (호출자 잘못).
        """
        facts = get_doyoon_p0_facts(
            user_name=user_name,
            ilgan=ilgan,
            ohang_excess=ohang_excess,
            ohang_lack=ohang_lack,
        )
        rule_fallback: str = facts["rule_text"]

        try:
            system_prompt, user_prompt = build_p0_diagnosis_prompt(facts)
            ai_text = await self._ai_client.generate_chapter(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=_MAX_TOKENS,
                temperature=_TEMPERATURE,
                model=DOYOON_P0_MODEL,
            )
        except AIClientError as exc:
            logger.warning(
                "doyoon_p0 AI 호출 실패 → 룰 fallback (user=%s, ilgan=%s, exc=%s)",
                _mask_user_name(user_name), ilgan, exc,
            )
            return rule_fallback

        ok, reason = validate_p0_diagnosis(ai_text, facts)
        if not ok:
            logger.warning(
                "doyoon_p0 AI 검증 실패 → 룰 fallback (user=%s, ilgan=%s, reason=%s)",
                _mask_user_name(user_name), ilgan, reason,
            )
            return rule_fallback

        return ai_text
