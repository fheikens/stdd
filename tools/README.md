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

Spec IDs are detected as `| WORD-NUMBER` patterns in markdown tables. Test references are detected as `WORD-NUMBER` patterns anywhere in test files (`test_*.py`, `*_test.py`, `*_test.go`, `test_*.go`).

## yaml_to_pytests.py

Generates a pytest test skeleton from an STDD `acceptance-cases.yaml` file. Each acceptance case becomes a test function with a docstring referencing the spec ID, commented inputs/outputs, and a `NotImplementedError` placeholder. Error cases (those with `error: true` in their `then` block) get a `pytest.raises` skeleton.

```bash
# Print generated tests to stdout
python yaml_to_pytests.py examples/order-cancellation/acceptance-cases.yaml

# Write directly to a file
python yaml_to_pytests.py examples/order-cancellation/acceptance-cases.yaml --output tests/test_generated.py
```

The `--language` flag defaults to `python`. Go support could be added in a future version.

## Requirements

Python 3.10+ with PyYAML (`pip install pyyaml`). The `compute_fingerprint.py` and `validate_traceability.py` scripts use only the standard library.
