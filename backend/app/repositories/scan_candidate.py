from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.scan_candidate import ScanCandidate


class DuplicateScanCandidateError(Exception):
    pass


class ScanCandidateRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        scan_run_id: UUID,
        symbol: str,
        rank: int | None = None,
        composite_score: float | None = None,
    ) -> ScanCandidate:
        candidate = ScanCandidate(
            scan_run_id=scan_run_id,
            symbol=symbol,
            rank=rank,
            composite_score=composite_score,
        )

        self.session.add(candidate)

        try:
            self.session.flush()
        except IntegrityError as error:
            self.session.rollback()
            raise DuplicateScanCandidateError from error

        return candidate

    def get_by_id(
        self,
        candidate_id: UUID,
    ) -> ScanCandidate | None:
        return self.session.get(
            ScanCandidate,
            candidate_id,
        )

    def list_for_scan_run(
        self,
        scan_run_id: UUID,
    ) -> list[ScanCandidate]:
        statement = (
            select(ScanCandidate)
            .where(
                ScanCandidate.scan_run_id == scan_run_id,
            )
            .order_by(
                ScanCandidate.rank.asc().nulls_last(),
                ScanCandidate.composite_score.desc().nulls_last(),
                ScanCandidate.discovered_at.asc(),
            )
        )

        return list(
            self.session.scalars(statement).all(),
        )
