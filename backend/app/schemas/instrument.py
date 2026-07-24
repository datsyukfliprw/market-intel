from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.instrument import InstrumentAssetType


class InstrumentCreate(BaseModel):
    symbol: str = Field(
        min_length=1,
        max_length=20,
    )

    name: str | None = None
    exchange: str | None = None
    asset_type: InstrumentAssetType
    sector: str | None = None
    industry: str | None = None
    currency: str = Field(
        default="USD",
        min_length=3,
        max_length=3,
    )

    @model_validator(mode="before")
    @classmethod
    def _normalize_fields(cls, data: dict[str, Any]) -> Any:
        if not isinstance(data, dict):
            return data

        upper_keys = {"symbol", "currency"}
        strip_keys = {"symbol", "name", "exchange", "sector", "industry", "currency"}

        for key, value in data.items():
            if not isinstance(value, str):
                continue
            if key in strip_keys:
                value = value.strip()
            if key in upper_keys:
                value = value.upper()
            data[key] = value

        return data


class InstrumentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    exchange: str | None = None
    asset_type: InstrumentAssetType | None = None
    sector: str | None = None
    industry: str | None = None
    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )
    is_active: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def _normalize_fields(cls, data: dict[str, Any]) -> Any:
        if not isinstance(data, dict):
            return data

        upper_keys = {"currency"}
        strip_keys = {"name", "exchange", "sector", "industry", "currency"}

        for key, value in data.items():
            if not isinstance(value, str):
                continue
            if key in strip_keys:
                value = value.strip()
            if key in upper_keys:
                value = value.upper()
            data[key] = value

        return data


class InstrumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    symbol: str
    name: str | None
    exchange: str | None
    asset_type: InstrumentAssetType
    sector: str | None
    industry: str | None
    currency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
