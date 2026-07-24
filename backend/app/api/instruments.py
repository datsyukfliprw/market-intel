from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.instrument import DuplicateInstrumentError
from app.schemas.instrument import InstrumentCreate, InstrumentRead, InstrumentUpdate
from app.services.instrument import InstrumentNotFoundError, InstrumentService

router = APIRouter(
    prefix="/instruments",
    tags=["instruments"],
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


def get_service(
    session: DatabaseSession,
) -> InstrumentService:
    return InstrumentService(session)


def instrument_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Instrument not found",
    )


def duplicate_instrument() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Instrument with this symbol already exists",
    )


@router.post(
    "",
    response_model=InstrumentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_instrument(
    data: InstrumentCreate,
    session: DatabaseSession,
) -> InstrumentRead:
    service = get_service(session)

    try:
        instrument = service.create_instrument(data)
    except DuplicateInstrumentError as error:
        raise duplicate_instrument() from error

    return InstrumentRead.model_validate(instrument)


@router.get(
    "",
    response_model=list[InstrumentRead],
)
def list_instruments(
    session: DatabaseSession,
    query: str | None = Query(
        None,
        min_length=1,
    ),
    limit: int = Query(
        50,
        ge=1,
        le=200,
    ),
    offset: int = Query(
        0,
        ge=0,
    ),
) -> list[InstrumentRead]:
    service = get_service(session)

    if query:
        instruments = service.search_instruments(query, limit, offset)
    else:
        instruments = service.list_instruments(limit, offset)

    return [InstrumentRead.model_validate(instrument) for instrument in instruments]


@router.get(
    "/by-symbol/{symbol}",
    response_model=InstrumentRead,
)
def get_instrument_by_symbol(
    symbol: str,
    session: DatabaseSession,
) -> InstrumentRead:
    service = get_service(session)

    try:
        instrument = service.get_instrument_by_symbol(symbol)
    except InstrumentNotFoundError as error:
        raise instrument_not_found() from error

    return InstrumentRead.model_validate(instrument)


@router.get(
    "/{instrument_id}",
    response_model=InstrumentRead,
)
def get_instrument(
    instrument_id: UUID,
    session: DatabaseSession,
) -> InstrumentRead:
    service = get_service(session)

    try:
        instrument = service.get_instrument(instrument_id)
    except InstrumentNotFoundError as error:
        raise instrument_not_found() from error

    return InstrumentRead.model_validate(instrument)


@router.patch(
    "/{instrument_id}",
    response_model=InstrumentRead,
)
def update_instrument(
    instrument_id: UUID,
    data: InstrumentUpdate,
    session: DatabaseSession,
) -> InstrumentRead:
    service = get_service(session)

    try:
        instrument = service.update_instrument(instrument_id, data)
    except InstrumentNotFoundError as error:
        raise instrument_not_found() from error
    except DuplicateInstrumentError as error:
        raise duplicate_instrument() from error

    return InstrumentRead.model_validate(instrument)
