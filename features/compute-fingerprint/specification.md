# Feature: Specification Fingerprint

Version: 1.0
Status: accepted

## Description

Computes a SHA-256 hash of all specification and test files in an STDD project. The fingerprint detects when the knowledge layer changes, enabling Continuous Specification Integrity (CSI) enforcement in CI/CD pipelines.

## Inputs

| ID | Name | Type | Constraints |
|----|------|------|-------------|
| FP-IN-01 | spec_dir | string | Required. Path to the specification directory. |
| FP-IN-02 | test_dir | string | Required. Path to the test directory. |
| FP-IN-03 | nfr_file | string | Optional. Path to a non-functional requirements file. |
| FP-IN-04 | --compare | flag | Optional. Compare computed hash against stored .fingerprint. |
| FP-IN-05 | --update | flag | Optional. Write computed hash to .fingerprint file. |

## Outputs

| ID | Name | Type |
|----|------|------|
| FP-OUT-01 | fingerprint | string | SHA-256 hex digest, 64 characters, printed to stdout. |
| FP-OUT-02 | exit_code | integer | 0 on success or first run; 1 on mismatch. |
| FP-OUT-03 | .fingerprint | file | Created/updated when --update is used. Contains hash + newline. |

## Behavioral Scenarios

### Scenario: compute fingerprint from spec and test directories
  Given: a spec directory and test directory containing files
  When: compute_fingerprint is called with both directories
  Then: a deterministic SHA-256 hex digest is returned

### Scenario: compare against stored fingerprint — match
  Given: a .fingerprint file containing the current hash
  When: --compare is used
  Then: exit code is 0, "Fingerprint matches." printed to stderr

### Scenario: compare against stored fingerprint — mismatch
  Given: a .fingerprint file containing a different hash
  When: --compare is used
  Then: exit code is 1, "MISMATCH" printed to stderr

### Scenario: compare with no stored fingerprint
  Given: no .fingerprint file exists
  When: --compare is used
  Then: exit code is 0, guidance to run --update printed to stderr

### Scenario: update fingerprint
  Given: any spec and test directories
  When: --update is used
  Then: .fingerprint file is written with hash + newline

## Rules

| ID | Description |
|----|-------------|
| FP-01 | All knowledge-layer files in spec_dir are included in the hash, discovered recursively and sorted by relative path. Build artifacts (\_\_pycache\_\_, .pyc, .pytest\_cache) are excluded. |
| FP-02 | All knowledge-layer files in test_dir are included in the hash, discovered recursively and sorted by relative path. Build artifacts are excluded. |
| FP-03 | A directory label (`SPEC_DIR\n` or `TEST_DIR\n`) is written into the hash stream before each directory's files. |
| FP-04 | Each file contributes its relative path (encoded as UTF-8) followed by its raw content to the hash. |
| FP-05 | When --nfr-file is provided and the file exists, `NFR_FILE\n` label and file content are appended to the hash. |
| FP-06 | When --nfr-file is provided but the file does not exist, it is silently skipped. |
| FP-07 | When a directory does not exist, a warning is printed to stderr and hashing continues (no failure). |
| FP-08 | The computed hash is deterministic: identical inputs always produce the identical hash. |
| FP-09 | In --compare mode, exit code is 0 when the stored fingerprint matches the computed fingerprint. |
| FP-10 | In --compare mode, exit code is 1 when the stored fingerprint does not match the computed fingerprint. |
| FP-11 | In --compare mode, when no .fingerprint file exists, exit code is 0 (treated as first run). |
| FP-12 | In --update mode, the computed hash followed by a newline is written to the .fingerprint file. |
| FP-13 | The computed hash is always printed to stdout, regardless of --compare or --update flags. |

## Invariants

| ID | Description |
|----|-------------|
| FP-INV-01 | Same file set with same content always produces the same hash. |
| FP-INV-02 | Changing any file's content changes the resulting hash. |
| FP-INV-03 | Files within each directory are processed in deterministic sorted order. |

## Failure Conditions

| ID | Trigger | Response |
|----|---------|----------|
| FP-FAIL-01 | spec_dir does not exist | Warning printed to stderr; hashing continues with remaining inputs. |
| FP-FAIL-02 | test_dir does not exist | Warning printed to stderr; hashing continues with remaining inputs. |
| FP-FAIL-03 | .fingerprint mismatch in --compare mode | Exit code 1 with stored and current hashes printed to stderr. |

## Constraints

- Uses only Python standard library (hashlib, pathlib, argparse).
- The .fingerprint file path is hardcoded as `.fingerprint` in the working directory.

## Acceptance Cases

See: acceptance-cases.yaml

## Technologies

Python 3.10+

## Domain

Developer tooling / CI-CD

## NFR Overrides

None
