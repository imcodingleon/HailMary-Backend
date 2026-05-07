from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.user.domain.entity.user import User
from app.domains.user.infrastructure.mapper.user_mapper import UserMapper
from app.domains.user.infrastructure.orm.user_orm import UserORM


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, user: User) -> User:
        orm = UserMapper.to_orm(user)
        self._session.add(orm)
        await self._session.flush()
        await self._session.refresh(orm)
        return UserMapper.to_entity(orm)

    async def find_by_id(self, user_id: int) -> User | None:
        result = await self._session.execute(select(UserORM).where(UserORM.id == user_id))
        orm = result.scalar_one_or_none()
        return UserMapper.to_entity(orm) if orm else None

    async def find_by_session_token(self, token: str) -> User | None:
        result = await self._session.execute(select(UserORM).where(UserORM.session_token == token))
        orm = result.scalar_one_or_none()
        return UserMapper.to_entity(orm) if orm else None
