from uuid import uuid4

from fastapi.testclient import TestClient


def test_start_scan_run(
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
        f"/scan-runs/{scan_run_id}/start",
    )

    assert response.status_code == 200
    assert response.json()["status"] == "running"
    assert response.json()["completed_at"] is None


def test_complete_scan_run(
    client: TestClient,
) -> None:
    create_response = client.post(
        "/scan-runs",
        json={
            "strategy_name": "momentum_breakout",
        },
    )

    scan_run_id = create_response.json()["id"]

    start_response = client.post(
        f"/scan-runs/{scan_run_id}/start",
    )

    assert start_response.status_code == 200

    response = client.post(
        f"/scan-runs/{scan_run_id}/complete",
        json={
            "candidates_found": 14,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["candidates_found"] == 14
    assert response.json()["error_message"] is None
    assert response.json()["completed_at"] is not None


def test_fail_scan_run(
    client: TestClient,
) -> None:
    create_response = client.post(
        "/scan-runs",
        json={
            "strategy_name": "momentum_breakout",
        },
    )

    scan_run_id = create_response.json()["id"]

    start_response = client.post(
        f"/scan-runs/{scan_run_id}/start",
    )

    assert start_response.status_code == 200

    response = client.post(
        f"/scan-runs/{scan_run_id}/fail",
        json={
            "error_message": ("Market data provider unavailable."),
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "failed"
    assert response.json()["error_message"] == ("Market data provider unavailable.")
    assert response.json()["completed_at"] is not None


def test_cannot_complete_pending_scan_run(
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
        f"/scan-runs/{scan_run_id}/complete",
        json={
            "candidates_found": 5,
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": ("Only running scan runs can be completed."),
    }


def test_cannot_fail_pending_scan_run(
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
        f"/scan-runs/{scan_run_id}/fail",
        json={
            "error_message": "Something failed.",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": ("Only running scan runs can be failed."),
    }


def test_cannot_restart_completed_scan_run(
    client: TestClient,
) -> None:
    create_response = client.post(
        "/scan-runs",
        json={
            "strategy_name": "momentum_breakout",
        },
    )

    scan_run_id = create_response.json()["id"]

    client.post(
        f"/scan-runs/{scan_run_id}/start",
    )

    client.post(
        f"/scan-runs/{scan_run_id}/complete",
        json={
            "candidates_found": 3,
        },
    )

    response = client.post(
        f"/scan-runs/{scan_run_id}/start",
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": ("Only pending scan runs can be started."),
    }


def test_start_missing_scan_run_returns_404(
    client: TestClient,
) -> None:
    response = client.post(
        f"/scan-runs/{uuid4()}/start",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Scan run not found",
    }


def test_rejects_negative_candidate_count(
    client: TestClient,
) -> None:
    create_response = client.post(
        "/scan-runs",
        json={
            "strategy_name": "momentum_breakout",
        },
    )

    scan_run_id = create_response.json()["id"]

    client.post(
        f"/scan-runs/{scan_run_id}/start",
    )

    response = client.post(
        f"/scan-runs/{scan_run_id}/complete",
        json={
            "candidates_found": -1,
        },
    )

    assert response.status_code == 422


def test_rejects_empty_failure_message(
    client: TestClient,
) -> None:
    create_response = client.post(
        "/scan-runs",
        json={
            "strategy_name": "momentum_breakout",
        },
    )

    scan_run_id = create_response.json()["id"]

    client.post(
        f"/scan-runs/{scan_run_id}/start",
    )

    response = client.post(
        f"/scan-runs/{scan_run_id}/fail",
        json={
            "error_message": "",
        },
    )

    assert response.status_code == 422
