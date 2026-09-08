from __future__ import annotations

from enum import StrEnum
from math import log10

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.outcomes import LongTradePlan

SCORING_VERSION = "penny-v1.0.0"


class MarketSession(StrEnum):
    PREMARKET = "premarket"
    REGULAR = "regular"
    AFTER_HOURS = "after_hours"


class CandidateClassification(StrEnum):
    A_TIER = "a_tier"
    WATCH_FOR_ENTRY = "watch_for_entry"
    CATALYST_WATCH = "catalyst_watch"
    HIGH_RISK = "high_risk_speculative"
    AVOID = "avoid"


class GateSeverity(StrEnum):
    HARD = "hard"
    CAUTION = "caution"


class PennyFeatures(BaseModel):
    """Frozen scan-time facts used by the deterministic penny scorer.

    Qualitative fields are bounded to a documented 0-5 rubric. Research agents
    may populate those facts from evidence, but they never create the score or
    classification themselves.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: str = Field(min_length=1, max_length=20)
    session: MarketSession = MarketSession.REGULAR
    price: float = Field(gt=0, le=100)
    volume: int = Field(ge=0)
    relative_volume: float = Field(ge=0, le=1000)
    float_shares: int | None = Field(default=None, ge=0)
    gap_pct: float = Field(ge=-100, le=5000)
    spread_pct: float = Field(ge=0, le=100)

    catalyst_quality: int = Field(ge=0, le=5)
    structure_quality: int = Field(ge=0, le=5)
    execution_quality: int = Field(ge=0, le=5)
    financing_risk: int = Field(ge=0, le=5)
    data_quality: int = Field(ge=0, le=5)

    verified_catalyst: bool = False
    recent_dilution: bool = False
    material_financing_unknown: bool = False
    halted: bool = False
    foreign_issuer: bool = False

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("symbol cannot be blank")
        return normalized


class ScoreComponent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    points: float
    maximum: float
    explanation: str


class GateResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    passed: bool
    severity: GateSeverity
    message: str


class RewardRiskProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    risk_per_share: float = Field(gt=0)
    base_reward_per_share: float = Field(gt=0)
    base_reward_risk: float = Field(gt=0)
    maximum_reward_risk: float = Field(gt=0)


class PennyScoreResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    scoring_version: str = SCORING_VERSION
    symbol: str
    score: float = Field(ge=0, le=100)
    classification: CandidateClassification
    complete_gate_passed: bool
    reward_risk: RewardRiskProfile | None
    components: tuple[ScoreComponent, ...]
    gates: tuple[GateResult, ...]
    strengths: tuple[str, ...]
    risks: tuple[str, ...]


class PennyScorer:
    """Explainable, versioned scorer with conservative penny-stock gates."""

    MIN_PRICE = 0.50
    MAX_PRICE = 5.00
    MIN_VOLUME = 1_000_000
    MIN_RELATIVE_VOLUME = 1.50
    MAX_SPREAD_PCT = 2.50
    MAX_A_TIER_GAP_PCT = 100.0
    MIN_BASE_REWARD_RISK = 2.0
    MIN_A_TIER_SCORE = 75.0

    def score(
        self,
        features: PennyFeatures,
        trade_plan: LongTradePlan | None = None,
    ) -> PennyScoreResult:
        reward_risk = self._reward_risk(trade_plan)
        components = (
            self._liquidity_component(features),
            self._momentum_component(features),
            self._catalyst_component(features),
            self._structure_component(features),
            self._execution_component(features),
            self._financing_component(features),
            self._data_component(features),
        )
        total = round(sum(component.points for component in components), 2)
        gates = self._gates(features, reward_risk)
        complete_gate_passed = all(
            gate.passed for gate in gates if gate.severity == GateSeverity.HARD
        )
        classification = self._classify(
            features=features,
            score=total,
            complete_gate_passed=complete_gate_passed,
            reward_risk=reward_risk,
        )

        return PennyScoreResult(
            symbol=features.symbol,
            score=total,
            classification=classification,
            complete_gate_passed=complete_gate_passed,
            reward_risk=reward_risk,
            components=components,
            gates=gates,
            strengths=self._strengths(features, components, reward_risk),
            risks=self._risks(features, gates),
        )

    @staticmethod
    def _reward_risk(trade_plan: LongTradePlan | None) -> RewardRiskProfile | None:
        if trade_plan is None:
            return None
        risk = trade_plan.risk_per_share
        base_reward = trade_plan.targets[0] - trade_plan.entry_price
        return RewardRiskProfile(
            risk_per_share=round(risk, 6),
            base_reward_per_share=round(base_reward, 6),
            base_reward_risk=round(base_reward / risk, 4),
            maximum_reward_risk=round(
                (trade_plan.targets[-1] - trade_plan.entry_price) / risk,
                4,
            ),
        )

    def _liquidity_component(self, features: PennyFeatures) -> ScoreComponent:
        # Log scaling prevents a 100M-volume outlier from dwarfing otherwise
        # executable names while still rewarding genuine participation.
        if features.volume <= 100_000:
            volume_points = 0.0
        else:
            volume_points = self._clamp(
                (log10(features.volume) - 5.0) / 3.0 * 12.0,
                0.0,
                12.0,
            )

        rel_volume_points = self._clamp(
            (features.relative_volume - 1.0) / 4.0 * 8.0,
            0.0,
            8.0,
        )
        points = round(volume_points + rel_volume_points, 2)
        return ScoreComponent(
            name="liquidity",
            points=points,
            maximum=20,
            explanation=(
                f"{features.volume:,} shares and {features.relative_volume:.2f}x "
                "relative volume"
            ),
        )

    def _momentum_component(self, features: PennyFeatures) -> ScoreComponent:
        gap = features.gap_pct
        if gap <= 0:
            points = 0.0
        elif gap < 5:
            points = gap / 5 * 3
        elif gap < 20:
            points = 3 + (gap - 5) / 15 * 9
        elif gap <= 50:
            points = 12 + (gap - 20) / 30 * 3
        elif gap <= 100:
            # Momentum remains meaningful, but the score fades as chase risk
            # grows. A 100% gap must not automatically outrank a clean 25% gap.
            points = 15 - (gap - 50) / 50 * 6
        else:
            points = max(0.0, 9 - (gap - 100) / 100 * 9)

        return ScoreComponent(
            name="momentum",
            points=round(points, 2),
            maximum=15,
            explanation=f"{features.gap_pct:+.2f}% session gap",
        )

    @staticmethod
    def _catalyst_component(features: PennyFeatures) -> ScoreComponent:
        raw = float(features.catalyst_quality * 4)
        points = raw if features.verified_catalyst else min(raw, 8.0)
        explanation = (
            "verified material catalyst"
            if features.verified_catalyst
            else "catalyst unverified or absent; component capped"
        )
        return ScoreComponent(
            name="catalyst",
            points=round(points, 2),
            maximum=20,
            explanation=explanation,
        )

    @staticmethod
    def _structure_component(features: PennyFeatures) -> ScoreComponent:
        return ScoreComponent(
            name="structure",
            points=float(features.structure_quality * 3),
            maximum=15,
            explanation=f"structure rubric {features.structure_quality}/5",
        )

    def _execution_component(self, features: PennyFeatures) -> ScoreComponent:
        qualitative = float(features.execution_quality * 2)
        spread = self._clamp(5.0 * (1.0 - features.spread_pct / 5.0), 0.0, 5.0)
        return ScoreComponent(
            name="execution",
            points=round(qualitative + spread, 2),
            maximum=15,
            explanation=(
                f"execution rubric {features.execution_quality}/5 with "
                f"{features.spread_pct:.2f}% spread"
            ),
        )

    def _financing_component(self, features: PennyFeatures) -> ScoreComponent:
        points = float((5 - features.financing_risk) * 2)
        if features.recent_dilution:
            points -= 4
        if features.material_financing_unknown:
            points -= 2
        points = self._clamp(points, 0.0, 10.0)
        return ScoreComponent(
            name="financing",
            points=round(points, 2),
            maximum=10,
            explanation=(
                f"financing-risk rubric {features.financing_risk}/5; "
                f"recent dilution={features.recent_dilution}; "
                f"material terms unknown={features.material_financing_unknown}"
            ),
        )

    @staticmethod
    def _data_component(features: PennyFeatures) -> ScoreComponent:
        return ScoreComponent(
            name="data_quality",
            points=float(features.data_quality),
            maximum=5,
            explanation=f"source and quote quality {features.data_quality}/5",
        )

    def _gates(
        self,
        features: PennyFeatures,
        reward_risk: RewardRiskProfile | None,
    ) -> tuple[GateResult, ...]:
        return (
            GateResult(
                code="tradable_price",
                passed=self.MIN_PRICE <= features.price <= self.MAX_PRICE,
                severity=GateSeverity.HARD,
                message=(
                    f"Price must be ${self.MIN_PRICE:.2f}-${self.MAX_PRICE:.2f}; "
                    f"observed ${features.price:.4f}."
                ),
            ),
            GateResult(
                code="minimum_volume",
                passed=features.volume >= self.MIN_VOLUME,
                severity=GateSeverity.HARD,
                message=(
                    f"Volume must be at least {self.MIN_VOLUME:,}; "
                    f"observed {features.volume:,}."
                ),
            ),
            GateResult(
                code="relative_volume",
                passed=features.relative_volume >= self.MIN_RELATIVE_VOLUME,
                severity=GateSeverity.HARD,
                message=(
                    f"Relative volume must be at least {self.MIN_RELATIVE_VOLUME:.2f}x; "
                    f"observed {features.relative_volume:.2f}x."
                ),
            ),
            GateResult(
                code="executable_spread",
                passed=features.spread_pct <= self.MAX_SPREAD_PCT,
                severity=GateSeverity.HARD,
                message=(
                    f"Spread must be no more than {self.MAX_SPREAD_PCT:.2f}%; "
                    f"observed {features.spread_pct:.2f}%."
                ),
            ),
            GateResult(
                code="verified_catalyst",
                passed=features.verified_catalyst and features.catalyst_quality >= 3,
                severity=GateSeverity.HARD,
                message="A-tier requires a verified catalyst rated at least 3/5.",
            ),
            GateResult(
                code="acceptable_financing",
                passed=(
                    features.financing_risk <= 2
                    and not features.recent_dilution
                    and not features.material_financing_unknown
                ),
                severity=GateSeverity.HARD,
                message=(
                    "A-tier requires financing risk <=2/5, no recent dilution, "
                    "and no unresolved material financing terms."
                ),
            ),
            GateResult(
                code="clean_structure",
                passed=features.structure_quality >= 3,
                severity=GateSeverity.HARD,
                message="Structure quality must be at least 3/5.",
            ),
            GateResult(
                code="execution_quality",
                passed=features.execution_quality >= 3,
                severity=GateSeverity.HARD,
                message="Execution quality must be at least 3/5.",
            ),
            GateResult(
                code="reliable_data",
                passed=features.data_quality >= 3,
                severity=GateSeverity.HARD,
                message="Data quality must be at least 3/5.",
            ),
            GateResult(
                code="not_halted",
                passed=not features.halted,
                severity=GateSeverity.HARD,
                message="Halted names cannot qualify.",
            ),
            GateResult(
                code="anti_chase",
                passed=features.gap_pct <= self.MAX_A_TIER_GAP_PCT,
                severity=GateSeverity.HARD,
                message=(
                    f"A-tier gap must not exceed {self.MAX_A_TIER_GAP_PCT:.0f}%; "
                    f"observed {features.gap_pct:.2f}%."
                ),
            ),
            GateResult(
                code="defined_trade_plan",
                passed=reward_risk is not None,
                severity=GateSeverity.HARD,
                message="A-tier requires explicit entry, invalidation, and targets.",
            ),
            GateResult(
                code="conservative_reward_risk",
                passed=(
                    reward_risk is not None
                    and reward_risk.base_reward_risk >= self.MIN_BASE_REWARD_RISK
                ),
                severity=GateSeverity.HARD,
                message=(
                    f"Base target must offer at least {self.MIN_BASE_REWARD_RISK:.1f}:1 "
                    "reward/risk."
                ),
            ),
            GateResult(
                code="domestic_issuer_preference",
                passed=not features.foreign_issuer,
                severity=GateSeverity.CAUTION,
                message=(
                    "Foreign issuers require additional disclosure and execution "
                    "scrutiny."
                ),
            ),
        )

    def _classify(
        self,
        *,
        features: PennyFeatures,
        score: float,
        complete_gate_passed: bool,
        reward_risk: RewardRiskProfile | None,
    ) -> CandidateClassification:
        catastrophic = (
            features.halted
            or features.data_quality <= 1
            or features.spread_pct > 8
            or (features.recent_dilution and features.financing_risk >= 4)
        )
        if catastrophic:
            return CandidateClassification.AVOID

        if score >= self.MIN_A_TIER_SCORE and complete_gate_passed:
            return CandidateClassification.A_TIER

        catalyst_ready = features.verified_catalyst and features.catalyst_quality >= 3
        setup_not_ready = (
            features.structure_quality < 3
            or features.execution_quality < 3
            or features.spread_pct > self.MAX_SPREAD_PCT
        )
        if catalyst_ready and score >= 55 and setup_not_ready:
            return CandidateClassification.CATALYST_WATCH

        reward_risk_acceptable = (
            reward_risk is not None
            and reward_risk.base_reward_risk >= self.MIN_BASE_REWARD_RISK
        )
        if score >= 70 and not features.recent_dilution and reward_risk_acceptable:
            return CandidateClassification.WATCH_FOR_ENTRY

        if score >= 45:
            return CandidateClassification.HIGH_RISK

        return CandidateClassification.AVOID

    def _strengths(
        self,
        features: PennyFeatures,
        components: tuple[ScoreComponent, ...],
        reward_risk: RewardRiskProfile | None,
    ) -> tuple[str, ...]:
        strengths: list[str] = []
        component_map = {component.name: component for component in components}
        if component_map["liquidity"].points >= 15:
            strengths.append("Strong participation and relative volume")
        if features.verified_catalyst and features.catalyst_quality >= 4:
            strengths.append("High-quality verified catalyst")
        if features.structure_quality >= 4:
            strengths.append("Constructive price structure")
        if features.execution_quality >= 4 and features.spread_pct <= 1:
            strengths.append("Tight, executable market")
        if features.financing_risk <= 1 and not features.material_financing_unknown:
            strengths.append("Low identified near-term financing risk")
        if reward_risk is not None and reward_risk.base_reward_risk >= 3:
            strengths.append("Base target offers at least 3:1 reward/risk")
        return tuple(strengths)

    @staticmethod
    def _risks(
        features: PennyFeatures,
        gates: tuple[GateResult, ...],
    ) -> tuple[str, ...]:
        risks = [gate.message for gate in gates if not gate.passed]
        if features.gap_pct > 100:
            risks.append("Parabolic gap creates severe chase and reversal risk")
        if features.float_shares is None:
            risks.append("Float is unknown")
        elif features.float_shares < 2_000_000:
            risks.append("Extremely low float can amplify halts and slippage")
        return tuple(dict.fromkeys(risks))

    @staticmethod
    def _clamp(value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(maximum, value))
