
# Versioning the Knowledge Layer in STDD
## Specification & Test‑Driven Development

Author: Frank Heikens
Version: 1.0
Date: 2026

---

## 1. Introduction

Specification & Test‑Driven Development (STDD) treats organizational knowledge as a first‑class artifact.

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

## 4. Repository Structure Example

Example STDD repository structure:

```
stdd-system/
  features/
  implementations/
  prompts/
  diagrams/
  docs/
  tools/
```

This keeps **organizational knowledge separate from technical realization**.

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

## 8. Conclusion

In STDD, source control protects not only code but the **behavioral definition of the system**.

By storing the knowledge layer in Git, organizations gain:

- full history
- traceability
- safe regeneration of implementations
- stable system behavior over time

**The knowledge layer becomes the permanent record of system intent.**

---

For guidance on writing the specifications that form the knowledge layer, see **Writing Specifications in STDD**.

For non‑functional quality constraints that must be versioned alongside specifications, see **STDD Non‑Functional Requirements Framework**.
