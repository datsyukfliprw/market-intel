from app.domain.outcomes import LongTradePlan
from app.domain.scoring import (
    CandidateClassification,
    PennyFeatures,
    PennyScorer,
)


def strong_features(**overrides: object) -> PennyFeatures:
    values: dict[str, object] = {
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
    }
    values.update(overrides)
    return PennyFeatures.model_validate(values)


def good_plan(**overrides: object) -> LongTradePlan:
    values: dict[str, object] = {
        "entry_price": 2.0,
        "invalidation_price": 1.85,
        "targets": (2.30, 2.60),
    }
    values.update(overrides)
    return LongTradePlan.model_validate(values)


def test_strong_candidate_passes_complete_gate_and_is_a_tier() -> None:
    result = PennyScorer().score(strong_features(), good_plan())

    assert result.score >= 75
    assert result.complete_gate_passed is True
    assert result.classification == CandidateClassification.A_TIER
    assert result.reward_risk is not None
    assert result.reward_risk.base_reward_risk == 2.0
    assert sum(component.maximum for component in result.components) == 100


def test_a_tier_requires_a_defined_trade_plan() -> None:
    result = PennyScorer().score(strong_features())

    assert result.complete_gate_passed is False
    assert result.classification != CandidateClassification.A_TIER
    assert "defined_trade_plan" in {
        gate.code for gate in result.gates if not gate.passed
    }


def test_base_reward_risk_below_two_fails_complete_gate() -> None:
    plan = good_plan(targets=(2.20, 2.50))
    result = PennyScorer().score(strong_features(), plan)

    assert result.reward_risk is not None
    assert result.reward_risk.base_reward_risk < 2
    assert result.complete_gate_passed is False
    assert result.classification != CandidateClassification.A_TIER


def test_unverified_catalyst_is_capped_and_cannot_be_a_tier() -> None:
    result = PennyScorer().score(
        strong_features(verified_catalyst=False),
        good_plan(),
    )

    catalyst = next(
        component for component in result.components if component.name == "catalyst"
    )
    assert catalyst.points == 8
    assert result.complete_gate_passed is False
    assert result.classification != CandidateClassification.A_TIER


def test_parabolic_gap_fails_anti_chase_gate() -> None:
    result = PennyScorer().score(
        strong_features(gap_pct=155.0),
        good_plan(),
    )

    anti_chase = next(gate for gate in result.gates if gate.code == "anti_chase")
    assert anti_chase.passed is False
    assert result.classification != CandidateClassification.A_TIER
    assert any("Parabolic gap" in risk for risk in result.risks)


def test_halt_forces_avoid() -> None:
    result = PennyScorer().score(
        strong_features(halted=True),
        good_plan(),
    )

    assert result.classification == CandidateClassification.AVOID


def test_scoring_is_deterministic() -> None:
    scorer = PennyScorer()
    features = strong_features()
    plan = good_plan()

    assert scorer.score(features, plan) == scorer.score(features, plan)
