from uuid import UUID

from sqlalchemy.orm import Session

from app.models.scan_run import ScanRun
from app.repositories.scan_run import ScanRunRepository
from app.schemas.scan_run import ScanRunCreate


class ScanRunService:
    def __init__(self, session: Session) -> None:
        self.repository = ScanRunRepository(session)

    def create_scan_run(self, data: ScanRunCreate) -> ScanRun:
        return self.repository.create(strategy_name=data.strategy_name)

    def list_scan_runs(self) -> list[ScanRun]:
        return self.repository.list_all()

    def get_scan_run(self, scan_run_id: UUID) -> ScanRun | None:
        return self.repository.get_by_id(scan_run_id)
