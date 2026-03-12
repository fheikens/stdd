
# Order Cancellation -- Complete STDD Feature Example

This directory contains a complete, standalone example of a single feature developed using Specification & Test-Driven Development. It demonstrates what a team's feature directory looks like in practice.

## Files

| File | Purpose |
|------|---------|
| `specification.md` | The specification: inputs, outputs, 8 rules, 3 invariants, 4 failure conditions, state model, and behavioral scenarios. |
| `acceptance-cases.yaml` | Canonical acceptance cases in structured YAML. Each case maps to a spec ID and defines given/when/then data. |
| `traceability-matrix.md` | Maps every specification element (rules, invariants, failure conditions) to its corresponding test(s). |
| `implementations/python/cancel_order.py` | Reference Python implementation satisfying all specifications. |
| `implementations/python/test_cancel_order.py` | Complete pytest suite. Every test docstring references the spec ID it verifies. |

## STDD Lifecycle Demonstrated

1. **Specification first** -- `specification.md` defines all behavior before any code exists.
2. **Acceptance cases bridge spec to tests** -- `acceptance-cases.yaml` provides structured, language-neutral test data.
3. **Tests enforce behavior** -- `test_cancel_order.py` covers every rule, invariant, and failure condition.
4. **Traceability closes the gap** -- `traceability-matrix.md` ensures no spec is untested and no test is orphaned.
5. **Implementation is regenerable** -- `cancel_order.py` can be discarded and regenerated; the tests verify correctness.

## Running the Tests

```
cd implementations/python
pytest test_cancel_order.py -v
```
