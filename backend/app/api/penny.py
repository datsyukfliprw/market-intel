from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.domain.outcomes import OutcomeCalculator, OutcomeResult
from app.domain.scoring import PennyScorer, PennyScoreResult
from app.db.session import get_db
from app.schemas.penny import (
    PennyEvaluationRead,
    PennyObservationBatchCreate,
    PennyObservationRead,
    PennyOutcomeRequest,
    PennyPerformanceRead,
    PennyScoreRequest,
    PennySnapshotCreate,
    PennySnapshotList,
    PennySnapshotRead,
    PennyStoredEvaluationCreate,
)
from app.services.penny import (
    DuplicatePennySnapshotError,
    PennyCandidateNotFoundError,
    PennyLedgerService,
    PennyObservationBeforeSnapshotError,
    PennyObservationConflictError,
    PennyObservationsMissingError,
    PennyObservationSourceAmbiguousError,
    PennySnapshotIntegrityError,
    PennySnapshotNotFoundError,
    PennySnapshotSymbolMismatchError,
    PennyTradePlanMissingError,
)

router = APIRouter(prefix="/penny", tags=["penny"])
DatabaseSession = Annotated[Session, Depends(get_db)]


def get_service(session: DatabaseSession) -> PennyLedgerService:
    return PennyLedgerService(session)


@router.post("/score", response_model=PennyScoreResult)
def score_candidate(data: PennyScoreRequest) -> PennyScoreResult:
    return PennyScorer().score(data.features, data.trade_plan)


@router.post("/outcomes/evaluate", response_model=OutcomeResult)
def evaluate_outcome(data: PennyOutcomeRequest) -> OutcomeResult:
    try:
        return OutcomeCalculator().calculate(
            data.trade_plan,
            data.observations,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error


@router.post(
    "/candidates/{candidate_id}/snapshot",
    response_model=PennySnapshotRead,
    status_code=status.HTTP_201_CREATED,
)
def create_snapshot(
    candidate_id: UUID,
    data: PennySnapshotCreate,
    session: DatabaseSession,
) -> PennySnapshotRead:
    service = get_service(session)
    try:
        return service.create_snapshot(candidate_id, data)
    except PennyCandidateNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan candidate not found",
        ) from error
    except DuplicatePennySnapshotError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An immutable penny snapshot already exists for this candidate",
        ) from error
    except PennySnapshotSymbolMismatchError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error


@router.get("/snapshots", response_model=PennySnapshotList)
def list_snapshots(
    session: DatabaseSession,
    symbol: str | None = None,
    classification: str | None = None,
    scoring_version: str | None = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> PennySnapshotList:
    items = get_service(session).list_snapshots(
        symbol=symbol,
        classification=classification,
        scoring_version=scoring_version,
        limit=limit,
    )
    return PennySnapshotList(items=items)


@router.get("/snapshots/{snapshot_id}", response_model=PennySnapshotRead)
def get_snapshot(
    snapshot_id: UUID,
    session: DatabaseSession,
) -> PennySnapshotRead:
    try:
        return get_service(session).get_snapshot(snapshot_id)
    except PennySnapshotNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Penny snapshot not found",
        ) from error


@router.post(
    "/snapshots/{snapshot_id}/observations",
    response_model=list[PennyObservationRead],
    status_code=status.HTTP_201_CREATED,
)
def append_observations(
    snapshot_id: UUID,
    data: PennyObservationBatchCreate,
    session: DatabaseSession,
) -> list[PennyObservationRead]:
    service = get_service(session)
    try:
        return list(service.append_observations(snapshot_id, data.observations))
    except PennySnapshotNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Penny snapshot not found",
        ) from error
    except PennySnapshotIntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Snapshot integrity verification failed",
        ) from error
    except PennyObservationBeforeSnapshotError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
    except PennyObservationConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/snapshots/{snapshot_id}/observations",
    response_model=list[PennyObservationRead],
)
def list_observations(
    snapshot_id: UUID,
    session: DatabaseSession,
    source: str | None = None,
) -> list[PennyObservationRead]:
    try:
        return list(
            get_service(session).list_observations(snapshot_id, source=source)
        )
    except PennySnapshotNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Penny snapshot not found",
        ) from error


@router.post(
    "/snapshots/{snapshot_id}/evaluations",
    response_model=PennyEvaluationRead,
    status_code=status.HTTP_201_CREATED,
)
def evaluate_snapshot(
    snapshot_id: UUID,
    data: PennyStoredEvaluationCreate,
    session: DatabaseSession,
) -> PennyEvaluationRead:
    service = get_service(session)
    try:
        return service.evaluate_snapshot(snapshot_id, source=data.source)
    except PennySnapshotNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Penny snapshot not found",
        ) from error
    except PennySnapshotIntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Snapshot integrity verification failed",
        ) from error
    except PennyTradePlanMissingError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Snapshot has no trade plan to evaluate",
        ) from error
    except PennyObservationsMissingError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error) or "No observations are available",
        ) from error
    except PennyObservationSourceAmbiguousError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/snapshots/{snapshot_id}/evaluations",
    response_model=list[PennyEvaluationRead],
)
def list_evaluations(
    snapshot_id: UUID,
    session: DatabaseSession,
    source: str | None = None,
) -> list[PennyEvaluationRead]:
    try:
        return list(
            get_service(session).list_evaluations(snapshot_id, source=source)
        )
    except PennySnapshotNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Penny snapshot not found",
        ) from error


@router.get("/analytics/performance", response_model=PennyPerformanceRead)
def performance_summary(
    session: DatabaseSession,
    scoring_version: str | None = None,
    source: str | None = None,
) -> PennyPerformanceRead:
    try:
        summary = get_service(session).performance_summary(
            scoring_version=scoring_version,
            source=source,
        )
    except PennySnapshotIntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Snapshot integrity verification failed",
        ) from error
    return PennyPerformanceRead(
        scoring_version=scoring_version,
        source=source.strip().lower() if source is not None else None,
        summary=summary,
    )
