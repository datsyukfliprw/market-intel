from uuid import UUID

from sqlalchemy.orm import Session

from app.models.scan_candidate import ScanCandidate
from app.models.scan_run import ScanRunStatus
from app.repositories.instrument import InstrumentRepository
from app.repositories.scan_candidate import (
    DuplicateScanCandidateError,
    ScanCandidateRepository,
)
from app.repositories.scan_run import ScanRunRepository
from app.schemas.scan_candidate import ScanCandidateCreate


class ScanCandidateNotFoundError(Exception):
    pass


class CandidateScanRunNotFoundError(Exception):
    pass


class InvalidCandidateScanRunStateError(Exception):
    pass


class ScanCandidateSymbolNotFoundError(Exception):
    pass


class ScanCandidateService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ScanCandidateRepository(session)
        self.scan_run_repository = ScanRunRepository(session)
        self.instrument_repository = InstrumentRepository(session)

    def create_candidate(
        self,
        scan_run_id: UUID,
        data: ScanCandidateCreate,
    ) -> ScanCandidate:
        scan_run = self.scan_run_repository.get_by_id(
            scan_run_id,
        )

        if scan_run is None:
            raise CandidateScanRunNotFoundError

        if scan_run.status != ScanRunStatus.RUNNING:
            raise InvalidCandidateScanRunStateError(
                "Candidates can only be added to running scan runs.",
            )

        instrument = self.instrument_repository.get_by_symbol(
            data.symbol,
        )

        if instrument is None:
            raise ScanCandidateSymbolNotFoundError

        try:
            candidate = self.repository.create(
                scan_run_id=scan_run_id,
                symbol=data.symbol,
                instrument_id=instrument.id,
                rank=data.rank,
                composite_score=data.composite_score,
            )

            self.session.commit()
            self.session.refresh(candidate)

            return candidate
        except DuplicateScanCandidateError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise

    def list_candidates(
        self,
        scan_run_id: UUID,
    ) -> list[ScanCandidate]:
        scan_run = self.scan_run_repository.get_by_id(
            scan_run_id,
        )

        if scan_run is None:
            raise CandidateScanRunNotFoundError

        return self.repository.list_for_scan_run(
            scan_run_id,
        )

    def get_candidate(
        self,
        candidate_id: UUID,
    ) -> ScanCandidate:
        candidate = self.repository.get_by_id(
            candidate_id,
        )

        if candidate is None:
            raise ScanCandidateNotFoundError

        return candidate
