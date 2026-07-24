from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.instrument import Instrument, InstrumentAssetType
from app.repositories.instrument import (
    DuplicateInstrumentError,
    InstrumentRepository,
)
from app.schemas.instrument import InstrumentCreate, InstrumentUpdate
from app.services.instrument import InstrumentService


def _build_instrument(
    symbol: str = "AAPL",
    currency: str = "USD",
) -> Instrument:
    return Instrument(
        symbol=symbol,
        name="Apple Inc.",
        exchange="NASDAQ",
        asset_type=InstrumentAssetType.STOCK,
        sector="Technology",
        industry="Consumer Electronics",
        currency=currency,
    )


def test_model_uppercases_symbol_and_currency() -> None:
    instrument = _build_instrument(symbol="aapl", currency="usd")

    assert instrument.symbol == "AAPL"
    assert instrument.currency == "USD"


def test_repository_create_does_not_call_commit_or_rollback(
    session: Session,
) -> None:
    repository = InstrumentRepository(session)
    instrument = _build_instrument()

    with (
        patch.object(session, "commit") as mock_commit,
        patch.object(session, "rollback") as mock_rollback,
    ):
        repository.create(instrument)

    mock_commit.assert_not_called()
    mock_rollback.assert_not_called()

    session.rollback()


def test_repository_create_duplicate_does_not_rollback(
    session: Session,
) -> None:
    repository = InstrumentRepository(session)

    first = _build_instrument(symbol="AAPL")
    repository.create(first)
    session.commit()

    second = _build_instrument(symbol="AAPL")

    with (
        patch.object(session, "rollback") as mock_rollback,
        pytest.raises(DuplicateInstrumentError),
    ):
        repository.create(second)

    mock_rollback.assert_not_called()

    session.rollback()


def test_service_rolls_back_on_duplicate_and_session_is_usable(
    session: Session,
) -> None:
    service = InstrumentService(session)

    service.create_instrument(
        InstrumentCreate(
            symbol="AAPL",
            name="Apple Inc.",
            exchange="NASDAQ",
            asset_type=InstrumentAssetType.STOCK,
        ),
    )

    with pytest.raises(DuplicateInstrumentError):
        service.create_instrument(
            InstrumentCreate(
                symbol="aapl",
                name="Apple Inc.",
                exchange="NASDAQ",
                asset_type=InstrumentAssetType.STOCK,
            ),
        )

    instruments = (
        session.execute(
            select(Instrument),
        )
        .scalars()
        .all()
    )

    assert len(instruments) == 1
    assert instruments[0].symbol == "AAPL"


def test_created_at_and_updated_at_set_on_create(
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

    assert instrument.created_at is not None
    assert instrument.updated_at is not None
    assert instrument.created_at <= instrument.updated_at
    assert (instrument.updated_at - instrument.created_at).total_seconds() < 1


def test_updated_at_changes_on_update(
    session: Session,
) -> None:
    import time

    service = InstrumentService(session)

    instrument = service.create_instrument(
        InstrumentCreate(
            symbol="AAPL",
            name="Apple Inc.",
            exchange="NASDAQ",
            asset_type=InstrumentAssetType.STOCK,
        ),
    )

    original_updated_at = instrument.updated_at

    time.sleep(0.01)

    updated = service.update_instrument(
        instrument.id,
        InstrumentUpdate(name="Apple Computer, Inc."),
    )

    assert updated.updated_at > original_updated_at


def test_database_uniqueness_enforces_symbol(
    session: Session,
) -> None:
    repository = InstrumentRepository(session)

    first = _build_instrument(symbol="AAPL")
    repository.create(first)
    session.commit()

    second = _build_instrument(symbol="AAPL")

    with pytest.raises(DuplicateInstrumentError):
        repository.create(second)

    session.rollback()
