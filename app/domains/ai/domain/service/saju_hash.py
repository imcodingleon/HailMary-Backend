import hashlib


def compute_saju_hash(
    *,
    birth_date: str,
    birth_time: str,
    name: str,
    gender: str,
    calendar_type: str,
) -> str:
    """사주 입력값을 정규화 후 SHA-256 hash 반환.

    같은 사주(생년월일시 + 이름 + 성별 + 양/음력) → 동일 hash → 결과 캐시 hit.

    개인정보(이름/생년월일)는 hash 결과만 사용. 로그 출력 금지.
    """
    normalized_name = name.strip().replace(" ", "").lower()
    payload = "|".join(
        [
            birth_date.strip(),
            birth_time.strip().lower(),
            normalized_name,
            gender.strip().lower(),
            calendar_type.strip().lower(),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
