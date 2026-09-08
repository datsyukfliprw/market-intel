from collections.abc import Generator
from datetime import UTC, datetime, timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.penny import router
from app.db.session import get_db
from app.models.instrument import Instrument, InstrumentAssetType
from app.models.scan_candidate import ScanCandidate
from app.models.scan_run import ScanRun

CAPTURED_AT = datetime(2026, 8, 10, 13, 30, tzinfo=UTC)


def make_client(engine: Engine) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    testing_session_local = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    def override_get_db() -> Generator[Session, None, None]:
        with testing_session_local() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def make_candidate(engine: Engine) -> ScanCandidate:
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    with session_factory() as session:
        instrument = Instrument(
            symbol="TEST",
            name="Test Corp",
            exchange="NASDAQ",
            asset_type=InstrumentAssetType.STOCK,
        )
        run = ScanRun(strategy_name="penny-v1")
        session.add_all([instrument, run])
        session.flush()
        candidate = ScanCandidate(
            scan_run_id=run.id,
            instrument_id=instrument.id,
            symbol="TEST",
            rank=1,
        )
        session.add(candidate)
        session.commit()
        session.refresh(candidate)
        return candidate


def snapshot_payload() -> dict[str, object]:
    return {
        "captured_at": CAPTURED_AT.isoformat(),
        "features": {
            "symbol": "TEST",
            "price": 2.0,
            "volume": 12_000_000,
            "relative_volume": 6.0,
            "float_shares": 12_000_000,
            "gap_pct": 30.0,
            "spread_pct": 0.5,
            "catalyst_quality": 5,
            "structure_quality": 5,
            "execution_quality": 5,
            "financing_risk": 0,
            "data_quality": 5,
            "verified_catalyst": True,
        },
        "trade_plan": {
            "entry_price": 2.0,
            "invalidation_price": 1.9,
            "targets": [2.2, 2.4],
        },
        "research": {
            "thesis": "Verified catalyst with a controlled reclaim.",
            "strongest_counterevidence": "Microcap execution remains fragile.",
        },
        "provenance": [
            {
                "source": "webull",
                "kind": "quote",
                "observed_at": CAPTURED_AT.isoformat(),
                "reference": "quote:test",
            }
        ],
    }


def test_pure_scoring_endpoint(engine: Engine) -> None:
    with make_client(engine) as client:
        response = client.post(
            "/penny/score",
            json={
                "features": snapshot_payload()["features"],
                "trade_plan": snapshot_payload()["trade_plan"],
            },
        )

    assert response.status_code == 200
    assert response.json()["classification"] == "a_tier"
    assert response.json()["complete_gate_passed"] is True


def test_snapshot_observation_evaluation_and_analytics_flow(engine: Engine) -> None:
    candidate = make_candidate(engine)
    with make_client(engine) as client:
        created = client.post(
            f"/penny/candidates/{candidate.id}/snapshot",
            json=snapshot_payload(),
        )
        assert created.status_code == 201, created.text
        snapshot_id = created.json()["id"]

        bars = []
        for minute, high, low, close in (
            (0, 2.05, 1.98, 2.02),
            (5, 2.25, 2.00, 2.20),
            (15, 2.45, 2.18, 2.40),
        ):
            bars.append(
                {
                    "observed_at": (
                        CAPTURED_AT + timedelta(minutes=minute)
                    ).isoformat(),
                    "open": close,
                    "high": high,
                    "low": low,
                    "close": close,
                    "volume": 100_000,
                    "source": "webull",
                    "provenance": f"bar-{minute}",
                }
            )

        appended = client.post(
            f"/penny/snapshots/{snapshot_id}/observations",
            json={"observations": bars},
        )
        assert appended.status_code == 201, appended.text
        assert len(appended.json()) == 3

        evaluated = client.post(
            f"/penny/snapshots/{snapshot_id}/evaluations",
            json={"source": "webull"},
        )
        assert evaluated.status_code == 201, evaluated.text
        assert evaluated.json()["result"]["targets_triggered"] == [True, True]

        analytics = client.get(
            "/penny/analytics/performance",
            params={"source": "webull"},
        )
        assert analytics.status_code == 200, analytics.text
        assert analytics.json()["summary"]["overall"]["sample_size"] == 1


def test_pure_outcome_endpoint_rejects_mixed_sources(engine: Engine) -> None:
    observations = [
        {
            "observed_at": CAPTURED_AT.isoformat(),
            "open": 2.0,
            "high": 2.1,
            "low": 1.98,
            "close": 2.05,
            "source": "webull",
        },
        {
            "observed_at": (CAPTURED_AT + timedelta(minutes=1)).isoformat(),
            "open": 2.05,
            "high": 2.1,
            "low": 2.0,
            "close": 2.08,
            "source": "alpaca",
        },
    ]
    with make_client(engine) as client:
        response = client.post(
            "/penny/outcomes/evaluate",
            json={
                "trade_plan": snapshot_payload()["trade_plan"],
                "observations": observations,
            },
        )

    assert response.status_code == 422
    assert "exactly one" in response.json()["detail"]
