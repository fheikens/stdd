# STDD Glossary

Author: Frank Heikens
Version: 1.0
Date: 2026

Licensed under Creative Commons Attribution 4.0 (CC BY 4.0)

---

**Acceptance Case** --- A structured, language-neutral test case defined in YAML format that specifies concrete inputs and expected outputs for a behavioral scenario. Acceptance cases serve as the mechanical bridge between specifications and executable tests, and can be used to generate test suites in any programming language. See [Writing Specifications](writing-specifications.md), Section 8.

**Behavioral Scenario** --- A specification element that describes system behavior under a specific condition using Given/When/Then form. Each scenario defines a precondition, an action, and an expected outcome, and must map to at least one executable test. See [Writing Specifications](writing-specifications.md), Section 6.

**Brownfield System** --- An existing system with established code, limited test coverage, and implicit specifications embedded in the implementation. STDD can be applied incrementally to brownfield systems using the strangler pattern. See [Architecture](architecture.md), Section 10.

**Canonical Test** --- A behavior test that belongs to the feature definition rather than to any specific implementation. Canonical tests are expressed in a language-neutral format (typically YAML) and define the behavior that every implementation must satisfy. See [Features vs Implementations](features-vs-implementations.md), Section 6.

**Continuous Specification Integrity (CSI)** --- The CI/CD practice that ensures specifications, tests, and implementations never drift apart. A CSI pipeline enforces three gates: specification validation (traceability), test execution, and fingerprint verification. A build that breaks the fingerprint does not ship. See [Engineering Playbook](engineering-playbook.md), Section 5.

**Coverage Grade** --- The ratio of specification elements (rules, invariants, failure conditions, NFRs) that are directly verified by at least one test. Each element is classified as COVERED, PARTIALLY COVERED, or UNCOVERED. Coverage Grade is one of the five STDD quality metrics and is automatically validated by the CSI pipeline's Gate 1. See [Metrics & Measurement](metrics.md), Section 5.

**Contract** --- A defined interface between two components specifying inputs, outputs, constraints, and failure conditions. Contracts enable independent regeneration because components depend on the contract, not on each other's implementations. See [Architecture](architecture.md), Section 5.

**Defect Origin** --- A classification scheme for root-causing bugs. Every defect is traced to one of three origins: specification gap (the spec did not define the behavior), implementation bug (the spec and test existed but the code violated them), or test gap (the spec defined the behavior but no test verified it). Tracking defect origin over time reveals whether quality problems stem from the knowledge layer or the code layer. See [Metrics & Measurement](metrics.md), Section 8.

**Decomposition** --- The practice of breaking large functions or components into smaller, well-specified units that are each within AI's reliable generation capability. STDD targets approximately 50 lines per function, each with its own specification and tests. See [Engineering Playbook](engineering-playbook.md), Section 4.

**Dependency Injection** --- The primary architectural pattern that makes STDD components testable and regenerable. Components receive their dependencies as constructor parameters rather than creating them internally, allowing tests to inject fakes or alternative implementations. See [Architecture](architecture.md), Section 6.

**Feature** --- A language-independent definition of what the system must do. A feature typically contains a specification, behavioral scenarios, invariants, acceptance cases, and canonical tests. In STDD, the feature is permanent; the implementation is replaceable. See [Features vs Implementations](features-vs-implementations.md), Section 3.

**Implementation** --- A language-specific realization of a feature that satisfies the specification and passes all tests. Implementations are deliberately disposable artifacts in STDD; they can be discarded and regenerated at any time because the knowledge layer fully defines the expected behavior. See [Manifesto](../manifesto.md), Terminology.

**Invariant** --- A rule that must hold across all scenarios and all states of the system, regardless of the specific situation. Unlike scenarios that describe specific input-output pairs, invariants describe universal truths (e.g., "a balance must never be negative"). See [Writing Specifications](writing-specifications.md), Section 7.

**Knowledge Layer** --- The permanent layer above the code consisting of specifications, tests, acceptance cases, invariants, and contracts. The knowledge layer defines the system. Implementations are generated from it and verified against it. Its quality determines whether regeneration is safe. See [Manifesto](../manifesto.md), Terminology.

**NFR (Non-Functional Requirement)** --- A quality constraint under which functional behavior must operate, such as performance, security, accessibility, or data integrity requirements. In STDD, NFRs follow the same discipline as functional requirements: they must be explicitly defined, attached to specifications, and verified through tests. See [NFR Framework](nfr-framework.md).

**NFR Profile** --- A reusable bundle of universal, technology-triggered, and domain-triggered non-functional requirements packaged for a common system type (e.g., Web Application Profile, Internal API Service Profile). Profiles serve as starting points that teams refine with project-specific overrides. See [NFR Framework](nfr-framework.md), Section 9.

**Quality Score** --- A composite metric (0–1 scale) that combines the five STDD quality metrics — Specification Depth, Coverage Grade, Regeneration Confidence, Specification Stability, and Defect Origin — into a single number for reporting and comparison. Regeneration Confidence carries the highest weight because it is the most holistic measure of knowledge layer strength. See [Metrics & Measurement](metrics.md), Section 9.

**Regeneration** --- The act of discarding an existing implementation and generating a new one from the specification and tests. Regeneration is not an emergency measure; it is a normal STDD operation. Code is deliberately disposable. See [Method](method.md), Section 9.

**Regeneration Confidence** --- The most distinctive STDD quality metric. Measures whether an implementation can be discarded and regenerated from the specification and tests alone, with the new implementation passing all tests. A feature that passes regeneration demonstrates that the knowledge layer fully captures its behavior. See [Metrics & Measurement](metrics.md), Section 6.

**Regeneration Loop** --- The central mechanism that distinguishes STDD from traditional test-first approaches. The loop consists of: keep specification, keep tests, discard implementation, generate new implementation, execute tests, accept if tests pass. This is only safe when the knowledge layer is strong enough to fully define the expected behavior. See [Method](method.md), Section 9.

**Regeneration Safe Zone** --- A category of code that is well suited for regeneration, such as business logic, application services, data transformations, and algorithmic components. Code that is not safe to regenerate (database schemas, external integrations, security boundaries) is maintained manually behind interfaces. See [Architecture](architecture.md), Section 8.

**Requirement** --- A high-level description of desired system behavior or business intent. In STDD, a requirement must be refined into a precise, testable specification before it can be built. If a requirement cannot be tested, it does not exist. See [Manifesto](../manifesto.md), Terminology.

**Specification** --- A precise, testable definition of system behavior derived from a requirement. A complete specification answers six questions: what does the system do, what are the inputs and outputs, what are the behavioral scenarios, what are the invariants, what are the failure conditions, and what are the constraints. See [Writing Specifications](writing-specifications.md), Section 3.

**Specification Readiness** --- A pre-generation checklist that verifies a specification is precise enough for AI generation. Readiness criteria include: every rule has a unique ID, every rule describes one behavior, constraints are quantified, failure conditions are explicit, boundaries are defined, and language is unambiguous. A specification that fails readiness checks is likely to require multiple generation attempts. See [AI Prompt Engineering](prompt-engineering.md), Section 10.

**Specification Depth** --- A measure of how thoroughly a specification captures the behavior that matters, calculated as the count of rules, invariants, failure conditions, and NFRs. Shallow depth is a reliable signal of risk: a feature with few specified rules likely has unverified behavior. See [Metrics & Measurement](metrics.md), Section 4.

**Specification Fingerprint** --- A cryptographic hash of the knowledge layer (specifications, tests, behavioral contracts, and acceptance cases) that defines a system's behavioral identity. Two implementations passing the same fingerprint are behaviorally equivalent, regardless of language or internal design. Pure implementation changes do not alter the fingerprint. See [Manifesto](../manifesto.md), Core Concepts; [Engineering Playbook](engineering-playbook.md), Section 5.

**Specification Stability** --- A metric that tracks how often the knowledge layer changes relative to the implementation layer. High stability (few spec changes, many implementation changes) indicates a mature knowledge layer where the specification has settled. Low stability indicates the specification is still being discovered. The CSI fingerprint gate detects when implementation changes happen without corresponding specification updates. See [Metrics & Measurement](metrics.md), Section 7.

**Specification Pyramid** --- A four-level model that ensures compositions are tested, not just individual parts. The levels are: unit (single function), component (multiple functions within one module), integration (multiple components collaborating), and system (full end-to-end workflows). Each level has its own specifications and tests. See [Method](method.md), Section 10.

**Specification-to-Test Gap** --- The risk that the test suite does not fully cover the behavioral intent expressed in the specification. STDD narrows this gap through traceability matrices, acceptance case generation, coverage audits, invariant tests, and paired specification-test reviews. See [Writing Specifications](writing-specifications.md), Section 13.

**STDD (Specification & Test-Driven Development)** --- A software engineering methodology for the AI era in which specifications and tests together define a system's behavior, while implementations are replaceable artifacts. Specifications define intent, tests verify behavior, and AI generates implementations. See [Manifesto](../manifesto.md).

**Strangler Pattern** --- An incremental adoption strategy for applying STDD to existing systems. New features follow full STDD; modified features receive specifications and tests before changes are made; stable features are left as-is until they need to change. See [Architecture](architecture.md), Section 10.

**T-Spec (Testable Specification)** --- A specification written in verifiable Given/When/Then form. If a requirement cannot be expressed as a testable specification, it is not ready to build. The T-Spec is the foundational format that connects requirements to executable tests. See [Manifesto](../manifesto.md), Core Concepts.

**Test** --- An automated verification that confirms a specification is satisfied. Tests translate specifications into verifiable system behavior and serve multiple purposes: verify correctness, prevent regressions, enable safe regeneration, and provide executable documentation. See [Manifesto](../manifesto.md), Terminology; [Method](method.md), Section 6.

**Test-First Prompting (TFP)** --- The practice of providing AI with the specification and failing tests, then letting it generate implementations until the tests pass. An effective TFP prompt includes four parts: specification, tests, constraints, and context. TFP is not "ask AI to write code and then add tests." See [Engineering Playbook](engineering-playbook.md), Section 3.

**Traceability Matrix** --- A mapping that links every specification element (scenario, invariant, failure condition) to at least one executable test. The matrix makes coverage gaps immediately visible and is validated as part of the CSI pipeline. See [Writing Specifications](writing-specifications.md), Section 13; [Engineering Playbook](engineering-playbook.md), Section 5.
