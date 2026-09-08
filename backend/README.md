# Market Intel Backend

FastAPI backend for Market Intel. The `$penny` workflow now includes a deterministic scoring and outcome-learning engine rather than relying on an alphabetical placeholder ranker.

## What `$penny` now does

The penny workflow has three deliberately separate records:

1. **Immutable candidate snapshot** — scan-time facts, qualitative evidence, trade plan, deterministic score, classification, source provenance, and a SHA-256 integrity hash.
2. **Append-only market observations** — timestamped, normalized OHLC bars with provider and provenance.
3. **Append-only outcome evaluations** — versioned deterministic replays derived from one snapshot and one provider's observation series.

That separation prevents later market data from rewriting what the system knew when it made a call.

The engine also provides:

- A versioned 100-point score with component explanations.
- Hard A-tier gates for price, liquidity, relative volume, spread, catalyst verification, financing risk, structure, execution, data quality, anti-chase protection, a defined trade plan, and at least 2:1 base reward/risk.
- A conservative default for ambiguous OHLC bars: invalidation is assumed to occur before a target when both are touched inside the same bar.
- Ordered entry, target, and invalidation events.
- +5, +15, +30, and +60 minute checkpoint returns.
- MFE, MAE, terminal R, and mark-to-market R.
- Score-band and classification performance summaries using the latest evaluation for each snapshot.
- Automatic score-driven reranking of the mutable scan queue when a frozen snapshot is created.

The result describes observed setup behavior. It does **not** claim brokerage fills or realized portfolio profit.

## Local setup

```bash
cd backend
uv sync --all-groups
cp ../.env.example .env
uv run alembic upgrade head
uv run fastapi dev main.py
```

API documentation is available at `/docs`.

## Core `$penny` API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/penny/score` | Score structured frozen evidence without writing to the database. |
| `POST` | `/penny/outcomes/evaluate` | Replay a trade plan against one normalized price series. |
| `POST` | `/penny/candidates/{candidate_id}/snapshot` | Score and freeze a candidate snapshot. |
| `GET` | `/penny/snapshots` | Query historical snapshots by symbol, class, or scoring version. |
| `POST` | `/penny/snapshots/{id}/observations` | Append source-attributed OHLC observations. |
| `POST` | `/penny/snapshots/{id}/evaluations` | Derive and persist an idempotent outcome evaluation. |
| `GET` | `/penny/analytics/performance` | Compare observed performance by class and score band. |

## Verification

```bash
cd backend
uv run ruff check app tests
uv run ruff format --check app tests
uv run mypy app main.py
uv run pytest -q
```

The migration installs database-level update/delete guards for the three immutable ledger tables on SQLite and PostgreSQL. The application also refuses ORM mutations and verifies snapshot hashes before accepting observations or deriving outcomes.

## Current boundary

This milestone intentionally does not invent market data or place trades. Provider ingestion remains a separate infrastructure concern. Webull, Alpaca, or another adapter should normalize evidence into the typed API contracts; research agents may summarize cited evidence, but deterministic code owns scoring, gates, replay, and analytics.
