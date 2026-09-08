from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
import json
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.analytics import (
    EvaluationSample,
    PerformanceAggregator,
    PerformanceSummary,
)
from app.domain.outcomes import (
    OUTCOME_CALCULATOR_VERSION,
    LongTradePlan,
    OutcomeCalculator,
    OutcomeResult,
    PriceObservation,
)
from app.domain.scoring import PennyFeatures, PennyScorer, PennyScoreResult
from app.models.penny import (
    PennyCandidateSnapshot,
    PennyMarketObservation,
    PennyOutcomeEvaluation,
)
from app.repositories.penny import PennyRepository
from app.schemas.penny import (
    EvidenceReference,
    PennyEvaluationRead,
    PennyObservationRead,
    PennyResearchContext,
    PennySnapshotCreate,
    PennySnapshotRead,
)


class PennyCandidateNotFoundError(Exception):
    pass


class PennySnapshotNotFoundError(Exception):
    pass


class DuplicatePennySnapshotError(Exception):
    pass


class PennySnapshotSymbolMismatchError(Exception):
    pass


class PennySnapshotIntegrityError(Exception):
    pass


class PennyObservationBeforeSnapshotError(Exception):
    pass


class PennyObservationConflictError(Exception):
    pass


class PennyTradePlanMissingError(Exception):
    pass


class PennyObservationsMissingError(Exception):
    pass


class PennyObservationSourceAmbiguousError(Exception):
    pass


class PennyLedgerService:
    """Orchestrate immutable snapshots, append-only evidence, and replay."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = PennyRepository(session)
        self.scorer = PennyScorer()
        self.calculator = OutcomeCalculator()
        self.aggregator = PerformanceAggregator()

    def create_snapshot(
        self,
        candidate_id: UUID,
        data: PennySnapshotCreate,
    ) -> PennySnapshotRead:
        candidate = self.repository.get_candidate(candidate_id)
        if candidate is None:
            raise PennyCandidateNotFoundError

        if self.repository.get_snapshot_for_candidate(candidate_id) is not None:
            raise DuplicatePennySnapshotError

        if candidate.symbol != data.features.symbol:
            raise PennySnapshotSymbolMismatchError(
                f"candidate symbol {candidate.symbol} does not match "
                f"snapshot symbol {data.features.symbol}"
            )

        score_result = self.scorer.score(data.features, data.trade_plan)
        payload = self._creation_payload(
            candidate_id=candidate_id,
            symbol=data.features.symbol,
            captured_at=data.captured_at,
            scoring_version=score_result.scoring_version,
            score=score_result.score,
            classification=score_result.classification.value,
            complete_gate_passed=score_result.complete_gate_passed,
            features=data.features,
            score_result=score_result,
            trade_plan=data.trade_plan,
            research=data.research,
            provenance=data.provenance,
        )
        snapshot = PennyCandidateSnapshot(
            candidate_id=candidate_id,
            symbol=data.features.symbol,
            captured_at=data.captured_at,
            scoring_version=score_result.scoring_version,
            score=score_result.score,
            classification=score_result.classification.value,
            complete_gate_passed=score_result.complete_gate_passed,
            features_json=data.features.model_dump(mode="json"),
            score_result_json=score_result.model_dump(mode="json"),
            trade_plan_json=(
                data.trade_plan.model_dump(mode="json")
                if data.trade_plan is not None
                else None
            ),
            research_json=data.research.model_dump(mode="json"),
            provenance_json=[
                reference.model_dump(mode="json") for reference in data.provenance
            ],
            snapshot_hash=self._digest(payload),
        )

        try:
            self.repository.add_snapshot(snapshot)
            self.repository.rerank_scan_candidates(candidate.scan_run_id)
            self.session.commit()
            self.session.refresh(snapshot)
        except Exception:
            self.session.rollback()
            raise

        return self.snapshot_read(snapshot)

    def get_snapshot(self, snapshot_id: UUID) -> PennySnapshotRead:
        snapshot = self._require_snapshot(snapshot_id)
        return self.snapshot_read(snapshot)

    def list_snapshots(
        self,
        *,
        symbol: str | None = None,
        classification: str | None = None,
        scoring_version: str | None = None,
        limit: int = 100,
    ) -> tuple[PennySnapshotRead, ...]:
        normalized_symbol = symbol.strip().upper() if symbol is not None else None
        snapshots = self.repository.list_snapshots(
            symbol=normalized_symbol,
            classification=classification,
            scoring_version=scoring_version,
            limit=limit,
        )
        return tuple(self.snapshot_read(snapshot) for snapshot in snapshots)

    def append_observations(
        self,
        snapshot_id: UUID,
        observations: tuple[PriceObservation, ...],
    ) -> tuple[PennyObservationRead, ...]:
        snapshot = self._require_snapshot(snapshot_id)
        if not self.verify_snapshot(snapshot):
            raise PennySnapshotIntegrityError

        captured_at = self._aware(snapshot.captured_at)
        existing = {
            (self._aware(item.observed_at), item.source): item
            for item in self.repository.list_observations(snapshot_id)
        }
        requested: dict[tuple[datetime, str], PriceObservation] = {}

        for observation in observations:
            if observation.observed_at < captured_at:
                raise PennyObservationBeforeSnapshotError(
                    "outcome observations cannot predate the frozen snapshot"
                )
            key = (observation.observed_at, observation.source)
            previous = requested.get(key)
            if previous is not None and previous != observation:
                raise PennyObservationConflictError(
                    f"conflicting observations for {observation.observed_at.isoformat()} "
                    f"from {observation.source}"
                )
            requested[key] = observation

        returned: list[PennyMarketObservation] = []
        for key, observation in sorted(requested.items()):
            prior = existing.get(key)
            if prior is not None:
                if self._observation_domain(prior) != observation:
                    raise PennyObservationConflictError(
                        f"stored observation conflicts at "
                        f"{observation.observed_at.isoformat()} from {observation.source}"
                    )
                returned.append(prior)
                continue

            record = PennyMarketObservation(
                snapshot_id=snapshot_id,
                observed_at=observation.observed_at,
                open=observation.open,
                high=observation.high,
                low=observation.low,
                close=observation.close,
                volume=observation.volume,
                source=observation.source,
                provenance=observation.provenance,
            )
            self.repository.add_observation(record)
            returned.append(record)

        try:
            self.session.commit()
            for item in returned:
                self.session.refresh(item)
        except Exception:
            self.session.rollback()
            raise

        return tuple(self.observation_read(item) for item in returned)

    def list_observations(
        self,
        snapshot_id: UUID,
        *,
        source: str | None = None,
    ) -> tuple[PennyObservationRead, ...]:
        self._require_snapshot(snapshot_id)
        normalized_source = source.strip().lower() if source is not None else None
        return tuple(
            self.observation_read(observation)
            for observation in self.repository.list_observations(
                snapshot_id,
                source=normalized_source,
            )
        )

    def evaluate_snapshot(
        self,
        snapshot_id: UUID,
        *,
        source: str | None = None,
    ) -> PennyEvaluationRead:
        snapshot = self._require_snapshot(snapshot_id)
        if not self.verify_snapshot(snapshot):
            raise PennySnapshotIntegrityError
        if snapshot.trade_plan_json is None:
            raise PennyTradePlanMissingError

        available = self.repository.list_observations(snapshot_id)
        if not available:
            raise PennyObservationsMissingError

        sources = {item.source for item in available}
        normalized_source = source.strip().lower() if source is not None else None
        if normalized_source is None:
            if len(sources) > 1:
                raise PennyObservationSourceAmbiguousError(
                    "multiple market-data sources exist; choose one explicitly"
                )
            normalized_source = next(iter(sources))
        elif normalized_source not in sources:
            raise PennyObservationsMissingError(
                f"no observations found for source {normalized_source}"
            )

        selected = [item for item in available if item.source == normalized_source]
        observations = tuple(self._observation_domain(item) for item in selected)
        trade_plan = LongTradePlan.model_validate(snapshot.trade_plan_json)
        result = self.calculator.calculate(trade_plan, observations)
        observation_digest = self._digest(
            {
                "snapshot_hash": snapshot.snapshot_hash,
                "calculator_version": OUTCOME_CALCULATOR_VERSION,
                "source": normalized_source,
                "trade_plan": trade_plan.model_dump(mode="json"),
                "observations": [
                    observation.model_dump(mode="json") for observation in observations
                ],
            }
        )
        existing = self.repository.find_evaluation(
            snapshot_id=snapshot_id,
            calculator_version=OUTCOME_CALCULATOR_VERSION,
            observation_digest=observation_digest,
        )
        if existing is not None:
            return self.evaluation_read(existing)

        evaluation = PennyOutcomeEvaluation(
            snapshot_id=snapshot_id,
            calculator_version=OUTCOME_CALCULATOR_VERSION,
            source=normalized_source,
            observation_digest=observation_digest,
            observation_count=len(observations),
            result_json=result.model_dump(mode="json"),
        )
        try:
            self.repository.add_evaluation(evaluation)
            self.session.commit()
            self.session.refresh(evaluation)
        except Exception:
            self.session.rollback()
            raise

        return self.evaluation_read(evaluation)

    def list_evaluations(
        self,
        snapshot_id: UUID,
        *,
        source: str | None = None,
    ) -> tuple[PennyEvaluationRead, ...]:
        self._require_snapshot(snapshot_id)
        normalized_source = source.strip().lower() if source is not None else None
        return tuple(
            self.evaluation_read(evaluation)
            for evaluation in self.repository.list_evaluations(
                snapshot_id,
                source=normalized_source,
            )
        )

    def performance_summary(
        self,
        *,
        scoring_version: str | None = None,
        source: str | None = None,
    ) -> PerformanceSummary:
        normalized_source = source.strip().lower() if source is not None else None
        rows = self.repository.latest_evaluations(
            scoring_version=scoring_version,
            source=normalized_source,
        )
        samples: list[EvaluationSample] = []
        for snapshot, evaluation in rows:
            if not self.verify_snapshot(snapshot):
                raise PennySnapshotIntegrityError
            score_result = PennyScoreResult.model_validate(snapshot.score_result_json)
            samples.append(
                EvaluationSample(
                    score=snapshot.score,
                    classification=score_result.classification,
                    outcome=OutcomeResult.model_validate(evaluation.result_json),
                )
            )
        return self.aggregator.summarize(samples)

    def snapshot_read(
        self,
        snapshot: PennyCandidateSnapshot,
    ) -> PennySnapshotRead:
        return PennySnapshotRead(
            id=snapshot.id,
            candidate_id=snapshot.candidate_id,
            symbol=snapshot.symbol,
            captured_at=self._aware(snapshot.captured_at),
            created_at=self._aware(snapshot.created_at),
            scoring_version=snapshot.scoring_version,
            score=snapshot.score,
            classification=snapshot.classification,
            complete_gate_passed=snapshot.complete_gate_passed,
            features=PennyFeatures.model_validate(snapshot.features_json),
            score_result=PennyScoreResult.model_validate(snapshot.score_result_json),
            trade_plan=(
                LongTradePlan.model_validate(snapshot.trade_plan_json)
                if snapshot.trade_plan_json is not None
                else None
            ),
            research=PennyResearchContext.model_validate(snapshot.research_json),
            provenance=tuple(
                EvidenceReference.model_validate(item)
                for item in snapshot.provenance_json
            ),
            snapshot_hash=snapshot.snapshot_hash,
            integrity_valid=self.verify_snapshot(snapshot),
        )

    def observation_read(
        self,
        observation: PennyMarketObservation,
    ) -> PennyObservationRead:
        return PennyObservationRead(
            id=observation.id,
            snapshot_id=observation.snapshot_id,
            observed_at=self._aware(observation.observed_at),
            open=observation.open,
            high=observation.high,
            low=observation.low,
            close=observation.close,
            volume=observation.volume,
            source=observation.source,
            provenance=observation.provenance,
            created_at=self._aware(observation.created_at),
        )

    def evaluation_read(
        self,
        evaluation: PennyOutcomeEvaluation,
    ) -> PennyEvaluationRead:
        return PennyEvaluationRead(
            id=evaluation.id,
            snapshot_id=evaluation.snapshot_id,
            calculator_version=evaluation.calculator_version,
            source=evaluation.source,
            observation_digest=evaluation.observation_digest,
            observation_count=evaluation.observation_count,
            result=OutcomeResult.model_validate(evaluation.result_json),
            created_at=self._aware(evaluation.created_at),
        )

    def verify_snapshot(self, snapshot: PennyCandidateSnapshot) -> bool:
        expected = self._digest(self._stored_payload(snapshot))
        return expected == snapshot.snapshot_hash

    def _require_snapshot(self, snapshot_id: UUID) -> PennyCandidateSnapshot:
        snapshot = self.repository.get_snapshot(snapshot_id)
        if snapshot is None:
            raise PennySnapshotNotFoundError
        return snapshot

    def _stored_payload(self, snapshot: PennyCandidateSnapshot) -> dict[str, Any]:
        return {
            "candidate_id": str(snapshot.candidate_id),
            "symbol": snapshot.symbol,
            "captured_at": self._aware(snapshot.captured_at).isoformat(),
            "scoring_version": snapshot.scoring_version,
            "score": snapshot.score,
            "classification": snapshot.classification,
            "complete_gate_passed": snapshot.complete_gate_passed,
            "features": snapshot.features_json,
            "score_result": snapshot.score_result_json,
            "trade_plan": snapshot.trade_plan_json,
            "research": snapshot.research_json,
            "provenance": snapshot.provenance_json,
        }

    @staticmethod
    def _creation_payload(
        *,
        candidate_id: UUID,
        symbol: str,
        captured_at: datetime,
        scoring_version: str,
        score: float,
        classification: str,
        complete_gate_passed: bool,
        features: PennyFeatures,
        score_result: PennyScoreResult,
        trade_plan: LongTradePlan | None,
        research: PennyResearchContext,
        provenance: tuple[EvidenceReference, ...],
    ) -> dict[str, Any]:
        return {
            "candidate_id": str(candidate_id),
            "symbol": symbol,
            "captured_at": captured_at.astimezone(UTC).isoformat(),
            "scoring_version": scoring_version,
            "score": score,
            "classification": classification,
            "complete_gate_passed": complete_gate_passed,
            "features": features.model_dump(mode="json"),
            "score_result": score_result.model_dump(mode="json"),
            "trade_plan": (
                trade_plan.model_dump(mode="json") if trade_plan is not None else None
            ),
            "research": research.model_dump(mode="json"),
            "provenance": [item.model_dump(mode="json") for item in provenance],
        }

    def _observation_domain(
        self,
        observation: PennyMarketObservation,
    ) -> PriceObservation:
        return PriceObservation(
            observed_at=self._aware(observation.observed_at),
            open=observation.open,
            high=observation.high,
            low=observation.low,
            close=observation.close,
            volume=observation.volume,
            source=observation.source,
            provenance=observation.provenance,
        )

    @staticmethod
    def _digest(payload: dict[str, Any]) -> str:
        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        return sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _aware(value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
