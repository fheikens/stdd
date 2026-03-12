
# Adopting STDD
## A Migration Guide for Existing Teams

Author: Frank Heikens
Version: 1.0
Date: 2026

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. Prerequisites](#2-prerequisites)
- [3. Starting Small](#3-starting-small)
- [4. The First STDD Feature](#4-the-first-stdd-feature)
- [5. Migrating Existing Features](#5-migrating-existing-features)
- [6. Introducing the CI Pipeline](#6-introducing-the-ci-pipeline)
- [7. Team Transition](#7-team-transition)
- [8. Common Objections](#8-common-objections)
- [9. Measuring Progress](#9-measuring-progress)
- [10. What Not to Do](#10-what-not-to-do)

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

# 5. Migrating Existing Features

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

At this point, the feature is under STDD control. Future changes start with a specification update.

For architectural guidance on handling tightly coupled components, global state, and other brownfield challenges, see [Architecture](architecture.md), Section 10.

---

# 6. Introducing the CI Pipeline

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

---

# 7. Team Transition

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

# 8. Common Objections

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

# 9. Measuring Progress

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

# 10. What Not to Do

**Do not mandate STDD for the entire codebase on day one.** Adopt incrementally.

**Do not write specifications for stable code that is not changing.** Prioritize code that is actively being modified.

**Do not skip the specification and go straight to tests.** Tests without specifications lose the "why." The specification captures intent; the test captures behavior. Both are necessary.

**Do not let AI write the specifications.** AI generates implementations. Humans define behavior. If AI writes the specification, no one has verified that the specification captures the intended behavior.

**Do not regenerate without running the full test pyramid.** A regenerated component may pass unit tests while breaking integration tests. Always run tests at all levels.

**Do not weaken tests to accommodate AI limitations.** If AI cannot satisfy a test, strengthen the prompt or decompose the component. The test represents the specification. It does not change to accommodate a flawed implementation.

For a comprehensive catalog of these and other STDD mistakes, see [Anti-Patterns](../reference/anti-patterns.md).

---

# Conclusion

Adopting STDD is a gradual process. Start with one feature, learn the workflow, migrate existing features as they are modified, and introduce CI enforcement as the team builds confidence.

The investment is in the knowledge layer: specifications and tests that define system behavior. The return is a system that can be safely regenerated, reliably tested, and clearly understood.

---

For the step-by-step methodology, see the [Method](method.md).

For guidance on writing specifications, see [Writing Specifications](writing-specifications.md).

For CI pipeline setup, see [Engineering Playbook](engineering-playbook.md).

For a complete worked example, see [Seat Reservation API](../examples/seat-reservation.md).
