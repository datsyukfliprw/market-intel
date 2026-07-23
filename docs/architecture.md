# Market Intel Architecture

> **A layered, explainable market intelligence platform.**

---

# Guiding Principle

Every layer has one responsibility.

Each layer should be testable independently.

Each layer should improve the information before passing it to the next.

No layer should depend on the internal implementation of another.

Information flows in one direction.

Raw data becomes intelligence.

Intelligence becomes research.

Research becomes decisions.

Decisions become learning.

---

# High-Level Pipeline

```
                External Data
                      │
                      ▼
              Data Collection
                      │
                      ▼
              Data Normalization
                      │
                      ▼
               Market Scanner
                      │
                      ▼
             Technical Analysis
                      │
                      ▼
            Intelligence Layer
                      │
                      ▼
             Opportunity Engine
                      │
                      ▼
                AI Reasoning
                      │
                      ▼
               Report Builder
                      │
                      ▼
             Alert Generation
                      │
                      ▼
              Paper Trading
                      │
                      ▼
            Performance Engine
                      │
                      ▼
            Continuous Learning
```

---

# Layer 1

## Data Collection

Purpose:

Collect information from external providers.

Examples:

- Price history
- OHLCV data
- Company information
- SEC filings
- News
- Social sentiment
- Insider activity

Responsibilities:

- Download
- Cache
- Retry
- Rate limiting
- Error handling

Output:

Normalized raw data.

---

# Layer 2

## Data Normalization

Purpose:

Every provider formats information differently.

This layer converts everything into a common internal format.

Examples:

Price

Instead of:

```
close_price
```

or

```
c
```

Everything becomes:

```
close
```

This allows every later layer to ignore which provider supplied the data.

---

# Layer 3

## Market Scanner

Purpose

Remove obvious non-candidates.

Possible filters:

- Price
- Exchange
- Liquidity
- Average volume
- Market capitalization
- Float
- Trading status

Output:

Candidate universe.

Thousands become hundreds.

---

# Layer 4

## Technical Analysis

Purpose

Calculate measurable indicators.

Examples

- RSI
- MACD
- ATR
- EMA
- SMA
- VWAP
- Relative Volume
- Breakout Detection
- Trend Strength

No opinions.

Only calculations.

---

# Layer 5

## Intelligence Layer

Purpose

Understand _why_ something is happening.

Examples

- News
- SEC filings
- Insider buying
- Dilution
- Social activity
- Catalysts
- Earnings
- Corporate actions

Output

Structured intelligence.

---

# Layer 6

## Opportunity Engine

Purpose

Combine everything into a single evaluation.

This layer creates:

- Opportunity Score
- Risk Score
- Confidence
- Bullish Factors
- Bearish Factors
- Unknown Factors

No AI opinions yet.

Only structured evidence.

---

# Layer 7

## AI Reasoning

Purpose

Translate evidence into research.

Agents may include:

### Research Analyst

Summarizes the company.

---

### Bull Analyst

Builds the strongest positive case.

---

### Bear Analyst

Builds the strongest negative case.

---

### Judge

Compares both.

Produces a balanced conclusion.

---

### Risk Analyst

Looks specifically for:

- Dilution
- Bankruptcy
- Promotion
- Liquidity
- Volatility

---

The AI never invents evidence.

It reasons only from available data.

---

# Layer 8

## Report Builder

Purpose

Generate human-readable reports.

Examples

Daily Report

Company Report

Watchlist Summary

Market Summary

Markdown

HTML

JSON

API

Everything comes from the same structured data.

---

# Layer 9

## Alert Engine

Purpose

Notify users.

Examples

Telegram

Discord

Email

Push Notifications

Alerts should be concise.

The full explanation belongs in the report.

---

# Layer 10

## Paper Trading

Purpose

Track recommendations.

Record

Entry

Exit

Profit

Loss

Maximum Drawdown

Maximum Favorable Excursion

Holding Time

Everything.

---

# Layer 11

## Performance Engine

Purpose

Measure reality.

Metrics

Win Rate

Profit Factor

Sharpe Ratio

Drawdown

Average Return

Strategy Performance

Market Condition Performance

Signal Score Performance

Nothing should rely on intuition.

Everything should be measured.

---

# Layer 12

## Continuous Learning

Purpose

Improve the platform.

Possible improvements

Weight adjustments

Pattern discovery

Historical similarity

Confidence calibration

Signal refinement

No automatic deployment.

New models must outperform previous versions before replacing them.

---

# Design Principles

Every layer:

- Has one responsibility.
- Is independently testable.
- Can be replaced.
- Can be improved without affecting unrelated layers.

---

# Explainability

Every recommendation should be traceable.

Users should always be able to answer:

Why?

The platform should never require blind trust.

---

# Technology

Backend

- Python
- FastAPI

Frontend

- React
- TypeScript
- Tailwind

Storage

- SQLite initially
- PostgreSQL later

Data

- Pandas
- SQLAlchemy

AI

- GPT
- Local models
- Specialized financial models

Infrastructure

- Docker (later)
- GitHub Actions
- Automated testing

---

# Future Expansion

The architecture should support:

- Additional brokers
- Additional markets
- Additional AI models
- Multiple data providers
- Distributed scanning
- Mobile applications
- Team collaboration

without requiring major redesign.

---

# Final Principle

Raw data has little value.

Understanding creates value.

Every layer exists to transform information into understanding while preserving transparency and trust.
