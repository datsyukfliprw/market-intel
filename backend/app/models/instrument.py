from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.db.base import Base
from app.models.mixins import AuditMixin


class InstrumentAssetType(StrEnum):
    STOCK = "stock"
    ETF = "etf"
    ADR = "adr"


class Instrument(Base, AuditMixin):
    __tablename__ = "instruments"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    symbol: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
    )

    name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    exchange: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    asset_type: Mapped[InstrumentAssetType] = mapped_column(
        Enum(InstrumentAssetType, native_enum=False),
        nullable=False,
    )

    sector: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    industry: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    @validates("symbol", "currency")
    def _uppercase_strings(
        self,
        key: str,
        value: str,
    ) -> str:
        if value is None:
            return value
        return value.strip().upper()

    @validates("name", "exchange", "sector", "industry")
    def _strip_optional_strings(
        self,
        key: str,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None
        return value.strip()
