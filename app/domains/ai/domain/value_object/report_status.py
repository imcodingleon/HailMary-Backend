from enum import Enum


class ReportStatus(str, Enum):
    """유료 리포트 라이프사이클 상태."""

    PENDING = "pending"
    READY = "ready"
    EXPIRED = "expired"
