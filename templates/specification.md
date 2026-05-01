Feature: [FEATURE_NAME]
Version: 1.0
Type: behavioral
Status: DRAFT

---

## Description

[1-3 sentences describing what this feature does and why it exists.]

## Inputs

| Name | Type | Constraints |
|------|------|-------------|
| [input_name] | [string / integer / decimal / list / object] | [required, max length, allowed values, etc.] |
| [input_name] | [type] | [constraints] |
| [input_name] | [type] | [constraints] |

## Outputs

| Name | Type | Description |
|------|------|-------------|
| [output_name] | [type] | [description] |
| [output_name] | [type] | [description] |

## Behavioral Scenarios

### Scenario: [normal case name]
  Given: [precondition]
  When: [action]
  Then: [expected outcome]

### Scenario: [edge case name]
  Given: [precondition]
  When: [action]
  Then: [expected outcome]

### Scenario: [another variation]
  Given: [precondition]
  When: [action]
  Then: [expected outcome]

## Rules

| ID | Description |
|----|-------------|
| [PREFIX]-RULE-01 | [Business rule that governs behavior, e.g. "Group discount of 10% applies for groups of 4 or more"] |
| [PREFIX]-RULE-02 | [Another rule] |
| [PREFIX]-RULE-03 | [Another rule] |

## Invariants

| ID | Description |
|----|-------------|
| [PREFIX]-INV-01 | [Rule that must always hold regardless of scenario, e.g. "Total must never be negative"] |
| [PREFIX]-INV-02 | [Another invariant] |
| [PREFIX]-INV-03 | [Another invariant] |

## Failure Conditions

| ID | Trigger | Response |
|----|---------|----------|
| [PREFIX]-FAIL-01 | [What goes wrong, e.g. "Input exceeds maximum length"] | [What the system does, e.g. "Return validation error with field name and constraint"] |
| [PREFIX]-FAIL-02 | [Trigger] | [Response] |
| [PREFIX]-FAIL-03 | [Trigger] | [Response] |

## Constraints

- [Boundary or limitation, e.g. "Maximum 500 items per request"]
- [Performance constraint, e.g. "Response within 200ms at p95"]
- [Precision constraint, e.g. "All monetary values use decimal arithmetic, not floating point"]

## Acceptance Cases

See: acceptance_cases.yaml

## Technologies

[List technologies, e.g. PostgreSQL, REST API, Python]

## Domain

[Business domain, e.g. E-commerce, Financial Services, Healthcare]

## NFR Overrides

[Any project-specific threshold changes with justification, or "None" if defaults apply]
