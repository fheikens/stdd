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

## Requirements

Python 3.10+ (standard library only, no dependencies).
