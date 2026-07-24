from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.scan_run import ScanRun, ScanRunStatus
from app.repositories.scan_run import ScanRunRepository
from app.schemas.scan_run import (
    ScanRunComplete,
    ScanRunCreate,
    ScanRunFail,
)


class ScanRunNotFoundError(Exception):
    pass


class InvalidScanRunTransitionError(Exception):
    pass


class ScanRunService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ScanRunRepository(session)

    def create_scan_run(
        self,
        data: ScanRunCreate,
    ) -> ScanRun:
        try:
            scan_run = self.repository.create(
                strategy_name=data.strategy_name,
            )

            self.session.commit()
            self.session.refresh(scan_run)

            return scan_run
        except Exception:
            self.session.rollback()
            raise

    def list_scan_runs(self) -> list[ScanRun]:
        return self.repository.list_all()

    def get_scan_run(
        self,
        scan_run_id: UUID,
    ) -> ScanRun:
        scan_run = self.repository.get_by_id(
            scan_run_id,
        )

        if scan_run is None:
            raise ScanRunNotFoundError

        return scan_run

    def start_scan_run(
        self,
        scan_run_id: UUID,
    ) -> ScanRun:
        scan_run = self.get_scan_run(scan_run_id)

        if scan_run.status != ScanRunStatus.PENDING:
            raise InvalidScanRunTransitionError(
                "Only pending scan runs can be started.",
            )

        try:
            scan_run.status = ScanRunStatus.RUNNING

            self.session.commit()
            self.session.refresh(scan_run)

            return scan_run
        except Exception:
            self.session.rollback()
            raise

    def complete_scan_run(
        self,
        scan_run_id: UUID,
        data: ScanRunComplete,
    ) -> ScanRun:
        scan_run = self.get_scan_run(scan_run_id)

        if scan_run.status != ScanRunStatus.RUNNING:
            raise InvalidScanRunTransitionError(
                "Only running scan runs can be completed.",
            )

        try:
            scan_run.status = ScanRunStatus.COMPLETED
            scan_run.candidates_found = data.candidates_found
            scan_run.error_message = None
            scan_run.completed_at = datetime.now(UTC)

            self.session.commit()
            self.session.refresh(scan_run)

            return scan_run
        except Exception:
            self.session.rollback()
            raise

    def fail_scan_run(
        self,
        scan_run_id: UUID,
        data: ScanRunFail,
    ) -> ScanRun:
        scan_run = self.get_scan_run(scan_run_id)

        if scan_run.status != ScanRunStatus.RUNNING:
            raise InvalidScanRunTransitionError(
                "Only running scan runs can be failed.",
            )

        try:
            scan_run.status = ScanRunStatus.FAILED
            scan_run.error_message = data.error_message
            scan_run.completed_at = datetime.now(UTC)

            self.session.commit()
            self.session.refresh(scan_run)

            return scan_run
        except Exception:
            self.session.rollback()
            raise
