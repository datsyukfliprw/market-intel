from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    UniqueConstraint,
    event,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.scan_candidate import ScanCandidate


class ImmutableRecordError(RuntimeError):
    """Raised when application code tries to mutate frozen evidence."""


def _utcnow() -> datetime:
    return datetime.now(UTC)


class PennyCandidateSnapshot(Base):
    """One immutable, scored point-in-time record for a scan candidate."""

    __tablename__ = "penny_candidate_snapshots"
    __table_args__ = (
        Index("ix_penny_snapshots_symbol_score", "symbol", "score"),
        Index(
            "ix_penny_snapshots_classification_captured",
            "classification",
            "captured_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    candidate_id: Mapped[UUID] = mapped_column(
        ForeignKey("scan_candidates.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
        index=True,
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    scoring_version: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    classification: Mapped[str] = mapped_column(String(50), nullable=False)
    complete_gate_passed: Mapped[bool] = mapped_column(nullable=False)

    features_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    score_result_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    trade_plan_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    research_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    provenance_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    candidate: Mapped["ScanCandidate"] = relationship("ScanCandidate")
    observations: Mapped[list[PennyMarketObservation]] = relationship(
        back_populates="snapshot",
        passive_deletes=True,
        order_by="PennyMarketObservation.observed_at",
    )
    evaluations: Mapped[list[PennyOutcomeEvaluation]] = relationship(
        back_populates="snapshot",
        passive_deletes=True,
        order_by="PennyOutcomeEvaluation.created_at",
    )


class PennyMarketObservation(Base):
    """Append-only normalized OHLC evidence collected after a snapshot."""

    __tablename__ = "penny_market_observations"
    __table_args__ = (
        UniqueConstraint(
            "snapshot_id",
            "observed_at",
            "source",
            name="uq_penny_observation_snapshot_time_source",
        ),
        Index(
            "ix_penny_observation_snapshot_time",
            "snapshot_id",
            "observed_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    snapshot_id: Mapped[UUID] = mapped_column(
        ForeignKey("penny_candidate_snapshots.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    provenance: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    snapshot: Mapped[PennyCandidateSnapshot] = relationship(
        back_populates="observations"
    )


class PennyOutcomeEvaluation(Base):
    """Append-only derived evaluation for a specific observation set."""

    __tablename__ = "penny_outcome_evaluations"
    __table_args__ = (
        UniqueConstraint(
            "snapshot_id",
            "calculator_version",
            "observation_digest",
            name="uq_penny_evaluation_input_digest",
        ),
        Index(
            "ix_penny_evaluation_snapshot_created",
            "snapshot_id",
            "created_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    snapshot_id: Mapped[UUID] = mapped_column(
        ForeignKey("penny_candidate_snapshots.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    calculator_version: Mapped[str] = mapped_column(String(100), nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    observation_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    observation_count: Mapped[int] = mapped_column(Integer, nullable=False)
    result_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    snapshot: Mapped[PennyCandidateSnapshot] = relationship(
        back_populates="evaluations"
    )


def _reject_change(mapper: object, connection: object, target: object) -> None:
    raise ImmutableRecordError(
        f"{type(target).__name__} is immutable; append a new record instead"
    )


for _model in (
    PennyCandidateSnapshot,
    PennyMarketObservation,
    PennyOutcomeEvaluation,
):
    event.listen(_model, "before_update", _reject_change)
    event.listen(_model, "before_delete", _reject_change)
