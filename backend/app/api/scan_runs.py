from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.scan_run import ScanRunCreate, ScanRunRead
from app.services.scan_run import ScanRunService

router = APIRouter(
    prefix="/scan-runs",
    tags=["scan runs"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=ScanRunRead,
    status_code=status.HTTP_201_CREATED,
)
def create_scan_run(
    data: ScanRunCreate,
    session: DatabaseSession,
) -> ScanRunRead:
    service = ScanRunService(session)
    scan_run = service.create_scan_run(data)

    return ScanRunRead.model_validate(scan_run)


@router.get(
    "",
    response_model=list[ScanRunRead],
)
def list_scan_runs(
    session: DatabaseSession,
) -> list[ScanRunRead]:
    service = ScanRunService(session)
    scan_runs = service.list_scan_runs()

    return [ScanRunRead.model_validate(scan_run) for scan_run in scan_runs]


@router.get(
    "/{scan_run_id}",
    response_model=ScanRunRead,
)
def get_scan_run(
    scan_run_id: UUID,
    session: DatabaseSession,
) -> ScanRunRead:
    service = ScanRunService(session)
    scan_run = service.get_scan_run(scan_run_id)

    if scan_run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan run not found",
        )

    return ScanRunRead.model_validate(scan_run)
