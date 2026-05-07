from abc import ABC, abstractmethod

from app.domains.ai.domain.entity.paid_report import PaidReport


class PaidReportRepositoryPort(ABC):
    @abstractmethod
    async def save(self, report: PaidReport) -> PaidReport: ...

    @abstractmethod
    async def find_by_order_id(self, order_id: str) -> PaidReport | None: ...

    @abstractmethod
    async def find_ready_by_saju_hash(self, saju_hash: str) -> PaidReport | None: ...
