Feature: [FEATURE_NAME]
Version: 1.0
Status: draft

---

## Description

[1-3 sentences describing what this feature does and why it exists.]

## Inputs

| ID | Name | Type | Constraints |
|----|------|------|-------------|
| IN-1 | [input_name] | [string / integer / decimal / list / object] | [required, max length, allowed values, etc.] |
| IN-2 | [input_name] | [type] | [constraints] |
| IN-3 | [input_name] | [type] | [constraints] |

## Outputs

| ID | Name | Type |
|----|------|------|
| OUT-1 | [output_name] | [type] |
| OUT-2 | [output_name] | [type] |

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
| RULE-1 | [Business rule that governs behavior, e.g. "Group discount of 10% applies for groups of 4 or more"] |
| RULE-2 | [Another rule] |
| RULE-3 | [Another rule] |

## Invariants

| ID | Description |
|----|-------------|
| INV-1 | [Rule that must always hold regardless of scenario, e.g. "Total must never be negative"] |
| INV-2 | [Another invariant] |
| INV-3 | [Another invariant] |

## Failure Conditions

| ID | Trigger | Response |
|----|---------|----------|
| FAIL-1 | [What goes wrong, e.g. "Input exceeds maximum length"] | [What the system does, e.g. "Return validation error with field name and constraint"] |
| FAIL-2 | [Trigger] | [Response] |
| FAIL-3 | [Trigger] | [Response] |

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
