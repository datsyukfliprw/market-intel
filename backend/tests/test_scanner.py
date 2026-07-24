from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api import scan_runs as scan_runs_module
from app.models.instrument import Instrument, InstrumentAssetType
from app.models.scan_candidate import ScanCandidate
from app.models.scan_run import ScanRun, ScanRunStatus
from app.services.scan_run import InvalidScanRunTransitionError, ScanRunNotFoundError
from app.services.scanner import (
    AlphabeticalRanker,
    ConfigUniverseProvider,
    ScannerExecutionError,
    ScannerService,
    UniverseFilter,
    UniverseProvider,
)


def _create_instrument(
    session: Session,
    symbol: str,
    asset_type: InstrumentAssetType = InstrumentAssetType.STOCK,
    exchange: str = "NASDAQ",
    is_active: bool = True,
) -> Instrument:
    instrument = Instrument(
        symbol=symbol,
        asset_type=asset_type,
        exchange=exchange,
        is_active=is_active,
    )
    session.add(instrument)
    session.commit()
    return instrument


def _create_scan_run(
    session: Session, status: ScanRunStatus = ScanRunStatus.PENDING
) -> ScanRun:
    scan_run = ScanRun(
        strategy_name="test_scanner",
        status=status,
    )
    session.add(scan_run)
    session.commit()
    return scan_run


def test_config_universe_provider_returns_uppercase_symbols() -> None:
    provider = ConfigUniverseProvider(symbols=" aapl , msft, nvda ")

    assert provider.get_symbols() == ["AAPL", "MSFT", "NVDA"]


def test_config_universe_provider_returns_empty_list_for_empty_string() -> None:
    provider = ConfigUniverseProvider(symbols="")

    assert provider.get_symbols() == []


def test_universe_filter_accepts_active_us_stock() -> None:
    instrument = Instrument(
        symbol="AAPL",
        asset_type=InstrumentAssetType.STOCK,
        exchange="NASDAQ",
        is_active=True,
    )

    assert UniverseFilter().is_eligible(instrument) is True


def test_universe_filter_rejects_inactive_instrument() -> None:
    instrument = Instrument(
        symbol="AAPL",
        asset_type=InstrumentAssetType.STOCK,
        exchange="NASDAQ",
        is_active=False,
    )

    assert UniverseFilter().is_eligible(instrument) is False


def test_universe_filter_rejects_non_stock() -> None:
    instrument = Instrument(
        symbol="SPY",
        asset_type=InstrumentAssetType.ETF,
        exchange="NYSE",
        is_active=True,
    )

    assert UniverseFilter().is_eligible(instrument) is False


def test_universe_filter_rejects_non_us_exchange() -> None:
    instrument = Instrument(
        symbol="BARC",
        asset_type=InstrumentAssetType.STOCK,
        exchange="LSE",
        is_active=True,
    )

    assert UniverseFilter().is_eligible(instrument) is False


def test_alphabetical_ranker_orders_by_symbol_and_assigns_rank_only() -> None:
    instruments = [
        Instrument(symbol="MSFT", asset_type=InstrumentAssetType.STOCK),
        Instrument(symbol="AAPL", asset_type=InstrumentAssetType.STOCK),
    ]

    ranked = AlphabeticalRanker().rank(instruments)

    assert len(ranked) == 2
    assert ranked[0].instrument.symbol == "AAPL"
    assert ranked[0].rank == 1
    assert ranked[0].composite_score is None
    assert ranked[1].instrument.symbol == "MSFT"
    assert ranked[1].rank == 2
    assert ranked[1].composite_score is None


def test_scanner_service_executes_scan_and_persists_candidates(
    session: Session,
) -> None:
    scan_run = _create_scan_run(session)
    _create_instrument(session, "C")
    _create_instrument(session, "A")
    _create_instrument(session, "B")

    service = ScannerService(
        session,
        universe_provider=ConfigUniverseProvider(symbols="C,A,B"),
    )

    completed_run = service.execute(scan_run.id)

    assert completed_run.status == ScanRunStatus.COMPLETED
    assert completed_run.candidates_found == 3
    assert completed_run.completed_at is not None
    assert completed_run.error_message is None

    candidates = session.scalars(
        select(ScanCandidate)
        .where(ScanCandidate.scan_run_id == scan_run.id)
        .order_by(ScanCandidate.rank.asc())
    ).all()

    assert len(candidates) == 3
    assert [candidate.symbol for candidate in candidates] == ["A", "B", "C"]
    assert [candidate.rank for candidate in candidates] == [1, 2, 3]
    assert all(candidate.composite_score is None for candidate in candidates)


def test_scanner_created_candidates_have_rank_and_no_composite_score(
    session: Session,
) -> None:
    scan_run = _create_scan_run(session)
    _create_instrument(session, "AAPL")
    _create_instrument(session, "MSFT")

    service = ScannerService(
        session,
        universe_provider=ConfigUniverseProvider(symbols="MSFT,AAPL"),
    )

    service.execute(scan_run.id)

    candidates = session.scalars(
        select(ScanCandidate)
        .where(ScanCandidate.scan_run_id == scan_run.id)
        .order_by(ScanCandidate.rank.asc()),
    ).all()

    assert len(candidates) == 2
    assert [candidate.rank for candidate in candidates] == [1, 2]
    assert [candidate.symbol for candidate in candidates] == ["AAPL", "MSFT"]
    assert all(candidate.composite_score is None for candidate in candidates)


def test_scanner_service_skips_unknown_symbols(session: Session) -> None:
    scan_run = _create_scan_run(session)
    _create_instrument(session, "AAPL")

    service = ScannerService(
        session,
        universe_provider=ConfigUniverseProvider(symbols="AAPL,UNKNOWN,MSFT"),
    )

    completed_run = service.execute(scan_run.id)

    assert completed_run.candidates_found == 1

    candidate = session.scalar(
        select(ScanCandidate).where(ScanCandidate.scan_run_id == scan_run.id),
    )
    assert candidate is not None
    assert candidate.symbol == "AAPL"


def test_scanner_service_skips_ineligible_instruments(session: Session) -> None:
    scan_run = _create_scan_run(session)
    _create_instrument(session, "AAPL", is_active=True)
    _create_instrument(session, "INACTIVE", is_active=False)
    _create_instrument(session, "SPY", asset_type=InstrumentAssetType.ETF)
    _create_instrument(session, "BARC", exchange="LSE")

    service = ScannerService(
        session,
        universe_provider=ConfigUniverseProvider(symbols="AAPL,INACTIVE,SPY,BARC"),
    )

    completed_run = service.execute(scan_run.id)

    assert completed_run.candidates_found == 1

    candidate = session.scalar(
        select(ScanCandidate).where(ScanCandidate.scan_run_id == scan_run.id),
    )
    assert candidate is not None
    assert candidate.symbol == "AAPL"


def test_scanner_service_completes_with_empty_universe(session: Session) -> None:
    scan_run = _create_scan_run(session)

    service = ScannerService(
        session,
        universe_provider=ConfigUniverseProvider(symbols=""),
    )

    completed_run = service.execute(scan_run.id)

    assert completed_run.status == ScanRunStatus.COMPLETED
    assert completed_run.candidates_found == 0

    count = session.scalar(
        select(func.count()).select_from(ScanCandidate),
    )
    assert count == 0


def test_scanner_service_fails_and_marks_run_failed(session: Session) -> None:
    scan_run = _create_scan_run(session)

    class FaultyUniverseProvider(UniverseProvider):
        def get_symbols(self) -> list[str]:
            raise RuntimeError("boom")

    service = ScannerService(
        session,
        universe_provider=FaultyUniverseProvider(),
    )

    with pytest.raises(ScannerExecutionError):
        service.execute(scan_run.id)

    failed_run = session.get(ScanRun, scan_run.id)
    assert failed_run is not None
    assert failed_run.status == ScanRunStatus.FAILED
    assert failed_run.error_message == "boom"
    assert failed_run.completed_at is not None

    count = session.scalar(
        select(func.count()).select_from(ScanCandidate),
    )
    assert count == 0


def test_scanner_service_raises_not_found_for_missing_run(session: Session) -> None:
    service = ScannerService(
        session,
        universe_provider=ConfigUniverseProvider(symbols=""),
    )

    with pytest.raises(ScanRunNotFoundError):
        service.execute(uuid4())


def test_scanner_service_raises_invalid_transition_for_non_pending_run(
    session: Session,
) -> None:
    scan_run = _create_scan_run(session)
    scan_run.status = ScanRunStatus.RUNNING
    session.commit()

    service = ScannerService(
        session,
        universe_provider=ConfigUniverseProvider(symbols=""),
    )

    with pytest.raises(InvalidScanRunTransitionError):
        service.execute(scan_run.id)


def _create_instrument_via_api(client: TestClient, symbol: str) -> dict[str, Any]:
    response = client.post(
        "/instruments",
        json={
            "symbol": symbol,
            "asset_type": "stock",
            "exchange": "NASDAQ",
        },
    )
    assert response.status_code == 201
    return cast(dict[str, Any], response.json())


def _create_scan_run_via_api(client: TestClient) -> UUID:
    response = client.post(
        "/scan-runs",
        json={"strategy_name": "test_scanner"},
    )
    assert response.status_code == 201
    return UUID(cast(dict[str, Any], response.json())["id"])


def test_api_execute_scan_run(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    scan_run_id = _create_scan_run_via_api(client)
    instrument_a = _create_instrument_via_api(client, "A")
    _create_instrument_via_api(client, "B")
    _create_instrument_via_api(client, "C")

    def _get_scanner_service(session: Session) -> ScannerService:
        return ScannerService(
            session,
            universe_provider=ConfigUniverseProvider(symbols="C,A,B"),
        )

    monkeypatch.setattr(scan_runs_module, "get_scanner_service", _get_scanner_service)

    response = client.post(f"/scan-runs/{scan_run_id}/execute")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["candidates_found"] == 3
    assert body["error_message"] is None
    assert body["completed_at"] is not None

    candidates_response = client.get(f"/scan-runs/{scan_run_id}/candidates")
    assert candidates_response.status_code == 200
    candidates = candidates_response.json()
    assert len(candidates) == 3
    assert [candidate["symbol"] for candidate in candidates] == ["A", "B", "C"]
    assert candidates[0]["instrument_id"] == instrument_a["id"]


def test_api_execute_scan_run_not_found(client: TestClient) -> None:
    response = client.post(f"/scan-runs/{uuid4()}/execute")

    assert response.status_code == 404
    assert response.json() == {"detail": "Scan run not found"}


def test_api_execute_scan_run_invalid_transition(client: TestClient) -> None:
    scan_run_id = _create_scan_run_via_api(client)
    client.post(f"/scan-runs/{scan_run_id}/start")

    response = client.post(f"/scan-runs/{scan_run_id}/execute")

    assert response.status_code == 409
    assert response.json()["detail"] == "Only pending scan runs can be executed."


def test_api_execute_scan_run_internal_failure(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scan_run_id = _create_scan_run_via_api(client)

    class FaultyUniverseProvider(UniverseProvider):
        def get_symbols(self) -> list[str]:
            raise RuntimeError("provider failure")

    def _get_scanner_service(session: Session) -> ScannerService:
        return ScannerService(
            session,
            universe_provider=FaultyUniverseProvider(),
        )

    monkeypatch.setattr(scan_runs_module, "get_scanner_service", _get_scanner_service)

    response = client.post(f"/scan-runs/{scan_run_id}/execute")

    assert response.status_code == 500
    assert response.json()["detail"] == "provider failure"

    run_response = client.get(f"/scan-runs/{scan_run_id}")
    assert run_response.status_code == 200
    assert run_response.json()["status"] == "failed"
    assert run_response.json()["error_message"] == "provider failure"
