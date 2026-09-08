from __future__ import annotations

from uuid import UUID

from sqlalchemy import case, select
from sqlalchemy.orm import Session

from app.models.penny import (
    PennyCandidateSnapshot,
    PennyMarketObservation,
    PennyOutcomeEvaluation,
)
from app.models.scan_candidate import ScanCandidate


class PennyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_candidate(self, candidate_id: UUID) -> ScanCandidate | None:
        return self.session.get(ScanCandidate, candidate_id)

    def get_snapshot(self, snapshot_id: UUID) -> PennyCandidateSnapshot | None:
        return self.session.get(PennyCandidateSnapshot, snapshot_id)

    def get_snapshot_for_candidate(
        self,
        candidate_id: UUID,
    ) -> PennyCandidateSnapshot | None:
        statement = select(PennyCandidateSnapshot).where(
            PennyCandidateSnapshot.candidate_id == candidate_id
        )
        return self.session.scalar(statement)

    def add_snapshot(
        self,
        snapshot: PennyCandidateSnapshot,
    ) -> PennyCandidateSnapshot:
        self.session.add(snapshot)
        self.session.flush()
        return snapshot

    def rerank_scan_candidates(self, scan_run_id: UUID) -> None:
        """Project immutable snapshot scores onto the mutable scan queue."""

        unscored_last = case(
            (PennyCandidateSnapshot.score.is_(None), 1),
            else_=0,
        )
        statement = (
            select(ScanCandidate, PennyCandidateSnapshot.score)
            .outerjoin(
                PennyCandidateSnapshot,
                PennyCandidateSnapshot.candidate_id == ScanCandidate.id,
            )
            .where(ScanCandidate.scan_run_id == scan_run_id)
            .order_by(
                unscored_last.asc(),
                PennyCandidateSnapshot.score.desc(),
                ScanCandidate.symbol.asc(),
            )
        )
        for rank, (candidate, score) in enumerate(
            self.session.execute(statement).all(),
            start=1,
        ):
            candidate.rank = rank
            candidate.composite_score = score

    def list_snapshots(
        self,
        *,
        symbol: str | None = None,
        classification: str | None = None,
        scoring_version: str | None = None,
        limit: int = 100,
    ) -> list[PennyCandidateSnapshot]:
        statement = select(PennyCandidateSnapshot)
        if symbol is not None:
            statement = statement.where(PennyCandidateSnapshot.symbol == symbol)
        if classification is not None:
            statement = statement.where(
                PennyCandidateSnapshot.classification == classification
            )
        if scoring_version is not None:
            statement = statement.where(
                PennyCandidateSnapshot.scoring_version == scoring_version
            )
        statement = statement.order_by(PennyCandidateSnapshot.captured_at.desc()).limit(
            limit
        )
        return list(self.session.scalars(statement).all())

    def list_observations(
        self,
        snapshot_id: UUID,
        *,
        source: str | None = None,
    ) -> list[PennyMarketObservation]:
        statement = select(PennyMarketObservation).where(
            PennyMarketObservation.snapshot_id == snapshot_id
        )
        if source is not None:
            statement = statement.where(PennyMarketObservation.source == source)
        statement = statement.order_by(PennyMarketObservation.observed_at.asc())
        return list(self.session.scalars(statement).all())

    def add_observation(
        self,
        observation: PennyMarketObservation,
    ) -> PennyMarketObservation:
        self.session.add(observation)
        self.session.flush()
        return observation

    def add_evaluation(
        self,
        evaluation: PennyOutcomeEvaluation,
    ) -> PennyOutcomeEvaluation:
        self.session.add(evaluation)
        self.session.flush()
        return evaluation

    def find_evaluation(
        self,
        *,
        snapshot_id: UUID,
        calculator_version: str,
        observation_digest: str,
    ) -> PennyOutcomeEvaluation | None:
        statement = select(PennyOutcomeEvaluation).where(
            PennyOutcomeEvaluation.snapshot_id == snapshot_id,
            PennyOutcomeEvaluation.calculator_version == calculator_version,
            PennyOutcomeEvaluation.observation_digest == observation_digest,
        )
        return self.session.scalar(statement)

    def list_evaluations(
        self,
        snapshot_id: UUID,
        *,
        source: str | None = None,
    ) -> list[PennyOutcomeEvaluation]:
        statement = select(PennyOutcomeEvaluation).where(
            PennyOutcomeEvaluation.snapshot_id == snapshot_id
        )
        if source is not None:
            statement = statement.where(PennyOutcomeEvaluation.source == source)
        statement = statement.order_by(PennyOutcomeEvaluation.created_at.asc())
        return list(self.session.scalars(statement).all())

    def latest_evaluations(
        self,
        *,
        scoring_version: str | None = None,
        source: str | None = None,
    ) -> list[tuple[PennyCandidateSnapshot, PennyOutcomeEvaluation]]:
        statement = (
            select(PennyCandidateSnapshot, PennyOutcomeEvaluation)
            .join(
                PennyOutcomeEvaluation,
                PennyOutcomeEvaluation.snapshot_id == PennyCandidateSnapshot.id,
            )
            .order_by(
                PennyCandidateSnapshot.id,
                PennyOutcomeEvaluation.created_at.desc(),
            )
        )
        if scoring_version is not None:
            statement = statement.where(
                PennyCandidateSnapshot.scoring_version == scoring_version
            )
        if source is not None:
            statement = statement.where(PennyOutcomeEvaluation.source == source)

        rows = list(self.session.execute(statement).all())
        latest: dict[UUID, tuple[PennyCandidateSnapshot, PennyOutcomeEvaluation]] = {}
        for snapshot, evaluation in rows:
            latest.setdefault(snapshot.id, (snapshot, evaluation))
        return list(latest.values())
