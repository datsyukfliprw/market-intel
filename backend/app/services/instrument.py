from uuid import UUID

from sqlalchemy.orm import Session

from app.models.instrument import Instrument
from app.repositories.instrument import DuplicateInstrumentError, InstrumentRepository
from app.schemas.instrument import InstrumentCreate, InstrumentUpdate


class InstrumentNotFoundError(Exception):
    pass


class InstrumentService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = InstrumentRepository(session)

    def create_instrument(
        self,
        data: InstrumentCreate,
    ) -> Instrument:
        instrument = Instrument(**data.model_dump())

        try:
            instrument = self.repository.create(instrument)
            self.session.commit()
            self.session.refresh(instrument)
            return instrument
        except DuplicateInstrumentError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise

    def get_instrument(
        self,
        instrument_id: UUID,
    ) -> Instrument:
        instrument = self.repository.get_by_id(instrument_id)

        if instrument is None:
            raise InstrumentNotFoundError

        return instrument

    def get_instrument_by_symbol(
        self,
        symbol: str,
    ) -> Instrument:
        instrument = self.repository.get_by_symbol(symbol)

        if instrument is None:
            raise InstrumentNotFoundError

        return instrument

    def list_instruments(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Instrument]:
        return self.repository.list_all(limit, offset)

    def update_instrument(
        self,
        instrument_id: UUID,
        data: InstrumentUpdate,
    ) -> Instrument:
        instrument = self.repository.get_by_id(instrument_id)

        if instrument is None:
            raise InstrumentNotFoundError

        try:
            instrument = self.repository.update(instrument, data)
            self.session.commit()
            self.session.refresh(instrument)
            return instrument
        except DuplicateInstrumentError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise

    def search_instruments(
        self,
        query: str,
        limit: int,
        offset: int,
    ) -> list[Instrument]:
        return self.repository.search(query, limit, offset)
