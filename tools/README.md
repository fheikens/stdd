# STDD Tools

Reference implementations of CI/CD scripts for STDD projects. Copy these into your own project and adapt paths as needed.

## compute_fingerprint.py

Computes a SHA-256 hash of all specification and test files (the "specification fingerprint"). Use it in CI to detect when the knowledge layer changes.

```bash
# Compute and print the fingerprint
python compute_fingerprint.py --spec-dir features/ --test-dir tests/

# Include NFR file in the hash
python compute_fingerprint.py --spec-dir features/ --test-dir tests/ --nfr-file features/nfr.md

# Compare against stored .fingerprint file (exits 1 on mismatch)
python compute_fingerprint.py --spec-dir features/ --test-dir tests/ --compare

# Update the stored .fingerprint file
python compute_fingerprint.py --spec-dir features/ --test-dir tests/ --update
```

## validate_traceability.py

Checks that every specification ID found in markdown files has at least one corresponding reference in test files. Catches untested specifications before they reach production.

```bash
# Validate traceability (exits 1 if any spec ID lacks a test)
python validate_traceability.py --spec-dir features/ --test-dir tests/
```

Spec IDs are detected in markdown tables (`| WORD-NUMBER`), headings (`## WORD-NUMBER`), and code comments (`# WORD-NUMBER`, `// WORD-NUMBER`). A custom pattern can be supplied via `--spec-pattern`. Multiple `--spec-dir` values are supported.

## yaml_to_pytests.py

Generates test skeletons from an STDD `acceptance-cases.yaml` file. Each acceptance case becomes a test function with a docstring referencing the spec ID. Error cases (those with `error: true` in their `then` block) get a `pytest.raises` skeleton.

```bash
# Print generated Python tests to stdout
python yaml_to_pytests.py acceptance-cases.yaml

# Write directly to a file
python yaml_to_pytests.py acceptance-cases.yaml --output tests/test_generated.py

# Generate with import and call stubs
python yaml_to_pytests.py acceptance-cases.yaml --module myapp.orders --function cancel_order

# Generate Go table-driven test skeleton
python yaml_to_pytests.py acceptance-cases.yaml --language go --output order_test.go
```

**Flags:**
- `--module` — adds `from MODULE import FUNCTION` to the generated file
- `--function` — generates call stubs with arguments from the YAML inputs
- `--language` — `python` (default) or `go` (table-driven test skeleton)

### How argument mapping works

When `--function` is specified, the `given` and `when` keys from each acceptance case are **merged** into a single keyword-argument call. For example, given this YAML:

```yaml
given:
  order_id: "ORD-100"
  order_status: "pending"
when:
  action: cancel_order
  reason: "Changed my mind"
```

Running with `--function cancel_order` produces:

```python
result = cancel_order(order_id='ORD-100', order_status='pending',
                      action='cancel_order', reason='Changed my mind')
```

All `given` keys appear first, followed by `when` keys — in the order they appear in the YAML. The `then` keys become assertion lines (`assert result.KEY == VALUE`).

### Go end-to-end example

Generate a Go table-driven test skeleton from the same YAML used by Python:

```bash
python yaml_to_pytests.py examples/order-cancellation/acceptance-cases.yaml \
    --language go \
    --output order_cancel_test.go
```

This produces a single `TestAcceptanceCases` function with one sub-test per acceptance case. Input and expected-output fields appear as comments — fill in the struct fields and assertions to connect to your production code:

```go
func TestAcceptanceCases(t *testing.T) {
    tests := []struct {
        name    string
        // TODO: add input and expected output fields
        wantErr bool
    }{
        {
            name:    "ORD-CANCEL-01: cancel pending order — no refund",
            // order_id: 'ORD-100'
            // order_status: 'pending'
            // want new_status: 'cancelled'
        },
        // ... one entry per acceptance case
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // TODO: call target function, assert results
        })
    }
}
```

## Requirements

Python 3.10+ with PyYAML (`pip install pyyaml`). The `compute_fingerprint.py` and `validate_traceability.py` scripts use only the standard library.
