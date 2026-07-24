from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.scan_candidate import (
    DuplicateScanCandidateError,
)
from app.schemas.scan_candidate import (
    ScanCandidateCreate,
    ScanCandidateRead,
)
from app.services.scan_candidate import (
    CandidateScanRunNotFoundError,
    InvalidCandidateScanRunStateError,
    ScanCandidateNotFoundError,
    ScanCandidateService,
)

router = APIRouter(
    tags=["scan candidates"],
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


def get_service(
    session: DatabaseSession,
) -> ScanCandidateService:
    return ScanCandidateService(session)


@router.post(
    "/scan-runs/{scan_run_id}/candidates",
    response_model=ScanCandidateRead,
    status_code=status.HTTP_201_CREATED,
)
def create_scan_candidate(
    scan_run_id: UUID,
    data: ScanCandidateCreate,
    session: DatabaseSession,
) -> ScanCandidateRead:
    service = get_service(session)

    try:
        candidate = service.create_candidate(
            scan_run_id,
            data,
        )
    except CandidateScanRunNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan run not found",
        ) from error
    except InvalidCandidateScanRunStateError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except DuplicateScanCandidateError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Candidate already exists for this scan run",
        ) from error

    return ScanCandidateRead.model_validate(candidate)


@router.get(
    "/scan-runs/{scan_run_id}/candidates",
    response_model=list[ScanCandidateRead],
)
def list_scan_candidates(
    scan_run_id: UUID,
    session: DatabaseSession,
) -> list[ScanCandidateRead]:
    service = get_service(session)

    try:
        candidates = service.list_candidates(
            scan_run_id,
        )
    except CandidateScanRunNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan run not found",
        ) from error

    return [ScanCandidateRead.model_validate(candidate) for candidate in candidates]


@router.get(
    "/scan-candidates/{candidate_id}",
    response_model=ScanCandidateRead,
)
def get_scan_candidate(
    candidate_id: UUID,
    session: DatabaseSession,
) -> ScanCandidateRead:
    service = get_service(session)

    try:
        candidate = service.get_candidate(
            candidate_id,
        )
    except ScanCandidateNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan candidate not found",
        ) from error

    return ScanCandidateRead.model_validate(candidate)
