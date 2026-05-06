from app.domains.payment.infrastructure.orm.payment_orm import PaymentORM  # noqa: F401
from app.domains.user.infrastructure.orm.saju_result_orm import SajuResultORM  # noqa: F401
from app.domains.user.infrastructure.orm.survey_orm import SurveyORM  # noqa: F401

# Alembic이 모든 테이블을 자동 탐색할 수 있도록 ORM 모델을 import한다.
from app.domains.user.infrastructure.orm.user_orm import UserORM  # noqa: F401
from app.infrastructure.database.session import Base

__all__ = ["Base"]
