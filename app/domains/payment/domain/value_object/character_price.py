"""캐릭터별 결제 가격 마스터 — BE 단일 진실원.

PayApp 플로에서는 FE가 가격을 보낼 필요 없음. BE가 character 만 받아서 가격 결정.
가격 위변조 차단 + 단일 관리 지점.
"""

from app.domains.payment.domain.value_object.payment_status import CharacterCode

# ⚠️ PayApp 마이그레이션 라이브 검증 중 — 임시로 1,000원.
# 본 배포 전 두 값 모두 20000으로 원복 + 본 SSOT (`결제_마이그레이션/PAYAPP_MIGRATION.md`)
# 의 Phase 10 체크리스트에 "가격 원복" 확인.
_CHARACTER_PRICES_KRW: dict[CharacterCode, int] = {
    CharacterCode.YEONWOO: 1000,
    CharacterCode.DOYOON: 1000,
}

_CHARACTER_GOODS_NAMES: dict[CharacterCode, str] = {
    CharacterCode.YEONWOO: "강연우의 정통 연애 사주",
    CharacterCode.DOYOON: "한도윤의 데이터 기반 연애분석",
}


def get_character_price(character: CharacterCode) -> int:
    if character not in _CHARACTER_PRICES_KRW:
        raise ValueError(f"가격이 정의되지 않은 캐릭터: {character}")
    return _CHARACTER_PRICES_KRW[character]


def get_character_goods_name(character: CharacterCode) -> str:
    if character not in _CHARACTER_GOODS_NAMES:
        raise ValueError(f"상품명이 정의되지 않은 캐릭터: {character}")
    return _CHARACTER_GOODS_NAMES[character]
