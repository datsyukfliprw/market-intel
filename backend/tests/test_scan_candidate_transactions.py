from unittest.mock import patch

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.instrument import Instrument
from app.models.scan_candidate import ScanCandidate
from app.models.scan_run import ScanRun, ScanRunStatus
from app.repositories.scan_candidate import (
    DuplicateScanCandidateError,
    ScanCandidateRepository,
)
from app.schemas.instrument import InstrumentCreate
from app.schemas.scan_candidate import ScanCandidateCreate
from app.schemas.scan_run import ScanRunCreate
from app.services.instrument import InstrumentService
from app.services.scan_candidate import (
    ScanCandidateService,
    ScanCandidateSymbolNotFoundError,
)
from app.services.scan_run import ScanRunService


def _create_running_scan_run(session: Session) -> ScanRun:
    scan_run_service = ScanRunService(session)
    scan_run = scan_run_service.create_scan_run(ScanRunCreate(strategy_name="test"))
    return scan_run_service.start_scan_run(scan_run.id)


def _create_instrument(session: Session, symbol: str) -> None:
    instrument_service = InstrumentService(session)
    instrument_service.create_instrument(
        InstrumentCreate(
            symbol=symbol,
            asset_type="stock",
        ),
    )


def test_service_raises_duplicate_scan_candidate_error(
    session: Session,
) -> None:
    scan_run = _create_running_scan_run(session)
    _create_instrument(session, "AAPL")
    service = ScanCandidateService(session)

    service.create_candidate(
        scan_run.id,
        ScanCandidateCreate(symbol="AAPL"),
    )

    with pytest.raises(DuplicateScanCandidateError):
        service.create_candidate(
            scan_run.id,
            ScanCandidateCreate(symbol="AAPL"),
        )


def test_session_usable_after_duplicate_candidate_failure(
    session: Session,
) -> None:
    scan_run = _create_running_scan_run(session)
    _create_instrument(session, "AAPL")
    service = ScanCandidateService(session)

    service.create_candidate(
        scan_run.id,
        ScanCandidateCreate(symbol="AAPL"),
    )

    with pytest.raises(DuplicateScanCandidateError):
        service.create_candidate(
            scan_run.id,
            ScanCandidateCreate(symbol="AAPL"),
        )

    result = session.execute(
        select(ScanRun).where(ScanRun.id == scan_run.id),
    ).scalar_one()

    assert result.id == scan_run.id
    assert result.status == ScanRunStatus.RUNNING


def test_repository_create_does_not_call_commit_or_rollback(
    session: Session,
) -> None:
    scan_run = _create_running_scan_run(session)
    repository = ScanCandidateRepository(session)

    with (
        patch.object(session, "commit") as mock_commit,
        patch.object(session, "rollback") as mock_rollback,
    ):
        repository.create(
            scan_run_id=scan_run.id,
            symbol="AAPL",
        )

    mock_commit.assert_not_called()
    mock_rollback.assert_not_called()

    session.rollback()


def test_repository_create_duplicate_does_not_rollback(
    session: Session,
) -> None:
    scan_run = _create_running_scan_run(session)
    repository = ScanCandidateRepository(session)

    repository.create(
        scan_run_id=scan_run.id,
        symbol="AAPL",
    )
    session.commit()

    with (
        patch.object(session, "rollback") as mock_rollback,
        pytest.raises(DuplicateScanCandidateError),
    ):
        repository.create(
            scan_run_id=scan_run.id,
            symbol="AAPL",
        )

    mock_rollback.assert_not_called()

    session.rollback()


def test_service_rolls_back_on_duplicate_and_session_is_usable(
    session: Session,
) -> None:
    scan_run = _create_running_scan_run(session)
    _create_instrument(session, "AAPL")
    service = ScanCandidateService(session)

    service.create_candidate(
        scan_run.id,
        ScanCandidateCreate(symbol="AAPL"),
    )

    with pytest.raises(DuplicateScanCandidateError):
        service.create_candidate(
            scan_run.id,
            ScanCandidateCreate(symbol="AAPL"),
        )

    # The session must remain usable for new queries after the service
    # cleaned up the failed transaction.
    candidates = (
        session.execute(
            select(ScanCandidate).where(
                ScanCandidate.scan_run_id == scan_run.id,
            ),
        )
        .scalars()
        .all()
    )

    assert len(candidates) == 1
    assert candidates[0].symbol == "AAPL"


def test_scan_candidate_symbol_is_uppercased_at_model_level(
    session: Session,
) -> None:
    scan_run = _create_running_scan_run(session)

    candidate = ScanCandidate(
        scan_run_id=scan_run.id,
        symbol=" aapl ",
    )

    session.add(candidate)
    session.flush()

    assert candidate.symbol == "AAPL"


def test_session_usable_after_unknown_symbol_failure(
    session: Session,
) -> None:
    scan_run = _create_running_scan_run(session)
    service = ScanCandidateService(session)

    with pytest.raises(ScanCandidateSymbolNotFoundError):
        service.create_candidate(
            scan_run.id,
            ScanCandidateCreate(symbol="UNKNOWN"),
        )

    scan_candidate_count = session.scalar(
        select(func.count()).select_from(ScanCandidate),
    )
    assert scan_candidate_count == 0

    instrument_count = session.scalar(
        select(func.count()).select_from(Instrument),
    )
    assert instrument_count == 0

    _create_instrument(session, "AAPL")
    candidate = service.create_candidate(
        scan_run.id,
        ScanCandidateCreate(symbol="AAPL"),
    )

    assert candidate.symbol == "AAPL"
    assert candidate.instrument_id is not None


def test_can_read_legacy_candidate_with_null_instrument_id(
    session: Session,
) -> None:
    scan_run = _create_running_scan_run(session)

    candidate = ScanCandidate(
        scan_run_id=scan_run.id,
        symbol="AAPL",
    )
    session.add(candidate)
    session.commit()

    repository = ScanCandidateRepository(session)
    retrieved = repository.get_by_id(candidate.id)

    assert retrieved is not None
    assert retrieved.instrument_id is None
    assert retrieved.symbol == "AAPL"
