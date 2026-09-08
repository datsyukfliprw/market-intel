from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.domain.outcomes import PriceObservation
from app.models.instrument import Instrument, InstrumentAssetType
from app.models.penny import (
    ImmutableRecordError,
    PennyCandidateSnapshot,
    PennyMarketObservation,
)
from app.models.scan_candidate import ScanCandidate
from app.models.scan_run import ScanRun
from app.schemas.penny import PennySnapshotCreate
from app.services.penny import (
    PennyLedgerService,
    PennyObservationBeforeSnapshotError,
    PennyObservationConflictError,
    PennyObservationSourceAmbiguousError,
    PennySnapshotIntegrityError,
)

CAPTURED_AT = datetime(2026, 8, 10, 13, 30, tzinfo=UTC)


def candidate(session: Session, symbol: str = "TEST") -> ScanCandidate:
    instrument = Instrument(
        symbol=symbol,
        name="Test Corp",
        exchange="NASDAQ",
        asset_type=InstrumentAssetType.STOCK,
    )
    run = ScanRun(strategy_name="penny-v1")
    session.add_all([instrument, run])
    session.flush()
    item = ScanCandidate(
        scan_run_id=run.id,
        instrument_id=instrument.id,
        symbol=symbol,
        rank=1,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def snapshot_data(symbol: str = "TEST") -> PennySnapshotCreate:
    return PennySnapshotCreate.model_validate(
        {
            "captured_at": CAPTURED_AT,
            "features": {
                "symbol": symbol,
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
                    "observed_at": CAPTURED_AT,
                    "reference": "quote:test:2026-08-10T13:30:00Z",
                }
            ],
        }
    )


def observation(
    minute: int,
    *,
    high: float,
    low: float,
    close: float,
    source: str = "webull",
) -> PriceObservation:
    return PriceObservation(
        observed_at=CAPTURED_AT + timedelta(minutes=minute),
        open=close,
        high=high,
        low=low,
        close=close,
        volume=100_000,
        source=source,
        provenance=f"bar-{minute}",
    )


def create_snapshot(session: Session) -> tuple[PennyLedgerService, UUID]:
    item = candidate(session)
    service = PennyLedgerService(session)
    snapshot = service.create_snapshot(item.id, snapshot_data())
    return service, snapshot.id


def test_snapshot_is_scored_hashed_and_integrity_verified(session: Session) -> None:
    item = candidate(session)
    service = PennyLedgerService(session)

    snapshot = service.create_snapshot(item.id, snapshot_data())

    assert snapshot.score_result.score == snapshot.score
    assert snapshot.score_result.classification.value == snapshot.classification
    assert snapshot.complete_gate_passed is True
    assert snapshot.integrity_valid is True
    assert len(snapshot.snapshot_hash) == 64


def test_orm_update_and_delete_are_rejected(session: Session) -> None:
    service, snapshot_id = create_snapshot(session)
    record = session.get(PennyCandidateSnapshot, snapshot_id)
    assert record is not None

    record.score = 0
    with pytest.raises(ImmutableRecordError):
        session.commit()
    session.rollback()

    record = session.get(PennyCandidateSnapshot, snapshot_id)
    assert record is not None
    session.delete(record)
    with pytest.raises(ImmutableRecordError):
        session.commit()
    session.rollback()

    assert service.get_snapshot(snapshot_id).integrity_valid is True


def test_append_is_idempotent_but_conflicting_data_is_rejected(
    session: Session,
) -> None:
    service, snapshot_id = create_snapshot(session)
    first = observation(0, high=2.05, low=1.98, close=2.02)

    created = service.append_observations(snapshot_id, (first,))
    repeated = service.append_observations(snapshot_id, (first,))

    assert created[0].id == repeated[0].id
    assert len(service.list_observations(snapshot_id)) == 1

    conflicting = first.model_copy(update={"close": 2.03, "high": 2.06})
    with pytest.raises(PennyObservationConflictError):
        service.append_observations(snapshot_id, (conflicting,))


def test_observations_cannot_predate_snapshot(session: Session) -> None:
    service, snapshot_id = create_snapshot(session)
    too_early = observation(-1, high=2.05, low=1.98, close=2.02)

    with pytest.raises(PennyObservationBeforeSnapshotError):
        service.append_observations(snapshot_id, (too_early,))


def test_evaluation_is_append_only_and_idempotent_per_observation_set(
    session: Session,
) -> None:
    service, snapshot_id = create_snapshot(session)
    service.append_observations(
        snapshot_id,
        (
            observation(0, high=2.05, low=1.98, close=2.02),
            observation(5, high=2.25, low=2.00, close=2.20),
        ),
    )

    first = service.evaluate_snapshot(snapshot_id)
    repeated = service.evaluate_snapshot(snapshot_id)
    assert first.id == repeated.id
    assert first.result.targets_triggered == (True, False)

    service.append_observations(
        snapshot_id,
        (observation(15, high=2.45, low=2.18, close=2.40),),
    )
    second = service.evaluate_snapshot(snapshot_id)

    assert second.id != first.id
    assert second.observation_count == 3
    assert second.result.targets_triggered == (True, True)
    assert len(service.list_evaluations(snapshot_id)) == 2


def test_multiple_sources_require_explicit_selection(session: Session) -> None:
    service, snapshot_id = create_snapshot(session)
    service.append_observations(
        snapshot_id,
        (
            observation(0, high=2.05, low=1.98, close=2.02, source="webull"),
            observation(0, high=2.06, low=1.99, close=2.03, source="alpaca"),
        ),
    )

    with pytest.raises(PennyObservationSourceAmbiguousError):
        service.evaluate_snapshot(snapshot_id)

    evaluation = service.evaluate_snapshot(snapshot_id, source="alpaca")
    assert evaluation.source == "alpaca"


def test_direct_database_tampering_is_detected_before_evaluation(
    session: Session,
) -> None:
    service, snapshot_id = create_snapshot(session)
    session.execute(
        update(PennyCandidateSnapshot)
        .where(PennyCandidateSnapshot.id == snapshot_id)
        .values(score=1.0)
    )
    session.commit()

    snapshot = service.get_snapshot(snapshot_id)
    assert snapshot.integrity_valid is False

    with pytest.raises(PennySnapshotIntegrityError):
        service.append_observations(
            snapshot_id,
            (observation(0, high=2.05, low=1.98, close=2.02),),
        )
    with pytest.raises(PennySnapshotIntegrityError):
        service.evaluate_snapshot(snapshot_id)


def test_performance_summary_uses_latest_evaluation_per_snapshot(
    session: Session,
) -> None:
    service, snapshot_id = create_snapshot(session)
    service.append_observations(
        snapshot_id,
        (
            observation(0, high=2.05, low=1.98, close=2.02),
            observation(5, high=2.25, low=2.00, close=2.20),
        ),
    )
    service.evaluate_snapshot(snapshot_id)
    service.append_observations(
        snapshot_id,
        (observation(15, high=2.45, low=2.18, close=2.40),),
    )
    service.evaluate_snapshot(snapshot_id)

    summary = service.performance_summary(source="webull")

    assert summary.overall.sample_size == 1
    assert summary.overall.entry_trigger_rate == 1.0
    assert summary.overall.target_hit_rate_given_entry == 1.0
    assert summary.by_score_band[0].label == "75-100"


def test_observation_records_are_immutable(session: Session) -> None:
    service, snapshot_id = create_snapshot(session)
    created = service.append_observations(
        snapshot_id,
        (observation(0, high=2.05, low=1.98, close=2.02),),
    )[0]
    record = session.get(PennyMarketObservation, created.id)
    assert record is not None
    record.close = 9.99

    with pytest.raises(ImmutableRecordError):
        session.commit()
    session.rollback()


def test_snapshot_scores_replace_alphabetical_queue_order(session: Session) -> None:
    run = ScanRun(strategy_name="penny-v1")
    strong_instrument = Instrument(
        symbol="ZZZZ",
        name="Strong",
        exchange="NASDAQ",
        asset_type=InstrumentAssetType.STOCK,
    )
    weak_instrument = Instrument(
        symbol="AAAA",
        name="Weak",
        exchange="NASDAQ",
        asset_type=InstrumentAssetType.STOCK,
    )
    session.add_all([run, strong_instrument, weak_instrument])
    session.flush()
    strong_candidate = ScanCandidate(
        scan_run_id=run.id,
        instrument_id=strong_instrument.id,
        symbol="ZZZZ",
        rank=2,
    )
    weak_candidate = ScanCandidate(
        scan_run_id=run.id,
        instrument_id=weak_instrument.id,
        symbol="AAAA",
        rank=1,
    )
    session.add_all([strong_candidate, weak_candidate])
    session.commit()

    service = PennyLedgerService(session)
    weak_data = snapshot_data("AAAA").model_copy(
        update={
            "features": snapshot_data("AAAA").features.model_copy(
                update={
                    "volume": 1_100_000,
                    "relative_volume": 1.6,
                    "gap_pct": 5.0,
                    "catalyst_quality": 2,
                    "structure_quality": 2,
                    "execution_quality": 2,
                    "financing_risk": 3,
                    "data_quality": 3,
                    "verified_catalyst": False,
                }
            )
        }
    )
    service.create_snapshot(weak_candidate.id, weak_data)
    service.create_snapshot(strong_candidate.id, snapshot_data("ZZZZ"))

    session.refresh(strong_candidate)
    session.refresh(weak_candidate)
    assert strong_candidate.rank == 1
    assert weak_candidate.rank == 2
    assert strong_candidate.composite_score is not None
    assert weak_candidate.composite_score is not None
    assert strong_candidate.composite_score > weak_candidate.composite_score
