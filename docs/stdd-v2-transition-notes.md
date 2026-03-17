# STDD v2 Transition Notes
## What Is Changing, Why, and How to Interpret Older Documents

Author: Frank Heikens
Version: 1.0
Date: 2026

---

## What Is Changing

The STDD Core Model introduces explicit structure that was previously implicit. The core ideas of STDD are unchanged. What changes is how the method names, categorizes, and tracks its artifacts.

### 1. Specification Taxonomy

**Before:** "Specification" was a single concept. All specifications were treated the same way — a precise, testable definition of system behavior.

**After:** STDD recognizes three specification types:
- **Behavioral specification** — defines what the system must do (the original "specification")
- **Integration mapping** — defines how components connect (previously called "contracts" or "boundary specifications")
- **Configuration decision** — documents a technical choice and its rationale (previously informal or undocumented)

**Impact:** Existing specifications are behavioral specifications. No renaming is needed. The taxonomy adds categories for artifacts that existed but were not formally classified.

### 2. Test Taxonomy

**Before:** Tests were categorized by pyramid level (unit, component, integration, system) but not by purpose.

**After:** STDD recognizes three test categories:
- **Requirement test** — directly verifies a behavioral specification rule
- **Integration test** — verifies that components honor a contract
- **Regression artifact** — detects unintended changes in output (golden files, snapshots)

**Impact:** Existing tests are either requirement tests or integration tests. This naming makes traceability more precise — you can now ask "what percentage of behavioral rules are verified by requirement tests?" separately from "what percentage of contracts are verified by integration tests?"

### 3. Artifact Lifecycle

**Before:** Specifications had informal states: `draft`, `review`, `accepted`. No formal model for supersession, deprecation, or rejection.

**After:** STDD defines five lifecycle states: DRAFT, ACTIVE, SUPERSEDED, DEPRECATED, REJECTED. Transition rules are explicit. Supersession has a formal recording mechanism.

**Impact:** Existing specifications in `accepted` state are ACTIVE. Existing specifications in `draft` remain DRAFT. The `review` state is removed — review is a process step, not a lifecycle state.

### 4. Execution Flows

**Before:** The method presented a single workflow: specification → tests → implementation. Exceptions for bug fixes and brownfield adoption were described in separate documents but not named as formal flows.

**After:** STDD defines four named execution flows:
- **New Feature** — the standard spec-first flow
- **Behavior Change** — update spec first, then implementation
- **Bug Fix (Spec Already Correct)** — fix the implementation, verify/add tests
- **Discovery and Reverse Engineering** — extract spec from existing reality

**Impact:** The biggest practical change. Teams no longer need to force every scenario through the spec-first pipeline. Bug fixes where the specification already defines the correct behavior can proceed directly to the fix. Discovery work can start from observation rather than prescription.

### 5. Traceability Refinement

**Before:** The traceability matrix linked specification IDs to tests in a flat structure.

**After:** The traceability matrix adds columns for specification type, specification status, and test type. Coverage is reported in three categories: requirement coverage, integration coverage, and regression coverage.

**Impact:** More structured reporting. No existing traceability matrices need to change immediately — the additional columns can be added incrementally.

### 6. Metadata Convention

**Before:** Specifications used `Feature: / Version: / Status:` headers with informal states.

**After:** Specifications use a metadata header with `Type:`, `Status:` (using the formal lifecycle states), and optional `Superseded-by:` / `Supersedes:` fields.

**Impact:** Existing specification headers remain valid. The `Type` field is new. Existing `Status: draft` maps to DRAFT. Existing `Status: accepted` maps to ACTIVE. Add the new fields when specifications are next modified.

---

## Why These Changes Were Made

### Reducing ambiguity for teams

The original STDD documents were written for a single author and early adopters. As teams adopt STDD, the lack of explicit categories created recurring questions: "Is this a specification or a contract?" "What happens when we find a bug but the spec is already correct?" "How do we mark a spec as replaced?"

The core model answers these questions once.

### Making the method teachable

A method that presents a single flow for all scenarios forces practitioners to discover exceptions through experience. Named execution flows make the method teachable: "For this situation, use this flow."

### Preparing for tooling

Future STDD tooling (traceability validators, coverage dashboards, lifecycle trackers) needs structured data. The metadata convention and traceability matrix structure provide that foundation without requiring tooling today.

### Preserving pragmatism

The bug-fix flow explicitly allows fixing before writing tests when the specification is already correct. This removes a friction point that made STDD feel dogmatic for a common scenario.

---

## What Remains Unchanged

- **Core philosophy:** Specifications define intent. Tests verify behavior. Implementations are replaceable.
- **Regeneration model:** Code is deliberately disposable. The knowledge layer makes regeneration safe.
- **Specification Pyramid:** Unit, component, integration, and system levels remain the same.
- **Test-First Prompting:** The TFP prompt structure and workflow are unchanged.
- **Continuous Specification Integrity:** The CSI pipeline gates (traceability, tests, fingerprint) are unchanged.
- **Specification Fingerprint:** The fingerprint mechanism is unchanged.
- **NFR Framework:** The layered NFR model is unchanged.
- **Writing Specifications guidance:** The six-question structure, Given/When/Then scenarios, invariants, acceptance cases, and review checklist are unchanged.
- **All existing documents:** No documents are deleted or renamed. Existing content remains valid.

---

## How to Interpret Older Documents

Existing STDD documents were written before the core model was formalized. When reading them:

1. **"Specification" in older documents means "behavioral specification"** unless the context clearly indicates a contract or configuration decision.

2. **"Every change begins with a specification"** applies to behavioral changes. Bug fixes where the specification already defines the correct behavior follow the bug-fix flow.

3. **`Status: accepted`** in older specifications means ACTIVE.

4. **`Status: review`** in older specifications has no direct equivalent. If the specification has been accepted and drives implementation, treat it as ACTIVE. If it has open questions, treat it as DRAFT.

5. **Traceability matrices without type columns** are valid. The additional columns (spec type, spec status, test type) can be added when the matrix is next updated.

6. **Integration tests and contract tests** described in older documents correspond to the "integration test" category in the test taxonomy. The system-level STDD document's "service boundary specifications" correspond to "integration mappings."

7. **The ordering rule** ("specification before implementation") applies to defining new behavior and changing existing behavior. It does not apply to fixing bugs where the specification already covers the correct behavior. Older documents may present the rule as absolute — the core model's execution flows take precedence.

---

## Migration Steps for Existing STDD Users

**No immediate action is required.** The core model is additive. Existing specifications, tests, and workflows remain valid.

When convenient:

1. **Add metadata headers** to specifications as they are modified. Use `Type: behavioral` for existing feature specs. Use `Status: ACTIVE` for accepted specs.

2. **Add type columns** to traceability matrices when they are next updated. Mark existing test entries as `requirement` or `integration` based on what they verify.

3. **Reference the named execution flows** in team workflows. This is a naming change, not a process change — the flows already existed in practice.

4. **Update specification templates** to include the full metadata header. The updated template is in [Templates](../templates/specification.md).

5. **Review the glossary** for new terms. The glossary has been updated with core model terminology.

---

## Questions and Trade-offs

**Q: Should we retroactively add Type and Status to all existing specifications?**
A: Not recommended. Add metadata when specs are next modified. Mass edits create commit noise without behavioral value.

**Q: Does the bug-fix flow weaken the spec-first principle?**
A: No. The bug-fix flow applies only when the specification already defines the correct behavior. The spec was written first — the implementation just failed to follow it. The principle is preserved: the specification is authoritative.

**Q: Are configuration decisions really specifications?**
A: They are a type of documented artifact in the STDD knowledge layer. They carry less rigor than behavioral specifications (tests are not always mandatory), but they capture decisions that affect system behavior and would otherwise be lost.

**Q: Should regression artifacts be eliminated in favor of requirement tests?**
A: Ideally, yes — requirement tests are stronger. Practically, regression artifacts are useful for complex outputs where writing individual assertions is impractical. The core model classifies them honestly: they provide PARTIALLY COVERED status, not full coverage.
