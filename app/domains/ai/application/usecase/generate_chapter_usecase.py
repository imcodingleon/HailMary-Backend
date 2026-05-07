"""챕터 생성 UseCase.

chapter_key → 템플릿 합성 (AI 호출 0) 또는 프롬프트 빌더 + Claude 호출.

사용자 결정 (P-0):
- 0-5 첫인사는 22조각 템플릿 합성으로 전환 (AI 호출 폐기).
- 추후 AI 호출 챕터(P-4 악연 인물 묘사 등)는 _ai_client.generate_chapter 분기에 추가.
"""

from app.domains.ai.domain.port.ai_client_port import AIClientPort
from app.domains.ai.domain.templates.yeonwoo_p0_intro import compose_p0_intro


class UnknownChapterError(Exception):
    """등록되지 않은 chapter_key."""


class MissingChapterVariableError(Exception):
    """필수 입력 변수 누락."""


_REQUIRED_VARS: dict[str, tuple[str, ...]] = {
    "p0_intro": ("ilgan", "ohang_excess", "ohang_lack"),
}

# 템플릿 합성 챕터 (AI 호출 0).
_TEMPLATE_CHAPTERS: frozenset[str] = frozenset({"p0_intro"})


class GenerateChapterUseCase:
    """챕터 생성 — 템플릿 또는 Claude 호출.

    Application 레이어. AIClientPort만 의존, anthropic SDK 직접 import 금지.
    """

    def __init__(self, *, ai_client: AIClientPort) -> None:
        # 향후 AI 호출 챕터 추가 시 사용. 현재 P-0는 템플릿만.
        self._ai_client = ai_client

    async def execute(
        self,
        *,
        chapter_key: str,
        variables: dict[str, str],
    ) -> str:
        self._assert_variables(chapter_key, variables)
        if chapter_key in _TEMPLATE_CHAPTERS:
            return self._compose_template(chapter_key, variables)
        # 향후 AI 챕터 추가 시 여기에 분기 + self._ai_client.generate_chapter(...) 호출.
        raise UnknownChapterError(chapter_key)

    @staticmethod
    def _assert_variables(chapter_key: str, variables: dict[str, str]) -> None:
        required = _REQUIRED_VARS.get(chapter_key)
        if required is None:
            raise UnknownChapterError(chapter_key)
        missing = [k for k in required if not variables.get(k)]
        if missing:
            raise MissingChapterVariableError(
                f"chapter_key={chapter_key} 필수 변수 누락: {missing}"
            )

    @staticmethod
    def _compose_template(chapter_key: str, variables: dict[str, str]) -> str:
        if chapter_key == "p0_intro":
            return compose_p0_intro(
                ilgan=variables["ilgan"],
                ohang_excess=variables["ohang_excess"],
                ohang_lack=variables["ohang_lack"],
            )
        raise UnknownChapterError(chapter_key)
