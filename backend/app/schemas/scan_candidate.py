from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ScanCandidateCreate(BaseModel):
    symbol: str = Field(
        min_length=1,
        max_length=10,
    )

    rank: int | None = Field(
        default=None,
        ge=1,
    )

    composite_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return value.strip().upper()


class ScanCandidateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    scan_run_id: UUID
    symbol: str
    rank: int | None
    composite_score: float | None
    discovered_at: datetime
