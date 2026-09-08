from datetime import UTC, datetime, timedelta

import pytest

from app.domain.outcomes import (
    LongTradePlan,
    OutcomeCalculator,
    OutcomeEventType,
    OutcomeStatus,
    PriceObservation,
    SameBarPolicy,
)

BASE_TIME = datetime(2026, 8, 10, 13, 30, tzinfo=UTC)


def bar(
    minute: int,
    *,
    open_: float,
    high: float,
    low: float,
    close: float,
    source: str = "webull",
) -> PriceObservation:
    return PriceObservation(
        observed_at=BASE_TIME + timedelta(minutes=minute),
        open=open_,
        high=high,
        low=low,
        close=close,
        volume=100_000,
        source=source,
    )


def plan(**overrides: object) -> LongTradePlan:
    values: dict[str, object] = {
        "entry_price": 2.0,
        "invalidation_price": 1.90,
        "targets": (2.20, 2.40),
    }
    values.update(overrides)
    return LongTradePlan.model_validate(values)


def test_not_triggered() -> None:
    result = OutcomeCalculator().calculate(
        plan(),
        [bar(0, open_=2.10, high=2.15, low=2.05, close=2.12)],
    )

    assert result.status == OutcomeStatus.NOT_TRIGGERED
    assert result.entry_triggered is False
    assert result.events == ()
    assert result.observations_available == 1


def test_unsorted_bars_are_replayed_in_timestamp_order() -> None:
    result = OutcomeCalculator().calculate(
        plan(),
        [
            bar(10, open_=2.25, high=2.45, low=2.22, close=2.38),
            bar(0, open_=2.05, high=2.08, low=1.98, close=2.04),
            bar(5, open_=2.04, high=2.22, low=2.02, close=2.18),
        ],
    )

    assert result.status == OutcomeStatus.TARGET_REACHED
    assert result.targets_triggered == (True, True)
    assert [event.event_type for event in result.events] == [
        OutcomeEventType.ENTRY,
        OutcomeEventType.TARGET,
        OutcomeEventType.TARGET,
    ]
    assert [event.sequence for event in result.events] == [1, 2, 3]
    assert result.mfe_r == 4.5
    assert result.mark_to_market_r == 3.8


def test_adverse_first_resolves_same_bar_against_the_setup() -> None:
    result = OutcomeCalculator().calculate(
        plan(),
        [bar(0, open_=2.0, high=2.25, low=1.85, close=2.05)],
    )

    assert result.status == OutcomeStatus.INVALIDATED
    assert result.targets_triggered == (False, False)
    assert result.terminal_r == -1.0
    assert result.entry_bar_path_ambiguous is True
    assert [event.event_type for event in result.events] == [
        OutcomeEventType.ENTRY,
        OutcomeEventType.INVALIDATION,
    ]


def test_favorable_first_records_target_before_stop() -> None:
    result = OutcomeCalculator().calculate(
        plan(same_bar_policy=SameBarPolicy.FAVORABLE_FIRST),
        [bar(0, open_=2.0, high=2.25, low=1.85, close=2.05)],
    )

    assert result.status == OutcomeStatus.TARGET_THEN_INVALIDATED
    assert result.targets_triggered == (True, False)
    assert [event.event_type for event in result.events] == [
        OutcomeEventType.ENTRY,
        OutcomeEventType.TARGET,
        OutcomeEventType.INVALIDATION,
    ]


def test_checkpoints_continue_after_invalidation_for_predictive_review() -> None:
    result = OutcomeCalculator().calculate(
        plan(),
        [
            bar(0, open_=2.05, high=2.08, low=1.98, close=2.02),
            bar(2, open_=2.02, high=2.03, low=1.88, close=1.90),
            bar(5, open_=1.90, high=2.10, low=1.89, close=2.08),
            bar(15, open_=2.08, high=2.30, low=2.04, close=2.25),
            bar(30, open_=2.25, high=2.50, low=2.20, close=2.40),
            bar(60, open_=2.40, high=2.60, low=2.35, close=2.55),
        ],
    )

    assert result.status == OutcomeStatus.INVALIDATED
    assert result.observations_through_terminal == 2
    assert result.checkpoints[0].price == 2.08
    assert result.checkpoints[0].return_r == 0.8
    assert result.checkpoints[-1].price == 2.55
    assert result.terminal_r == -1.0
    assert result.mark_to_market_r == 5.5


def test_duplicate_timestamp_and_source_is_rejected() -> None:
    duplicate = bar(0, open_=2.0, high=2.1, low=1.99, close=2.05)
    with pytest.raises(ValueError, match="unique"):
        OutcomeCalculator().calculate(plan(), [duplicate, duplicate])


def test_trade_plan_validates_strict_target_order() -> None:
    with pytest.raises(ValueError, match="ascending"):
        plan(targets=(2.40, 2.20))


def test_replay_requires_one_normalized_source() -> None:
    with pytest.raises(ValueError, match="exactly one"):
        OutcomeCalculator().calculate(
            plan(),
            [
                bar(0, open_=2.0, high=2.1, low=1.99, close=2.05),
                bar(
                    1,
                    open_=2.05,
                    high=2.1,
                    low=2.0,
                    close=2.08,
                    source="alpaca",
                ),
            ],
        )
