# Feature: Traceability Validation

Version: 1.1
Type: behavioral
Status: ACTIVE

## Description

Validates that every specification ID found in markdown files has at least one corresponding reference in test files. Catches untested specifications before they reach production, enforcing the STDD bidirectional traceability requirement.

## Inputs

| Name | Type | Constraints |
|------|------|-------------|
| spec_dir | string | Required, repeatable. Path(s) to specification directories. |
| test_dir | string | Required. Path to the test directory. |
| --spec-pattern | string | Optional. Regex pattern for spec IDs. Default: `\w+(?:-\w+)*-\d+`. |

## Outputs

| Name | Type | Description |
|------|------|-------------|
| coverage_report | text | Printed to stdout: counts of found, covered, and missing spec IDs. |
| exit_code | integer | 0 when all specs are covered; 1 when any spec lacks a test. |

## Behavioral Scenarios

### Scenario: all specifications covered
  Given: spec files with IDs FEAT-01, FEAT-02 and test files referencing both
  When: validate_traceability is run
  Then: exit code is 0, report shows 0 missing

### Scenario: untested specification found
  Given: spec files with IDs FEAT-01, FEAT-02 and test files referencing only FEAT-01
  When: validate_traceability is run
  Then: exit code is 1, report lists FEAT-02 as missing

### Scenario: multiple spec directories
  Given: two spec directories each containing spec IDs, and tests covering all IDs
  When: validate_traceability is run with both --spec-dir values
  Then: exit code is 0, all IDs from both directories are found

### Scenario: custom spec pattern
  Given: spec files using REQ-123 format and a matching --spec-pattern
  When: validate_traceability is run
  Then: IDs matching the custom pattern are detected

## Rules

| ID | Description |
|----|-------------|
| TR-01 | Scans all .md files in each spec_dir recursively for spec IDs. |
| TR-02 | Detects spec IDs in markdown table rows (pipe at start of line, then the ID). |
| TR-03 | Detects spec IDs in markdown headings (heading marker, then text containing the ID). |
| TR-04 | Detects spec IDs in hash comments (hash, space, then the ID). |
| TR-05 | Detects spec IDs in slash comments (double slash, space, then the ID). |
| TR-06 | Scans test files matching patterns: `test_*.py`, `*_test.py`, `*_test.go`, `test_*.go`. |
| TR-07 | Exits 0 when every spec ID has at least one reference in a test file. |
| TR-08 | Exits 1 when any spec ID has no reference in any test file. |
| TR-09 | Exits 1 immediately if any spec_dir does not exist. |
| TR-10 | Exits 1 immediately if test_dir does not exist. |
| TR-11 | Multiple --spec-dir values are accepted and all are scanned. |
| TR-12 | A custom --spec-pattern overrides the default `\w+(?:-\w+)*-\d+` regex for ID detection. |
| TR-13 | Reports total spec count, covered count, and missing count to stdout. |
| TR-14 | The default spec ID pattern matches multi-segment IDs of the form `\w+(?:-\w+)*-\d+`, permitting IDs such as `FEAT-01`, `FP-INV-01`, `FP-FAIL-01`, or `X-Y-Z-01`. |

## Invariants

| ID | Description |
|----|-------------|
| TR-INV-01 | A spec ID found in any scanned .md file will appear in the report. |
| TR-INV-02 | Exit code 0 implies missing count is zero. |
| TR-INV-03 | Exit code 1 implies missing count is greater than zero. |

## Failure Conditions

| ID | Trigger | Response |
|----|---------|----------|
| TR-FAIL-01 | spec_dir does not exist | Error printed to stderr, exit code 1. |
| TR-FAIL-02 | test_dir does not exist | Error printed to stderr, exit code 1. |
| TR-FAIL-03 | Untested spec IDs found | Missing IDs listed, "FAILED" printed to stderr, exit code 1. |

## Constraints

- Uses only Python standard library (re, pathlib, argparse).
- Test file detection is filename-based, not content-based.
- Default spec ID pattern is `\w+(?:-\w+)*-\d+` (word characters, then zero or more hyphenated word segments, ending in hyphen + digits). This permits multi-segment IDs (e.g., `FP-INV-01`, `FP-FAIL-01`) without requiring a custom pattern.

## Acceptance Cases

See: acceptance-cases.yaml

## Technologies

Python 3.10+

## Domain

Developer tooling / CI-CD

## NFR Overrides

None
