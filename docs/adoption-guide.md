
# Adopting STDD
## A Migration Guide for Existing Teams

Author: Frank Heikens
Version: 1.1
Date: 2026

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. Prerequisites](#2-prerequisites)
- [3. Starting Small](#3-starting-small)
- [4. The First STDD Feature](#4-the-first-stdd-feature)
- [5. Migration Example: Shipping Cost Calculator](#5-migration-example-shipping-cost-calculator)
- [6. Adoption Timeline](#6-adoption-timeline)
- [7. Migrating Existing Features](#7-migrating-existing-features)
  - [Forks and Divergence from Upstream](#forks-and-divergence-from-upstream)
- [8. Introducing the CI Pipeline](#8-introducing-the-ci-pipeline)
- [9. Team Transition](#9-team-transition)
- [10. Common Objections](#10-common-objections)
- [11. Measuring Progress](#11-measuring-progress)
- [12. What Not to Do](#12-what-not-to-do)
- [13. Retrospective Checklist](#13-retrospective-checklist)

---

# 1. Introduction

STDD is most naturally applied to new projects where specifications and tests can be written before any implementation exists. But most teams do not have the luxury of starting from scratch. They have existing systems, existing tests (or no tests), and existing processes.

This guide describes how to adopt STDD incrementally, starting with a single feature and expanding over time.

The key principle: **STDD is adopted one feature at a time, not one system at a time.**

---

# 2. Prerequisites

Before adopting STDD, a team needs:

**A test runner.** STDD requires automated tests. If the team does not have a test framework configured, set one up first. Any standard framework works: pytest, Jest, Go testing, JUnit.

**Version control.** Specifications and tests are versioned alongside code. Git is the standard choice.

**CI pipeline (optional but recommended).** Continuous integration makes STDD's feedback loop fast. But you can start without it and add it later.

**Willingness to write specifications before code.** This is the cultural shift. Everything else is tooling.

---

# 3. Starting Small

Do not attempt to convert an entire system to STDD at once. This fails for the same reason that rewriting a system from scratch fails: the scope is too large, the team loses momentum, and the effort is abandoned.

Instead, pick a single upcoming feature — something the team was going to build anyway — and apply STDD to that feature.

## Choosing the First Feature

Good candidates for a first STDD feature:

- **New functionality** that does not depend heavily on existing code
- **A clearly defined scope** with known inputs, outputs, and rules
- **Business logic**, not infrastructure (no database migrations, no deployment scripts)
- **Something small enough** to complete in one sprint

Bad candidates:

- A cross-cutting refactoring that touches everything
- Infrastructure or configuration changes
- A feature that requires understanding undocumented legacy behavior

---

# 4. The First STDD Feature

The first feature follows the standard STDD workflow. This is also a learning exercise for the team.

## Step 1: Write the Specification

Define the feature in precise terms:

- What does it do?
- What are the inputs?
- What are the outputs?
- What constraints apply?
- What are the failure conditions?

Write behavioral scenarios in Given/When/Then form. Write invariants. Define acceptance cases.

Use the templates in [Writing Specifications](writing-specifications.md).

## Step 2: Write the Tests

Translate each behavioral scenario into a test. Translate invariants into property tests. Map every test to a specification ID.

At this point, all tests fail. No implementation exists yet.

## Step 3: Generate the Implementation

Give AI the specification and the failing test suite. Let it generate an implementation. Run the tests.

If tests fail, refine the prompt. Do not change the tests.

## Step 4: Review

The team reviews:

- Are the specifications precise enough?
- Do the tests cover all scenarios?
- Does the traceability matrix have gaps?
- Did AI generate correct code, or did it require multiple attempts?

This review produces lessons for the next STDD feature.

---

# 5. Migration Example: Shipping Cost Calculator

Before migrating an existing feature, it helps to see what the full process looks like. This section walks through a complete migration of a small but realistic function.

## The Legacy Code

The team finds this function in the codebase. It has no tests. It has no documentation beyond the function signature.

```python
def calculate_shipping(weight, destination, express=False):
    if destination == "domestic":
        rate = 5.0
    elif destination == "international":
        rate = 15.0
    else:
        rate = 10.0

    cost = weight * rate
    if express:
        cost *= 1.5
    if cost < 5.0:
        cost = 5.0  # minimum charge
    return round(cost, 2)
```

Twenty lines of code. No tests, no specification, and one undocumented business rule buried in line 12: a minimum charge of $5.00.

## Step 1: Extract the Specification

Read the code and document what it does. Every branch, every edge case, every implicit rule.

**Specification: Shipping Cost Calculator**

| ID | Element | Description |
|----|---------|-------------|
| SC-1 | Input: weight | Numeric, the package weight in kilograms |
| SC-2 | Input: destination | String, one of "domestic", "international", or other |
| SC-3 | Input: express | Boolean, default false |
| SC-4 | Rule: domestic rate | Domestic shipments use a rate of $5.00/kg |
| SC-5 | Rule: international rate | International shipments use a rate of $15.00/kg |
| SC-6 | Rule: default rate | Unrecognized destinations use a rate of $10.00/kg |
| SC-7 | Rule: express multiplier | Express shipping multiplies the cost by 1.5 |
| SC-8 | Rule: minimum charge | The final cost is never less than $5.00 |
| SC-9 | Output | Numeric, rounded to 2 decimal places |
| SC-10 | Failure: invalid weight | Weight must be a positive number |

Note that SC-8 (minimum charge) was not documented anywhere. It was only visible by reading the code. This is exactly the kind of implicit knowledge that migration surfaces.

SC-10 (invalid weight) is not handled in the legacy code at all — it would silently compute nonsensical results for negative weights. The specification makes this gap visible.

## Step 2: Behavioral Scenarios

```gherkin
Scenario: Domestic standard shipping
  Given a package weighing 3.0 kg
  And destination is "domestic"
  And express is false
  When shipping cost is calculated
  Then the cost is $15.00

Scenario: International standard shipping
  Given a package weighing 2.0 kg
  And destination is "international"
  And express is false
  When shipping cost is calculated
  Then the cost is $30.00

Scenario: Domestic express shipping
  Given a package weighing 4.0 kg
  And destination is "domestic"
  And express is true
  When shipping cost is calculated
  Then the cost is $30.00

Scenario: Minimum charge applies
  Given a package weighing 0.5 kg
  And destination is "domestic"
  And express is false
  When shipping cost is calculated
  Then the cost is $5.00 (minimum charge overrides calculated $2.50)

Scenario: Unrecognized destination uses default rate
  Given a package weighing 2.0 kg
  And destination is "mars"
  And express is false
  When shipping cost is calculated
  Then the cost is $20.00

Scenario: Express with minimum charge
  Given a package weighing 0.3 kg
  And destination is "domestic"
  And express is true
  When shipping cost is calculated
  Then the cost is $5.00 (minimum charge overrides calculated $2.25)
```

## Step 3: Invariants

```
INV-1: Shipping cost is always >= $5.00
INV-2: Shipping cost is always a non-negative number
INV-3: Express shipping cost >= standard shipping cost for same weight and destination
```

## Step 4: Tests Against the Existing Code

Write the tests and run them against the legacy implementation. Every test must pass. If a test fails, the specification is wrong — the code defines current behavior.

```python
def test_domestic_standard():
    assert calculate_shipping(3.0, "domestic") == 15.00

def test_international_standard():
    assert calculate_shipping(2.0, "international") == 30.00

def test_domestic_express():
    assert calculate_shipping(4.0, "domestic", express=True) == 30.00

def test_minimum_charge_applies():
    assert calculate_shipping(0.5, "domestic") == 5.00

def test_unrecognized_destination():
    assert calculate_shipping(2.0, "mars") == 20.00

def test_express_with_minimum_charge():
    assert calculate_shipping(0.3, "domestic", express=True) == 5.00

def test_rounding():
    assert calculate_shipping(1.333, "domestic") == 6.67

# Invariant tests
def test_cost_never_below_minimum(weight, destination, express):
    """Property test: cost is always >= 5.00 for any valid input."""
    cost = calculate_shipping(weight, destination, express)
    assert cost >= 5.00

def test_express_never_cheaper(weight, destination):
    """Property test: express is never cheaper than standard."""
    standard = calculate_shipping(weight, destination, express=False)
    express = calculate_shipping(weight, destination, express=True)
    assert express >= standard
```

All tests pass against the existing implementation.

## Step 5: Traceability Matrix

| Spec ID | Test |
|---------|------|
| SC-4 | test_domestic_standard |
| SC-5 | test_international_standard |
| SC-6 | test_unrecognized_destination |
| SC-7 | test_domestic_express |
| SC-8 | test_minimum_charge_applies, test_express_with_minimum_charge |
| SC-9 | test_rounding |
| INV-1 | test_cost_never_below_minimum |
| INV-3 | test_express_never_cheaper |

## Step 6: Regeneration Attempt

**First attempt:** The specification was provided to an AI model along with the test suite. The generated implementation correctly handled rates and express multipliers but did not apply the minimum charge. Three tests failed: `test_minimum_charge_applies`, `test_express_with_minimum_charge`, and `test_cost_never_below_minimum`.

The cause was clear: the specification listed the minimum charge rule (SC-8), but the prompt did not emphasize it as a post-calculation constraint. The AI treated it as a note rather than a rule.

**Second attempt:** The specification was strengthened. SC-8 was rewritten from "The final cost is never less than $5.00" to "After all calculations (rate * weight * express multiplier), if the result is less than $5.00, the cost is set to $5.00. This minimum charge applies regardless of weight, destination, or express status." The AI generated a correct implementation. All tests passed.

## Lesson Learned

Migration reveals undocumented behavior. The minimum charge was implicit in the code — a single conditional buried on line 12 — but existed in no documentation, no requirements document, no ticket. Without reading the code line by line, this rule would have been lost during regeneration.

This is the value of the migration process: it forces every business rule into the specification, where it can be verified by tests and communicated to any future implementation — human or AI.

---

# 6. Adoption Timeline

Adopting STDD takes practice. The first feature is the slowest because the team is learning the workflow, not just building the feature. This timeline sets realistic expectations for a team's first eight weeks.

## Weeks 1-2: First Feature — Specification

- Choose the first feature using the criteria in Section 3
- Write the specification as a team — this is a group exercise for the first feature
- Hold a specification review where team members challenge the precision of each rule, scenario, and failure condition
- Goal: a complete specification with behavioral scenarios, invariants, and a specification ID scheme

Writing the first specification takes longer than expected. This is normal. The team is building a new skill.

## Weeks 3-4: First Feature — Tests and Generation

- Translate the specification into tests, one test per scenario
- Build the traceability matrix
- Feed the specification and tests to AI and generate the implementation
- Iterate: when tests fail, refine the prompt or decompose the component — do not change the tests
- Goal: a working implementation that passes all tests, generated from the specification

Expect 2-4 generation attempts for the first feature. The team is learning what level of specification precision AI requires.

## Week 5: Retrospective

- Review what worked and what did not
- Identify where the specification was too vague (AI generated wrong behavior)
- Identify where tests were missing (behavior was unverified)
- Document lessons for the second feature
- Use the Retrospective Checklist in Section 13

## Weeks 6-8: Second Feature + First Migration

- Apply STDD to a second new feature — this one goes faster because the team knows the workflow
- In parallel, begin migrating one existing feature using the process in Section 7 and the example in Section 5
- Goal: two features under STDD (one new, one migrated) by the end of week 8

By the third feature, specification writing feels natural. The team spends less time debating format and more time debating behavior, which is the productive outcome.

## Effort Estimates

For a single well-scoped function (approximately 50 lines of implementation):

| Activity | Approximate Time |
|----------|-----------------|
| Specification writing | ~30 minutes |
| Test writing | ~45 minutes |
| AI generation + iteration | ~30 minutes |
| Review and refinement | ~15 minutes |

A complete feature with 3-5 functions takes approximately 1-2 days of STDD work. This includes the specification, all tests, generation, and review.

These estimates assume the team has completed at least one STDD feature. The first feature takes roughly twice as long while the team learns the workflow.

---

# 7. Migrating Existing Features

After the team is comfortable with STDD on new features, existing features can be migrated gradually.

## When to Migrate

Migrate an existing feature when:

- It needs to be modified (new requirement, bug fix)
- It has poor or no test coverage
- It is a candidate for regeneration (tech debt, language migration)

Do not migrate features that are stable and not being changed. That is unnecessary work.

## The Migration Process

1. **Document the current behavior.** Read the code and write a specification for what it does now. Include edge cases and failure conditions.

2. **Write tests for the current behavior.** The tests must pass against the existing implementation. If a test fails, the specification is wrong — the existing code defines the current behavior.

3. **Verify completeness.** Run code coverage to check that the tests exercise all paths. Add tests for any uncovered paths.

4. **Create the traceability matrix.** Map every specification ID to its tests.

5. **Validate by regeneration (optional).** Discard the implementation, give AI the specification and tests, and see if the generated code passes all tests. If it does, the specification is strong enough for STDD. If it does not, strengthen the specification and add more tests.

At this point, the feature is under STDD control. Future behavioral changes start with a specification update. Bug fixes where the specification already defines the correct behavior can proceed directly — see the [Core Model](stdd-core-model.md) execution flows.

This migration process corresponds to the **Discovery and Reverse Engineering** execution flow defined in the [Core Model](stdd-core-model.md), Section 5.4. For architectural guidance on handling tightly coupled components, global state, and other brownfield challenges, see [Architecture](architecture.md), Section 10.

## Forks and Divergence from Upstream

Forks deserve special attention. A fork inherits an entire body of behavior from upstream, and any divergence — intentional or accidental — is a place where compatibility claims can drift away from reality. STDD applies a stricter rule for forks: every behavior changed from upstream is classified, and compatibility is never inferred from internal structure.

For each behavioral rule in the fork's specification, classify it as one of the categories defined in [Core Model](stdd-core-model.md), Section 6.6:

- **Compatibility-preserving** — produces the same observable result as upstream.
- **Intentional breaking change** — diverges deliberately, with a documented reason.
- **Security hardening** — diverges to close a vulnerability or tighten a guarantee.
- **Migration risk** — diverges in a way that may require existing users to migrate data, configuration, or workflow.
- **Implementation-only change** — internals changed; no externally observable behavior changed.

Record the classification in the specification metadata for each affected rule. The classification is part of the specification, not a side note.

**Compatibility-preserving status requires test evidence.** A rule classified compatibility-preserving must be backed by at least one test that proves the equivalence — typically by loading an upstream-produced artifact (configuration file, data file, backup, on-disk format, message format) and asserting the fork produces the same observable outcome. Without that test, downgrade to migration risk and document what would need to change for users.

**What does not count as compatibility evidence:**

- Unchanged constants, type names, filenames, or function signatures.
- An implementation that "looks the same" as upstream.
- A unit test of an internal helper that has the same name as upstream's helper.
- Helper-level tests that exercise a parser, decoder, or formatter in isolation when the requirement is about the externally observable round-trip.

These are inspection artifacts, not test evidence. The Core Model coverage rules (Section 6.4) apply: a compatibility-preserving rule that names an externally observable surface needs a test against that surface, and an unverified channel keeps the row at PARTIALLY COVERED.

This applies symmetrically to security hardening claims. A security hardening rule that names redaction across logs, stderr, stdout, argv, and trace output is COVERED only when each of those channels has direct test evidence. A test against one channel makes the rule PARTIALLY COVERED with the others listed as NOT COVERED / FUTURE WORK.

---

# 8. Introducing the CI Pipeline

Once several features are under STDD, introduce Continuous Specification Integrity (CSI) into the CI pipeline.

## Minimal Pipeline

Start with two gates:

1. **Test execution**: all tests pass
2. **Traceability validation**: every specification ID has at least one test

This catches the most common failures: broken implementations and untested specifications.

## Full Pipeline

Add the third gate when the team is ready:

3. **Specification Fingerprint**: detect when specifications change without test updates, or tests change without specification updates

See [Engineering Playbook](engineering-playbook.md), Section 5, for implementation details and a GitHub Actions example.

## Incremental Adoption

The CI pipeline only validates features that have STDD specifications. Legacy features without specifications are not blocked by the pipeline — they continue to be tested by whatever test coverage they have.

As more features migrate to STDD, the pipeline covers more of the system.

## Handling Partial Adoption

During the transition period, the codebase contains both STDD and non-STDD code. The CI pipeline must handle this cleanly.

**Scoped validation.** The CI pipeline only runs STDD validation — traceability checks, fingerprint verification — on directories that contain specifications. If a directory has no specification files, the pipeline skips STDD validation for that directory entirely. Non-STDD code continues to run whatever test coverage it already has.

**Mixed PRs.** Some pull requests touch both STDD and non-STDD code. This is normal during transition. The pipeline applies STDD validation only to the STDD portions. The non-STDD portions are validated by existing test suites without STDD-specific gates.

**Non-STDD dependencies.** When an STDD feature depends on a non-STDD component, treat the non-STDD component as an external dependency. Define its contract in the STDD specification: what does the STDD feature expect from the dependency? What inputs does it provide? What outputs does it expect? What error conditions does it handle?

Write tests against this contract. If the non-STDD component changes and breaks the contract, the STDD tests catch it.

**Contract-to-specification migration.** Over time, as non-STDD components are migrated to STDD, the contracts defined by dependent features become the starting point for the component's own specification. The contract says "this is what we expect from it." The specification says "this is what it does." When both align, the migration is validated.

This approach avoids the all-or-nothing trap. The system can run with partial STDD coverage indefinitely, with the coverage expanding as features are migrated.

---

# 9. Team Transition

STDD changes how team members work. The transition should be explicit, not assumed.

## New Skills

**Writing specifications.** Most developers are not trained to write precise behavioral specifications. This is the most important skill to develop. The [Writing Specifications](writing-specifications.md) guide provides templates, but practice is the real teacher.

**Thinking in Given/When/Then.** Behavioral scenarios force precision. Instead of "the system should handle errors," a specification says "Given a seat that is already held, when another customer attempts to hold the same seat, then an error is returned with message 'Seat is not available'." This level of precision takes practice.

**Reading test failures diagnostically.** When AI generates code that fails tests, the team needs to diagnose whether the problem is in the specification (ambiguous), the prompt (insufficient context), or the decomposition (too complex for AI to handle). See [Method](method.md), Section 11, for guidance.

## Changed Roles

**Developers** spend more time writing specifications and tests, less time writing implementation code. The implementation is generated. The human value is in defining the correct behavior.

**QA/Test engineers** become specification reviewers. They validate that specifications are complete, that tests are faithful to specifications, and that the traceability matrix has no gaps.

**Tech leads** review the knowledge layer first, implementation second. A PR in STDD is judged primarily by the quality of its specifications and tests.

## Common Resistance

Some team members will resist writing specifications before code. Common reasons:

- "It's faster to just write the code." It may be faster for the first implementation, but it is slower for every subsequent change, bug fix, and regeneration.
- "I know what the code should do — I don't need to write it down." Implicit knowledge is the leading cause of bugs in software. Making it explicit is the point.
- "AI can figure it out from the code." AI can generate code that looks correct. Without tests, there is no way to verify it.

The best response is the first STDD feature. When the team sees AI generate a correct implementation from specifications and tests — and then sees the same tests catch a bug when the implementation is changed — the value becomes concrete.

---

# 10. Common Objections

## "We already do TDD"

TDD writes tests before code. STDD writes specifications before tests. The specification layer captures intent, constraints, invariants, and failure conditions that tests alone do not express. TDD is a subset of STDD.

If the team already practices TDD, the transition is smaller: add specifications above the tests, add a traceability matrix, and introduce the regeneration mindset.

## "Our system is too complex for specifications"

If a system is too complex to specify, it is too complex to test correctly, and too complex to maintain. The complexity is the problem, not the specification.

STDD's decomposition discipline — every function fits in approximately 50 lines, every component has a clear responsibility — naturally reduces complexity. Adopt it incrementally, one feature at a time.

## "AI-generated code is not reliable enough"

AI reliably generates correct implementations for well-specified functions under approximately 50 lines. It struggles with large, under-specified, or tightly coupled code. STDD forces the decomposition that makes AI generation reliable.

If AI cannot generate a correct implementation, the specification needs strengthening or the component needs further decomposition. See [Method](method.md), Section 11.

## "We don't have time to write specifications"

You don't have time not to. Every hour spent on a specification saves multiple hours in debugging, rework, and regression fixing. Specifications are the investment; reliable software is the return.

## "What about performance-critical code?"

Performance is specified through NFRs. Benchmark tests verify performance thresholds. AI-generated code that passes functional tests but fails performance benchmarks is rejected and regenerated with performance constraints added to the prompt. See [NFR Framework](nfr-framework.md).

---

# 11. Measuring Progress

Track adoption progress to demonstrate value and identify gaps.

## Feature Coverage

How many features have STDD specifications versus total features? This is the primary adoption metric.

```
STDD coverage = features with specifications / total features
```

Start tracking this when you begin migration. The goal is not 100% immediately — it is steady progress.

## Specification Completeness

For features under STDD, how complete are the specifications?

- Does every feature have behavioral scenarios?
- Does every scenario have a test?
- Is the traceability matrix complete (no untested specs, no orphaned tests)?
- Are invariants defined and tested?
- Are failure conditions specified and tested?

## Regeneration Success Rate

When a component is regenerated, does AI produce a passing implementation on the first attempt?

A low success rate indicates specifications need strengthening. A high success rate indicates the knowledge layer is strong.

## Regression Frequency

How often do changes break existing behavior? In a well-adopted STDD system, regressions are caught by tests before they reach production. Track how often a PR's test suite catches a regression versus how often a regression is found in production.

---

# 12. What Not to Do

**Do not mandate STDD for the entire codebase on day one.** Adopt incrementally.

**Do not write specifications for stable code that is not changing.** Prioritize code that is actively being modified.

**Do not skip the specification and go straight to tests.** Tests without specifications lose the "why." The specification captures intent; the test captures behavior. Both are necessary.

**Do not let AI write the specifications.** AI generates implementations. Humans define behavior. If AI writes the specification, no one has verified that the specification captures the intended behavior.

**Do not regenerate without running the full test pyramid.** A regenerated component may pass unit tests while breaking integration tests. Always run tests at all levels.

**Do not weaken tests to accommodate AI limitations.** If AI cannot satisfy a test, strengthen the prompt or decompose the component. The test represents the specification. It does not change to accommodate a flawed implementation.

For a comprehensive catalog of these and other STDD mistakes, see [Anti-Patterns](../reference/anti-patterns.md).

---

# 13. Retrospective Checklist

After completing each STDD feature, the team should conduct a structured review. This checklist ensures the team captures lessons and improves the process for the next feature.

## Specification Quality

- Was the specification precise enough for AI to generate correct code on the first attempt?
- Which constraints were missing from the initial specification?
- Were all failure conditions identified before writing tests?
- Did the specification use unambiguous language, or did AI misinterpret any rules?
- Would a developer unfamiliar with the feature understand the specification without reading the code?

## Test Coverage

- Did the tests cover all behavioral scenarios in the specification?
- Were any edge cases discovered during generation that were not in the specification?
- Is the traceability matrix complete — every specification ID has at least one test, and every test maps to a specification ID?
- Are invariants tested with property-based tests, not just example-based tests?
- Did code coverage reveal any untested paths?

## AI Generation

- How many generation attempts were needed before all tests passed?
- What caused failures — ambiguous specification, missing context, or component too large?
- Would further decomposition have reduced the number of attempts?
- Did the AI introduce any behavior not in the specification? If so, was it caught by the tests?
- Is the generated code readable, or does it need restructuring before review?

## Process

- How long did each step take — specification writing, test writing, generation, review?
- What would the team do differently next time?
- Is the specification strong enough to survive regeneration by a different AI model?
- Did the team discover business rules that were previously undocumented?
- Are there reusable patterns from this feature that should be captured for future specifications?

Use this checklist in the Week 5 retrospective (Section 6) and after every subsequent STDD feature. Over time, the team will develop intuition for what makes a strong specification, and the checklist becomes a quick confirmation rather than a discovery exercise.

---

# Conclusion

Adopting STDD is a gradual process. Start with one feature, learn the workflow, migrate existing features as they are modified, and introduce CI enforcement as the team builds confidence.

The investment is in the knowledge layer: specifications and tests that define system behavior. The return is a system that can be safely regenerated, reliably tested, and clearly understood.

---

For the step-by-step methodology, see the [Method](method.md).

For specification types, lifecycle states, and execution flows (including the bug-fix and discovery flows), see the [Core Model](stdd-core-model.md).

For guidance on writing specifications, see [Writing Specifications](writing-specifications.md).

For CI pipeline setup, see [Engineering Playbook](engineering-playbook.md).

For a complete worked example, see [Seat Reservation API](../examples/seat-reservation.md).
