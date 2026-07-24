# Market Intel Scoring Engine

> **Scores should summarize evidence, not replace it.**

---

# Philosophy

The scoring engine exists to organize evidence.

It does not predict the future.

Every score should answer a specific question and be traceable back to measurable inputs.

The overall opportunity score is simply a summary of many independent evaluations.

---

# Core Principles

A score must be:

- Explainable
- Measurable
- Repeatable
- Testable
- Comparable over time

Every score should be decomposable into the factors that created it.

---

# Multiple Scores

Market Intel intentionally avoids using a single "magic number."

Instead, the platform evaluates several independent dimensions.

Each dimension contributes to the final opportunity assessment.

---

# Technical Strength

Question:

> Does the chart currently look healthy?

Potential Inputs

- Relative Volume
- RSI
- MACD
- EMA alignment
- Trend strength
- ATR
- Breakout status
- Moving averages
- Support
- Resistance

Range

0-100

---

# Momentum Score

Question

> Is buying pressure increasing?

Potential Inputs

- Relative volume
- Consecutive green candles
- New highs
- Gap strength
- Acceleration
- Price velocity

Range

0-100

---

# Catalyst Score

Question

> Is there a legitimate reason for recent interest?

Potential Inputs

- News
- Earnings
- Contracts
- FDA announcements
- Partnerships
- Acquisitions
- Product launches
- SEC events

Range

0-100

---

# Financial Health

Question

> How financially stable is the company?

Potential Inputs

- Cash
- Debt
- Revenue
- Cash burn
- Going concern warnings
- Profitability
- Balance sheet

Range

0-100

---

# Liquidity Score

Question

> Can positions realistically be entered and exited?

Potential Inputs

- Daily volume
- Dollar volume
- Bid/ask spread
- Float
- Exchange

Range

0-100

---

# Dilution Risk

Question

> How likely is shareholder dilution?

Potential Inputs

- ATM offerings
- Shelf registrations
- Convertible notes
- Warrants
- Share authorization changes
- Historical dilution

Range

0-100

Higher values represent **higher risk**.

---

# Promotion Risk

Question

> Is the stock being artificially promoted?

Potential Inputs

- Social spikes
- Paid promotions
- Repeated marketing language
- Bot-like activity
- Historical pump behavior

Range

0-100

Higher values represent **higher risk**.

---

# Volatility Score

Question

> How violently does the stock move?

Potential Inputs

- ATR
- Historical volatility
- Gap frequency
- Daily range

Range

0-100

This is descriptive, not good or bad.

---

# Sentiment Score

Question

> What is the market's overall attitude?

Potential Inputs

- News sentiment
- Social sentiment
- Analyst commentary
- Retail attention

Range

0-100

---

# Confidence Score

Question

> How complete and trustworthy is the available evidence?

Potential Inputs

- Data completeness
- Agreement between indicators
- Missing information
- Historical confidence
- Source reliability

Range

0-100

Confidence measures confidence in the **analysis**, not confidence that the trade will succeed.

---

# Historical Similarity

Question

> How similar is this setup to previous ones?

Potential Inputs

- Pattern matching
- Historical scans
- Similar catalysts
- Similar technical setups
- Similar volatility

Output

Similarity percentage.

Historical performance statistics.

---

# Overall Opportunity Score

The final score combines all dimensions.

It should never be a simple average.

Weights may evolve as the platform learns.

Example

Technical

82

Catalyst

94

Financial

61

Liquidity

85

Momentum

88

Dilution Risk

12

Promotion Risk

8

Confidence

91

↓

Overall Opportunity

89

The user should always be able to inspect every contributing score.

---

# Score Interpretation

Scores should always be accompanied by plain-language explanations.

Example

Technical Strength

89

Strong uptrend with increasing volume and a confirmed breakout above recent resistance.

---

# Risk Summary

Every report should include a dedicated risk section.

Possible risks

- Dilution
- Bankruptcy
- Low liquidity
- Promotion
- Insider selling
- Weak balance sheet
- High volatility

Risk deserves equal prominence to opportunity.

---

# Confidence

Confidence should decrease when:

- Data is missing.
- Sources disagree.
- Indicators conflict.
- Filings are unavailable.
- Market conditions are unusual.

High confidence should be earned.

---

# Calibration

Scores should be continuously evaluated.

Examples

- Do high technical scores outperform low ones?
- Does momentum matter?
- Which catalysts actually predict better outcomes?
- Which signals create false positives?

The scoring system should evolve based on measured performance rather than intuition.

---

# Explainability

Every score should answer:

- Why?
- Which factors helped?
- Which factors hurt?
- What information is missing?
- How certain is this evaluation?

The user should never need to guess.

---

# Future Enhancements

Potential additions

- Sector strength
- Macroeconomic score
- Seasonal score
- Insider confidence
- Institutional confidence
- AI confidence
- Portfolio fit
- User preference weighting

These should only be added if they provide measurable value.

---

# Final Principle

The scoring engine should never pretend to predict the future.

Its purpose is to organize evidence, quantify uncertainty, and help users make better-informed decisions.
