# Versioning the Knowledge Layer in STDD
## Specification & Test-Driven Development

Author: Frank Heikens
Version: 1.1
Date: 2026

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Why the Knowledge Layer Must Be Versioned](#2-why-the-knowledge-layer-must-be-versioned)
3. [What Must Be Stored in Version Control](#3-what-must-be-stored-in-version-control)
4. [Repository Structure](#4-repository-structure)
5. [Change Workflow](#5-change-workflow)
6. [Traceability](#6-traceability)
7. [Pull Requests and Reviews](#7-pull-requests-and-reviews)
8. [Branching Strategy for Specification Changes](#8-branching-strategy-for-specification-changes)
9. [Conflict Resolution When Specifications Diverge](#9-conflict-resolution-when-specifications-diverge)
10. [Release Tagging and the Knowledge Layer](#10-release-tagging-and-the-knowledge-layer)
11. [Conclusion](#11-conclusion)

---

## 1. Introduction

Specification & Test-Driven Development (STDD) treats organizational knowledge as a first-class artifact.

In STDD, the behavioral definition of a system — its specifications, invariants, acceptance cases, and constraints — is the **true source of truth**. Implementations are replaceable realizations of that knowledge.

---

## 2. Why the Knowledge Layer Must Be Versioned

The knowledge layer defines **what the system must do**.

Changes to specifications or invariants represent real behavioral changes and therefore must be tracked with the same rigor as source code.

Version control provides:

- history
- traceability
- review workflows
- rollback capability
- distributed backups

---

## 3. What Must Be Stored in Version Control

At minimum, the following artifacts should live in Git:

- feature specifications
- behavior scenarios
- invariants and rules
- canonical acceptance cases
- capability requirements
- implementation constraints
- prompts used for generation and clarification
- diagrams and architectural documentation
- generated executable tests
- implementations

---

## 4. Repository Structure

The STDD repository structure keeps **organizational knowledge separate from technical realization**. Features, specifications, and acceptance cases live under `features/`, while language-specific source and tests live under `implementations/`.

For the canonical repository structure, see [Engineering Playbook](engineering-playbook.md), Section 2.

---

## 5. Change Workflow

A typical STDD change process follows this sequence:

1. Update the feature specification
2. Update invariants and acceptance cases
3. Regenerate or update implementations
4. Execute tests
5. Commit the complete change set

This ensures **behavioral intent remains synchronized with executable code**.

---

## 6. Traceability

Every implementation should be traceable to a specific version of the knowledge layer.

For example:

- implementation built from feature commit `abc123`
- test generation based on acceptance cases at commit `abc123`
- release `v1.4.0` tied to feature-set tag `features-v1.4.0`

This guarantees reproducibility and simplifies audits.

---

## 7. Pull Requests and Reviews

Changes to the knowledge layer should go through pull request review just like source code.

Reviewers focus on:

- ambiguity
- missing edge cases
- rule conflicts
- invariant violations

rather than syntax or style.

---

## 8. Branching Strategy for Specification Changes

Specification changes follow the same branching model as code changes, but with additional discipline to keep the knowledge layer coherent.

### One branch per feature, specs included

Each feature gets its own branch. The specification, acceptance cases, invariants, and tests for that feature all live on the same branch as the implementation. Never split specification changes across multiple branches and never put specs on one branch while the corresponding tests live on another. The unit of change is the complete behavioral definition plus its verification plus its realization.

### Knowledge layer commits come first

On any feature branch, the commit history should reflect the STDD workflow order:

1. **Specification changes** are committed first (feature definition, invariants, acceptance cases).
2. **Test changes** are committed next (executable tests derived from the spec).
3. **Implementation changes** are committed last (code that satisfies the tests).

This ordering makes the branch history readable as a narrative: here is what the system should do, here is how we verify it, and here is one way to make it happen. It also means that if the implementation is later regenerated, the spec and test commits remain untouched.

### PR review order mirrors commit order

When reviewing a pull request, reviewers should read the spec diff first, then the test diff, then the implementation diff. This matches the STDD principle that behavioral intent drives everything. A spec change that is ambiguous or incomplete should block the entire PR, regardless of how clean the implementation looks.

### Merge frequently, branch briefly

Long-lived specification branches are dangerous. When two branches independently evolve the same area of the knowledge layer for weeks, the resulting merge conflicts are not just textual — they represent genuine behavioral disagreements that are expensive to resolve. Spec branches should merge to the main branch as soon as the behavioral change is stable and reviewed. Short-lived branches keep the knowledge layer convergent.

If a large feature requires extended development, prefer incremental spec additions that merge independently over a single large spec rewrite that lives on a branch for weeks (see also Section 9 for handling conflicts when branches do diverge).

---

## 9. Conflict Resolution When Specifications Diverge

When two branches modify the same specification, the resulting merge conflict is fundamentally different from a code conflict. A code conflict is a textual disagreement about how to do something. A specification conflict is a behavioral disagreement about what the system should do. These require different resolution strategies.

### Spec file merge conflicts

When Git reports a merge conflict in a specification file, do not resolve it by mechanically choosing one side. Instead, read both versions and determine whether the behaviors are compatible or contradictory.

- **Compatible behaviors:** both branches add new scenarios or extend existing ones without contradiction. Resolution: combine both additions into a single specification that covers all described behaviors.
- **Contradictory behaviors:** the two branches define mutually exclusive behavior for the same scenario. Resolution: this is a real design disagreement. It cannot be resolved by Git. The team must decide which behavior the system should exhibit, or whether a new spec element is needed to accommodate both (see the concrete example below).

### Conflicting invariants

If two branches add invariants that contradict each other, the conflict is a design-level problem. For example, if Branch A adds "a customer may hold at most 4 seats" and Branch B adds "a customer may hold at most 6 seats," no amount of textual merging resolves the disagreement. The team must decide on the correct business rule. The resolution is a single invariant that reflects the agreed-upon constraint.

Treat invariant conflicts as the highest-priority merge issue. An unresolved invariant conflict means the system has no coherent behavioral definition.

### Test conflicts

When two branches add tests for the same spec ID, both sets of tests should generally be kept. Unlike invariants, tests are additive — they verify different aspects or scenarios of the same behavior. After merging, run the full test suite. If any tests contradict each other (one asserts a result of X, the other asserts a result of Y for the same input), the root cause is a spec conflict that was not fully resolved.

### Fingerprint conflicts

The Specification Fingerprint is a computed value. Never resolve a fingerprint merge conflict by manually editing the `.fingerprint` file or choosing one side. Instead, after resolving all spec and test conflicts, recompute the fingerprint from the merged knowledge layer. The recomputed fingerprint becomes the single source of truth for the merged state.

### Concrete example

Branch A adds the following invariant to the seat reservation spec:

> "Seat holds expire after 15 minutes."

Branch B adds:

> "VIP seat holds expire after 30 minutes."

These are not contradictory — they are incomplete. Neither branch accounts for the other's use case. The correct resolution introduces a new spec element:

> "Hold duration depends on customer tier. Standard holds expire after 15 minutes. VIP holds expire after 30 minutes."

This requires:
- A new invariant defining hold duration by tier
- Updated acceptance cases covering both standard and VIP expiration
- A recomputed fingerprint reflecting the merged behavioral definition

The key insight is that the merge conflict revealed a missing dimension in the specification (customer tier). This is a feature of the STDD workflow, not a problem — specification conflicts surface real design questions early.

---

## 10. Release Tagging and the Knowledge Layer

In STDD, a release is not just a snapshot of code. It is a snapshot of behavior. Release tagging should reflect this by linking every release to a specific state of the knowledge layer.

### Dual tagging: version number plus fingerprint

Tag each release with both a semantic version number and the Specification Fingerprint of the knowledge layer at that point:

```
v1.4.0 + fingerprint abc123
```

This means: "release v1.4.0 implements the behavior defined by the knowledge layer whose fingerprint is `abc123`." The version number is for humans and package managers. The fingerprint is for machines and verification tooling.

### Semantic versioning aligned to spec changes

Align semantic version increments to the nature of the specification change, not the size of the code change:

| Spec change | Version increment | Example |
|---|---|---|
| New spec additions (new features, new scenarios) | **Minor** version bump | `v1.3.0` to `v1.4.0` |
| Spec removals or behavioral changes to existing specs | **Major** version bump | `v1.4.0` to `v2.0.0` |
| Implementation-only changes (refactoring, performance, regeneration) with no spec change | **Patch** version bump | `v1.4.0` to `v1.4.1` |

This convention makes version numbers meaningful. A major version bump tells consumers that the system's behavioral contract has changed in a potentially breaking way. A minor bump means new behavior was added but existing behavior is preserved. A patch bump means the observable behavior is identical — only the realization changed.

### Release notes from spec diffs

Generate release notes by diffing the knowledge layer between two tags rather than by reading commit messages. The spec diff between `v1.3.0` and `v1.4.0` tells you exactly which behaviors were added, modified, or removed. This produces release notes that describe what the system does differently, not what the developers did.

### Rollback safety

If you need to roll back to a previous release, the fingerprint tells you exactly which behavioral specification that release satisfies. Rolling back to `v1.3.0` means restoring the behavior defined by fingerprint `def456`. You can then verify the rollback by running the test suite associated with that fingerprint.

This eliminates the ambiguity of traditional rollbacks, where reverting code changes may or may not restore the intended behavior depending on database migrations, configuration changes, and other side effects. In STDD, the fingerprint is the behavioral contract. If the tests for that fingerprint pass, the rollback is correct.

For the complementary CI/CD perspective on fingerprint verification, see [Engineering Playbook](engineering-playbook.md), Section 5 (CSI).

---

## 11. Conclusion

In STDD, source control protects not only code but the **behavioral definition of the system**.

By storing the knowledge layer in Git, organizations gain:

- full history
- traceability
- safe regeneration of implementations
- stable system behavior over time

**The knowledge layer becomes the permanent record of system intent.**

---

For guidance on writing the specifications that form the knowledge layer, see [Writing Specifications](writing-specifications.md).

For non-functional quality constraints that must be versioned alongside specifications, see [NFR Framework](nfr-framework.md). For CI/CD enforcement of specification integrity, see [Engineering Playbook](engineering-playbook.md), Section 5 (CSI).
