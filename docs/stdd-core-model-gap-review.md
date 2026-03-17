# STDD Core Model — Gap Review
## Terminology and Guidance Conflicts with the Core Model

Author: Frank Heikens
Version: 1.0
Date: 2026

---

This document identifies where existing STDD documents use terminology or guidance that conflicts with, or is ambiguous relative to, the [Core Model](stdd-core-model.md). Each issue includes a severity, a recommended change, and whether the change should happen now or later.

**Severity levels:**
- **High** — Creates confusion or contradicts the core model. Should be addressed soon.
- **Medium** — Imprecise but not contradictory. Causes ambiguity for new adopters.
- **Low** — Minor inconsistency or missed opportunity. Can be addressed when convenient.

---

## manifesto.md

| # | Issue | Severity | Recommended Change | When |
|---|-------|----------|-------------------|------|
| 1 | Uses "specification" as undifferentiated concept. No distinction between behavioral specification, integration mapping, or configuration decision. | Medium | Add a sentence noting that specifications come in different types, with a reference to the core model. Not a full rewrite — the manifesto is philosophical, not structural. | Later |
| 2 | "Every change begins with a specification" (line 119) is presented as absolute. The core model allows fix-then-test for bug fixes where the spec is already correct. | High | Soften to "Every behavioral change begins with a specification" or add a qualifying note. The bug-fix flow must not contradict the manifesto. | Now |
| 3 | No lifecycle language. Specifications are presented as permanent, with no mention of SUPERSEDED, DEPRECATED, or DRAFT states. | Low | The manifesto is not the right place for lifecycle details. No change needed — the core model document covers this. | No change needed |

---

## docs/method.md

| # | Issue | Severity | Recommended Change | When |
|---|-------|----------|-------------------|------|
| 4 | Section 4 (STDD Workflow) presents a single linear flow: spec → behavior → tests → implementation. No acknowledgment of the bug-fix or discovery flows. | High | Add a brief note after the workflow that variations exist for bug fixes and brownfield systems, with a reference to the core model. | Now |
| 5 | Section 12 (Maintaining System Stability) says "When a system evolves: 1. The specification is updated, 2. New tests are added, 3. The implementation is regenerated." This implies all changes require spec updates, which contradicts the bug-fix flow. | Medium | Qualify: "When a system's intended behavior evolves" to distinguish behavioral changes from implementation fixes. | Now |
| 6 | The Specification Pyramid (Section 10) defines four levels (unit, component, integration, system) but does not distinguish behavioral specifications from integration mappings. At the integration level, both exist. | Medium | Add a sentence in Section 10 noting that integration-level specifications may be behavioral (what a composed system does) or contractual (how components connect), and that both are needed. Reference the core model. | Later |
| 7 | "Specification" is used 80+ times as a monolithic concept. | Medium | Not practical to differentiate every usage. A note in the introduction referencing the core model's taxonomy is sufficient. | Later |

---

## docs/writing-specifications.md

| # | Issue | Severity | Recommended Change | When |
|---|-------|----------|-------------------|------|
| 8 | Section 5 (Anatomy of a Feature Specification) defines `Status: draft | review | accepted`. The core model defines DRAFT, ACTIVE, SUPERSEDED, DEPRECATED, REJECTED. The `review` and `accepted` states are not in the core model; `ACTIVE` replaces `accepted`. | High | Update Section 5 and the template to use the core model states. Map: `draft` → DRAFT, `review` → (removed, review is a process step not a state), `accepted` → ACTIVE. | Now |
| 9 | Section 11 (Specification Templates) shows `Status: draft` in the feature template. The unit template and integration contract template have no Status field at all. | Medium | Update all templates to include the full metadata header from the core model: Type, Status, and optional Superseded-by/Supersedes fields. | Now |
| 10 | The document focuses exclusively on behavioral specifications. This is appropriate for its scope, but it does not acknowledge integration mappings or configuration decisions as distinct types. | Low | Add a sentence in the introduction noting that this document covers behavioral specifications specifically, and that integration mappings and configuration decisions are defined in the core model. | Later |
| 11 | "Integration specification" in Section 4.2 blurs the line between a behavioral specification at the integration level and an integration mapping (contract). The text says "Integration specifications are the primary unit of work in STDD" — this overweights one level over others. | Medium | Clarify that integration-level work involves both behavioral specifications (what the composed system does) and integration mappings (how the components connect). Remove or soften the claim that integration specs are "the primary unit of work." | Later |

---

## docs/engineering-playbook.md

| # | Issue | Severity | Recommended Change | When |
|---|-------|----------|-------------------|------|
| 12 | Section 2 (Repository Structure) shows `features/` containing `specification.md`, `scenarios.md`, `invariants.md`, and `acceptance_cases.yaml`. No mention of specification type or lifecycle metadata. | Low | Add a note that the specification.md should include the metadata header. Not a structural change — the repo structure is fine. | Later |
| 13 | The TFP examples (Section 3) do not reference specification types. All prompts use "Specification:" as a flat header. | Low | This is acceptable. TFP prompts do not need to distinguish specification types — the prompt structure works for all types. No change needed. | No change needed |
| 14 | Pre-flight checklists (Section 8) do not include lifecycle state verification. A specification in DRAFT state should not pass "Before Generation." | Medium | Add "Specification status is ACTIVE (not DRAFT or DEPRECATED)" to the Before Generation checklist. | Now |

---

## docs/architecture.md

| # | Issue | Severity | Recommended Change | When |
|---|-------|----------|-------------------|------|
| 15 | Section 5 (Contract-Based Interfaces) defines contracts inline without using the term "integration mapping." The core model formalizes this as a specification type. | Low | Add a note that contracts as described here correspond to the "integration mapping" type in the core model. | Later |
| 16 | Section 11 (System Evolution) describes Adding, Changing, and Removing features but does not mention lifecycle states. "Remove the specification" should be "DEPRECATE or SUPERSEDE the specification." | Medium | Update Section 11 to reference lifecycle states. Removing a specification should follow the lifecycle rules. | Later |

---

## docs/adoption-guide.md

| # | Issue | Severity | Recommended Change | When |
|---|-------|----------|-------------------|------|
| 17 | Section 4 (The First STDD Feature) presents only the new-feature flow. The discovery flow (for existing code migration, covered in Section 7) is a separate section. The core model unifies these as named execution flows. | Low | Add a cross-reference from Section 4 to the core model's execution flows. The existing structure is fine — the flows are described, just not named consistently. | Later |
| 18 | Section 7 (Migrating Existing Features) describes extracting specifications from code. This is the discovery flow from the core model. Naming it explicitly would help consistency. | Low | Add a sentence: "This process corresponds to the Discovery and Reverse Engineering flow defined in the [Core Model](stdd-core-model.md)." | Later |

---

## docs/glossary.md

| # | Issue | Severity | Recommended Change | When |
|---|-------|----------|-------------------|------|
| 19 | No glossary entries for: Behavioral Specification, Integration Mapping, Configuration Decision, Requirement Test, Integration Test, Regression Artifact, or the lifecycle states (ACTIVE, SUPERSEDED, DEPRECATED, REJECTED). | High | Add glossary entries for all core model terms. This is essential for the glossary to remain the definitive term reference. | Now |
| 20 | The "Specification" glossary entry describes it as a monolithic concept: "A precise, testable definition of system behavior." This does not acknowledge the taxonomy. | Medium | Expand the entry to note that specifications come in three types (behavioral, integration mapping, configuration decision), with a reference to the core model. | Now |

---

## docs/nfr-framework.md

| # | Issue | Severity | Recommended Change | When |
|---|-------|----------|-------------------|------|
| 21 | NFRs are treated as additions to behavioral specifications. The core model classifies some NFRs (technology choices, thresholds) as configuration decisions. | Low | This is a minor conceptual overlap, not a conflict. The NFR framework's structure (layered model, activation by technology/domain) is compatible with the core model. No change needed now. | Later |

---

## docs/system-level-stdd.md

| # | Issue | Severity | Recommended Change | When |
|---|-------|----------|-------------------|------|
| 22 | Section 3 (Service Boundary Specifications) describes what the core model calls "integration mappings" but uses the term "boundary specification." | Medium | Add a note that boundary specifications correspond to the "integration mapping" specification type in the core model. The existing terminology can be kept as a domain-specific alias. | Later |
| 23 | Section 11 (System-Level Traceability) defines a traceability matrix structure that includes service and test columns but does not include test type or spec type columns. | Low | The system-level matrix can be extended later when tooling is built. The conceptual structure in the core model is compatible. | Later |

---

## docs/metrics.md

| # | Issue | Severity | Recommended Change | When |
|---|-------|----------|-------------------|------|
| 24 | Coverage Grade (Section 5) uses states COVERED, PARTIALLY COVERED, UNCOVERED but does not define what makes a test "partial." The core model defines this: a regression artifact provides PARTIALLY COVERED status. | Medium | Add the distinction: a spec rule verified only by a regression artifact is PARTIALLY COVERED. A rule verified by a requirement test is COVERED. | Later |

---

## docs/versioning-the-knowledge-layer.md

| # | Issue | Severity | Recommended Change | When |
|---|-------|----------|-------------------|------|
| 25 | No mention of specification lifecycle states. The document discusses versioning and branching but does not address how SUPERSEDED or DEPRECATED specifications interact with version control. | Low | Add a brief section noting that lifecycle state changes (ACTIVE → SUPERSEDED) should be committed with the same discipline as behavioral changes. | Later |

---

## docs/features-vs-implementations.md

| # | Issue | Severity | Recommended Change | When |
|---|-------|----------|-------------------|------|
| 26 | Uses "feature" and "specification" somewhat interchangeably. The core model distinguishes them: a feature is a capability; a specification is its formal definition. | Low | Minor terminology imprecision. A note in the introduction acknowledging the distinction would help. | Later |

---

## reference/anti-patterns.md

| # | Issue | Severity | Recommended Change | When |
|---|-------|----------|-------------------|------|
| 27 | Section 2 ("Writing Code Before Specifications") presents the ordering rule as absolute: "Correct STDD workflow: 1. Define specification, 2. Define behavior, 3. Define tests, 4. Generate implementation." No exception for bug fixes. | High | Add a qualifying note: "Exception: when the specification already defines the correct behavior and a bug is found in the implementation, the fix may proceed before updating tests. See the [Core Model](../docs/stdd-core-model.md) bug-fix flow." | Now |

---

## docs/prompt-engineering.md

| # | Issue | Severity | Recommended Change | When |
|---|-------|----------|-------------------|------|
| 28 | No issues found. The prompt engineering document is well-aligned with the core model. It focuses on specification quality, which applies to behavioral specifications regardless of the taxonomy. | — | No change needed. | — |

---

## docs/quick-start.md

| # | Issue | Severity | Recommended Change | When |
|---|-------|----------|-------------------|------|
| 29 | No mention of specification type or lifecycle state. The quick start presents a single happy-path flow for new features. | Low | This is appropriate for a quick-start guide. Adding taxonomy would slow it down. A reference to the core model at the end is sufficient. | Later |

---

## templates/specification.md

| # | Issue | Severity | Recommended Change | When |
|---|-------|----------|-------------------|------|
| 30 | Uses `Status: draft`. Does not include Type or Superseded-by/Supersedes fields. | High | Update to include the full metadata header from the core model. | Now |

---

## Summary: Changes Recommended Now

The following changes are recommended for this pass (low-risk, clearly beneficial):

| # | File | Change |
|---|------|--------|
| 2 | manifesto.md | Qualify "every change begins with a specification" |
| 4 | docs/method.md | Add note about execution flow variations |
| 5 | docs/method.md | Qualify "when a system evolves" language |
| 8 | docs/writing-specifications.md | Update lifecycle states to match core model |
| 14 | docs/engineering-playbook.md | Add lifecycle check to pre-flight checklist |
| 19 | docs/glossary.md | Add core model terms |
| 20 | docs/glossary.md | Expand "Specification" entry |
| 27 | reference/anti-patterns.md | Add bug-fix exception to ordering rule |
| 30 | templates/specification.md | Add metadata fields |
