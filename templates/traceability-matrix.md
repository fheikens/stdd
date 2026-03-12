# Traceability Matrix: [FEATURE_NAME]

## Specification-to-Test Mapping

| Spec ID | Test | Status |
|---------|------|--------|
| RULE-1 | test_[describe_what_is_tested] | pending |
| INV-1 | test_invariant_[describe_invariant] | pending |
| FAIL-1 | test_[describe_failure_case] | pending |

## Notes

**Every spec ID must have at least one test.** If a specification element has no corresponding test, the spec-to-test gap is not closed and the feature is not ready for generation.

**Every test must reference a spec ID.** Tests that do not trace back to a specification element are orphaned. They may be testing implementation details rather than specified behavior.

**Status values:**
- `pending` -- test is planned but not yet written
- `passing` -- test exists and passes
- `failing` -- test exists but fails (expected during test-first development)

**How to maintain this matrix:**
1. Add a row for every scenario, invariant, and failure condition in the specification.
2. Write the test name once the test exists. Include the spec ID in the test docstring or name.
3. Update the status as development progresses.
4. Before moving the specification to `accepted`, every row must have status `passing`.
