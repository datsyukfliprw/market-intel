from datetime import UTC, datetime

from app.domain.analytics import EvaluationSample, PerformanceAggregator
from app.domain.outcomes import (
    CheckpointPrice,
    OutcomeResult,
    OutcomeStatus,
    SameBarPolicy,
)
from app.domain.scoring import CandidateClassification


def outcome(
    *,
    entered: bool,
    target: bool = False,
    invalidated: bool = False,
    mfe_r: float | None = None,
    mae_r: float | None = None,
    mark_to_market_r: float | None = None,
) -> OutcomeResult:
    now = datetime(2026, 8, 10, tzinfo=UTC)
    checkpoints = tuple(
        CheckpointPrice(
            minutes_after_entry=minutes,
            observed_at=None,
            price=None,
            return_pct=None,
            return_r=None,
        )
        for minutes in (5, 15, 30, 60)
    )
    return OutcomeResult(
        status=(
            OutcomeStatus.NOT_TRIGGERED
            if not entered
            else OutcomeStatus.TARGET_THEN_INVALIDATED
            if target and invalidated
            else OutcomeStatus.TARGET_REACHED
            if target
            else OutcomeStatus.INVALIDATED
            if invalidated
            else OutcomeStatus.OPEN
        ),
        same_bar_policy=SameBarPolicy.ADVERSE_FIRST,
        entry_triggered=entered,
        entry_triggered_at=now if entered else None,
        invalidation_triggered=invalidated,
        invalidation_triggered_at=now if invalidated else None,
        targets_triggered=(target,),
        target_triggered_at=(now if target else None,),
        highest_target_index=0 if target else None,
        events=(),
        checkpoints=checkpoints,
        observations_available=1,
        observations_through_terminal=1 if entered else 0,
        high_until_terminal=2.2 if entered else None,
        low_until_terminal=1.9 if entered else None,
        high_after_entry_all_observations=2.2 if entered else None,
        low_after_entry_all_observations=1.9 if entered else None,
        last_observed_close=2.1 if entered else None,
        mfe_per_share=0.2 if entered else None,
        mae_per_share=0.1 if entered else None,
        mfe_r=mfe_r,
        mae_r=mae_r,
        mark_to_market_r=mark_to_market_r,
        terminal_price=2.1 if entered else None,
        terminal_r=mark_to_market_r,
        entry_bar_path_ambiguous=False,
    )


def test_performance_summary_uses_given_entry_denominators() -> None:
    samples = [
        EvaluationSample(
            score=82,
            classification=CandidateClassification.A_TIER,
            outcome=outcome(
                entered=True,
                target=True,
                mfe_r=3.0,
                mae_r=0.5,
                mark_to_market_r=2.0,
            ),
        ),
        EvaluationSample(
            score=78,
            classification=CandidateClassification.A_TIER,
            outcome=outcome(
                entered=True,
                invalidated=True,
                mfe_r=0.5,
                mae_r=1.2,
                mark_to_market_r=-1.0,
            ),
        ),
        EvaluationSample(
            score=71,
            classification=CandidateClassification.WATCH_FOR_ENTRY,
            outcome=outcome(entered=False),
        ),
    ]

    summary = PerformanceAggregator().summarize(samples)

    assert summary.overall.sample_size == 3
    assert summary.overall.entry_trigger_rate == 0.6667
    assert summary.overall.target_hit_rate_given_entry == 0.5
    assert summary.overall.invalidation_rate_given_entry == 0.5
    assert summary.overall.average_mfe_r == 1.75
    assert summary.overall.average_mae_r == 0.85
    assert summary.overall.average_mark_to_market_r == 0.5
    assert summary.overall.low_sample_warning is True
    assert {item.label for item in summary.by_score_band} == {"70-74", "75-100"}


def test_empty_summary_has_null_rates() -> None:
    summary = PerformanceAggregator().summarize([])

    assert summary.overall.sample_size == 0
    assert summary.overall.entry_trigger_rate is None
    assert summary.by_classification == ()
    assert summary.by_score_band == ()
