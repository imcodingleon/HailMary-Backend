from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime

from app.domains.auth.application.request.social_login_request import SocialLoginRequest
from app.domains.auth.application.response.account_profile_response import (
    AccountProfileResponse,
)
from app.domains.auth.application.response.social_login_response import (
    SocialLoginResponse,
)
from app.domains.auth.domain.entity.account import Account
from app.domains.auth.domain.port.account_repository_port import (
    AccountAlreadyExistsError,
    AccountRepositoryPort,
)
from app.domains.auth.domain.port.oauth_client_port import OAuthClientPort
from app.domains.auth.domain.port.signup_bonus_port import SignupBonusPort
from app.domains.auth.domain.port.token_port import TokenIssuerPort
from app.domains.auth.domain.value_object.oauth_profile import OAuthProfile
from app.domains.auth.domain.value_object.provider import Provider


class UnsupportedProviderError(Exception):
    """해당 provider의 OAuth 클라이언트가 설정되지 않음 (환경변수 미설정 포함)."""


class SocialLoginUseCase:
    """소셜 로그인: code 교환 → 계정 upsert → JWT 발급.

    과거(비로그인) 결제의 이메일 매칭 귀속은 의도적으로 하지 않는다 —
    customer_email이 무인증 /update-email로 변조 가능해 타인 결제 탈취 경로가 되기 때문.
    보관함의 연우/도윤은 '로그인 후 결제'한 건만(결제 시점 account_id 직접 연결, P7).
    """

    def __init__(
        self,
        *,
        oauth_clients: Mapping[Provider, OAuthClientPort],
        account_repo: AccountRepositoryPort,
        token_issuer: TokenIssuerPort,
        signup_bonus: SignupBonusPort | None = None,
    ) -> None:
        self._oauth_clients = oauth_clients
        self._account_repo = account_repo
        self._token_issuer = token_issuer
        self._signup_bonus = signup_bonus

    async def execute(self, request: SocialLoginRequest) -> SocialLoginResponse:
        client = self._oauth_clients.get(request.provider)
        if client is None:
            raise UnsupportedProviderError(
                f"지원하지 않거나 설정되지 않은 provider: {request.provider.value}"
            )

        profile = await client.fetch_profile(
            code=request.code, redirect_uri=request.redirect_uri
        )

        existing = await self._account_repo.find_by_provider_user(
            profile.provider, profile.provider_user_id
        )
        now = datetime.now(UTC)

        if existing is None:
            try:
                account = await self._account_repo.save(
                    Account(
                        provider=profile.provider,
                        provider_user_id=profile.provider_user_id,
                        email=profile.email,
                        email_verified=profile.email_verified,
                        nickname=profile.nickname,
                        profile_image_url=profile.profile_image_url,
                        last_login_at=now,
                    )
                )
                is_new_account = True
            except AccountAlreadyExistsError:
                # 동시 첫 로그인 레이스 — 다른 요청이 먼저 INSERT. 재조회 후 update로 합류.
                account = await self._refetch_and_update(profile, now)
                is_new_account = False
        else:
            self._refresh_profile(existing, profile, now)
            account = await self._account_repo.update(existing)
            is_new_account = False

        if account.id is None:  # repository save/update 계약 위반 — 방어
            raise RuntimeError("계정 저장 후 id가 없습니다")

        if is_new_account and self._signup_bonus is not None:
            await self._signup_bonus.grant(account.id)

        return SocialLoginResponse(
            access_token=self._token_issuer.issue(account.id),
            is_new_account=is_new_account,
            profile=AccountProfileResponse.from_account(account),
        )

    async def _refetch_and_update(
        self, profile: OAuthProfile, now: datetime
    ) -> Account:
        """레이스 패자 경로 — 승자가 만든 계정을 재조회해 프로필 최신화 후 반환."""
        account = await self._account_repo.find_by_provider_user(
            profile.provider, profile.provider_user_id
        )
        if account is None:
            # UNIQUE 충돌 직후인데 재조회가 비어있다 — 정합성 위반, 방어적 실패.
            raise RuntimeError("계정 생성 충돌 후 재조회 실패")
        self._refresh_profile(account, profile, now)
        return await self._account_repo.update(account)

    @staticmethod
    def _refresh_profile(account: Account, profile: OAuthProfile, now: datetime) -> None:
        """재로그인 시 제공자 프로필 최신화. last_used는 건드리지 않는다.

        이메일 동의 철회 등으로 None이 내려오면 기존 프로필 값을 유지한다 (불필요한 소실 방지).
        """
        if profile.email:
            account.email = profile.email
            account.email_verified = profile.email_verified
        if profile.nickname:
            account.nickname = profile.nickname
        if profile.profile_image_url:
            account.profile_image_url = profile.profile_image_url
        account.last_login_at = now
