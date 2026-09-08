# `$penny` v0.2 — Deterministic Learning Engine

**Status:** Implemented in the v0.2 pull request  
**Scope:** Scoring, point-in-time evidence, outcome replay, and historical performance  
**Not in scope:** Live provider ingestion, order placement, or autonomous strategy retuning

## Executive finding

The original implementation had a useful FastAPI, SQLAlchemy, Alembic, and test foundation, but its active scanner only loaded a configured symbol list, filtered eligible instruments, and ranked the survivors alphabetically. `ScanCandidate.composite_score` was nullable and no executable scoring engine populated it. The broader architecture documents described recommendations, backtesting, and AI boundaries, but those concepts were not implemented.

The strongest existing asset was the separate `$penny` research method: staged discovery, catalyst review, financing and dilution checks, execution review, reward/risk, and adversarial rejection. The critical missing capability was a trustworthy feedback loop. The system could produce a persuasive report, but it could not preserve exactly what it knew, replay what happened next, or measure whether one scoring version outperformed another.

## Decision

Implement the smallest architecture that can learn without contaminating history:

```text
immutable scan snapshot
        +
append-only timestamped observations
        +
versioned derived outcome evaluation
        =
queryable historical evidence
```

This structure is intentionally narrower than a backtester or trading engine. It creates reliable labels first.

## Domain invariants

### 1. A snapshot is point-in-time evidence

A snapshot contains:

- Normalized scan-time features.
- The exact scoring version and component output.
- Classification and complete-gate result.
- Proposed entry, invalidation, targets, and same-bar policy.
- Thesis, counterevidence, financing notes, execution notes, and limitations.
- Source references and timestamps.
- A SHA-256 hash over all frozen content.

One `ScanCandidate` may have exactly one penny snapshot. A changed thesis or scoring method requires a new scan candidate and a new snapshot; the old record is never rewritten.

### 2. Observations are append-only

Each observation has a timestamp, OHLC values, optional volume, provider, and provenance. Exact repeats are idempotent. Conflicting data for the same snapshot, timestamp, and source is rejected. Observations earlier than the snapshot are rejected to prevent look-ahead leakage.

Multiple providers may be retained, but one replay uses exactly one provider series. Mixing Webull and Alpaca bars as if they were sequential candles would produce false event ordering, so the evaluation API requires explicit source selection when more than one is present.

### 3. Outcomes are derived, not retrofitted into the snapshot

The outcome calculator is a pure function of:

- A frozen `LongTradePlan`.
- One ordered provider series.
- A versioned ambiguity policy.

The result includes entry, target, and invalidation status; explicit event ordering; checkpoint prices and returns; MFE/MAE; terminal R; and mark-to-market R. The input digest makes repeated evaluation idempotent. Adding later bars creates a new evaluation instead of mutating the previous one.

### 4. OHLC ambiguity is never hidden

A candle exposes high and low, not the path between them. When a target and invalidation both occur inside one bar, the default policy is `adverse_first`. This avoids optimistic backtest leakage. `favorable_first` is available for sensitivity analysis, and the selected policy is persisted in the plan and result.

A target touch is not treated as a guaranteed fill. No realized P&L is reported without an execution model.

## Scoring model

The deterministic score totals 100 points:

| Component | Maximum |
|---|---:|
| Liquidity | 20 |
| Momentum / anti-chase shape | 15 |
| Catalyst | 20 |
| Structure | 15 |
| Execution | 15 |
| Financing | 10 |
| Data quality | 5 |

An unverified catalyst is capped at 8/20 even when an analyst assigns a high qualitative catalyst rating.

### Complete A-tier gate

A candidate must score at least 75 and pass every hard gate:

- Price between $0.50 and $5.00.
- Volume of at least 1,000,000 shares.
- Relative volume of at least 1.5x.
- Spread no wider than 2.5%.
- Verified catalyst rated at least 3/5.
- Financing risk no higher than 2/5, with no recent dilution and no unresolved material financing terms.
- Structure, execution, and data quality each at least 3/5.
- Not halted.
- Gap no larger than 100% for A-tier treatment.
- Explicit entry, invalidation, and targets.
- At least 2:1 reward/risk to the conservative base target.

Score cannot override a failed hard gate. This is essential for penny stocks: a spectacular momentum number does not compensate for unknown financing, an unusable spread, or missing evidence.

## Queue behavior

The original alphabetical rank remains a safe fallback during bare symbol discovery. As soon as candidates receive immutable snapshots, the application projects their frozen scores onto `ScanCandidate.composite_score` and reranks the mutable queue by score, with unscored names last. The snapshot remains the authoritative historical record; rank is only an operational view.

## Historical analytics

The performance endpoint uses the latest evaluation for each snapshot and reports:

- Entry-trigger rate.
- Target-hit rate among triggered entries.
- Invalidation rate among triggered entries.
- Average MFE R.
- Average MAE R.
- Average mark-to-market R.
- Breakdowns by classification and score band.

Every slice under 30 samples carries a low-sample warning. These metrics are diagnostic; they do not automatically change weights or gates. Strategy changes require a new explicit scoring version so old and new behavior can be compared without rewriting history.

## AI boundary

AI may:

- Extract structured evidence from filings, news, profiles, and financials.
- Summarize a thesis and strongest counterevidence.
- Explain deterministic component and gate results.

AI may not:

- Invent missing facts.
- Change the score after seeing the outcome.
- Hide unknown financing or source limitations.
- Blend later observations into scan-time evidence.
- Claim fills or realized returns from candle touches.

## Operational sequence

```text
create scan run and candidate
        ↓
normalize and cite scan-time evidence
        ↓
POST candidate snapshot (score + freeze + rerank)
        ↓
append bars from one or more providers
        ↓
select one provider and derive evaluation
        ↓
query performance by scoring version, class, and band
        ↓
only then propose a new scoring version
```

## Remaining work, in priority order

1. Implement a real Webull/Alpaca normalization adapter with clock, retry, and provenance guarantees.
2. Add scheduled post-scan observation collection and evaluation jobs.
3. Build the operator UI around frozen evidence, gate failures, event timelines, and calibration—not around decorative price cards.
4. Add paper-execution assumptions only after quote/trade data can support spread, slippage, and fill modeling.
5. Run prospective shadow scans long enough to reach useful sample sizes before changing scoring weights.

The v0.2 ledger is the foundation for those steps. It turns `$penny` from a one-off report generator into a system that can accumulate falsifiable evidence.
