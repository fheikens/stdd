# Traceability Matrix: [FEATURE_NAME]

## Specification-to-Test Mapping

| Spec ID | Test | Status | Coverage |
|---------|------|--------|----------|
| RULE-1 | test_[describe_what_is_tested] | pending | UNCOVERED |
| INV-1 | test_invariant_[describe_invariant] | pending | UNCOVERED |
| FAIL-1 | test_[describe_failure_case] | pending | UNCOVERED |

## Notes

**Every spec ID must have at least one test.** If a specification element has no corresponding test, the spec-to-test gap is not closed and the feature is not ready for generation.

**Every test must reference a spec ID.** Tests that do not trace back to a specification element are orphaned. They may be testing implementation details rather than specified behavior.

**Status values:**
- `pending` — test is planned but not yet written
- `passing` — test exists and passes
- `failing` — test exists but fails (expected during test-first development)

**Coverage values** (defined in [Core Model](../docs/stdd-core-model.md), Section 6.4):
- `COVERED` — at least one test verifies the same observable behavior the requirement claims, on the same surface the requirement names. Every COVERED row must include the evidence block shown below.
- `PARTIALLY COVERED` — the test verifies an internal helper, parser, or single channel while the requirement names a broader surface or multiple channels.
- `UNCOVERED` — no test verifies the behavior the requirement claims.

When in doubt, downgrade. Coverage is never inferred from implementation structure or helper-level tests.

## Evidence Block (required for every COVERED row)

For every requirement marked COVERED, record the evidence on the row or directly beneath it. This is what distinguishes a COVERED row from an unverified claim.

### Example: a multi-channel security claim, partially covered

```
Requirement: SEC-03 — Secure option values are never exposed in logs, errors,
              stdout, stderr, argv, or TRACE output.

Coverage: PARTIALLY COVERED

Claim:
  Secure option values are redacted on every externally observable channel.

Evidence verified:
  - test file:        tests/test_config_display.py
  - test name:        test_display_redacts_secure_option
  - behavior verified: Calling cfgOptionIdxDisplay() on a secure option
                       returns the redacted placeholder, not the raw value.
  - surface verified:  return value of cfgOptionIdxDisplay()

Evidence not yet verified:
  - real log output
  - stderr
  - stdout
  - TRACE output
  - argv / process listing (ps)
  - every secure option (only repo-cipher-pass is exercised by the test)
```

This row is **not** COVERED. The requirement names six channels; the test verifies one helper that feeds one of them. The other channels are listed explicitly so the gap is visible. Promote to COVERED only when each named channel has its own test.

### Example: a single-channel claim, fully covered

```
Requirement: ORD-CANCEL-03 — A shipped order cannot be cancelled; the
              cancellation API returns an error.

Coverage: COVERED

Claim:
  Calling cancel_order() with a shipped order returns an error and does
  not change the order's status.

Evidence verified:
  - test file:        tests/test_order_cancellation.py
  - test name:        test_cancel_shipped_order_rejected
  - behavior verified: cancel_order() raises OrderNotCancellableError and
                       leaves the order in status=shipped.
  - surface verified:  return value and persisted order state.
```

This row is COVERED because the requirement names exactly one surface (the API result and post-call order state), and the test exercises exactly that surface.

## How to maintain this matrix

1. Add a row for every scenario, invariant, and failure condition in the specification.
2. Write the test name once the test exists. Include the spec ID in the test docstring or name.
3. Update the status (pending → passing) and coverage (UNCOVERED → PARTIALLY COVERED → COVERED) as evidence accumulates.
4. For every COVERED row, record the evidence block. A COVERED row without an evidence block is not COVERED.
5. Before moving the specification to ACTIVE, every row must have status `passing` and coverage `COVERED` or `PARTIALLY COVERED` with explicit FUTURE WORK notes.

For the strict definitions of COVERED / PARTIALLY COVERED / UNCOVERED, the multi-channel rule, and the AI-agent discipline that applies when an AI assistant updates this matrix, see [Core Model](../docs/stdd-core-model.md), Sections 6.4 and 6.5.
