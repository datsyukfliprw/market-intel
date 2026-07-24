# Project Market Intel Constitution

**Status:** Approved (Architecture v1.0)

**Purpose**

This Constitution defines the principles that govern the design, architecture, and evolution of Project Market Intel.

Technologies will change.

Providers will change.

Models will improve.

Strategies will evolve.

These principles are intended to remain stable.

When faced with difficult architectural decisions, this Constitution takes precedence over convenience.

---

# Article I: Purpose

Project Market Intel exists to help people make better financial decisions through trustworthy, explainable, and evidence-based market analysis.

The system is designed to collect information, organize evidence, evaluate opportunities, and communicate conclusions clearly.

Its purpose is not to predict the future with certainty.

Its purpose is to reduce uncertainty through disciplined analysis.

---

# Article II: Core Values

## Truth Over Convenience

The system must represent reality as accurately as possible.

When uncertainty exists, it should be acknowledged rather than hidden.

The application should prefer saying:

> "Insufficient evidence."

rather than inventing confidence.

---

## Evidence Before Opinion

Recommendations are conclusions drawn from evidence.

Evidence must always exist independently of the recommendation itself.

Every recommendation should be explainable by the data that produced it.

---

## Determinism Before Intelligence

Mathematical calculations, technical indicators, financial metrics, scoring, and historical performance must be deterministic.

Artificial intelligence may interpret evidence.

It must never replace evidence.

---

## Simplicity Before Cleverness

Elegant systems are usually composed of small, understandable parts.

Complexity should only be introduced when it solves a demonstrated problem.

Avoid abstractions that exist only because they might be useful someday.

---

## Long-Term Thinking

Every architectural decision should consider the future health of the project.

Temporary shortcuts are acceptable only when consciously acknowledged and documented.

Technical debt should never be created accidentally.

---

# Article III: Architectural Principles

## Single Responsibility

Every component should have one clear purpose.

Services orchestrate.

Repositories persist.

Providers retrieve external information.

Domain models represent business concepts.

Responsibilities should not overlap.

---

## Replaceable Infrastructure

External services must remain replaceable.

The domain should never depend directly upon a specific vendor.

Provider-specific logic belongs inside provider adapters.

---

## Domain First

The business model defines the software.

Databases, APIs, user interfaces, and external providers exist to serve the domain rather than shape it.

---

## Immutable History

Historical business records should be preserved whenever practical.

Snapshots represent observations.

Recommendations represent conclusions.

Outcomes represent measured results.

History should be append-only whenever possible.

---

## Explicit Boundaries

Dependencies should flow inward toward the domain.

Infrastructure should depend on business concepts.

Business concepts should never depend on infrastructure.

---

# Article IV: Data Principles

## Every Fact Has One Source of Truth

Each important concept should have exactly one authoritative owner.

Duplicate ownership creates inconsistency.

Derived values should be calculated rather than redundantly stored whenever practical.

---

## Point-in-Time Integrity

Historical analysis must use information that would have been available at that point in time.

Future information must never influence historical evaluation.

Backtesting must remain reproducible.

---

## Preserve Context

Every important record should answer:

- Where did this come from?
- When was it observed?
- Which provider supplied it?
- Which version produced it?

Without context, data loses meaning.

---

# Article V: Artificial Intelligence

Artificial intelligence is an advisor.

It is not the authority.

AI may:

- summarize evidence
- explain technical concepts
- compare competing signals
- generate research summaries
- communicate findings

AI may not become the source of truth for:

- market prices
- financial calculations
- technical indicators
- scoring
- portfolio accounting
- historical outcomes

The system must remain useful even if every AI service becomes unavailable.

---

# Article VI: Engineering Standards

## Architecture Before Implementation

Foundational decisions require architectural discussion before implementation.

Not every implementation requires architecture.

Every architecture deserves thoughtful implementation.

---

## Small Vertical Slices

The project should evolve through complete, well-tested vertical slices.

Each slice should deliver meaningful functionality while strengthening the foundation for future work.

---

## Test Behavior

Tests should verify business behavior rather than implementation details.

Refactoring should rarely require rewriting tests.

---

## Documentation Matters

Significant architectural decisions should be documented.

Future developers should understand not only _what_ was built, but _why_ it exists.

---

# Article VII: Review Standards

Every significant implementation should answer:

- Does this match the approved architecture?
- Does it respect domain invariants?
- Does it reduce or increase coupling?
- Does it remain understandable?
- Does it support future milestones?
- Can another developer maintain it confidently?

Working code is necessary.

Maintainable code is the objective.

---

# Article VIII: Product Philosophy

Project Market Intel is not designed to replace human judgment.

It exists to strengthen it.

The application should help users think more clearly, ask better questions, and understand the evidence supporting every conclusion.

Recommendations should encourage informed decision-making rather than blind trust.

Transparency builds confidence.

Opacity destroys it.

---

# Article IX: Continuous Improvement

The architecture should evolve deliberately.

When a better design is discovered:

- discuss it,
- document it,
- implement it intentionally.

Do not allow architecture to drift through accidental changes.

Progress should be evolutionary rather than chaotic.

---

# Article X: Stewardship

The codebase is a long-term asset.

Every contributor shares responsibility for protecting it.

Future maintainers deserve software that is understandable.

Future users deserve software that is trustworthy.

Future versions deserve foundations that remain strong.

Whenever faced with competing choices, prefer the decision that leaves the project healthier than it was before.

---

# Engineering Creed

Before introducing a new abstraction, ask:

> Is this solving today's problem or anticipating tomorrow's?

Before introducing complexity, ask:

> Can the same result be achieved more simply?

Before accepting a shortcut, ask:

> Will this make the project easier or harder to evolve?

Before merging a change, ask:

> Would I be comfortable building the next five years of this project on top of this decision?

If the answer is no, continue designing.

If the answer is yes, build with confidence.

---

# Closing Principle

Project Market Intel is built on the belief that disciplined engineering and disciplined analysis reinforce one another.

Vision without architecture becomes chaos.

Architecture without vision becomes elegant software that nobody wants.

The purpose of this Constitution is to preserve both.
