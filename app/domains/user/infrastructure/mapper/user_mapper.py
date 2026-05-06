from app.domains.user.domain.entity.user import User
from app.domains.user.domain.value_object.birth_info import BirthInfo
from app.domains.user.infrastructure.orm.user_orm import UserORM


class UserMapper:
    @staticmethod
    def to_orm(entity: User) -> UserORM:
        return UserORM(
            id=entity.id,
            gender=entity.gender,
            birth_date=entity.birth_info.birth_date,
            calendar_type=entity.birth_info.calendar_type,
            birth_time=entity.birth_info.birth_time,
            birth_time_unknown=entity.birth_info.birth_time_unknown,
            name=entity.name,
            session_token=entity.session_token,
            character_id=entity.character_id,
        )

    @staticmethod
    def to_entity(orm: UserORM) -> User:
        birth_info = BirthInfo(
            birth_date=orm.birth_date,
            calendar_type=orm.calendar_type,
            birth_time=orm.birth_time,
            birth_time_unknown=orm.birth_time_unknown,
        )
        return User(
            id=orm.id,
            birth_info=birth_info,
            gender=orm.gender,
            name=orm.name,
            session_token=orm.session_token,
            character_id=orm.character_id,
            created_at=orm.created_at,
        )
