# Market Intel Roadmap

> **Build in layers. Validate every layer before adding the next.**

---

# Guiding Principle

Each phase should produce a working product.

A phase is complete only when it is:

- Functional
- Tested
- Documented
- Useful

Every new layer must be built on a stable foundation.

---

# Version 0.1

## Market Scanner Foundation

**Goal**

Build a reliable market scanner capable of identifying candidate penny stocks using deterministic rules.

### Features

- Connect to market data provider
- Download market data
- Filter eligible securities
- Penny stock filtering
- Historical data retrieval
- Technical indicator calculations
- Relative volume
- Moving averages
- RSI
- ATR
- MACD
- Daily ranking engine
- Export Markdown report
- Store scan results in SQLite
- Logging
- Unit tests

### Success Criteria

- Scan all eligible symbols
- Complete scan in under 10 minutes
- Produce a ranked report
- Zero manual intervention

---

# Version 0.2

## Smarter Screening

**Goal**

Improve signal quality using additional screening rules.

### Features

- Float analysis
- Market cap filtering
- Liquidity scoring
- Gap detection
- Breakout detection
- Support and resistance
- Relative strength
- Trend scoring
- Multi-factor ranking

### Success Criteria

- Fewer false positives
- Better opportunity ranking
- Transparent scoring

---

# Version 0.3

## Market Intelligence

**Goal**

Understand _why_ stocks are moving.

### Features

- News aggregation
- Press release analysis
- Earnings detection
- Insider transactions
- Corporate actions
- Catalyst extraction
- Event timeline

### Success Criteria

Every ranked stock includes an understandable catalyst summary.

---

# Version 0.4

## SEC Intelligence

**Goal**

Understand regulatory filings.

### Features

- SEC filing downloads
- Filing classification
- Dilution detection
- Shelf registrations
- ATM offerings
- Warrants
- Convertible debt
- Reverse splits
- Going concern warnings

### Success Criteria

Every company receives a filing risk summary.

---

# Version 0.5

## AI Research Assistant

**Goal**

Transform data into understandable research.

### Features

- AI summaries
- Bull thesis
- Bear thesis
- Risk explanation
- Opportunity explanation
- Missing information analysis

### Success Criteria

Every candidate receives a complete research report.

---

# Version 0.6

## Paper Trading

**Goal**

Measure real-world performance.

### Features

- Simulated entries
- Simulated exits
- Stop-loss tracking
- Target tracking
- Position sizing
- Trade journal
- Historical statistics

### Success Criteria

Every recommendation is automatically tracked.

---

# Version 0.7

## Learning System

**Goal**

Improve recommendations using historical results.

### Features

- Historical similarity engine
- Pattern clustering
- Signal grading
- Strategy comparison
- Performance by market condition
- Adaptive weighting

### Success Criteria

Signal quality measurably improves over time.

---

# Version 0.8

## Portfolio Intelligence

**Goal**

Help users manage positions.

### Features

- Watchlists
- Portfolio tracking
- Daily summaries
- Position monitoring
- Risk exposure
- Sector exposure
- Exit suggestions

---

# Version 0.9

## Personal Intelligence

**Goal**

Adapt to individual trading styles.

### Features

- User preferences
- Custom scanners
- Personalized scoring
- Strategy templates
- Custom alerts
- Saved searches

---

# Version 1.0

## Market Intel Platform

A complete AI-assisted market intelligence platform.

### Features

- Complete scanning engine
- AI research assistant
- SEC intelligence
- News intelligence
- Paper trading
- Historical analytics
- Explainable scoring
- Alert system
- Portfolio monitoring
- Web dashboard

---

# Future Ideas

These ideas are intentionally **not scheduled**.

They should only be considered after Version 1.0 is stable.

Potential areas include:

- Options analysis
- ETF analysis
- Cryptocurrency
- Global markets
- Broker integrations
- Mobile application
- AI chat assistant
- Voice interaction
- Institutional features
- Team collaboration

---

# Definition of Done

A feature is complete only when:

- It works correctly.
- It has automated tests.
- It is documented.
- It follows the manifesto.
- It improves the product.
- It has measurable value.
- It can be explained to users.

---

# What We Will Not Do

We will not:

- Chase every indicator.
- Add AI where deterministic logic is better.
- Build features without measurable value.
- Hide model reasoning.
- Optimize before measuring.
- Sacrifice maintainability for speed.

---

# Long-Term Goal

Market Intel should become the research platform we would personally trust before risking our own money.

Every release should move closer to that goal.
