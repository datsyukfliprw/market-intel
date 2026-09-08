from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

OUTCOME_CALCULATOR_VERSION = "penny-outcome-v1.0.0"


class SameBarPolicy(StrEnum):
    """How to resolve levels touched inside one OHLC bar.

    OHLC bars do not expose the path between high and low. ``adverse_first`` is
    deliberately conservative and is the default for evaluation and replay.
    """

    ADVERSE_FIRST = "adverse_first"
    FAVORABLE_FIRST = "favorable_first"


class OutcomeStatus(StrEnum):
    NOT_TRIGGERED = "not_triggered"
    OPEN = "open"
    TARGET_REACHED = "target_reached"
    INVALIDATED = "invalidated"
    TARGET_THEN_INVALIDATED = "target_then_invalidated"


class OutcomeEventType(StrEnum):
    ENTRY = "entry"
    TARGET = "target"
    INVALIDATION = "invalidation"


class LongTradePlan(BaseModel):
    """Frozen long setup used for both pre-trade scoring and later replay."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    entry_price: float = Field(gt=0)
    invalidation_price: float = Field(gt=0)
    targets: tuple[float, ...] = Field(min_length=1, max_length=10)
    same_bar_policy: SameBarPolicy = SameBarPolicy.ADVERSE_FIRST

    @model_validator(mode="after")
    def validate_price_order(self) -> LongTradePlan:
        if self.invalidation_price >= self.entry_price:
            raise ValueError("invalidation_price must be below entry_price")
        if any(target <= self.entry_price for target in self.targets):
            raise ValueError("every target must be above entry_price")
        if tuple(sorted(self.targets)) != self.targets:
            raise ValueError("targets must be strictly ascending")
        if len(set(self.targets)) != len(self.targets):
            raise ValueError("targets must be unique")
        return self

    @property
    def risk_per_share(self) -> float:
        return self.entry_price - self.invalidation_price

    def reward_risk_for_target(self, target_index: int) -> float:
        reward = self.targets[target_index] - self.entry_price
        return reward / self.risk_per_share


class PriceObservation(BaseModel):
    """One normalized, source-attributed OHLC observation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    observed_at: datetime
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: int | None = Field(default=None, ge=0)
    source: str = Field(default="unknown", min_length=1, max_length=100)
    provenance: str | None = Field(default=None, max_length=1000)

    @field_validator("observed_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        return value.astimezone(UTC)

    @field_validator("source")
    @classmethod
    def normalize_source(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("source cannot be blank")
        return normalized

    @model_validator(mode="after")
    def validate_ohlc(self) -> PriceObservation:
        if self.low > self.high:
            raise ValueError("low cannot exceed high")
        if self.high < max(self.open, self.close):
            raise ValueError("high must be at least open and close")
        if self.low > min(self.open, self.close):
            raise ValueError("low must be at most open and close")
        return self


class OutcomeEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    sequence: int = Field(ge=1)
    event_type: OutcomeEventType
    occurred_at: datetime
    price: float = Field(gt=0)
    target_index: int | None = Field(default=None, ge=0)


class CheckpointPrice(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    minutes_after_entry: int = Field(gt=0)
    observed_at: datetime | None
    price: float | None = Field(default=None, gt=0)
    return_pct: float | None
    return_r: float | None


class OutcomeResult(BaseModel):
    """Deterministic evaluation output; it is not a brokerage fill record."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    calculator_version: str = OUTCOME_CALCULATOR_VERSION
    status: OutcomeStatus
    same_bar_policy: SameBarPolicy

    entry_triggered: bool
    entry_triggered_at: datetime | None
    invalidation_triggered: bool
    invalidation_triggered_at: datetime | None
    targets_triggered: tuple[bool, ...]
    target_triggered_at: tuple[datetime | None, ...]
    highest_target_index: int | None
    events: tuple[OutcomeEvent, ...]

    checkpoints: tuple[CheckpointPrice, ...]
    observations_available: int = Field(ge=0)
    observations_through_terminal: int = Field(ge=0)

    high_until_terminal: float | None
    low_until_terminal: float | None
    high_after_entry_all_observations: float | None
    low_after_entry_all_observations: float | None
    last_observed_close: float | None

    mfe_per_share: float | None
    mae_per_share: float | None
    mfe_r: float | None
    mae_r: float | None
    mark_to_market_r: float | None
    terminal_price: float | None
    terminal_r: float | None

    entry_bar_path_ambiguous: bool


class OutcomeCalculator:
    """Pure deterministic replay of a long penny-stock setup.

    Bars cannot reveal the path inside a candle. When entry, target, and
    invalidation overlap in one bar, ``same_bar_policy`` controls the ordering.
    The default adverse-first policy prevents optimistic backtest leakage.

    Target touches are observations, not assumptions that an order was filled.
    Accordingly, the result reports event ordering and mark-to-market metrics,
    not realized portfolio P&L.
    """

    CHECKPOINT_MINUTES = (5, 15, 30, 60)

    def calculate(
        self,
        plan: LongTradePlan,
        observations: list[PriceObservation] | tuple[PriceObservation, ...],
    ) -> OutcomeResult:
        ordered = self._ordered_observations(observations)
        target_flags = [False] * len(plan.targets)
        target_times: list[datetime | None] = [None] * len(plan.targets)
        events: list[OutcomeEvent] = []

        entry_index: int | None = None
        entry_time: datetime | None = None
        invalidation_time: datetime | None = None
        terminal_index: int | None = None
        entry_bar_path_ambiguous = False

        for index, bar in enumerate(ordered):
            if entry_index is None:
                if not (bar.low <= plan.entry_price <= bar.high):
                    continue
                entry_index = index
                entry_time = bar.observed_at
                self._append_event(
                    events,
                    event_type=OutcomeEventType.ENTRY,
                    occurred_at=bar.observed_at,
                    price=plan.entry_price,
                )

            stop_touched = bar.low <= plan.invalidation_price
            newly_touched_targets = [
                target_index
                for target_index, target in enumerate(plan.targets)
                if not target_flags[target_index] and bar.high >= target
            ]

            if index == entry_index and (stop_touched or newly_touched_targets):
                entry_bar_path_ambiguous = True

            if stop_touched and newly_touched_targets:
                if plan.same_bar_policy == SameBarPolicy.ADVERSE_FIRST:
                    invalidation_time = bar.observed_at
                    terminal_index = index
                    self._append_event(
                        events,
                        event_type=OutcomeEventType.INVALIDATION,
                        occurred_at=bar.observed_at,
                        price=plan.invalidation_price,
                    )
                    break

                self._record_targets(
                    bar=bar,
                    plan=plan,
                    target_indices=newly_touched_targets,
                    target_flags=target_flags,
                    target_times=target_times,
                    events=events,
                )
                invalidation_time = bar.observed_at
                terminal_index = index
                self._append_event(
                    events,
                    event_type=OutcomeEventType.INVALIDATION,
                    occurred_at=bar.observed_at,
                    price=plan.invalidation_price,
                )
                break

            if newly_touched_targets:
                self._record_targets(
                    bar=bar,
                    plan=plan,
                    target_indices=newly_touched_targets,
                    target_flags=target_flags,
                    target_times=target_times,
                    events=events,
                )

            if stop_touched:
                invalidation_time = bar.observed_at
                terminal_index = index
                self._append_event(
                    events,
                    event_type=OutcomeEventType.INVALIDATION,
                    occurred_at=bar.observed_at,
                    price=plan.invalidation_price,
                )
                break

        if entry_index is None or entry_time is None:
            return OutcomeResult(
                status=OutcomeStatus.NOT_TRIGGERED,
                same_bar_policy=plan.same_bar_policy,
                entry_triggered=False,
                entry_triggered_at=None,
                invalidation_triggered=False,
                invalidation_triggered_at=None,
                targets_triggered=tuple(target_flags),
                target_triggered_at=tuple(target_times),
                highest_target_index=None,
                events=(),
                checkpoints=self._empty_checkpoints(),
                observations_available=len(ordered),
                observations_through_terminal=0,
                high_until_terminal=None,
                low_until_terminal=None,
                high_after_entry_all_observations=None,
                low_after_entry_all_observations=None,
                last_observed_close=None,
                mfe_per_share=None,
                mae_per_share=None,
                mfe_r=None,
                mae_r=None,
                mark_to_market_r=None,
                terminal_price=None,
                terminal_r=None,
                entry_bar_path_ambiguous=False,
            )

        post_entry_all = ordered[entry_index:]
        terminal_index = (
            terminal_index if terminal_index is not None else len(ordered) - 1
        )
        through_terminal = ordered[entry_index : terminal_index + 1]

        high_until_terminal = max(bar.high for bar in through_terminal)
        low_until_terminal = min(bar.low for bar in through_terminal)
        high_all = max(bar.high for bar in post_entry_all)
        low_all = min(bar.low for bar in post_entry_all)
        last_observed_close = post_entry_all[-1].close

        risk_per_share = plan.risk_per_share
        mfe_per_share = max(0.0, high_until_terminal - plan.entry_price)
        mae_per_share = max(0.0, plan.entry_price - low_until_terminal)
        any_target = any(target_flags)

        if invalidation_time is not None and any_target:
            status = OutcomeStatus.TARGET_THEN_INVALIDATED
        elif invalidation_time is not None:
            status = OutcomeStatus.INVALIDATED
        elif any_target:
            status = OutcomeStatus.TARGET_REACHED
        else:
            status = OutcomeStatus.OPEN

        highest_target_index = (
            max(index for index, hit in enumerate(target_flags) if hit)
            if any_target
            else None
        )
        terminal_price = (
            plan.invalidation_price
            if invalidation_time is not None
            else last_observed_close
        )

        return OutcomeResult(
            status=status,
            same_bar_policy=plan.same_bar_policy,
            entry_triggered=True,
            entry_triggered_at=entry_time,
            invalidation_triggered=invalidation_time is not None,
            invalidation_triggered_at=invalidation_time,
            targets_triggered=tuple(target_flags),
            target_triggered_at=tuple(target_times),
            highest_target_index=highest_target_index,
            events=tuple(events),
            checkpoints=self._checkpoints(entry_time, post_entry_all, plan),
            observations_available=len(ordered),
            observations_through_terminal=len(through_terminal),
            high_until_terminal=self._rounded(high_until_terminal),
            low_until_terminal=self._rounded(low_until_terminal),
            high_after_entry_all_observations=self._rounded(high_all),
            low_after_entry_all_observations=self._rounded(low_all),
            last_observed_close=self._rounded(last_observed_close),
            mfe_per_share=self._rounded(mfe_per_share),
            mae_per_share=self._rounded(mae_per_share),
            mfe_r=self._ratio(mfe_per_share, risk_per_share),
            mae_r=self._ratio(mae_per_share, risk_per_share),
            mark_to_market_r=self._ratio(
                last_observed_close - plan.entry_price,
                risk_per_share,
            ),
            terminal_price=self._rounded(terminal_price),
            terminal_r=self._ratio(
                terminal_price - plan.entry_price,
                risk_per_share,
            ),
            entry_bar_path_ambiguous=entry_bar_path_ambiguous,
        )

    def _record_targets(
        self,
        *,
        bar: PriceObservation,
        plan: LongTradePlan,
        target_indices: list[int],
        target_flags: list[bool],
        target_times: list[datetime | None],
        events: list[OutcomeEvent],
    ) -> None:
        for target_index in target_indices:
            target_flags[target_index] = True
            target_times[target_index] = bar.observed_at
            self._append_event(
                events,
                event_type=OutcomeEventType.TARGET,
                occurred_at=bar.observed_at,
                price=plan.targets[target_index],
                target_index=target_index,
            )

    @staticmethod
    def _append_event(
        events: list[OutcomeEvent],
        *,
        event_type: OutcomeEventType,
        occurred_at: datetime,
        price: float,
        target_index: int | None = None,
    ) -> None:
        events.append(
            OutcomeEvent(
                sequence=len(events) + 1,
                event_type=event_type,
                occurred_at=occurred_at,
                price=price,
                target_index=target_index,
            )
        )

    @staticmethod
    def _ordered_observations(
        observations: list[PriceObservation] | tuple[PriceObservation, ...],
    ) -> list[PriceObservation]:
        ordered = sorted(observations, key=lambda item: item.observed_at)
        sources = {item.source for item in ordered}
        if len(sources) > 1:
            raise ValueError(
                "one outcome replay must use exactly one market-data source"
            )
        timestamps = [item.observed_at for item in ordered]
        if len(timestamps) != len(set(timestamps)):
            raise ValueError("observations must be unique by observed_at")
        return ordered

    def _checkpoints(
        self,
        entry_time: datetime,
        bars: list[PriceObservation],
        plan: LongTradePlan,
    ) -> tuple[CheckpointPrice, ...]:
        checkpoints: list[CheckpointPrice] = []
        for minutes in self.CHECKPOINT_MINUTES:
            threshold = entry_time + timedelta(minutes=minutes)
            match = next((bar for bar in bars if bar.observed_at >= threshold), None)
            if match is None:
                checkpoints.append(
                    CheckpointPrice(
                        minutes_after_entry=minutes,
                        observed_at=None,
                        price=None,
                        return_pct=None,
                        return_r=None,
                    )
                )
                continue

            change = match.close - plan.entry_price
            checkpoints.append(
                CheckpointPrice(
                    minutes_after_entry=minutes,
                    observed_at=match.observed_at,
                    price=self._rounded(match.close),
                    return_pct=round(change / plan.entry_price * 100, 4),
                    return_r=self._ratio(change, plan.risk_per_share),
                )
            )
        return tuple(checkpoints)

    def _empty_checkpoints(self) -> tuple[CheckpointPrice, ...]:
        return tuple(
            CheckpointPrice(
                minutes_after_entry=minutes,
                observed_at=None,
                price=None,
                return_pct=None,
                return_r=None,
            )
            for minutes in self.CHECKPOINT_MINUTES
        )

    @staticmethod
    def _ratio(value: float, denominator: float) -> float:
        return round(value / denominator, 4)

    @staticmethod
    def _rounded(value: float) -> float:
        return round(value, 6)
