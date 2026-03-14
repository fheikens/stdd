
# STDD Metrics & Measurement
## Defining and Measuring Quality in Specification & Test-Driven Development

Author: Frank Heikens
Version: 1.0
Date: 2026

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. What Quality Means in STDD](#2-what-quality-means-in-stdd)
- [3. The Five Quality Metrics](#3-the-five-quality-metrics)
- [4. Specification Depth](#4-specification-depth)
- [5. Coverage Grade](#5-coverage-grade)
- [6. Regeneration Confidence](#6-regeneration-confidence)
- [7. Specification Stability](#7-specification-stability)
- [8. Defect Origin](#8-defect-origin)
- [9. Calculating a Quality Score](#9-calculating-a-quality-score)
- [10. Quality Anti-Metrics](#10-quality-anti-metrics)
- [11. Measuring Quality Across Teams](#11-measuring-quality-across-teams)
- [12. Relationship to Adoption Metrics](#12-relationship-to-adoption-metrics)
- [13. Conclusion](#13-conclusion)

---

# 1. Introduction

A common objection to STDD is that passing tests does not equal quality. Two implementations can both pass the same test suite, yet one can be superior to the other in performance, security, readability, or maintainability.

This objection is valid — but it targets the wrong layer.

In STDD, the test suite is not the quality definition. The specification is. If the specification does not mention performance, then performance is not part of the quality bar. If the specification does not define security constraints, then security is unverified. A shallow specification produces shallow verification — and any implementation that passes is "correct" only in the narrow sense of that shallow definition.

The solution is not to abandon specification-driven verification. The solution is to deepen the specification.

This document defines how to measure quality in STDD — not as an abstract aspiration, but as a set of concrete, trackable metrics that tell you whether your knowledge layer is strong enough to guarantee the behavior you care about.

---

# 2. What Quality Means in STDD

In traditional development, quality is often subjective. A senior engineer reviews the code and says "this looks good" or "this needs work." Quality lives in individual judgment.

STDD makes quality explicit and measurable. The quality bar is the specification. Everything that matters is written down as a numbered rule, an invariant, a failure condition, or a non-functional requirement. If it is written down, it is tested. If it is tested, it is verified on every build. If it is not written down, it is not part of the quality definition.

This creates a fundamental shift:

**Traditional:** Quality is assessed by reviewing the implementation.
**STDD:** Quality is assessed by reviewing the specification.

A poor specification with 100% test coverage gives false confidence. A comprehensive specification with 100% test coverage gives justified confidence. The metric that matters is not "do the tests pass?" but "does the specification capture everything that matters?"

This is the core insight: **quality in STDD is a property of the specification, not of the implementation.**

---

# 3. The Five Quality Metrics

STDD quality is measured across five dimensions:

| # | Metric | Question It Answers |
|---|--------|-------------------|
| 1 | **Specification Depth** | Does the specification capture all behavioral rules, invariants, failure conditions, and NFRs? |
| 2 | **Coverage Grade** | Is every specification element verified by at least one test? |
| 3 | **Regeneration Confidence** | Can a new implementation be generated from the specification alone and pass all tests? |
| 4 | **Specification Stability** | How often does the knowledge layer change relative to the implementation? |
| 5 | **Defect Origin** | When defects are found, are they specification gaps or implementation bugs? |

Each metric measures a different aspect of knowledge layer strength. Together, they define how much confidence you can place in the system's correctness.

---

# 4. Specification Depth

Specification Depth measures how thoroughly a specification captures the behavior that matters.

## What to Measure

For each feature under STDD, count the specification elements:

| Element | Description |
|---------|-------------|
| **Rules** | Numbered behavioral rules (e.g., FP-01, TR-05) |
| **Invariants** | Universal constraints that must hold across all scenarios |
| **Failure conditions** | Explicit definitions of how the system responds to invalid input, missing data, or error states |
| **NFRs** | Non-functional requirements: performance thresholds, security constraints, accessibility, data integrity |
| **Behavioral scenarios** | Given/When/Then scenarios covering normal paths, edge cases, and boundary values |

## Calculating Depth

```
Specification Depth = rules + invariants + failure conditions + NFRs
```

This is a raw count. A feature with 3 rules and no invariants has a depth of 3. A feature with 13 rules, 3 invariants, 3 failure conditions, and 4 NFRs has a depth of 23.

## Interpreting Depth

Depth alone does not guarantee quality — you can write 50 trivial rules. But shallow depth is a reliable signal of risk. A specification with only 3 rules for a feature that handles payments, errors, and concurrency is almost certainly incomplete.

Use depth comparatively:

- **Within a project:** Features with significantly lower depth than peers deserve review. Are rules missing, or is the feature genuinely simpler?
- **Over time:** Depth should increase as the team discovers edge cases, failure modes, and NFRs. A specification that never changes after the first draft is suspect.
- **Across teams:** Teams new to STDD tend to write shallow specifications. Depth improves with practice.

## Depth Targets

These are guidelines, not mandates. Every feature is different.

| Feature Complexity | Typical Depth |
|-------------------|---------------|
| Simple utility function | 5–10 |
| Business logic module | 10–20 |
| API endpoint with validation | 15–25 |
| Financial or safety-critical component | 25+ |

---

# 5. Coverage Grade

Coverage Grade measures the ratio of specified behavior that is actually verified by tests.

## Coverage States

Each specification element has one of three states:

| State | Definition |
|-------|-----------|
| **COVERED** | At least one test directly verifies this rule |
| **PARTIALLY COVERED** | A test exercises the rule indirectly but does not assert the specific behavior |
| **UNCOVERED** | No test verifies this rule |

## Calculating the Grade

```
Coverage Grade = COVERED / (COVERED + PARTIALLY COVERED + UNCOVERED)
```

Express as a percentage. 100% means every rule has at least one direct test.

## Interpreting Coverage

- **100% COVERED** — The target state. Every specified behavior is verified. Changes to the implementation that break any rule are caught by tests.
- **90–99% COVERED** — Acceptable during development. The remaining gaps should be documented and scheduled.
- **Below 90%** — The knowledge layer has significant gaps. Regeneration is risky because unverified behavior may silently change.
- **Any UNCOVERED NFR** — A red flag. Unverified non-functional requirements mean the quality constraints are aspirational, not enforced.

## Automating Coverage

The STDD traceability validator (`validate_traceability.py`) automates coverage checking:

```bash
python tools/validate_traceability.py --spec-dir features/ --test-dir tests/
```

This reports covered, missing, and orphaned test IDs. Integrate it into the CSI pipeline as Gate 1.

---

# 6. Regeneration Confidence

Regeneration Confidence is the most distinctive STDD quality metric. It answers: **can the implementation be discarded and regenerated from the specification alone, with the new implementation passing all tests?**

This is the metric that separates STDD from traditional testing. Passing tests against an existing implementation proves the code works. Passing tests against a *regenerated* implementation proves the specification is strong enough to reproduce the behavior.

## How to Measure

1. Take a feature with a passing test suite
2. Discard the implementation entirely
3. Generate a new implementation from the specification and tests (using AI or by hand)
4. Run the full test suite against the new implementation
5. Record the outcome

## Regeneration Outcomes

| Outcome | What It Means |
|---------|--------------|
| **Pass on first attempt** | Specification is precise and complete. The knowledge layer fully defines the behavior. |
| **Pass after prompt refinement** | Specification is correct but may need clearer language or decomposition. |
| **Pass after specification update** | The original specification had gaps — implicit rules were discovered. This is valuable; update the spec. |
| **Fail — cannot regenerate** | The knowledge layer does not capture the behavior. The specification needs significant strengthening. |

## Calculating Confidence

```
Regeneration Confidence = features passing regeneration / total features attempted
```

Track per feature, not per function. A feature with 5 functions where 4 regenerate and 1 fails has a regeneration confidence of 0 — the feature does not regenerate.

## Why This Metric Matters

Regeneration Confidence directly answers the quality objection. If two implementations both pass the same tests, are they equivalent? In STDD, the answer is yes — because the specification defines what "equivalent" means.

If the specification captures only basic behavior, two passing implementations might differ in security or performance. But that is a specification problem, not a methodology problem. Strengthen the specification. Add NFRs. Add invariants. Run regeneration again.

Regeneration Confidence is the feedback loop that drives specification improvement. Every failed regeneration reveals a gap in the knowledge layer. Fix the gap, and the specification becomes stronger.

## Practical Frequency

Full regeneration is not required on every build. Use it at these checkpoints:

- After writing a new specification (validates initial completeness)
- After significant specification changes (validates the update)
- Before migrating to a new language or framework (validates portability)
- Periodically as a health check (quarterly for mature features)

---

# 7. Specification Stability

Specification Stability measures how often the knowledge layer changes relative to the implementation layer.

## What to Measure

Track commits over time and classify each as:

| Commit Type | Description |
|-------------|-------------|
| **Spec change** | Modifies specifications, acceptance cases, or tests |
| **Implementation change** | Modifies code only |
| **Both** | Modifies specification and implementation together |

## Calculating Stability

```
Specification Stability = spec-only commits / total commits
```

Low stability (many spec changes) indicates the knowledge layer is still being discovered. This is normal during initial development.

High stability (few spec changes, many implementation changes) indicates the knowledge layer is mature. The specification has settled, and changes are happening at the implementation level — refactoring, optimization, regeneration.

## Interpreting Stability

- **Stability below 20%** — The knowledge layer is still being defined. Expected in the first weeks of a feature.
- **Stability 20–50%** — The specification is stabilizing. Some new rules are still being discovered, but the core behavior is defined.
- **Stability above 50%** — The knowledge layer is mature. Most changes are pure implementation. This is the target state for established features.

## The Stability Paradox

High stability is good for mature features — it means the specification is complete. But high stability for a *new* feature is suspicious. It may mean the team is changing the implementation without updating the specification, which leads to drift.

The CSI fingerprint gate (Gate 3) catches this. If the implementation changes but the fingerprint does not, the change is a pure refactoring. If the behavior changes but the fingerprint does not, a specification is missing.

---

# 8. Defect Origin

Defect Origin tracks where bugs come from — the specification or the implementation.

## Classification

When a defect is found (in testing, QA, or production), classify its root cause:

| Origin | Description | Action |
|--------|-------------|--------|
| **Specification gap** | The spec did not define this behavior. The implementation did something undefined. | Add the missing rule or invariant to the specification. Write a new test. |
| **Implementation bug** | The spec defined the behavior. The test existed. The implementation violated it. | Regenerate or fix the implementation. No spec change needed. |
| **Test gap** | The spec defined the behavior. No test verified it. The implementation was wrong. | Add the missing test. The specification was correct but unverified. |

## Why This Matters

Defect Origin reveals whether quality problems are in the knowledge layer or the code layer.

- **Mostly specification gaps** — The team needs to write deeper specifications. More rules, more invariants, more failure conditions.
- **Mostly implementation bugs** — The knowledge layer is strong. The implementations are weak. Regenerate more frequently or decompose further.
- **Mostly test gaps** — The specifications are good but the traceability matrix has holes. Improve Gate 1 enforcement.

Over time, a well-practiced STDD team sees defect origin shift from specification gaps (early) to implementation bugs (mature). When defects stop originating from the specification, the knowledge layer is comprehensive.

## Tracking

Maintain a simple defect log:

```
| Date | Feature | Defect Description | Origin | Resolution |
|------|---------|-------------------|--------|------------|
| 2026-03-10 | fingerprint | Build artifacts in hash | Spec gap | Added FP-01 exclusion rule |
| 2026-03-11 | traceability | False positive on example ID | Spec gap | Reworded TR-02..TR-05 |
```

Review the log monthly. If specification gaps dominate, invest in specification depth. If implementation bugs dominate, invest in regeneration frequency.

---

# 9. Calculating a Quality Score

The five metrics can be combined into a single quality score for reporting and comparison.

## Formula

```
Quality Score = (Depth Score × 0.15) + (Coverage Grade × 0.25) + (Regeneration Confidence × 0.35) + (Stability Score × 0.10) + (Defect Origin Score × 0.15)
```

## Component Scoring

Each component is normalized to a 0–1 scale:

| Metric | How to Normalize |
|--------|-----------------|
| **Depth Score** | `min(actual_depth / target_depth, 1.0)` where target_depth is the guideline for the feature's complexity class |
| **Coverage Grade** | Already a ratio (COVERED / total) |
| **Regeneration Confidence** | Ratio of features passing regeneration |
| **Stability Score** | `min(stability_ratio / 0.5, 1.0)` — normalized so that 50%+ stability maps to 1.0 |
| **Defect Origin Score** | `1 - (spec_gap_defects / total_defects)` — fewer spec-origin defects means higher score |

## Interpreting the Score

| Score | Interpretation |
|-------|---------------|
| **0.9–1.0** | The knowledge layer is comprehensive. Regeneration is safe. Quality is well-defined and verified. |
| **0.7–0.9** | The knowledge layer is solid with minor gaps. Most behavior is specified and verified. |
| **0.5–0.7** | Significant gaps exist. Some behavior is unspecified or untested. Regeneration carries risk. |
| **Below 0.5** | The knowledge layer is incomplete. Quality is aspirational, not verified. Priority: deepen specifications. |

## Weight Rationale

Regeneration Confidence carries the highest weight (0.35) because it is the most holistic measure — a feature that can be regenerated and pass all tests demonstrates that the entire knowledge layer works. Coverage Grade is next (0.25) because unverified rules are invisible risks. The remaining metrics provide supporting signal.

Teams may adjust weights to reflect their priorities. A safety-critical system might weight Depth and Coverage higher. A rapidly iterating startup might weight Regeneration Confidence and Stability higher.

---

# 10. Quality Anti-Metrics

Some commonly used metrics are misleading in an STDD context. Avoid optimizing for these.

## Lines of Code

Lines of code measures volume, not quality. In STDD, less code is often better — a regenerated implementation might be 30 lines where the original was 200. Both pass the same tests. The shorter one is not worse.

Tracking lines of code created per week is a productivity metric, not a quality metric. High volume with low specification depth produces large amounts of unverified behavior.

## Code Coverage Percentage

Code coverage (how many lines of code are exercised by tests) measures the wrong thing in STDD. A test can exercise every line of code without verifying any behavioral rule.

STDD uses *specification coverage* instead — how many specification rules are verified by tests. A feature can have 100% code coverage and 0% specification coverage if the tests exercise the code without asserting the specified behavior.

## Number of Tests

More tests do not mean more quality. A specification with 5 precise rules and 5 focused tests is stronger than a specification with 5 vague rules and 50 unfocused tests. Quality comes from specification precision, not test quantity.

## PR Count

The number of pull requests measures throughput, not quality. Ten PRs with shallow specifications are weaker than one PR with a comprehensive specification, full traceability, and a passing regeneration test.

---

# 11. Measuring Quality Across Teams

When multiple teams use STDD, quality metrics enable comparison and knowledge sharing.

## Dashboard

A team-level quality dashboard shows:

```
┌─────────────────────────────────────────────────────┐
│  Team: Payments                                     │
│                                                     │
│  Features under STDD:    12 / 18 (67%)              │
│  Avg Specification Depth: 17.3                      │
│  Coverage Grade:          96%                       │
│  Regeneration Confidence: 83% (10/12)               │
│  Specification Stability: 62%                       │
│  Defect Origin:           78% implementation        │
│                                                     │
│  Quality Score:           0.84                       │
└─────────────────────────────────────────────────────┘
```

## Cross-Team Comparisons

Compare quality scores across teams, not depth or coverage in isolation. A payments team with depth 25 and a utility team with depth 8 are not directly comparable — their feature complexity differs. But their quality scores are comparable because each metric is normalized to the feature's context.

## Sharing Lessons

When one team achieves high Regeneration Confidence and another does not, the gap is almost always in specification depth or precision. The high-performing team's specifications serve as examples for the struggling team.

This is a natural consequence of STDD: the knowledge layer is human-readable. Unlike implementation patterns, which are language- and framework-specific, specification patterns transfer across teams regardless of their tech stack.

---

# 12. Relationship to Adoption Metrics

The [Adoption Guide](adoption-guide.md), Section 11, defines metrics for tracking STDD rollout: Feature Coverage, Specification Completeness, Regeneration Success Rate, and Regression Frequency.

Those are **adoption metrics** — they measure how broadly and consistently STDD is used.

The metrics in this document are **quality metrics** — they measure how strong the knowledge layer is for features already under STDD.

The relationship:

| Adoption Metric | Quality Metric |
|----------------|---------------|
| Feature Coverage (how many features use STDD?) | Not a quality metric — it measures breadth |
| Specification Completeness (are all elements present?) | Specification Depth (how many elements, and are they sufficient?) |
| Regeneration Success Rate | Regeneration Confidence (same concept, formalized with outcomes) |
| Regression Frequency | Defect Origin (root cause analysis, not just frequency) |

Adoption metrics tell you *where you are* in the rollout. Quality metrics tell you *how good it is* where you've adopted.

Both are necessary. High adoption with low quality means the team is going through the motions without deepening specifications. High quality on few features means the methodology works but is not being applied broadly enough.

---

# 13. Conclusion

Quality in STDD is not subjective. It is defined by the specification and measured through five concrete metrics.

Specification Depth measures whether the knowledge layer captures all behavioral rules that matter. Coverage Grade measures whether those rules are verified. Regeneration Confidence measures whether the knowledge layer is strong enough to reproduce the behavior from scratch. Specification Stability measures whether the knowledge layer has matured. Defect Origin measures where quality problems come from.

Together, these metrics answer the fundamental question: **is the specification comprehensive enough to be the sole definition of correct behavior?**

If the answer is yes, the implementation is truly disposable. Any black box that passes the tests is, by definition, correct — because "correct" means "satisfies the specification," and the specification captures everything that matters.

If the answer is no, the specification needs deepening. Add rules. Add invariants. Add NFRs. Add failure conditions. Run regeneration again. Every gap you close makes the quality bar more explicit, more measurable, and more enforceable.

Quality is not what the code looks like. Quality is what the specification demands.

---

For the STDD methodology, see the [Method](method.md).

For specification writing guidance, see [Writing Specifications](writing-specifications.md).

For non-functional requirements, see [NFR Framework](nfr-framework.md).

For adoption and rollout, see [Adoption Guide](adoption-guide.md).
