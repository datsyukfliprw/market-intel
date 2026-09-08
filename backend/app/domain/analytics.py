from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from statistics import fmean

from pydantic import BaseModel, ConfigDict, Field

from app.domain.outcomes import OutcomeResult
from app.domain.scoring import CandidateClassification

ANALYTICS_VERSION = "penny-analytics-v1.0.0"


class EvaluationSample(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    score: float = Field(ge=0, le=100)
    classification: CandidateClassification
    outcome: OutcomeResult


class PerformanceSlice(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    label: str
    sample_size: int = Field(ge=0)
    entry_trigger_rate: float | None
    target_hit_rate_given_entry: float | None
    invalidation_rate_given_entry: float | None
    average_mfe_r: float | None
    average_mae_r: float | None
    average_mark_to_market_r: float | None
    low_sample_warning: bool


class PerformanceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    analytics_version: str = ANALYTICS_VERSION
    overall: PerformanceSlice
    by_classification: tuple[PerformanceSlice, ...]
    by_score_band: tuple[PerformanceSlice, ...]


class PerformanceAggregator:
    """Summarize latest snapshot evaluations without tuning the strategy."""

    SCORE_BANDS = (
        (0.0, 44.9999, "0-44"),
        (45.0, 54.9999, "45-54"),
        (55.0, 69.9999, "55-69"),
        (70.0, 74.9999, "70-74"),
        (75.0, 100.0, "75-100"),
    )
    LOW_SAMPLE_THRESHOLD = 30

    def summarize(
        self,
        samples: list[EvaluationSample] | tuple[EvaluationSample, ...],
    ) -> PerformanceSummary:
        materialized = list(samples)
        by_classification: dict[CandidateClassification, list[EvaluationSample]] = (
            defaultdict(list)
        )
        for sample in materialized:
            by_classification[sample.classification].append(sample)

        classification_slices = tuple(
            self._slice(classification.value, by_classification[classification])
            for classification in CandidateClassification
            if by_classification[classification]
        )

        score_slices: list[PerformanceSlice] = []
        for minimum, maximum, label in self.SCORE_BANDS:
            band = [
                sample for sample in materialized if minimum <= sample.score <= maximum
            ]
            if band:
                score_slices.append(self._slice(label, band))

        return PerformanceSummary(
            overall=self._slice("overall", materialized),
            by_classification=classification_slices,
            by_score_band=tuple(score_slices),
        )

    def _slice(
        self,
        label: str,
        samples: list[EvaluationSample],
    ) -> PerformanceSlice:
        entered = [sample for sample in samples if sample.outcome.entry_triggered]
        targets = [
            sample for sample in entered if any(sample.outcome.targets_triggered)
        ]
        invalidated = [
            sample for sample in entered if sample.outcome.invalidation_triggered
        ]

        return PerformanceSlice(
            label=label,
            sample_size=len(samples),
            entry_trigger_rate=self._rate(len(entered), len(samples)),
            target_hit_rate_given_entry=self._rate(len(targets), len(entered)),
            invalidation_rate_given_entry=self._rate(len(invalidated), len(entered)),
            average_mfe_r=self._average(sample.outcome.mfe_r for sample in entered),
            average_mae_r=self._average(sample.outcome.mae_r for sample in entered),
            average_mark_to_market_r=self._average(
                sample.outcome.mark_to_market_r for sample in entered
            ),
            low_sample_warning=len(samples) < self.LOW_SAMPLE_THRESHOLD,
        )

    @staticmethod
    def _rate(numerator: int, denominator: int) -> float | None:
        if denominator == 0:
            return None
        return round(numerator / denominator, 4)

    @staticmethod
    def _average(values: Iterable[float | None]) -> float | None:
        materialized = [value for value in values if value is not None]
        if not materialized:
            return None
        return round(fmean(materialized), 4)
