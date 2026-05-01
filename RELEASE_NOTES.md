# STDD v0.4 — Behavioral / Structural ID Convention

## What changed in v0.4

STDD v0.4 sharpens the distinction between *behavioral* and *structural* artifacts in a specification, and aligns the default traceability tooling with that distinction. The motivation surfaced during v0.3.1 cleanup: the pre-existing default regex (`\w+-\d+`) silently dropped multi-segment spec IDs from traceability validation, hiding 9 invariant IDs and 9 failure-condition IDs across the three reference tools.

### Spec ID convention

- **Behavioral artifacts** — rules, invariants, failure conditions — keep prefixed multi-segment IDs (`PREFIX-NN`, `PREFIX-INV-NN`, `PREFIX-FAIL-NN`). These are testable claims; every one carries a row in the traceability matrix.
- **Structural artifacts** — input and output field descriptors — no longer carry rule-style IDs at all. They are described by name, type, and constraints/description, matching the convention already used in `examples/order-cancellation/specification.md`. The template is updated to match (it had previously diverged with unprefixed `IN-1` / `OUT-1` IDs).

### Validator

- The default `--spec-pattern` is now `\w+(?:-\w+)*-\d+` (was `\w+-\d+`). This permits multi-segment IDs like `FP-INV-01` and `FP-FAIL-01` without requiring a custom pattern.
- A new behavioral rule **TR-14** documents this matching guarantee.
- Failure conditions and invariants now appear in Gate 1 reports.

### Self-application

- All 9 `*-FAIL-*` rows added to `features/traceability-matrix.md` with evidence blocks.
- New test `test_missing_test_directory_warns_but_continues` covers the previously untested FP-FAIL-02.
- Existing failure-condition tests (TR-FAIL-01..03, GEN-FAIL-01..03, FP-FAIL-03) extended to assert on the stderr channel each rule names.
- Matrix moves from 49 → 59 spec IDs; COVERED 22 → 32; PARTIALLY COVERED unchanged at 27.

## Compatibility note for adopters

If your spec files use `PREFIX-IN-NN` or `PREFIX-OUT-NN` style IDs in Inputs / Outputs tables, the new default regex will now match them, and Gate 1 will demand tests for them. The recommended migration is one of:

1. **Drop the ID column** from Inputs and Outputs (recommended — matches the order-cancellation example and the updated template).
2. **Override the spec pattern** with a stricter regex (e.g. `--spec-pattern '\w+-(?:RULE|INV|FAIL)-\d+'`).

Option 1 is the methodology-aligned path: input/output IDs were never testable behavioral claims; treating them as such was a mistake the regex used to hide.

## License

Creative Commons Attribution 4.0 International (CC BY 4.0)

Author: Frank Heikens

---

# STDD v0.3 — Tightened Coverage Rules

## What changed in v0.3

STDD v0.3 strengthens the traceability rules so a requirement cannot be marked COVERED on the strength of helper-level tests, plausible reasoning, or implementation inspection. The motivation is brownfield and forked projects, where AI agents have been observed promoting unit-level evidence to system-level COVERED claims that the system did not actually provide.

### Core Model

- **Rule 1 (revised)** — the test must verify the same observable behavior on the same surface the requirement names. Helper-level evidence does not satisfy a system-level requirement.
- **Rule 8 (new)** — multi-channel requirements need evidence per channel. A requirement that constrains both an HTTP API and a CLI is not COVERED until both channels have tests.
- **Rule 9 (new)** — when in doubt, downgrade. The default classification is PARTIALLY COVERED, not COVERED.
- **§6.4 (new)** — strict definitions of COVERED, PARTIALLY COVERED, and UNCOVERED, with a required evidence block (test file, test name, behavior verified, surface verified) on every COVERED row.
- **§6.5 (new)** — AI-agent coverage discipline as a binding directive.
- **§6.6 (new)** — brownfield and fork classification: every divergence from upstream is compatibility-preserving, intentional breaking, security hardening, migration risk, or implementation-only. Compatibility requires test evidence and is never inferred from internal similarity.

### Adoption Guide

- **§7 (new)** — forks-and-divergence subsection applying the brownfield classification to the migration workflow.

### Templates

- **traceability-matrix.md** — stricter format with worked examples of COVERED and PARTIALLY COVERED rows, including the evidence block.

### Prompt Engineering

- **§8.6 (new)** — anti-pattern: promoting coverage without test evidence.
- **§13 (new)** — directive section for AI agents on coverage discipline.

### Anti-Patterns

- **§13 (new)** — Overclaiming Coverage: traceability inflation, helper-level proof, multi-channel coverage gaps, fork compatibility without corpus evidence, security guarantees without channel-level tests.

## Why this matters

Traceability is only useful if COVERED actually means covered. Without strict rules, a 100% coverage claim becomes meaningless — and for AI-driven development, where agents generate the matrix, the failure mode is systematic, not occasional. v0.3 makes the rules tight enough that the matrix can be trusted as evidence rather than narrative.

## Compatibility

Documentation only. The `.fingerprint` is unchanged because no spec or test under `features/` or `tests/` changed. Existing traceability matrices remain valid but should be reviewed against the stricter §6.4 definitions; rows lacking an evidence block should be downgraded to PARTIALLY COVERED until evidence is added.

## License

Creative Commons Attribution 4.0 International (CC BY 4.0)

Author: Frank Heikens

---

# STDD v0.2 — Validated on a Real System

## What is STDD?

Specification & Test-Driven Development (STDD) is a software engineering methodology where specifications and tests define the system, and implementations are replaceable artifacts generated by AI or humans.

## What changed in v0.2

### Structural model (STDD v2 Core Model)

STDD now has an explicit structural foundation:

- **Specification taxonomy** — three types: behavioral specifications (correctness rules), integration mappings (contracts between components), and configuration decisions (documented choices with rationale).
- **Test taxonomy** — three types: requirement tests (verify behavioral rules), integration tests (verify contracts), and regression artifacts (detect output changes).
- **Artifact lifecycle** — five states: DRAFT, ACTIVE, SUPERSEDED, DEPRECATED, REJECTED. Explicit transition rules and supersession tracking.
- **Execution flows** — four named flows: New Feature (spec-first), Behavior Change (update spec first), Bug Fix when the spec is already correct (fix implementation directly), and Discovery/Reverse Engineering (extract spec from existing systems).
- **Traceability rules** — eight rules governing how specifications map to tests, including scoped spec IDs, separate requirement and integration coverage tracking, and explicit handling of regression artifacts and configuration decisions.

### Metadata convention

Every specification now carries a machine-readable metadata header:

```
Feature: [Name]
Version: [x.y]
Type: behavioral | integration-mapping | configuration-decision
Status: DRAFT | ACTIVE | SUPERSEDED | DEPRECATED | REJECTED
```

### Traceability matrix (v2 format)

The traceability matrix now includes six columns: Spec ID, Spec Type, Spec Status, Test, Test Type, and Coverage. This makes coverage gaps visible by category — requirement coverage vs integration coverage vs regression artifacts.

### Metrics alignment

Coverage Grade now explicitly defines how test types affect coverage status:
- Requirement tests → COVERED
- Integration tests → COVERED (for contracts)
- Regression artifacts → PARTIALLY COVERED only

NFR tests that assert behavioral constraints are classified as requirement tests.

### Documentation alignment

All specifications in the repository carry v2 metadata. Satellite documents reference the core model. The spec-first ordering rule is qualified: it applies to new behavior, not to bug fixes where the specification is already correct. Lifecycle states are consistent across all documents.

## Real-world validation

STDD v0.2 has been applied to the [Arq](https://github.com/fheikens/arq) project:

- **521 specification rules** — behavioral requirements, integration contracts, invariants, failure conditions, and NFRs
- **Full traceability** — every specification rule maps to at least one test, every test maps to a specification rule
- **Explicit coverage** — every rule is classified as COVERED, PARTIALLY COVERED, or UNCOVERED
- **Three spec types in practice** — behavioral specifications define correctness, integration mappings define service contracts, configuration decisions document architectural choices

This is the first time STDD has been validated end-to-end on a real system with the full v2 structural model.

## Why this matters

- **No ambiguity** — system behavior is defined by numbered, testable rules, not by code or tribal knowledge
- **Machine-readable structure** — metadata headers, scoped spec IDs, and typed traceability enable automation
- **Foundation for AI-driven development** — specifications strong enough to regenerate any implementation from scratch

## New documents

| Document | Description |
|----------|-------------|
| [Core Model](docs/stdd-core-model.md) | The v2 structural foundation |
| [Worked Example](docs/worked-example-core-model.md) | The core model applied to the seat reservation system |
| [v2 Transition Notes](docs/stdd-v2-transition-notes.md) | What changed and how to interpret older documents |
| [Gap Review](docs/stdd-core-model-gap-review.md) | Systematic review of all documents against the core model |

## License

Creative Commons Attribution 4.0 International (CC BY 4.0)

Author: Frank Heikens
