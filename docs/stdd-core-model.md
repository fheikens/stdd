# STDD Core Model
## Specification Taxonomy, Test Taxonomy, Artifact Lifecycle, Execution Flows, and Traceability

Author: Frank Heikens
Version: 1.1
Date: 2026

---

## Table of Contents

- [1. Purpose](#1-purpose)
- [2. Specification Taxonomy](#2-specification-taxonomy)
  - [2.1 Behavioral Specification](#21-behavioral-specification)
  - [2.2 Integration Mapping](#22-integration-mapping)
  - [2.3 Configuration Decision](#23-configuration-decision)
  - [2.4 Specification Type Summary](#24-specification-type-summary)
- [3. Test Taxonomy](#3-test-taxonomy)
  - [3.1 Requirement Test](#31-requirement-test)
  - [3.2 Integration Test](#32-integration-test)
  - [3.3 Regression Artifact](#33-regression-artifact)
  - [3.4 Test Type Summary](#34-test-type-summary)
- [4. Artifact Lifecycle](#4-artifact-lifecycle)
  - [4.1 Lifecycle States](#41-lifecycle-states)
  - [4.2 State Transitions](#42-state-transitions)
  - [4.3 Supersession](#43-supersession)
  - [4.4 Handling Stale Artifacts](#44-handling-stale-artifacts)
- [5. Execution Flows](#5-execution-flows)
  - [5.1 New Feature](#51-new-feature)
  - [5.2 Behavior Change](#52-behavior-change)
  - [5.3 Bug Fix (Spec Already Correct)](#53-bug-fix-spec-already-correct)
  - [5.4 Discovery and Reverse Engineering](#54-discovery-and-reverse-engineering)
  - [5.5 Flow Summary](#55-flow-summary)
- [6. Traceability Rules](#6-traceability-rules)
  - [6.1 Core Rules](#61-core-rules)
  - [6.2 Traceability Matrix Structure](#62-traceability-matrix-structure)
  - [6.3 Lifecycle Visibility](#63-lifecycle-visibility)
  - [6.4 Coverage Categories](#64-coverage-categories)
  - [6.5 AI-Agent Coverage Discipline](#65-ai-agent-coverage-discipline)
  - [6.6 Brownfield and Fork Compatibility](#66-brownfield-and-fork-compatibility)
- [7. Metadata Convention](#7-metadata-convention)
  - [7.1 Specification Metadata](#71-specification-metadata)
  - [7.2 Examples](#72-examples)
  - [7.3 Adoption](#73-adoption)

---

# 1. Purpose

This document defines the core model underlying STDD. It provides explicit definitions for the kinds of specifications, the kinds of tests, the lifecycle of artifacts, the execution flows for common development scenarios, and the rules that govern traceability.

The goal is to reduce ambiguity for teams adopting STDD by making the model concrete and teachable. Previous STDD documents describe specifications and tests in general terms. This document differentiates them into named categories with distinct purposes, rules, and expectations.

This is a reference document, not a tutorial. For the philosophy, see the [Manifesto](../manifesto.md). For the practical workflow, see the [Method](method.md). For how to write specifications, see [Writing Specifications](writing-specifications.md).

---

# 2. Specification Taxonomy

STDD recognizes three types of specification. Each type serves a different purpose and carries different obligations.

## 2.1 Behavioral Specification

A behavioral specification defines what the system must do. It is the heart of STDD.

**Purpose:** Capture intended system behavior as precise, testable rules. Behavioral specifications are the authoritative definition of correctness.

**When it must be written:** Before implementation begins for new features and behavior changes. Before tests are written. A behavioral specification is required for any functionality that has observable behavior.

**Authoritative:** Yes. The behavioral specification is the single source of truth for what the system should do. When a test and a behavioral specification disagree, the specification is reviewed first — it may need correction, but it is never silently overruled by a test or implementation.

**Tests mandatory:** Yes. Every rule, invariant, and failure condition in a behavioral specification must be verified by at least one requirement test. A behavioral specification without tests is incomplete.

**Expected level of detail:** Every behavioral specification must answer the six questions defined in [Writing Specifications](writing-specifications.md), Section 3: what does the system do, what are the inputs and outputs, what are the behavioral scenarios, what are the invariants, what are the failure conditions, and what are the constraints. Rules must be numbered, unambiguous, and independently testable.

**Examples:**
- A feature specification for a discount calculator: inputs, outputs, discount tiers, boundary behavior, invariants ("discount never exceeds total"), failure conditions ("negative amount rejected").
- A unit specification for `calculate_price`: section, event_id, group_size as inputs; unit_price, total_price as outputs; group discount rules; decimal precision invariant.
- A system specification for the seat reservation workflow: the end-to-end sequence from listing through confirmation with all intermediate states defined.

**Applies at all pyramid levels.** Behavioral specifications exist at the unit, component, integration, and system levels of the [Specification Pyramid](method.md) (Section 10). The level determines scope, not type. A unit behavioral specification and a system behavioral specification are both behavioral specifications.

## 2.2 Integration Mapping

An integration mapping documents how components or services interact. It captures the contracts, data flows, and coordination rules that emerge when behavioral specifications are composed into a working system.

**Purpose:** Define the boundaries between components or services — what one side provides and what the other expects. Integration mappings formalize the "wiring" of the system.

**When it must be written:** Integration mappings may be written before implementation (when designing service boundaries) or may emerge during implementation when the actual behavior of external systems is discovered. Both paths are valid. The key rule: an integration mapping must exist before integration tests are written.

**Authoritative:** Yes, for the contract it defines. An integration mapping is the authoritative definition of how two components interact. However, when an integration mapping describes external system behavior (e.g., a third-party API), the mapping reflects discovered reality rather than prescribed intent. It is authoritative within the project — it defines what the project expects from the external system — but it may need to be updated when the external system changes.

**Tests mandatory:** Yes. Every contract defined in an integration mapping must be verified by at least one integration test. Provider tests verify the service implements the contract. Consumer tests verify the calling service handles all responses correctly.

**Expected level of detail:** An integration mapping must define the protocol, endpoints or message topics, request and response schemas with types and constraints, error conditions, and any invariants that hold across the boundary. See [System-Level STDD](system-level-stdd.md), Section 3, for the full boundary specification format.

**Examples:**
- A service boundary specification: `OrderService → PaymentService`, defining POST /charge request schema, response schema, error codes, and SLA.
- An event schema: `OrderPlaced` event with producer, consumers, payload schema, and delivery guarantees.
- A consumer-driven contract fragment: the subset of a provider's API that a specific consumer depends on.

**Relationship to behavioral specifications:** Integration mappings complement behavioral specifications. A behavioral specification defines what a component does. An integration mapping defines how it connects to other components. Both are needed. A system with only behavioral specifications has no wiring documentation. A system with only integration mappings has no behavioral definition.

## 2.3 Configuration Decision

A configuration decision documents a technical or operational choice that affects system behavior but is not itself a behavioral rule. Configuration decisions record the "why" behind choices that would otherwise be implicit.

**Purpose:** Capture and justify decisions about technology, thresholds, library choices, infrastructure settings, and other configuration that shapes how behavioral specifications are realized.

**When it must be written:** When a decision is made that future team members or AI generators need to know about. Not every configuration choice needs a formal record. The threshold: if changing the decision would break tests or alter behavior, it should be documented. If it is purely cosmetic or stylistic, it may not need formal documentation.

**Authoritative:** Partially. A configuration decision records the current state of a choice and its rationale. It is authoritative in the sense that it is the documented reason for the current configuration. However, configuration decisions are more frequently superseded than behavioral specifications — technologies change, thresholds are tuned, and libraries are replaced.

**Tests mandatory:** Not always. Some configuration decisions are verifiable through tests (e.g., "use Decimal arithmetic, not float" can be verified by a type-checking test). Others are not directly testable (e.g., "use PostgreSQL because it supports JSONB columns"). When a configuration decision has testable implications, those implications should be captured as constraints in the relevant behavioral specification and tested there.

**Expected level of detail:** A configuration decision must state the choice, the alternatives considered, the rationale, and any implications for behavioral specifications or tests. It does not need the full six-question structure of a behavioral specification.

**Examples:**
- Technology choice: "Use `shopspring/decimal` for Go monetary calculations because the standard library lacks decimal support. This affects all pricing functions."
- Threshold decision: "Hold expiry is set to 15 minutes. This balances customer convenience against seat availability. The specific duration is a product decision, not a behavioral invariant — changing it does not change the system's correctness, only its tuning."
- Library selection: "Use Hypothesis for property-based testing in Python. Record all Hypothesis-discovered failures as explicit regression acceptance cases."

**Relationship to behavioral specifications:** Configuration decisions provide context for behavioral specifications. A behavioral specification says "prices use decimal precision." A configuration decision explains why, names the library, and documents the alternative that was rejected.

## 2.4 Specification Type Summary

| Property | Behavioral Specification | Integration Mapping | Configuration Decision |
|---|---|---|---|
| Defines | What the system must do | How components connect | Why a choice was made |
| Authoritative | Yes | Yes (for contract) | Partially |
| Tests mandatory | Yes | Yes | Only when testable |
| Written before implementation | Always | Usually, but may emerge | When the decision is made |
| Level of detail | Six questions, numbered rules | Protocol, schemas, errors, invariants | Choice, rationale, implications |
| Pyramid level | All (unit through system) | Integration and system | N/A |
| Change frequency | Low once mature | Medium | Medium to high |

---

# 3. Test Taxonomy

STDD recognizes three categories of test. Each category serves a different purpose and has a different relationship to the traceability matrix.

## 3.1 Requirement Test

A requirement test directly verifies a rule, invariant, or failure condition defined in a behavioral specification.

**Purpose:** Prove that the implementation satisfies a specific behavioral requirement. Requirement tests are the primary mechanism by which STDD ensures correctness.

**Relation to requirements:** One-to-one or many-to-one. Each requirement test maps to at least one specification rule. A single specification rule may have multiple tests (e.g., one per boundary value). Every specification rule must have at least one requirement test.

**What it proves:** That a specific behavioral rule is satisfied by the implementation. A passing requirement test means the implementation does what the specification says for that specific rule.

**Traceability:** Requirement tests carry specification IDs in their names, docstrings, or annotations. They appear in the traceability matrix with a direct link to the specification rule they verify.

**Includes:**
- Scenario tests: verify specific Given/When/Then cases
- Property-based tests: verify invariants across many random inputs
- Acceptance case tests: verify structured input-output pairs from YAML
- Failure condition tests: verify the system responds correctly to invalid input or error states

**Examples:**
```python
def test_group_discount_applied():
    """PRICE-01: Groups of 4+ receive 10% discount."""
    result = calculate_price("Orchestra", "E1", group_size=4)
    assert result.total == Decimal("360.00")

def test_discount_never_exceeds_total(order_total):
    """INV-01: Discount amount is always <= order total."""
    discount = calculate_discount(order_total)
    assert discount <= order_total
```

## 3.2 Integration Test

An integration test verifies that components collaborate correctly across a boundary defined in an integration mapping.

**Purpose:** Prove that the wiring between components is correct — that composed systems produce the right behavior when real components interact. Integration tests catch the composition bugs that requirement tests on individual components cannot.

**Relation to requirements:** Integration tests map to contract specifications defined in integration mappings. They may also validate system-level behavioral specifications that span multiple components.

**What it proves:** That two or more components, when connected through their actual interfaces, produce the behavior defined by the integration mapping. Passing integration tests mean the contracts hold when real code runs.

**Traceability:** Integration tests carry contract IDs or system specification IDs. They appear in the traceability matrix in a separate section or with a distinct type marker (e.g., `type: integration`) so that integration coverage is visible independently of requirement coverage.

**Includes:**
- Contract tests: verify provider and consumer honor the same contract
- End-to-end tests: verify full workflows across all components
- Cross-service tests: verify behavior across network boundaries

**Examples:**
```python
def test_confirmation_uses_pricing():
    """PAY-CTR-01: Confirmation price matches PricingEngine calculation."""
    service = ReservationService(inventory, pricing, clock)
    hold = service.hold_seats("E1", ["A1", "A2"])
    confirmation = service.confirm_reservation(hold.hold_id)
    expected = pricing.calculate("Orchestra", "E1", 2)
    assert confirmation.total_price == expected.total_price
```

## 3.3 Regression Artifact

A regression artifact captures a known-good output for comparison. Unlike requirement tests and integration tests, regression artifacts do not derive from a specification rule — they capture the current behavior as a baseline.

**Purpose:** Detect unintended changes in output. Regression artifacts are particularly useful for complex outputs (reports, rendered HTML, serialized data) where writing assertion-by-assertion tests would be impractical.

**Relation to requirements:** Indirect. A regression artifact does not prove a specification rule. It proves that the output has not changed since the last approved baseline. This is useful but fundamentally different from requirement verification.

**What it proves:** That the output is identical to the approved baseline. This is not the same as proving correctness — the baseline itself may be incorrect. Regression artifacts protect against unintended change, not against incorrectness.

**Traceability:** Regression artifacts appear in the traceability matrix with `type: regression`. They are tracked separately from requirement tests and integration tests. A specification rule that is only verified by a regression artifact is considered PARTIALLY COVERED, not COVERED, because the regression artifact does not assert the specific behavior — it asserts output stability.

**Maintenance behavior:** Regression artifacts require re-approval when the specification changes. When a behavioral specification is updated, the regression baseline must be regenerated and reviewed. This is a different maintenance pattern from requirement tests, which are updated by changing assertions. Regression artifacts are replaced wholesale.

**Examples:**
- A golden-file test comparing serialized JSON output to an approved baseline
- A snapshot test comparing rendered HTML to a stored reference
- An output comparison test for a report generator

**When to use regression artifacts vs requirement tests:**
- Use requirement tests when you can assert specific behavioral rules.
- Use regression artifacts when the output is too complex for individual assertions but stability matters.
- Never use regression artifacts as the sole verification for a behavioral specification rule. They supplement requirement tests; they do not replace them.

## 3.4 Test Type Summary

| Property | Requirement Test | Integration Test | Regression Artifact |
|---|---|---|---|
| Verifies | Behavioral specification rule | Contract / wiring | Output stability |
| Maps to | Spec rule ID | Contract ID / system spec ID | Baseline file |
| Proves correctness | Yes | Yes (for contracts) | No (proves stability) |
| Traceability type | `requirement` | `integration` | `regression` |
| Sufficient for coverage | Yes | Yes (for contract rules) | No (partial coverage) |
| Maintenance trigger | Spec rule changes | Contract changes | Any output change |

---

# 4. Artifact Lifecycle

Every specification artifact in STDD has a lifecycle state. The lifecycle tracks whether an artifact is current, superseded, or scheduled for removal.

## 4.1 Lifecycle States

| State | Meaning |
|---|---|
| **DRAFT** | Under development. May have open questions. Not yet authoritative. Tests may be incomplete. |
| **ACTIVE** | Accepted and authoritative. Drives test creation and implementation generation. The current definition of correctness. |
| **SUPERSEDED** | Replaced by a newer version. Kept for reference and audit trail. Not authoritative. Tests for superseded specs should be removed or redirected to the replacement. |
| **DEPRECATED** | Scheduled for removal. Still functional but should not be used for new work. Includes a target removal date or condition. |
| **REJECTED** | Evaluated and declined. Documents a specification that was considered but not adopted. Useful for recording why an approach was not taken. |

## 4.2 State Transitions

```
DRAFT → ACTIVE          Specification passes review, all tests written
DRAFT → REJECTED        Specification evaluated and declined

ACTIVE → SUPERSEDED     Replaced by a new specification version
ACTIVE → DEPRECATED     Scheduled for removal (no direct replacement)

DEPRECATED → removed    Removed from the project after deprecation period

SUPERSEDED → (retained) Kept indefinitely for reference
REJECTED → (retained)   Kept indefinitely for reference
```

**Rules:**
- A specification can only move from DRAFT to ACTIVE after passing the [Specification Review Checklist](writing-specifications.md) (Section 12).
- A specification must not be SUPERSEDED without a `superseded_by` reference to the replacement.
- A DEPRECATED specification must include a target date or condition for removal.
- An ACTIVE specification must never be deleted without first being SUPERSEDED or DEPRECATED.
- SUPERSEDED and REJECTED specifications may be moved to an archive directory or removed from the active repository once no active specifications reference them. Git history preserves the full record.
- REJECTED specifications should include the reason for rejection.

## 4.3 Supersession

Supersession occurs when a new specification replaces an existing one. This is different from updating a specification in place.

**When to supersede vs update:**
- **Update in place** when the change is incremental — adding a new rule, refining a boundary condition, fixing an ambiguity. The specification retains its identity and version number increments.
- **Supersede** when the change is structural — the specification is reorganized, split into multiple specifications, merged with another, or fundamentally rearchitected. The old specification gets a new document that replaces it.

**Recording supersession:**
- The superseded specification's status changes to SUPERSEDED.
- The superseded specification gains a `superseded_by` field pointing to the replacement.
- The new specification gains a `supersedes` field pointing to what it replaces.
- Both references use file paths relative to the repository root.
- The superseded specification's tests are migrated to the new specification or removed.

**Example:**
```
# Old specification (superseded)
Feature: Cart Discount v1
Status: SUPERSEDED
Superseded-by: features/cart-discount-v2/specification.md

# New specification
Feature: Cart Discount v2
Status: ACTIVE
Supersedes: features/cart-discount-v1/specification.md
```

## 4.4 Handling Stale Artifacts

A stale artifact is one where the specification no longer matches the system's actual behavior, or where no active development references the artifact.

**Detection:**
- The CSI fingerprint gate detects when implementations change without specification updates (potential staleness).
- Periodic review (quarterly recommended) identifies specifications that have not been touched.
- Failed regeneration may indicate a stale specification — the specification describes behavior the system no longer exhibits.

**Resolution:**
- If the specification is still correct and the implementation drifted, fix the implementation. The specification is authoritative.
- If the system's behavior has legitimately changed and the specification was not updated, update the specification. This is a process failure that should be addressed.
- If the specification describes a feature that has been removed, DEPRECATE or SUPERSEDE the specification.
- If the specification was never completed (stuck in DRAFT), either complete it or REJECT it with a reason.

---

# 5. Execution Flows

STDD defines explicit execution flows for common development scenarios. The standard flow (specification → tests → implementation) applies to new features. Other scenarios follow adapted flows that remain pragmatic while preserving the core STDD principle: specifications define correctness.

## 5.1 New Feature

The standard STDD flow. Used when building functionality that does not yet exist.

```
1. Write behavioral specification
2. Review specification (checklist, team review)
3. Write tests (requirement tests mapped to spec rules)
4. Build traceability matrix
5. Generate implementation (TFP)
6. Run tests
7. If tests fail → refine prompt or decompose, return to step 5
8. If tests pass → verify traceability, compute fingerprint, commit
```

**This is the canonical flow.** All rules from the [Method](method.md) and [Writing Specifications](writing-specifications.md) apply fully.

## 5.2 Behavior Change

Used when modifying the behavior of an existing feature. The specification already exists and must be updated before the implementation changes.

```
1. Identify the behavioral specification affected
2. Update the specification rules that change
3. Update or add tests for the changed rules
4. Update the traceability matrix
5. Regenerate or modify the implementation
6. Run the full test pyramid (unit + integration + system)
7. If tests fail → diagnose (spec ambiguity, missing test, implementation issue)
8. If tests pass → update fingerprint, commit
```

**Key principle:** The specification changes first. An implementation change without a specification update is a process violation that the CSI fingerprint gate should catch.

## 5.3 Bug Fix (Spec Already Correct)

Used when a bug is discovered and the existing behavioral specification already defines the correct behavior. The specification is not wrong — the implementation is.

```
1. Identify the specification rule that the bug violates
2. Verify that a test exists for that rule
   a. If a test exists and passes → the test does not assert the specific
      behavior that the bug violates. This is a test gap. Strengthen the test
      by adding the missing assertion, then proceed to step 3.
   b. If a test exists and fails → the test correctly identifies the bug.
      Proceed to step 3.
   c. If no test exists → write the missing test. This is a test gap (see
      Defect Origin in Metrics). Proceed to step 3.
3. Fix or regenerate the implementation
4. Run the full test pyramid
5. If all tests pass → commit
```

**This flow explicitly allows fix-then-test when the specification already covers the behavior.** The specification was right. The implementation was wrong. The immediate priority is fixing the implementation. If a test gap is discovered (step 2c), the test is added, but the fix is not blocked on writing a full specification update — because no specification update is needed.

**Why this is not a violation of STDD:** The specification already defined the correct behavior before the bug was found. The bug is an implementation failure, not a specification gap. STDD's ordering rule ("specification before implementation") applies to defining new behavior, not to correcting an implementation that fails to meet an existing specification.

**If the bug reveals a specification gap:** If no specification rule covers the scenario that triggered the bug, this is a specification gap, not a bug fix. Switch to the Behavior Change flow (Section 5.2): add the missing rule, add the test, then fix the implementation. Track this as a specification gap defect origin (see [Metrics](metrics.md), Section 8).

## 5.4 Discovery and Reverse Engineering

Used when working with existing code that lacks specifications, or when discovering the actual behavior of an external system. This is the brownfield entry point.

```
1. Read the existing code or observe the external system
2. Extract a behavioral specification from what you observe
3. Write tests that capture the observed behavior
4. Run tests against the existing code / system
   a. If all tests pass → the specification matches reality. Proceed.
   b. If some tests fail → the specification is wrong about the current
      behavior. Adjust the specification to match reality, OR document
      the discrepancy as a known bug.
5. Review the specification for completeness
6. Decide whether to accept the current behavior or define new behavior
   a. If accepting → the extracted specification becomes ACTIVE
   b. If changing → follow the Behavior Change flow (5.2) from the
      extracted specification
7. Optionally validate by regeneration
```

**Key principle:** In discovery mode, the existing system is the initial source of truth. The specification is extracted from reality, not prescribed. Once extracted and validated, the specification becomes authoritative — future changes follow the standard flows.

**When to use this flow:**
- Migrating legacy code to STDD (see [Adoption Guide](adoption-guide.md), Section 7)
- Documenting third-party API behavior as an integration mapping
- Onboarding to a codebase where behavior is undocumented
- Performing a specification extraction before regeneration

## 5.5 Flow Summary

| Scenario | Spec exists? | Spec correct? | Start with |
|---|---|---|---|
| New feature | No | N/A | Write specification |
| Behavior change | Yes | Will be updated | Update specification |
| Bug fix (spec correct) | Yes | Yes | Verify test, fix implementation |
| Discovery | No | N/A | Extract specification from reality |

---

# 6. Traceability Rules

Traceability connects specifications to tests and makes coverage visible. These rules define the conceptual model. Tooling to automate enforcement is a separate concern.

## 6.1 Core Rules

**Rule 0: Specification IDs must be scoped to the feature.**
Use a feature prefix (e.g., `PRICE-01`, `ORD-CANCEL-03`), not generic names like `RULE-1`. This prevents collisions when multiple features share a traceability matrix or are validated by the same tooling.

**Rule 1: Every behavioral specification rule must map to at least one requirement test that verifies the observable behavior the rule claims.**
This is the fundamental traceability rule. A behavioral rule without a test is an unverified claim. A behavioral rule with a test that exercises only an internal helper, parser, or isolated function is also an unverified claim — the test must verify the same surface the requirement names. The traceability matrix must show the link, and the link must be a behavioral one, not an incidental one.

**Rule 2: Every contract in an integration mapping must map to at least one integration test.**
Contracts are verified separately from behavioral rules. Integration tests verify that real components honor the contract when they interact.

**Rule 3: Regression artifacts are tracked separately and do not satisfy Rule 1 or Rule 2.**
A specification rule that is only verified by a regression artifact is PARTIALLY COVERED. Regression artifacts provide change detection, not correctness verification.

**Rule 4: Lifecycle state must be visible in the traceability matrix.**
The traceability matrix must indicate whether each specification is ACTIVE, SUPERSEDED, DEPRECATED, or DRAFT. Tests for non-ACTIVE specifications should be flagged for review.

**Rule 5: Orphaned tests must be flagged.**
A test that does not map to any specification rule is an orphan. Orphaned tests may indicate a missing specification rule or a test that is no longer needed. Both cases require investigation.

**Rule 6: Traceability must distinguish requirement coverage from integration coverage.**
The traceability matrix must allow independent assessment of: (a) how many behavioral rules are verified by requirement tests, and (b) how many contracts are verified by integration tests. These are different kinds of coverage with different implications.

**Rule 7: Configuration decisions with testable implications should appear in the traceability matrix with spec type `configuration`.**
Configuration decisions without testable implications are tracked via their metadata header and version history and do not require traceability matrix entries.

**Rule 8: Multi-channel requirements must show evidence for every named channel.**
When a requirement names more than one externally observable channel — for example, log output, stderr, stdout, command-line parsing, environment variables, subprocess argv, files on disk, network or TLS behavior, or backup/restore compatibility — every named channel must either have direct test evidence or be listed explicitly as NOT COVERED / FUTURE WORK. A test that verifies one channel does not establish coverage for the others. A test that exercises one secure option, one config key, one log level, one protocol path, or one platform does not establish coverage for the rest unless the requirement is scoped to only that case.

**Rule 9: When in doubt about coverage, downgrade.**
The classifications in §6.4 are conservative by design. If it is unclear whether the test evidence covers the full claim of the requirement, downgrade: COVERED becomes PARTIALLY COVERED, PARTIALLY COVERED becomes UNCOVERED. Coverage status must never be inferred from implementation structure, plausible reasoning, or the existence of helper-level tests; it must follow from explicit test evidence against the surface the requirement names. See §6.5 for the AI-agent application of this rule.

## 6.2 Traceability Matrix Structure

The traceability matrix has the following columns:

| Column | Description |
|---|---|
| **Spec ID** | The specification rule identifier (e.g., PRICE-01, PAY-CTR-01) |
| **Spec Type** | `behavioral`, `contract`, or `configuration`. (In the traceability matrix, `integration-mapping` specifications are labeled `contract` for brevity.) |
| **Spec Status** | DRAFT, ACTIVE, SUPERSEDED, DEPRECATED, REJECTED |
| **Test** | The test function or test case name |
| **Test Type** | `requirement`, `integration`, or `regression` |
| **Coverage** | COVERED, PARTIALLY COVERED, or UNCOVERED |

**Example:**

| Spec ID | Spec Type | Spec Status | Test | Test Type | Coverage |
|---|---|---|---|---|---|
| PRICE-01 | behavioral | ACTIVE | test_group_discount_applied | requirement | COVERED |
| PRICE-02 | behavioral | ACTIVE | test_no_discount_small_group | requirement | COVERED |
| INV-01 | behavioral | ACTIVE | test_discount_never_exceeds_total | requirement | COVERED |
| PAY-CTR-01 | contract | ACTIVE | test_charge_success | integration | COVERED |
| PAY-CTR-01 | contract | ACTIVE | test_charge_response_parsed | integration | COVERED |
| REPORT-01 | behavioral | ACTIVE | test_report_golden_file | regression | PARTIALLY COVERED |

## 6.3 Lifecycle Visibility

The traceability matrix serves double duty: it shows coverage and it shows lifecycle state. This means:

- A SUPERSEDED specification with tests still listed indicates tests that should be migrated or removed.
- A DEPRECATED specification with tests indicates tests that will eventually be removed.
- A DRAFT specification with no tests is expected. A DRAFT specification with tests that pass is ready for review.
- An ACTIVE specification with UNCOVERED rules is a gap that must be closed.

## 6.4 Coverage Categories

STDD distinguishes three categories of coverage, each measured independently:

**Requirement coverage:** The ratio of ACTIVE behavioral specification rules that have at least one COVERED requirement test. This is the primary quality signal.

**Integration coverage:** The ratio of ACTIVE contract rules that have at least one COVERED integration test. This measures wiring confidence.

**Regression coverage:** The count of features with regression artifacts. This is informational — regression artifacts do not contribute to requirement or integration coverage.

These three categories correspond to the three test types. Reporting them separately prevents a common failure mode: a feature that appears well-tested because it has many regression artifacts but has low requirement coverage because the behavioral rules are not individually verified.

### Coverage Status Definitions

The Coverage column takes one of three values. The definitions below are strict and apply uniformly across requirement, integration, and regression rows.

**COVERED.** A requirement is COVERED only when at least one test verifies the same observable behavior the requirement claims, on the same surface the requirement names. If the requirement names a user-visible or external surface — log output, stderr, stdout, command-line parsing, environment variables, subprocess argv, files on disk, network/TLS behavior, backup/restore compatibility, or any other externally observable channel — then a test against an internal helper, parser, or isolated function is **not sufficient**. The behavioral surface verified by the test must match the behavioral surface stated by the requirement.

For backup, restore, and security claims, COVERED additionally requires at least one integration or channel-level test. Helper-level tests are never enough on their own for these categories.

**PARTIALLY COVERED.** A requirement is PARTIALLY COVERED when:

- the existing test verifies only an internal helper, parser, or isolated function while the requirement names an external surface; or
- the requirement names multiple channels and only some channels have direct test evidence; or
- the test exercises only one secure option, one config key, one log level, one protocol path, or one platform while the requirement is broader; or
- the only evidence is a regression artifact (Rule 3).

PARTIALLY COVERED is a real status, not a euphemism. Use it.

**UNCOVERED.** No test verifies the behavior the requirement claims. The requirement is an unverified claim. UNCOVERED is also the correct status when the only available evidence comes from inspecting the implementation rather than running a test that asserts the behavior.

### Evidence Requirements for COVERED Rows

Every COVERED row in the traceability matrix must, on the row itself or in an evidence block beneath it, identify:

- **Test file** — the file path of the test.
- **Test name** — the specific test function or test case.
- **Behavior verified** — a one-sentence statement of what the test asserts, in the same vocabulary as the requirement.
- **Surface verified** — the exact externally observable surface the test exercises (e.g., "stderr of the CLI process", "the bytes written to the backup file", "log output at TRACE level").

If any element of the requirement's claim is not represented in this evidence, the row is PARTIALLY COVERED, not COVERED. List the missing channels explicitly under "Evidence not yet verified" or as a NOT COVERED / FUTURE WORK note.

A worked example of this evidence-rich form appears in [Templates › Traceability Matrix](../templates/traceability-matrix.md).

## 6.5 AI-Agent Coverage Discipline

AI agents (Claude, Codex, and equivalents) using STDD to assess or update a traceability matrix are bound by the same rules as human authors, but with one additional constraint: an AI agent must not promote a requirement to COVERED based on plausible reasoning, code inspection, or helper-level tests. AI agents are particularly prone to this failure mode because they can recognize that an implementation *appears* to satisfy a rule and from there infer coverage that no test actually proves.

**For every COVERED claim an AI agent makes or accepts, the agent must explicitly identify:**

1. The exact observable behavior the requirement claims.
2. The exact test that proves it (file path and test name).
3. The exact surface that test exercises.
4. The surfaces named by the requirement that are **not** covered by that test, if any.

If item 4 is non-empty, the requirement must remain PARTIALLY COVERED or UNCOVERED. The agent must not promote on the strength of items 1–3 alone when item 4 lists ungaranteed surfaces. The agent must apply Rule 9 (downgrade when in doubt) by default.

AI agents must not:

- Promote coverage based on the structure of the implementation.
- Promote coverage based on the existence of similar tests for adjacent requirements.
- Promote coverage based on a helper-level test when the requirement names a system-level or user-visible surface.
- Mark a multi-channel requirement COVERED on the strength of a single-channel test.
- Mark a security, backup, or restore claim COVERED without a channel-level or integration test.

When generating or revising a traceability matrix, an AI agent must produce the evidence block defined above (test file, test name, behavior verified, surface verified) for every COVERED row, and must list missing surfaces explicitly. A row without that evidence block is not a COVERED row.

## 6.6 Brownfield and Fork Compatibility

When STDD is applied to a fork or to a brownfield system that diverged from an upstream project, every behavior changed from upstream must be classified as exactly one of:

- **Compatibility-preserving** — the behavior produces the same observable result as upstream for the same inputs.
- **Intentional breaking change** — the behavior diverges deliberately, with a documented reason.
- **Security hardening** — the behavior diverges to close a vulnerability or tighten a guarantee.
- **Migration risk** — the behavior diverges in a way that may require existing users to migrate data, configuration, or workflow.
- **Implementation-only change** — internals changed; no externally observable behavior changed.

This classification is part of the specification's metadata for the affected rule, not a separate document.

**Compatibility may only be claimed COVERED when tests prove one of:**

- existing upstream data files (or a representative corpus of them) load and behave unchanged under the fork; or
- existing upstream configuration produces equivalent observable behavior under the fork; or
- the divergence is explicitly documented as intentional, with the affected rules classified accordingly.

Compatibility must not be inferred from unchanged constants, unchanged filenames, unchanged helper signatures, or unchanged internal structure. None of those are observable behavior. A fork that retains the upstream filename for its config file but changes how the file is parsed is not compatibility-preserving — it is a migration risk that looks compatibility-preserving on inspection. Only test evidence against the upstream-observable surface establishes compatibility.

For the brownfield migration workflow that produces these classifications, see [Adoption Guide](adoption-guide.md), Section 7. For the discovery flow this builds on, see Section 5.4.

---

# 7. Metadata Convention

STDD specifications benefit from machine-readable metadata that captures type, status, and relationships. This section defines a lightweight convention.

## 7.1 Specification Metadata

Specifications should include a metadata header at the top of the document. For Markdown files, this takes the form of a structured header block:

```
Feature: [Name]
Version: [x.y]
Type: behavioral | integration-mapping | configuration-decision
Status: DRAFT | ACTIVE | SUPERSEDED | DEPRECATED | REJECTED
Superseded-by: [path, if status is SUPERSEDED]
Supersedes: [path, if this replaces another spec]
```

**Fields:**

| Field | Required | Description |
|---|---|---|
| Feature / Contract / Decision | Yes | The name of the specification |
| Version | Yes | Semantic version of this specification |
| Type | Recommended | One of: `behavioral`, `integration-mapping`, `configuration-decision` |
| Status | Recommended | One of: DRAFT, ACTIVE, SUPERSEDED, DEPRECATED, REJECTED |
| Superseded-by | When SUPERSEDED | Path to the replacement specification |
| Supersedes | When replacing | Path to the specification this replaces |

## 7.2 Examples

**Behavioral specification:**
```
Feature: Seat Hold Expiry
Version: 1.2
Type: behavioral
Status: ACTIVE
```

**Integration mapping:**
```
Contract: OrderService → PaymentService
Version: 2.0
Type: integration-mapping
Status: ACTIVE
Supersedes: contracts/payment-v1/boundary.md
```

**Configuration decision:**
```
Decision: Decimal Library Selection
Version: 1.0
Type: configuration-decision
Status: ACTIVE
```

**Superseded specification:**
```
Feature: Cart Discount
Version: 1.0
Type: behavioral
Status: SUPERSEDED
Superseded-by: features/cart-discount-v2/specification.md
```

## 7.3 Adoption

**For new specifications:** Include the full metadata header from the start. Use the template in [Templates](../templates/specification.md).

**For existing specifications:** Add metadata incrementally. When an existing specification is modified for any reason, add the metadata header at that time. Do not perform a mass edit across all existing specifications solely to add metadata — this creates noise in the commit history without behavioral value.

**Tooling compatibility:** The metadata fields are plain text. They can be parsed by simple scripts or integrated into the traceability validator. The format is intentionally compatible with the existing `Feature: / Version: / Status:` header used in the specification template.

---

## Relationship to Other Documents

This core model is the structural foundation. Other documents provide depth:

- [Manifesto](../manifesto.md) — philosophy and core principles
- [Method](method.md) — the development workflow and specification pyramid
- [Writing Specifications](writing-specifications.md) — how to write behavioral specifications
- [Engineering Playbook](engineering-playbook.md) — practical application, CI/CD, team roles
- [Architecture](architecture.md) — system design for safe regeneration
- [NFR Framework](nfr-framework.md) — non-functional requirements
- [System-Level STDD](system-level-stdd.md) — multi-service specifications
- [Metrics & Measurement](metrics.md) — quality measurement
- [Glossary](glossary.md) — term definitions
