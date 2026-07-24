from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.scan_run import ScanRunStatus


class ScanRunCreate(BaseModel):
    strategy_name: str = Field(
        min_length=1,
        max_length=100,
    )


class ScanRunComplete(BaseModel):
    candidates_found: int = Field(
        ge=0,
    )


class ScanRunFail(BaseModel):
    error_message: str = Field(
        min_length=1,
        max_length=2000,
    )


class ScanRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: ScanRunStatus
    strategy_name: str
    candidates_found: int
    error_message: str | None
    started_at: datetime
    completed_at: datetime | None
