from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.instrument import Instrument
    from app.models.scan_run import ScanRun


class ScanCandidate(Base):
    __tablename__ = "scan_candidates"
    __table_args__ = (
        UniqueConstraint(
            "scan_run_id",
            "symbol",
            name="uq_scan_candidates_scan_run_symbol",
        ),
        UniqueConstraint(
            "scan_run_id",
            "instrument_id",
            name="uq_scan_candidates_scan_run_instrument",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    scan_run_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "scan_runs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    symbol: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    instrument_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "instruments.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    rank: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    composite_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    scan_run: Mapped["ScanRun"] = relationship(
        back_populates="candidates",
    )

    instrument: Mapped["Instrument"] = relationship(
        "Instrument",
    )

    @validates("symbol")
    def _uppercase_symbol(
        self,
        key: str,
        value: str,
    ) -> str:
        return value.strip().upper()
