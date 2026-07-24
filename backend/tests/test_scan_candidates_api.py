from typing import Any, cast
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.instrument import Instrument
from app.models.scan_candidate import ScanCandidate


def create_instrument(
    client: TestClient,
    symbol: str,
) -> dict[str, Any]:
    response = client.post(
        "/instruments",
        json={
            "symbol": symbol,
            "asset_type": "stock",
        },
    )

    assert response.status_code == 201

    return cast(dict[str, Any], response.json())


def create_running_scan_run(
    client: TestClient,
) -> str:
    create_response = client.post(
        "/scan-runs",
        json={
            "strategy_name": "momentum_breakout",
        },
    )

    assert create_response.status_code == 201

    scan_run_id = str(create_response.json()["id"])

    start_response = client.post(
        f"/scan-runs/{scan_run_id}/start",
    )

    assert start_response.status_code == 200

    return scan_run_id


def test_create_scan_candidate(
    client: TestClient,
) -> None:
    scan_run_id = create_running_scan_run(client)
    instrument = create_instrument(client, "AAPL")

    response = client.post(
        f"/scan-runs/{scan_run_id}/candidates",
        json={
            "symbol": "aapl",
            "rank": 1,
            "composite_score": 91.5,
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["scan_run_id"] == scan_run_id
    assert body["instrument_id"] == instrument["id"]
    assert body["symbol"] == "AAPL"
    assert body["rank"] == 1
    assert body["composite_score"] == 91.5
    assert body["discovered_at"] is not None


def test_list_scan_candidates(
    client: TestClient,
) -> None:
    scan_run_id = create_running_scan_run(client)
    create_instrument(client, "MSFT")
    create_instrument(client, "AAPL")

    client.post(
        f"/scan-runs/{scan_run_id}/candidates",
        json={
            "symbol": "MSFT",
            "rank": 2,
            "composite_score": 85.0,
        },
    )

    client.post(
        f"/scan-runs/{scan_run_id}/candidates",
        json={
            "symbol": "AAPL",
            "rank": 1,
            "composite_score": 92.0,
        },
    )

    response = client.get(
        f"/scan-runs/{scan_run_id}/candidates",
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert body[0]["symbol"] == "AAPL"
    assert body[0]["rank"] == 1
    assert body[1]["symbol"] == "MSFT"
    assert body[1]["rank"] == 2


def test_get_scan_candidate(
    client: TestClient,
) -> None:
    scan_run_id = create_running_scan_run(client)
    create_instrument(client, "NVDA")

    create_response = client.post(
        f"/scan-runs/{scan_run_id}/candidates",
        json={
            "symbol": "NVDA",
            "rank": 1,
            "composite_score": 94.2,
        },
    )

    candidate_id = create_response.json()["id"]

    response = client.get(
        f"/scan-candidates/{candidate_id}",
    )

    assert response.status_code == 200
    assert response.json()["id"] == candidate_id
    assert response.json()["symbol"] == "NVDA"


def test_cannot_add_candidate_to_pending_scan(
    client: TestClient,
) -> None:
    create_response = client.post(
        "/scan-runs",
        json={
            "strategy_name": "momentum_breakout",
        },
    )

    scan_run_id = create_response.json()["id"]

    response = client.post(
        f"/scan-runs/{scan_run_id}/candidates",
        json={
            "symbol": "AAPL",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": ("Candidates can only be added to running scan runs."),
    }


def test_rejects_duplicate_candidate_symbol(
    client: TestClient,
) -> None:
    scan_run_id = create_running_scan_run(client)
    create_instrument(client, "AAPL")

    first_response = client.post(
        f"/scan-runs/{scan_run_id}/candidates",
        json={
            "symbol": "AAPL",
        },
    )

    second_response = client.post(
        f"/scan-runs/{scan_run_id}/candidates",
        json={
            "symbol": "aapl",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": ("Candidate already exists for this scan run"),
    }


def test_same_symbol_allowed_in_different_scans(
    client: TestClient,
) -> None:
    first_scan_id = create_running_scan_run(client)
    second_scan_id = create_running_scan_run(client)
    create_instrument(client, "AAPL")

    first_response = client.post(
        f"/scan-runs/{first_scan_id}/candidates",
        json={
            "symbol": "AAPL",
        },
    )

    second_response = client.post(
        f"/scan-runs/{second_scan_id}/candidates",
        json={
            "symbol": "AAPL",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201


def test_missing_scan_run_returns_404(
    client: TestClient,
) -> None:
    response = client.post(
        f"/scan-runs/{uuid4()}/candidates",
        json={
            "symbol": "AAPL",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Scan run not found",
    }


def test_missing_candidate_returns_404(
    client: TestClient,
) -> None:
    response = client.get(
        f"/scan-candidates/{uuid4()}",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Scan candidate not found",
    }


def test_rejects_invalid_candidate_score(
    client: TestClient,
) -> None:
    scan_run_id = create_running_scan_run(client)
    create_instrument(client, "AAPL")

    response = client.post(
        f"/scan-runs/{scan_run_id}/candidates",
        json={
            "symbol": "AAPL",
            "composite_score": 101,
        },
    )

    assert response.status_code == 422


def test_rejects_invalid_candidate_rank(
    client: TestClient,
) -> None:
    scan_run_id = create_running_scan_run(client)
    create_instrument(client, "AAPL")

    response = client.post(
        f"/scan-runs/{scan_run_id}/candidates",
        json={
            "symbol": "AAPL",
            "rank": 0,
        },
    )

    assert response.status_code == 422


def test_rejects_candidate_for_unknown_symbol(
    client: TestClient,
    session: Session,
) -> None:
    scan_run_id = create_running_scan_run(client)

    response = client.post(
        f"/scan-runs/{scan_run_id}/candidates",
        json={
            "symbol": "UNKNOWN",
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "No canonical instrument found for symbol",
    }

    scan_candidate_count = session.scalar(
        select(func.count()).select_from(ScanCandidate),
    )
    assert scan_candidate_count == 0

    instrument_count = session.scalar(
        select(func.count()).select_from(Instrument),
    )
    assert instrument_count == 0

    instrument = create_instrument(client, "AAPL")
    success_response = client.post(
        f"/scan-runs/{scan_run_id}/candidates",
        json={
            "symbol": "aapl",
        },
    )

    assert success_response.status_code == 201
    body = success_response.json()
    assert body["symbol"] == "AAPL"
    assert body["instrument_id"] == instrument["id"]


def test_accepts_symbol_between_11_and_20_characters(
    client: TestClient,
) -> None:
    scan_run_id = create_running_scan_run(client)
    long_symbol = "A" * 20
    instrument = create_instrument(client, long_symbol)

    response = client.post(
        f"/scan-runs/{scan_run_id}/candidates",
        json={
            "symbol": long_symbol,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["symbol"] == long_symbol
    assert body["instrument_id"] == instrument["id"]
