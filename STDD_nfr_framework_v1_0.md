
# STDD Non‑Functional Requirements Framework
## Testable Quality Constraints for Specification & Test‑Driven Development

Author: Frank Heikens
Version: 1.0
Date: 2026

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. Why Non‑Functional Requirements Matter in STDD](#2-why-non-functional-requirements-matter-in-stdd)
- [3. The Layered NFR Model](#3-the-layered-nfr-model)
- [4. Universal Requirements](#4-universal-requirements)
- [5. Technology‑Triggered Requirements](#5-technology-triggered-requirements)
- [6. Domain‑Triggered Requirements](#6-domain-triggered-requirements)
- [7. Project‑Specific Overrides](#7-project-specific-overrides)
- [8. Making NFRs Testable](#8-making-nfrs-testable)
- [9. NFR Profiles](#9-nfr-profiles)
- [10. Integrating NFRs into the STDD Workflow](#10-integrating-nfrs-into-the-stdd-workflow)
- [11. NFR Regeneration Safety](#11-nfr-regeneration-safety)
- [12. Reference: Default NFR Sets](#12-reference-default-nfr-sets)
- [13. Conclusion](#13-conclusion)

---

# 1. Introduction

Specification & Test‑Driven Development defines systems through behavior.

Specifications describe what the system must do.
Tests verify that the behavior is correct.
AI generates the implementation.

However, a system can satisfy every functional requirement and still be unsuitable for production.

A shopping cart can calculate totals correctly but respond in ten seconds.
A login system can authenticate users correctly but store passwords in plain text.
An API can return valid data but expose stack traces on errors.

These failures are **non‑functional**.

Non‑functional requirements (NFRs) define the **quality constraints** under which functional behavior must operate.

STDD must account for NFRs explicitly.

This document introduces a framework for defining, organizing, and testing non‑functional requirements within the STDD methodology.

---

# 2. Why Non‑Functional Requirements Matter in STDD

In traditional development, non‑functional requirements are often carried as implicit knowledge by senior engineers.

An experienced developer knows to use parameterized queries.
An experienced developer knows to set timeouts on HTTP calls.
An experienced developer knows to validate input at system boundaries.

AI does not carry this implicit knowledge reliably.

When AI generates implementations, it may produce code that is functionally correct but violates non‑functional expectations.

This is especially dangerous in STDD because the regeneration loop only verifies what the tests cover.

If non‑functional requirements are not tested, they are not enforced.

**In STDD, an untested requirement does not exist.**

This applies to non‑functional requirements with the same force as functional requirements.

NFRs must be:

- explicitly defined
- attached to specifications
- verified through tests

---

# 3. The Layered NFR Model

Non‑functional requirements are not unique to each project.

Most NFRs are **implied by the technology stack and the domain**.

This framework organizes NFRs into four layers, ordered from most general to most specific.

```
Layer 4: Project‑Specific Overrides
Layer 3: Domain‑Triggered Requirements
Layer 2: Technology‑Triggered Requirements
Layer 1: Universal Requirements
```

Each layer builds on the one below it.

Higher layers can **add** requirements or **override thresholds** from lower layers.

Higher layers cannot **remove** requirements from lower layers unless explicitly justified and documented.

This model is analogous to CSS specificity: universal defaults form the base, and more specific contexts refine them.

---

# 4. Universal Requirements

Universal requirements apply to virtually every software system regardless of technology or domain.

These represent baseline engineering discipline.

## 4.1 Error Handling

- The system must not expose internal error details to end users.
- Errors must be logged with sufficient context for debugging.
- The system must fail gracefully under unexpected conditions.

## 4.2 Input Validation

- All input from external sources must be validated at system boundaries.
- Invalid input must be rejected with a clear error response.
- Internal function calls between trusted components do not require redundant validation.

## 4.3 Logging and Observability

- The system must produce structured logs for key operations.
- Logs must not contain sensitive data such as passwords, tokens, or personal identifiers.

## 4.4 Timeouts and Resource Limits

- All external calls must have explicit timeouts.
- The system must not allow unbounded resource consumption from a single request.

## 4.5 Dependency Management

- Dependencies must be pinned to specific versions.
- Known vulnerable dependencies must not be used.

## 4.6 Configuration

- Secrets must not be hardcoded in source code.
- Environment‑specific values must be externalized.

---

# 5. Technology‑Triggered Requirements

When a specification declares or implies a specific technology, additional NFRs are automatically activated.

These requirements are **triggered by the presence of a technology in the stack**.

## 5.1 SQL Databases

When the system uses a SQL database:

- All queries must use parameterized statements. No string concatenation or interpolation of user input into queries.
- Database connections must be pooled and limited.
- Migrations must be versioned and reversible.

## 5.2 HTML and Web Output

When the system renders HTML or serves web content:

- All dynamic content must be output‑encoded to prevent cross‑site scripting (XSS).
- HTTP responses must include appropriate security headers (Content‑Security‑Policy, X‑Content‑Type‑Options, X‑Frame‑Options).
- Cookies containing session data must use Secure, HttpOnly, and SameSite attributes.

## 5.3 REST and HTTP APIs

When the system exposes HTTP endpoints:

- Input payloads must be validated against a schema.
- Responses must use appropriate HTTP status codes.
- Rate limiting must be applied to public endpoints.
- API responses must not leak internal implementation details.

## 5.4 Authentication and Authorization

When the system handles user credentials:

- Passwords must be hashed using a modern adaptive algorithm (bcrypt, argon2, scrypt).
- Authentication endpoints must enforce rate limiting.
- Session tokens must be generated with cryptographically secure randomness.
- Failed authentication attempts must not reveal whether the username or password was incorrect.

## 5.5 File Uploads

When the system accepts file uploads:

- File size must be limited.
- File type must be validated by content inspection, not only by extension.
- Uploaded files must be stored outside the web root.
- File paths must be sanitized to prevent path traversal attacks.

## 5.6 Large Language Model Integration

When the system integrates with an LLM:

- User input must be separated from system instructions to mitigate prompt injection.
- LLM output must be treated as untrusted data and validated before use.
- Sensitive data must not be included in prompts sent to external LLM providers.
- Token usage and cost must be monitored and bounded.

## 5.7 Message Queues and Async Processing

When the system uses message queues or asynchronous job processing:

- Messages must be processed idempotently.
- Failed messages must be routed to a dead letter queue.
- Processing timeouts must be configured.

## 5.8 Caching

When the system uses a caching layer:

- Cache keys must be deterministic.
- Cache invalidation strategy must be defined.
- Sensitive data must not be cached without encryption.

---

# 6. Domain‑Triggered Requirements

Certain business domains carry additional quality constraints.

These requirements are triggered when the system operates within a specific domain.

## 6.1 Financial Systems

- Monetary calculations must use decimal types with defined precision. Floating point must not be used for currency.
- All financial transactions must be logged with an immutable audit trail.
- Operations that modify balances must be idempotent.
- Tax calculations must be traceable to specific rules and rates.

## 6.2 Healthcare Systems

- Patient data must be encrypted at rest and in transit.
- All access to patient records must be logged in an audit trail.
- Data retention and deletion must comply with applicable regulations (HIPAA, GDPR).
- Role‑based access control must enforce least‑privilege access.

## 6.3 User‑Facing Web Applications

- Pages must achieve interactive readiness within a defined threshold (default: 2 seconds).
- The interface must meet accessibility standards (WCAG 2.1 AA minimum).
- The system must function correctly across supported browsers and devices.

## 6.4 Multi‑Tenant Systems

- Tenant data must be strictly isolated. No tenant may access another tenant's data.
- Shared infrastructure must enforce per‑tenant resource limits.
- Tenant identifiers must be validated on every request.

## 6.5 Real‑Time Systems

- Message delivery latency must not exceed a defined threshold.
- The system must handle connection loss and reconnection gracefully.
- Message ordering guarantees must be specified and tested.

---

# 7. Project‑Specific Overrides

The previous layers define sensible defaults.

Individual projects may need to adjust thresholds or add requirements specific to their context.

Project‑specific overrides are defined in the project's specification and must be documented with justification.

Examples:

- Page load threshold reduced from 2 seconds to 500 milliseconds for a trading dashboard.
- Rate limit increased from 100 to 1000 requests per minute for an internal API.
- Accessibility requirement elevated from WCAG AA to WCAG AAA for a government service.
- Audit logging requirement added for a system that does not otherwise fall under financial or healthcare domains.

Overrides follow a simple rule:

**Overrides may tighten constraints. Loosening a lower‑layer constraint requires documented justification.**

---

# 8. Making NFRs Testable

Non‑functional requirements are only useful in STDD if they can be verified through tests.

Each NFR category maps to specific testing approaches.

## 8.1 Security

- Static analysis scans detect insecure patterns (SQL string concatenation, missing output encoding).
- Automated penetration tests verify input handling.
- Dependency scanning detects known vulnerabilities.

Example test:

```python
def test_no_sql_injection():
    malicious_input = "'; DROP TABLE users; --"
    result = search_users(malicious_input)
    assert users_table_exists()
    assert result == []
```

## 8.2 Performance

- Load tests verify response time under expected traffic.
- Benchmarks verify that critical operations complete within thresholds.

Example test:

```python
def test_page_load_time():
    start = time.monotonic()
    response = client.get("/dashboard")
    elapsed = time.monotonic() - start
    assert response.status_code == 200
    assert elapsed < 2.0
```

## 8.3 Resilience

- Fault injection tests verify behavior when dependencies fail.
- Timeout tests verify that external call failures do not block the system.

Example test:

```python
def test_external_service_timeout():
    with simulate_timeout("payment_gateway"):
        result = process_order(order)
    assert result.status == "payment_pending"
    assert result.error == "payment gateway unavailable"
```

## 8.4 Accessibility

- Automated accessibility audits verify WCAG compliance.
- Axe or Lighthouse scans run as part of the test suite.

## 8.5 Data Integrity

- Tests verify that monetary calculations produce correct results with decimal precision.
- Tests verify that audit logs are created for sensitive operations.

Example test:

```python
def test_currency_precision():
    result = calculate_total([0.1, 0.2], tax_rate=0.0)
    assert result == Decimal("0.3")
    assert isinstance(result, Decimal)
```

## 8.6 Code Quality (Static Analysis)

- Linters and static analysis tools enforce coding standards.
- Security‑focused scanners detect anti‑patterns.

These tools run as part of the CI pipeline alongside behavioral tests.

---

# 9. NFR Profiles

To simplify adoption, common combinations of NFRs can be packaged into **profiles**.

A profile bundles universal, technology, and domain requirements into a reusable set.

Example profiles:

### Web Application Profile

Includes:
- Universal requirements
- HTML/Web Output requirements (Section 5.2)
- REST API requirements (Section 5.3)
- Authentication requirements (Section 5.4)
- User‑Facing Web Application requirements (Section 6.3)

### Internal API Service Profile

Includes:
- Universal requirements
- REST API requirements (Section 5.3)
- SQL Database requirements (Section 5.1)
- Message Queue requirements (Section 5.7)

### AI‑Powered Application Profile

Includes:
- Universal requirements
- LLM Integration requirements (Section 5.6)
- REST API requirements (Section 5.3)
- Caching requirements (Section 5.8)

Profiles serve as starting points.

Teams select a profile and apply project‑specific overrides as needed.

---

# 10. Integrating NFRs into the STDD Workflow

NFRs integrate into the standard STDD development loop.

## Step 1: Specification

When writing a specification, declare:

- the technologies used
- the domain context
- any project‑specific overrides

Example:

```
Feature: User Registration

Technologies: PostgreSQL, REST API, HTML
Domain: User‑Facing Web Application

Override: Page load threshold = 1.5 seconds
```

## Step 2: NFR Activation

Based on the declared technologies and domain, the applicable NFR layers activate automatically.

The specification above triggers:

- Universal requirements (Layer 1)
- SQL Database requirements (Section 5.1)
- REST API requirements (Section 5.3)
- HTML/Web Output requirements (Section 5.2)
- Authentication requirements (Section 5.4)
- User‑Facing Web Application requirements (Section 6.3)
- Project override: page load threshold = 1.5 seconds

## Step 3: Test Suite

The test suite must include tests for both functional behavior and activated NFRs.

Functional tests verify **what the system does**.
NFR tests verify **how well the system does it**.

## Step 4: AI Generation

When providing specifications to AI for implementation generation, the activated NFRs are included as constraints.

This ensures that AI‑generated implementations respect quality requirements from the start rather than requiring fixes after the fact.

## Step 5: Verification

Tests execute. Both functional tests and NFR tests must pass.

A functionally correct implementation that fails NFR tests is rejected and regenerated.

---

# 11. NFR Regeneration Safety

NFR tests serve an additional purpose in STDD: they prevent **quality regression during regeneration**.

When an implementation is regenerated, functional tests verify behavior.

NFR tests verify that regenerated implementations:

- do not introduce security vulnerabilities
- do not degrade performance
- do not lose audit capabilities
- do not break accessibility
- do not violate data integrity constraints

Without NFR tests, a regenerated implementation could pass all functional tests while quietly violating quality constraints.

NFR tests act as a **safety net for regeneration**.

---

# 12. Reference: Default NFR Sets

The following tables summarize the default NFRs by trigger type.

## Universal (Always Active)

| Category | Requirement | Testable Via |
|---|---|---|
| Error handling | No internal details exposed to users | Integration test |
| Error handling | Errors logged with context | Log assertion |
| Input validation | External input validated at boundaries | Fuzz test, unit test |
| Logging | Structured logs for key operations | Log assertion |
| Logging | No sensitive data in logs | Log scan |
| Timeouts | External calls have explicit timeouts | Fault injection test |
| Dependencies | Pinned versions, no known vulnerabilities | Dependency scan |
| Configuration | No hardcoded secrets | Static analysis |

## Technology‑Triggered

| Technology | Requirement | Testable Via |
|---|---|---|
| SQL | Parameterized queries only | Static analysis, injection test |
| SQL | Connection pooling configured | Configuration test |
| HTML | Output encoding for dynamic content | XSS test |
| HTML | Security headers present | Response header test |
| HTTP API | Schema validation on input | Fuzz test |
| HTTP API | Rate limiting on public endpoints | Load test |
| Auth | Adaptive password hashing | Unit test |
| Auth | Secure session token generation | Randomness test |
| File upload | Size and type validation | Unit test |
| File upload | Path traversal prevention | Injection test |
| LLM | Prompt injection mitigation | Injection test |
| LLM | Output treated as untrusted | Integration test |
| Message queue | Idempotent processing | Replay test |
| Cache | Deterministic keys, invalidation strategy | Unit test |

## Domain‑Triggered

| Domain | Requirement | Testable Via |
|---|---|---|
| Finance | Decimal precision for currency | Unit test |
| Finance | Immutable audit trail | Integration test |
| Finance | Idempotent balance operations | Replay test |
| Healthcare | Encryption at rest and in transit | Configuration test |
| Healthcare | Access audit logging | Integration test |
| Web (user‑facing) | Interactive in < N seconds (default 2s) | Performance test |
| Web (user‑facing) | WCAG 2.1 AA compliance | Accessibility scan |
| Multi‑tenant | Tenant data isolation | Integration test |
| Multi‑tenant | Per‑tenant resource limits | Load test |
| Real‑time | Latency within threshold | Performance test |
| Real‑time | Graceful reconnection | Fault injection test |

---

# 13. Conclusion

Functional correctness is necessary but not sufficient.

A system that behaves correctly but is insecure, slow, or inaccessible is not ready for production.

Non‑functional requirements define the quality constraints under which functional behavior must operate.

In STDD, non‑functional requirements must follow the same discipline as functional requirements:

- Defined explicitly in specifications
- Verified through tests
- Enforced during regeneration

The layered NFR model provides a structured approach:

1. **Universal requirements** form the baseline
2. **Technology‑triggered requirements** activate based on the stack
3. **Domain‑triggered requirements** activate based on the business context
4. **Project‑specific overrides** adjust thresholds for individual systems

By treating non‑functional requirements as first‑class testable artifacts, STDD ensures that AI‑generated implementations meet not only behavioral expectations but also the quality standards required for production systems.

**Behavior defines what the system does.
NFRs define how well it does it.
Tests verify both.**
