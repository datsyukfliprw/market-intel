from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.scan_run import ScanRun


class ScanRunRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, strategy_name: str) -> ScanRun:
        scan_run = ScanRun(strategy_name=strategy_name)

        self.session.add(scan_run)
        self.session.commit()
        self.session.refresh(scan_run)

        return scan_run

    def list_all(self) -> list[ScanRun]:
        statement = select(ScanRun).order_by(ScanRun.started_at.desc())

        return list(self.session.scalars(statement).all())

    def get_by_id(self, scan_run_id: UUID) -> ScanRun | None:
        return self.session.get(ScanRun, scan_run_id)
