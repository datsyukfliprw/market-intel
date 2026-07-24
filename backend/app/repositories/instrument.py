from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.instrument import Instrument
from app.schemas.instrument import InstrumentUpdate


class DuplicateInstrumentError(Exception):
    pass


class InstrumentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        instrument: Instrument,
    ) -> Instrument:
        self.session.add(instrument)

        try:
            self.session.flush()
        except IntegrityError as error:
            raise DuplicateInstrumentError from error

        return instrument

    def get_by_id(
        self,
        instrument_id: UUID,
    ) -> Instrument | None:
        return self.session.get(
            Instrument,
            instrument_id,
        )

    def get_by_symbol(
        self,
        symbol: str,
    ) -> Instrument | None:
        normalized_symbol = symbol.strip().upper()

        statement = select(Instrument).where(
            Instrument.symbol == normalized_symbol,
        )

        return self.session.scalars(statement).first()

    def list_all(
        self,
        limit: int,
        offset: int,
    ) -> list[Instrument]:
        statement = (
            select(Instrument)
            .order_by(
                Instrument.is_active.desc(),
                Instrument.symbol.asc(),
            )
            .limit(limit)
            .offset(offset)
        )

        return list(self.session.scalars(statement).all())

    def update(
        self,
        instrument: Instrument,
        data: InstrumentUpdate,
    ) -> Instrument:
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "symbol":
                continue
            setattr(instrument, field, value)

        try:
            self.session.flush()
        except IntegrityError as error:
            raise DuplicateInstrumentError from error

        return instrument

    def search(
        self,
        query: str,
        limit: int,
        offset: int,
    ) -> list[Instrument]:
        search_term = f"%{query}%"

        statement = (
            select(Instrument)
            .where(
                (Instrument.symbol.ilike(search_term))
                | (Instrument.name.ilike(search_term))
            )
            .order_by(Instrument.symbol.asc())
            .limit(limit)
            .offset(offset)
        )

        return list(self.session.scalars(statement).all())
