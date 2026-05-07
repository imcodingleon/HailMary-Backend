from app.domains.ai.domain.entity.paid_report import PaidReport
from app.domains.ai.infrastructure.orm.paid_report_orm import PaidReportORM


class PaidReportMapper:
    @staticmethod
    def to_orm(entity: PaidReport) -> PaidReportORM:
        return PaidReportORM(
            order_id=entity.order_id,
            saju_hash=entity.saju_hash,
            status=entity.status,
            chapters=dict(entity.chapters),
        )

    @staticmethod
    def to_entity(orm: PaidReportORM) -> PaidReport:
        return PaidReport(
            order_id=orm.order_id,
            saju_hash=orm.saju_hash,
            status=orm.status,
            chapters=dict(orm.chapters or {}),
            created_at=orm.created_at,
        )
