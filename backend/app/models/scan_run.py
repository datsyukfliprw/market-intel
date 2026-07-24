from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.scan_candidate import ScanCandidate


class ScanRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScanRun(Base):
    __tablename__ = "scan_runs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    status: Mapped[ScanRunStatus] = mapped_column(
        Enum(ScanRunStatus, native_enum=False),
        default=ScanRunStatus.PENDING,
        nullable=False,
    )

    strategy_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    candidates_found: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    candidates: Mapped[list["ScanCandidate"]] = relationship(
        back_populates="scan_run",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
