from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.instrument import Instrument, InstrumentAssetType
from app.models.scan_run import ScanRun, ScanRunStatus
from app.repositories.instrument import InstrumentRepository
from app.repositories.scan_candidate import ScanCandidateRepository
from app.repositories.scan_run import ScanRunRepository
from app.services.scan_run import InvalidScanRunTransitionError, ScanRunNotFoundError

US_EXCHANGES = frozenset(
    {
        "NYSE",
        "NASDAQ",
        "AMEX",
        "BATS",
        "ARCA",
        "IEX",
        "OTCQB",
        "OTCQX",
        "OTCBB",
        "PINK",
    }
)


class UniverseProvider(ABC):
    """Source of symbol strings that a scan should evaluate."""

    @abstractmethod
    def get_symbols(self) -> list[str]:
        """Return a list of symbol strings for the scanner."""
        ...


class ConfigUniverseProvider(UniverseProvider):
    """Universe provider that reads a comma-separated symbol list from config."""

    def __init__(
        self,
        symbols: str | None = None,
        settings: Settings | None = None,
    ) -> None:
        if symbols is not None:
            self._symbols = symbols
        else:
            self._symbols = (settings or get_settings()).scanner_universe_symbols

    def get_symbols(self) -> list[str]:
        if not self._symbols:
            return []

        return [
            symbol.strip().upper()
            for symbol in self._symbols.split(",")
            if symbol.strip()
        ]


class UniverseFilter:
    """Deterministic eligibility filter for candidate instruments."""

    def __init__(
        self,
        exchanges: frozenset[str] | None = None,
    ) -> None:
        self.exchanges = exchanges or US_EXCHANGES

    def is_eligible(self, instrument: Instrument) -> bool:
        if not instrument.is_active:
            return False

        if instrument.asset_type != InstrumentAssetType.STOCK:
            return False

        if instrument.exchange is None:
            return False

        return instrument.exchange.strip().upper() in self.exchanges


@dataclass(frozen=True)
class RankedInstrument:
    instrument: Instrument
    rank: int
    composite_score: float | None


class AlphabeticalRanker:
    """Deterministic ranker that orders instruments by symbol."""

    def rank(self, instruments: list[Instrument]) -> list[RankedInstrument]:
        sorted_instruments = sorted(
            instruments, key=lambda instrument: instrument.symbol
        )

        return [
            RankedInstrument(
                instrument=instrument,
                rank=rank,
                composite_score=None,
            )
            for rank, instrument in enumerate(sorted_instruments, start=1)
        ]


class ScannerExecutionError(Exception):
    """Raised when a scan cannot be completed due to an internal failure."""


class ScannerService:
    """Orchestrates a scan from symbol discovery to candidate persistence."""

    def __init__(
        self,
        session: Session,
        universe_provider: UniverseProvider | None = None,
        universe_filter: UniverseFilter | None = None,
        ranker: AlphabeticalRanker | None = None,
    ) -> None:
        self.session = session
        self.scan_run_repository = ScanRunRepository(session)
        self.instrument_repository = InstrumentRepository(session)
        self.candidate_repository = ScanCandidateRepository(session)
        self.universe_provider = universe_provider or ConfigUniverseProvider()
        self.universe_filter = universe_filter or UniverseFilter()
        self.ranker = ranker or AlphabeticalRanker()

    def execute(self, scan_run_id: UUID) -> ScanRun:
        scan_run = self.scan_run_repository.get_by_id(scan_run_id)

        if scan_run is None:
            raise ScanRunNotFoundError

        if scan_run.status != ScanRunStatus.PENDING:
            raise InvalidScanRunTransitionError(
                "Only pending scan runs can be executed.",
            )

        scan_run.status = ScanRunStatus.RUNNING

        try:
            symbols = self.universe_provider.get_symbols()
            seen_symbols: set[str] = set()
            eligible_instruments: list[Instrument] = []

            for symbol in symbols:
                normalized_symbol = symbol.strip().upper()

                if normalized_symbol in seen_symbols:
                    continue

                seen_symbols.add(normalized_symbol)

                instrument = self.instrument_repository.get_by_symbol(
                    normalized_symbol,
                )

                if instrument is None:
                    continue

                if self.universe_filter.is_eligible(instrument):
                    eligible_instruments.append(instrument)

            ranked_instruments = self.ranker.rank(eligible_instruments)

            for ranked in ranked_instruments:
                self.candidate_repository.create(
                    scan_run_id=scan_run_id,
                    symbol=ranked.instrument.symbol,
                    instrument_id=ranked.instrument.id,
                    rank=ranked.rank,
                    composite_score=ranked.composite_score,
                )

            scan_run.status = ScanRunStatus.COMPLETED
            scan_run.candidates_found = len(ranked_instruments)
            scan_run.error_message = None
            scan_run.completed_at = datetime.now(UTC)

            self.session.commit()
            self.session.refresh(scan_run)

            return scan_run
        except Exception as exc:
            self.session.rollback()
            self._mark_failed(scan_run_id, str(exc))
            raise ScannerExecutionError(str(exc)) from exc

    def _mark_failed(
        self,
        scan_run_id: UUID,
        error_message: str,
    ) -> None:
        scan_run = self.scan_run_repository.get_by_id(scan_run_id)

        if scan_run is None:
            return

        scan_run.status = ScanRunStatus.FAILED
        scan_run.error_message = error_message[:1000]
        scan_run.completed_at = datetime.now(UTC)

        self.session.commit()
        self.session.refresh(scan_run)
