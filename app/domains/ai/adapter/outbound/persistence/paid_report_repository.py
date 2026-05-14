from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.ai.domain.entity.paid_report import PaidReport
from app.domains.ai.domain.port.paid_report_repository_port import (
    PaidReportRepositoryPort,
)
from app.domains.ai.domain.value_object.report_status import ReportStatus
from app.domains.ai.infrastructure.mapper.paid_report_mapper import PaidReportMapper
from app.domains.ai.infrastructure.orm.paid_report_orm import PaidReportORM


class PaidReportRepository(PaidReportRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, report: PaidReport) -> PaidReport:
        orm = await self._session.get(PaidReportORM, report.order_id)
        if orm is None:
            orm = PaidReportMapper.to_orm(report)
            self._session.add(orm)
        else:
            orm.saju_hash = report.saju_hash
            orm.status = report.status
            orm.chapters = dict(report.chapters)
            # share_code는 PK처럼 한 번 정해지면 안 바꿈 (UUID 충돌 시에만 재생성)
        await self._session.flush()
        # created_at은 server_default(func.now())로 설정되므로 refresh 필수.
        await self._session.refresh(orm)
        return PaidReportMapper.to_entity(orm)

    async def find_by_order_id(self, order_id: str) -> PaidReport | None:
        orm = await self._session.get(PaidReportORM, order_id)
        return PaidReportMapper.to_entity(orm) if orm else None

    async def find_ready_by_saju_hash(self, saju_hash: str) -> PaidReport | None:
        result = await self._session.execute(
            select(PaidReportORM)
            .where(PaidReportORM.saju_hash == saju_hash)
            .where(PaidReportORM.status == ReportStatus.READY)
            .limit(1)
        )
        orm = result.scalar_one_or_none()
        return PaidReportMapper.to_entity(orm) if orm else None

    async def find_by_share_code(self, share_code: str) -> PaidReport | None:
        """이메일 링크에서 재접속용 — share_code (UUID4 hex)로 조회."""
        result = await self._session.execute(
            select(PaidReportORM)
            .where(PaidReportORM.share_code == share_code)
            .limit(1)
        )
        orm = result.scalar_one_or_none()
        return PaidReportMapper.to_entity(orm) if orm else None
