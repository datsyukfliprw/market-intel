import time

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.db.base import Base
from app.models.instrument import InstrumentAssetType
from app.models.mixins import AuditMixin
from app.models.scan_candidate import ScanCandidate
from app.models.scan_run import ScanRun
from app.schemas.instrument import InstrumentCreate, InstrumentUpdate
from app.services.instrument import InstrumentService


class _AuditTest(Base, AuditMixin):
    __tablename__ = "audit_tests"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    label: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )


def test_audit_mixin_populates_created_at_and_updated_at(
    session: Session,
) -> None:
    record = _AuditTest(label="first")

    session.add(record)
    session.commit()
    session.refresh(record)

    assert record.created_at is not None
    assert record.updated_at is not None
    assert record.created_at <= record.updated_at
    assert (record.updated_at - record.created_at).total_seconds() < 1


def test_audit_mixin_updated_at_changes_after_update(
    session: Session,
) -> None:
    record = _AuditTest(label="first")

    session.add(record)
    session.commit()
    session.refresh(record)

    original_updated_at = record.updated_at
    original_created_at = record.created_at

    time.sleep(0.01)

    record.label = "second"
    session.commit()
    session.refresh(record)

    assert record.updated_at > original_updated_at
    assert record.created_at == original_created_at


def test_instrument_audit_behavior_unchanged(
    session: Session,
) -> None:
    service = InstrumentService(session)

    instrument = service.create_instrument(
        InstrumentCreate(
            symbol="AAPL",
            name="Apple Inc.",
            exchange="NASDAQ",
            asset_type=InstrumentAssetType.STOCK,
        ),
    )

    created_at = instrument.created_at
    updated_at = instrument.updated_at

    time.sleep(0.01)

    updated = service.update_instrument(
        instrument.id,
        InstrumentUpdate(name="Apple Computer, Inc."),
    )

    assert updated.created_at == created_at
    assert updated.updated_at > updated_at


def test_excluded_models_do_not_have_audit_columns() -> None:
    assert not hasattr(ScanRun, "created_at")
    assert not hasattr(ScanRun, "updated_at")
    assert not hasattr(ScanCandidate, "created_at")
    assert not hasattr(ScanCandidate, "updated_at")
