from pydantic import BaseModel, ConfigDict, field_validator
from pydantic.alias_generators import to_camel


class SubmitSurveyRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    saju_request_id: int
    survey_version: str = "v1"
    step1: list[str]
    step2: list[str]
    step3: str | None = None

    @field_validator("step1", "step2")
    @classmethod
    def validate_slugs(cls, v: list[str]) -> list[str]:
        if len(v) > 10:
            raise ValueError("최대 10개까지 선택 가능합니다.")
        for slug in v:
            if not (1 <= len(slug) <= 48):
                raise ValueError(f"슬러그 길이가 올바르지 않습니다: {slug}")
        return v

    @field_validator("step3")
    @classmethod
    def validate_step3(cls, v: str | None) -> str | None:
        if v is None:
            return None
        trimmed = v.strip()
        if len(trimmed) > 100:
            raise ValueError("step3는 최대 100자입니다.")
        return trimmed if trimmed else None
