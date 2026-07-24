from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.scan_run import (
    ScanRunComplete,
    ScanRunCreate,
    ScanRunFail,
    ScanRunRead,
)
from app.services.scan_run import (
    InvalidScanRunTransitionError,
    ScanRunNotFoundError,
    ScanRunService,
)
from app.services.scanner import ScannerExecutionError, ScannerService

router = APIRouter(
    prefix="/scan-runs",
    tags=["scan runs"],
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


def get_service(
    session: DatabaseSession,
) -> ScanRunService:
    return ScanRunService(session)


def get_scanner_service(
    session: DatabaseSession,
) -> ScannerService:
    return ScannerService(session)


def scan_run_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Scan run not found",
    )


def invalid_transition(
    error: InvalidScanRunTransitionError,
) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=str(error),
    )


@router.post(
    "",
    response_model=ScanRunRead,
    status_code=status.HTTP_201_CREATED,
)
def create_scan_run(
    data: ScanRunCreate,
    session: DatabaseSession,
) -> ScanRunRead:
    service = get_service(session)
    scan_run = service.create_scan_run(data)

    return ScanRunRead.model_validate(scan_run)


@router.get(
    "",
    response_model=list[ScanRunRead],
)
def list_scan_runs(
    session: DatabaseSession,
) -> list[ScanRunRead]:
    service = get_service(session)

    return [
        ScanRunRead.model_validate(scan_run) for scan_run in service.list_scan_runs()
    ]


@router.get(
    "/{scan_run_id}",
    response_model=ScanRunRead,
)
def get_scan_run(
    scan_run_id: UUID,
    session: DatabaseSession,
) -> ScanRunRead:
    service = get_service(session)

    try:
        scan_run = service.get_scan_run(
            scan_run_id,
        )
    except ScanRunNotFoundError as error:
        raise scan_run_not_found() from error

    return ScanRunRead.model_validate(scan_run)


@router.post(
    "/{scan_run_id}/start",
    response_model=ScanRunRead,
)
def start_scan_run(
    scan_run_id: UUID,
    session: DatabaseSession,
) -> ScanRunRead:
    service = get_service(session)

    try:
        scan_run = service.start_scan_run(
            scan_run_id,
        )
    except ScanRunNotFoundError as error:
        raise scan_run_not_found() from error
    except InvalidScanRunTransitionError as error:
        raise invalid_transition(error) from error

    return ScanRunRead.model_validate(scan_run)


@router.post(
    "/{scan_run_id}/complete",
    response_model=ScanRunRead,
)
def complete_scan_run(
    scan_run_id: UUID,
    data: ScanRunComplete,
    session: DatabaseSession,
) -> ScanRunRead:
    service = get_service(session)

    try:
        scan_run = service.complete_scan_run(
            scan_run_id,
            data,
        )
    except ScanRunNotFoundError as error:
        raise scan_run_not_found() from error
    except InvalidScanRunTransitionError as error:
        raise invalid_transition(error) from error

    return ScanRunRead.model_validate(scan_run)


@router.post(
    "/{scan_run_id}/fail",
    response_model=ScanRunRead,
)
def fail_scan_run(
    scan_run_id: UUID,
    data: ScanRunFail,
    session: DatabaseSession,
) -> ScanRunRead:
    service = get_service(session)

    try:
        scan_run = service.fail_scan_run(
            scan_run_id,
            data,
        )
    except ScanRunNotFoundError as error:
        raise scan_run_not_found() from error
    except InvalidScanRunTransitionError as error:
        raise invalid_transition(error) from error

    return ScanRunRead.model_validate(scan_run)


@router.post(
    "/{scan_run_id}/execute",
    response_model=ScanRunRead,
)
def execute_scan_run(
    scan_run_id: UUID,
    session: DatabaseSession,
) -> ScanRunRead:
    service = get_scanner_service(session)

    try:
        scan_run = service.execute(scan_run_id)
    except ScanRunNotFoundError as error:
        raise scan_run_not_found() from error
    except InvalidScanRunTransitionError as error:
        raise invalid_transition(error) from error
    except ScannerExecutionError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error

    return ScanRunRead.model_validate(scan_run)
