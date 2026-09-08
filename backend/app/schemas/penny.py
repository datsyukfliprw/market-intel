from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.analytics import PerformanceSummary
from app.domain.outcomes import LongTradePlan, OutcomeResult, PriceObservation
from app.domain.scoring import PennyFeatures, PennyScoreResult


class EvidenceKind(StrEnum):
    QUOTE = "quote"
    CHART = "chart"
    NEWS = "news"
    FILING = "filing"
    FINANCIALS = "financials"
    PROFILE = "profile"
    OTHER = "other"


class EvidenceReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source: str = Field(min_length=1, max_length=100)
    kind: EvidenceKind = EvidenceKind.OTHER
    observed_at: datetime | None = None
    reference: str = Field(min_length=1, max_length=2000)
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("source")
    @classmethod
    def normalize_source(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("source cannot be blank")
        return normalized

    @field_validator("observed_at")
    @classmethod
    def normalize_timestamp(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        return value.astimezone(UTC)


class PennyResearchContext(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    catalyst_summary: str | None = Field(default=None, max_length=4000)
    thesis: str | None = Field(default=None, max_length=4000)
    strongest_counterevidence: str | None = Field(default=None, max_length=4000)
    financing_notes: str | None = Field(default=None, max_length=4000)
    execution_notes: str | None = Field(default=None, max_length=4000)
    limitations: tuple[str, ...] = Field(default=(), max_length=50)


class PennyScoreRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    features: PennyFeatures
    trade_plan: LongTradePlan | None = None


class PennyOutcomeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trade_plan: LongTradePlan
    observations: tuple[PriceObservation, ...] = Field(
        min_length=1,
        max_length=10_000,
    )


class PennySnapshotCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    captured_at: datetime
    features: PennyFeatures
    trade_plan: LongTradePlan | None = None
    research: PennyResearchContext = Field(default_factory=PennyResearchContext)
    provenance: tuple[EvidenceReference, ...] = Field(default=(), max_length=250)

    @field_validator("captured_at")
    @classmethod
    def normalize_captured_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("captured_at must be timezone-aware")
        return value.astimezone(UTC)


class PennySnapshotRead(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: UUID
    candidate_id: UUID
    symbol: str
    captured_at: datetime
    created_at: datetime
    scoring_version: str
    score: float
    classification: str
    complete_gate_passed: bool
    features: PennyFeatures
    score_result: PennyScoreResult
    trade_plan: LongTradePlan | None
    research: PennyResearchContext
    provenance: tuple[EvidenceReference, ...]
    snapshot_hash: str
    integrity_valid: bool


class PennyObservationBatchCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observations: tuple[PriceObservation, ...] = Field(
        min_length=1,
        max_length=500,
    )


class PennyObservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid", frozen=True)

    id: UUID
    snapshot_id: UUID
    observed_at: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int | None
    source: str
    provenance: str | None
    created_at: datetime


class PennyStoredEvaluationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str | None = Field(default=None, min_length=1, max_length=100)

    @field_validator("source")
    @classmethod
    def normalize_source(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("source cannot be blank")
        return normalized


class PennyEvaluationRead(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: UUID
    snapshot_id: UUID
    calculator_version: str
    source: str
    observation_digest: str
    observation_count: int
    result: OutcomeResult
    created_at: datetime


class PennySnapshotList(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    items: tuple[PennySnapshotRead, ...]


class PennyPerformanceRead(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    scoring_version: str | None
    source: str | None
    latest_evaluation_only: bool = True
    summary: PerformanceSummary
