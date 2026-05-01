# Traceability Matrix: STDD Tools

This matrix follows STDD Core Model §6.2 (six-column structure) and §6.4 (strict
coverage definitions with required evidence blocks). Each row is classified
against the surface the rule names, not the surface the test happens to exercise.
Where the test only verifies an internal helper while the rule names a CLI or
file surface, the row is PARTIALLY COVERED and the missing channels are listed
explicitly under "Coverage gaps".

All specifications are `behavioral` and `ACTIVE`. All tests are `requirement` tests.

---

## Specification Fingerprint (`tools/compute_fingerprint.py`)

| Spec ID | Spec Type | Spec Status | Test | Test Type | Coverage |
|---|---|---|---|---|---|
| FP-01 | behavioral | ACTIVE | test_fingerprint_includes_spec_and_test_files | requirement | PARTIALLY COVERED |
| FP-02 | behavioral | ACTIVE | test_fingerprint_includes_spec_and_test_files | requirement | PARTIALLY COVERED |
| FP-03 | behavioral | ACTIVE | test_directory_labels_affect_hash | requirement | PARTIALLY COVERED |
| FP-04 | behavioral | ACTIVE | test_file_path_and_content_in_hash | requirement | PARTIALLY COVERED |
| FP-05 | behavioral | ACTIVE | test_nfr_file_changes_hash | requirement | PARTIALLY COVERED |
| FP-06 | behavioral | ACTIVE | test_nfr_file_skipped_when_absent | requirement | PARTIALLY COVERED |
| FP-07 | behavioral | ACTIVE | test_missing_directory_warns_but_continues | requirement | COVERED |
| FP-08 | behavioral | ACTIVE | test_deterministic_hash | requirement | COVERED |
| FP-09 | behavioral | ACTIVE | test_compare_matches | requirement | COVERED |
| FP-10 | behavioral | ACTIVE | test_compare_detects_mismatch | requirement | COVERED |
| FP-11 | behavioral | ACTIVE | test_compare_first_run | requirement | COVERED |
| FP-12 | behavioral | ACTIVE | test_update_writes_fingerprint | requirement | COVERED |
| FP-13 | behavioral | ACTIVE | test_hash_printed_to_stdout | requirement | PARTIALLY COVERED |
| FP-INV-01 | behavioral | ACTIVE | test_deterministic_hash | requirement | COVERED |
| FP-INV-02 | behavioral | ACTIVE | test_content_change_produces_different_hash | requirement | COVERED |
| FP-INV-03 | behavioral | ACTIVE | test_files_processed_in_sorted_order | requirement | PARTIALLY COVERED |
| FP-FAIL-01 | behavioral | ACTIVE | test_missing_directory_warns_but_continues | requirement | COVERED |
| FP-FAIL-02 | behavioral | ACTIVE | test_missing_test_directory_warns_but_continues | requirement | COVERED |
| FP-FAIL-03 | behavioral | ACTIVE | test_compare_detects_mismatch | requirement | COVERED |

### Evidence (COVERED rows)

**FP-07** — missing directory produces stderr warning and hashing continues.
- test file: `tests/test_compute_fingerprint.py`
- test name: `test_missing_directory_warns_but_continues`
- behavior verified: calling `compute_fingerprint` with a nonexistent spec dir returns a 64-char hex digest (no exception) and writes a string containing "Warning" to stderr.
- surface verified: function return value and `sys.stderr` (captured via `capsys`).

**FP-08 / FP-INV-01** — deterministic hash for identical inputs.
- test file: `tests/test_compute_fingerprint.py`
- test name: `test_deterministic_hash`
- behavior verified: two consecutive calls with the same spec/test directories return identical hashes.
- surface verified: function return value (the hash string itself).

**FP-09** — exit 0 when stored fingerprint matches.
- test file: `tests/test_compute_fingerprint.py`
- test name: `test_compare_matches`
- behavior verified: invoking `tools/compute_fingerprint.py --compare` as a subprocess returns exit code 0 when `.fingerprint` contains the current hash.
- surface verified: CLI process exit code.

**FP-10** — exit 1 and "MISMATCH" on stderr when stored fingerprint differs.
- test file: `tests/test_compute_fingerprint.py`
- test name: `test_compare_detects_mismatch`
- behavior verified: subprocess invocation with `--compare` against a wrong stored hash exits 1 and writes "MISMATCH" to stderr.
- surface verified: CLI process exit code and stderr.

**FP-11** — exit 0 with "first run" guidance when no `.fingerprint` exists.
- test file: `tests/test_compute_fingerprint.py`
- test name: `test_compare_first_run`
- behavior verified: subprocess invocation with `--compare` and no stored fingerprint exits 0 and writes "first run" guidance to stderr.
- surface verified: CLI process exit code and stderr.

**FP-12** — `--update` writes hash + newline to `.fingerprint`.
- test file: `tests/test_compute_fingerprint.py`
- test name: `test_update_writes_fingerprint`
- behavior verified: subprocess invocation with `--update` exits 0; the resulting `.fingerprint` file exists, ends with `\n`, and contains exactly 64 hex characters before the newline.
- surface verified: file on disk (`.fingerprint`) and CLI process exit code.

**FP-INV-02** — any content change changes the hash.
- test file: `tests/test_compute_fingerprint.py`
- test name: `test_content_change_produces_different_hash`
- behavior verified: rewriting the spec file content between two `compute_fingerprint` calls yields different hash values.
- surface verified: function return value (the hash string).

**FP-FAIL-01** — missing spec_dir produces stderr warning and hashing continues.
- test file: `tests/test_compute_fingerprint.py`
- test name: `test_missing_directory_warns_but_continues`
- behavior verified: passing a nonexistent spec_dir returns a 64-char hex digest (no exception) and writes "Warning" to stderr.
- surface verified: function return value and `sys.stderr` (captured via `capsys`).

**FP-FAIL-02** — missing test_dir produces stderr warning and hashing continues.
- test file: `tests/test_compute_fingerprint.py`
- test name: `test_missing_test_directory_warns_but_continues`
- behavior verified: passing a nonexistent test_dir returns a 64-char hex digest (no exception) and writes "Warning" to stderr.
- surface verified: function return value and `sys.stderr` (captured via `capsys`).

**FP-FAIL-03** — `.fingerprint` mismatch in --compare mode prints stored and current hashes to stderr with exit 1.
- test file: `tests/test_compute_fingerprint.py`
- test name: `test_compare_detects_mismatch`
- behavior verified: subprocess invocation with `--compare` against a wrong stored hash exits 1, writes "MISMATCH" to stderr, includes the literal stored hash, and labels the current hash with "Current:".
- surface verified: CLI process exit code and stderr.

### Coverage gaps (PARTIALLY COVERED rows)

- **FP-01 / FP-02** — the test only confirms that a 64-char hex digest is returned. It does not exercise recursive directory traversal or the build-artifact exclusion (`__pycache__`, `.pyc`, `.pytest_cache`) that the rule explicitly names.
- **FP-03** — the test proves that placing the same content in `spec_dir` vs `test_dir` produces different hashes (so the labels are *some* differentiator), but does not assert that the literal strings `SPEC_DIR\n` and `TEST_DIR\n` are written into the hash stream.
- **FP-04** — the test proves the file path participates in the hash, but does not verify UTF-8 encoding of the relative path or that the raw byte content is appended unmodified.
- **FP-05 / FP-06** — both tests call `compute_fingerprint(...)` directly with the `nfr_file=` kwarg. The CLI surface named in the rule (`--nfr-file` flag handling) is not exercised end-to-end.
- **FP-13** — the rule says "regardless of `--compare` or `--update` flags", but the test only invokes the CLI in default mode. No assertion confirms the hash is also printed to stdout when `--compare` or `--update` is used.
- **FP-INV-03** — the test creates files in reverse alphabetical order and asserts two consecutive calls return the same hash. That proves determinism (already covered by FP-INV-01) but does not prove sorted-by-relative-path ordering, which is the actual invariant.

---

## Traceability Validation (`tools/validate_traceability.py`)

| Spec ID | Spec Type | Spec Status | Test | Test Type | Coverage |
|---|---|---|---|---|---|
| TR-01 | behavioral | ACTIVE | test_scans_md_files_for_spec_ids | requirement | PARTIALLY COVERED |
| TR-02 | behavioral | ACTIVE | test_detect_spec_id_in_table_row | requirement | PARTIALLY COVERED |
| TR-03 | behavioral | ACTIVE | test_detect_spec_id_in_heading | requirement | PARTIALLY COVERED |
| TR-04 | behavioral | ACTIVE | test_detect_spec_id_in_hash_comment | requirement | PARTIALLY COVERED |
| TR-05 | behavioral | ACTIVE | test_detect_spec_id_in_slash_comment | requirement | PARTIALLY COVERED |
| TR-06 | behavioral | ACTIVE | test_scans_test_files_by_name_pattern | requirement | PARTIALLY COVERED |
| TR-07 | behavioral | ACTIVE | test_all_specs_covered_exits_0 | requirement | COVERED |
| TR-08 | behavioral | ACTIVE | test_untested_spec_exits_1 | requirement | COVERED |
| TR-09 | behavioral | ACTIVE | test_nonexistent_spec_dir_exits_1 | requirement | COVERED |
| TR-10 | behavioral | ACTIVE | test_nonexistent_test_dir_exits_1 | requirement | COVERED |
| TR-11 | behavioral | ACTIVE | test_multiple_spec_dirs | requirement | COVERED |
| TR-12 | behavioral | ACTIVE | test_custom_spec_pattern | requirement | COVERED |
| TR-13 | behavioral | ACTIVE | test_report_shows_counts | requirement | COVERED |
| TR-INV-01 | behavioral | ACTIVE | test_every_spec_id_appears_in_report | requirement | COVERED |
| TR-INV-02 | behavioral | ACTIVE | test_exit_0_implies_zero_missing | requirement | COVERED |
| TR-INV-03 | behavioral | ACTIVE | test_exit_1_implies_nonzero_missing | requirement | COVERED |
| TR-14 | behavioral | ACTIVE | test_default_pattern_matches_multi_segment_ids | requirement | COVERED |
| TR-FAIL-01 | behavioral | ACTIVE | test_nonexistent_spec_dir_exits_1 | requirement | COVERED |
| TR-FAIL-02 | behavioral | ACTIVE | test_nonexistent_test_dir_exits_1 | requirement | COVERED |
| TR-FAIL-03 | behavioral | ACTIVE | test_untested_spec_exits_1 | requirement | COVERED |

### Evidence (COVERED rows)

**TR-07** — exit 0 when every spec ID has a test reference.
- test file: `tests/test_validate_traceability.py`
- test name: `test_all_specs_covered_exits_0`
- behavior verified: subprocess invocation of the CLI with two specs and matching test references returns exit 0.
- surface verified: CLI process exit code.

**TR-08** — exit 1 with the missing ID listed when any spec is untested.
- test file: `tests/test_validate_traceability.py`
- test name: `test_untested_spec_exits_1`
- behavior verified: subprocess invocation exits 1 and writes the missing spec ID (`FEAT-02`) to stdout.
- surface verified: CLI process exit code and stdout.

**TR-09** — exit 1 if `spec_dir` does not exist.
- test file: `tests/test_validate_traceability.py`
- test name: `test_nonexistent_spec_dir_exits_1`
- behavior verified: subprocess invocation with a missing `--spec-dir` exits 1.
- surface verified: CLI process exit code.

**TR-10** — exit 1 if `test_dir` does not exist.
- test file: `tests/test_validate_traceability.py`
- test name: `test_nonexistent_test_dir_exits_1`
- behavior verified: subprocess invocation with a missing `--test-dir` exits 1.
- surface verified: CLI process exit code.

**TR-11** — multiple `--spec-dir` values are all scanned.
- test file: `tests/test_validate_traceability.py`
- test name: `test_multiple_spec_dirs`
- behavior verified: subprocess invocation with two `--spec-dir` flags exits 0 and the report announces "Specifications found: 2".
- surface verified: CLI process exit code and stdout.

**TR-12** — `--spec-pattern` overrides default ID detection.
- test file: `tests/test_validate_traceability.py`
- test name: `test_custom_spec_pattern`
- behavior verified: subprocess invocation with `--spec-pattern REQ-\d+` against `REQ-123` content exits 0 (custom regex matches and the ID is found).
- surface verified: CLI process exit code.

**TR-13** — report includes total, covered, and missing counts.
- test file: `tests/test_validate_traceability.py`
- test name: `test_report_shows_counts`
- behavior verified: subprocess invocation produces stdout containing "Specifications found: 2", "Covered by tests:     1", and "Missing tests:        1".
- surface verified: CLI stdout.

**TR-INV-01** — every found spec ID appears in the report.
- test file: `tests/test_validate_traceability.py`
- test name: `test_every_spec_id_appears_in_report`
- behavior verified: subprocess invocation produces stdout containing both `ALPHA-01` and `BETA-02`.
- surface verified: CLI stdout.

**TR-INV-02** — exit 0 implies zero missing.
- test file: `tests/test_validate_traceability.py`
- test name: `test_exit_0_implies_zero_missing`
- behavior verified: subprocess invocation that exits 0 also produces stdout containing "Missing tests:        0".
- surface verified: CLI process exit code and stdout, asserted jointly.

**TR-INV-03** — exit 1 implies nonzero missing.
- test file: `tests/test_validate_traceability.py`
- test name: `test_exit_1_implies_nonzero_missing`
- behavior verified: subprocess invocation that exits 1 also produces stdout containing "Missing tests:        1".
- surface verified: CLI process exit code and stdout, asserted jointly.

**TR-14** — default pattern matches multi-segment spec IDs.
- test file: `tests/test_validate_traceability.py`
- test name: `test_default_pattern_matches_multi_segment_ids`
- behavior verified: subprocess invocation with the default pattern detects `FP-INV-01`, `FP-FAIL-01`, and `FP-01` simultaneously (all three appear in the report and "Specifications found: 3" is printed).
- surface verified: CLI process exit code and stdout.

**TR-FAIL-01** — missing spec_dir produces stderr error and exit 1.
- test file: `tests/test_validate_traceability.py`
- test name: `test_nonexistent_spec_dir_exits_1`
- behavior verified: subprocess invocation with a missing `--spec-dir` exits 1 and writes "Error" + "spec directory" to stderr.
- surface verified: CLI process exit code and stderr.

**TR-FAIL-02** — missing test_dir produces stderr error and exit 1.
- test file: `tests/test_validate_traceability.py`
- test name: `test_nonexistent_test_dir_exits_1`
- behavior verified: subprocess invocation with a missing `--test-dir` exits 1 and writes "Error" + "test directory" to stderr.
- surface verified: CLI process exit code and stderr.

**TR-FAIL-03** — untested specs cause stdout listing, FAILED to stderr, exit 1.
- test file: `tests/test_validate_traceability.py`
- test name: `test_untested_spec_exits_1`
- behavior verified: subprocess invocation exits 1, writes the missing spec ID to stdout, and writes "FAILED" to stderr.
- surface verified: CLI process exit code, stdout, and stderr.

### Coverage gaps (PARTIALLY COVERED rows)

- **TR-01** — the test puts a single file at the top of one directory. It does not exercise recursion into subdirectories, which is part of the rule.
- **TR-02 / TR-03 / TR-04 / TR-05** — each calls the internal helper `find_spec_ids` directly. The rule's surface is the CLI report (which IDs land in stdout), and that integration path is not exercised for these detection patterns.
- **TR-06** — the test only verifies the `test_*.py` pattern (and that a non-matching name is excluded). The rule explicitly names four patterns: `test_*.py`, `*_test.py`, `*_test.go`, `test_*.go`. Three of the four are unverified.

---

## Test Skeleton Generator (`tools/yaml_to_pytests.py`)

| Spec ID | Spec Type | Spec Status | Test | Test Type | Coverage |
|---|---|---|---|---|---|
| GEN-01 | behavioral | ACTIVE | test_one_function_per_case | requirement | PARTIALLY COVERED |
| GEN-02 | behavioral | ACTIVE | test_slugify_basic | requirement | PARTIALLY COVERED |
| GEN-03 | behavioral | ACTIVE | test_docstring_references_spec_id | requirement | PARTIALLY COVERED |
| GEN-04 | behavioral | ACTIVE | test_error_case_gets_pytest_raises | requirement | PARTIALLY COVERED |
| GEN-05 | behavioral | ACTIVE | test_non_error_case_gets_assertions | requirement | PARTIALLY COVERED |
| GEN-06 | behavioral | ACTIVE | test_module_flag_adds_import + test_module_only_without_function | requirement | PARTIALLY COVERED |
| GEN-07 | behavioral | ACTIVE | test_function_merges_given_when | requirement | PARTIALLY COVERED |
| GEN-08 | behavioral | ACTIVE | test_given_before_when_in_args | requirement | PARTIALLY COVERED |
| GEN-09 | behavioral | ACTIVE | test_go_skeleton_generated | requirement | PARTIALLY COVERED |
| GEN-10 | behavioral | ACTIVE | test_output_writes_to_file | requirement | PARTIALLY COVERED |
| GEN-11 | behavioral | ACTIVE | test_accepts_underscore_key + test_accepts_hyphen_key | requirement | PARTIALLY COVERED |
| GEN-12 | behavioral | ACTIVE | test_file_not_found_exits_1 | requirement | COVERED |
| GEN-13 | behavioral | ACTIVE | test_invalid_yaml_structure_exits_1 + test_missing_key_exits_1 | requirement | COVERED |
| GEN-14 | behavioral | ACTIVE | test_slugify_special_chars + test_slugify_removes_leading_trailing_underscores | requirement | COVERED |
| GEN-INV-01 | behavioral | ACTIVE | test_function_count_equals_case_count | requirement | PARTIALLY COVERED |
| GEN-INV-02 | behavioral | ACTIVE | test_every_test_references_spec_id | requirement | PARTIALLY COVERED |
| GEN-INV-03 | behavioral | ACTIVE | test_generated_code_parses + test_generated_code_with_function_parses | requirement | COVERED |
| GEN-FAIL-01 | behavioral | ACTIVE | test_file_not_found_exits_1 | requirement | COVERED |
| GEN-FAIL-02 | behavioral | ACTIVE | test_invalid_yaml_structure_exits_1 | requirement | COVERED |
| GEN-FAIL-03 | behavioral | ACTIVE | test_missing_key_exits_1 | requirement | COVERED |

### Evidence (COVERED rows)

**GEN-12** — exit 1 when YAML file does not exist.
- test file: `tests/test_yaml_to_pytests.py`
- test name: `test_file_not_found_exits_1`
- behavior verified: subprocess invocation with a nonexistent path exits 1 and writes "not found" or "error" to stderr.
- surface verified: CLI process exit code and stderr.

**GEN-13** — exit 1 when YAML structure is invalid.
- test file: `tests/test_yaml_to_pytests.py`
- test names: `test_invalid_yaml_structure_exits_1`, `test_missing_key_exits_1`
- behavior verified: subprocess invocations exit 1 for two distinct invalid structures (top-level list, and mapping without the expected key).
- surface verified: CLI process exit code.

**GEN-14** — `slugify` produces valid Python identifiers.
- test file: `tests/test_yaml_to_pytests.py`
- test names: `test_slugify_special_chars`, `test_slugify_removes_leading_trailing_underscores`
- behavior verified: `slugify` lowercases, replaces non-alphanumerics with underscores, strips leading/trailing underscores, and the result satisfies `str.isidentifier()`.
- surface verified: return value of the `slugify` function — which is the surface the rule explicitly names.

**GEN-INV-03** — generated Python code is parseable.
- test file: `tests/test_yaml_to_pytests.py`
- test names: `test_generated_code_parses`, `test_generated_code_with_function_parses`
- behavior verified: `ast.parse` succeeds on the output of `generate_module(...)` for both default and `--module/--function` modes.
- surface verified: return value of `generate_module` (the generated source text), which is the artefact the rule constrains.

**GEN-FAIL-01** — missing YAML file produces stderr error and exit 1.
- test file: `tests/test_yaml_to_pytests.py`
- test name: `test_file_not_found_exits_1`
- behavior verified: subprocess invocation with a nonexistent path exits 1 and writes "not found" or "error" to stderr.
- surface verified: CLI process exit code and stderr.

**GEN-FAIL-02** — non-mapping YAML produces stderr error and exit 1.
- test file: `tests/test_yaml_to_pytests.py`
- test name: `test_invalid_yaml_structure_exits_1`
- behavior verified: subprocess invocation against a top-level YAML list exits 1 and writes "Error" to stderr.
- surface verified: CLI process exit code and stderr.

**GEN-FAIL-03** — missing acceptance_cases key produces stderr error and exit 1.
- test file: `tests/test_yaml_to_pytests.py`
- test name: `test_missing_key_exits_1`
- behavior verified: subprocess invocation against a YAML mapping without the expected key exits 1 and writes "Error" to stderr.
- surface verified: CLI process exit code and stderr.

### Coverage gaps (PARTIALLY COVERED rows)

- **GEN-01** — calls `generate_module` directly. The rule names two output formats (Python and Go); only the Python path is exercised here. (The Go path is touched by GEN-09, but also helper-only.)
- **GEN-02** — verifies `slugify` on a single example. The rule's surface is the generated test function name in the emitted file, not `slugify` in isolation.
- **GEN-03 / GEN-04 / GEN-05** — exercise `generate_test_function` directly. The CLI never invokes these tests, so it is not verified end-to-end that the spec_id, `pytest.raises` skeleton, or assertion placeholders survive into the CLI's stdout/file output.
- **GEN-06 / GEN-07 / GEN-08** — the rules name `--module` and `--function` flags, but the tests call `generate_module` directly with kwargs. The CLI argument parsing path is not exercised.
- **GEN-09** — calls `generate_go_module` directly. The `--language go` flag handling on the CLI is not exercised.
- **GEN-10** — the test verifies file creation and content via subprocess, which covers the file half of the rule. The other half of the rule — "a summary is printed to stderr" — has no assertion.
- **GEN-11** — calls `load_cases` directly. The CLI's behavior with each top-level key variant (in real subprocess invocations) is not verified.
- **GEN-INV-01 / GEN-INV-02** — both call `generate_module` directly. The invariant is asserted on the helper's output, not on the CLI's stdout/file output. If the CLI inserted a transformation step, the helper-level test would not catch it.

---

## Summary

| Tool | Specifications | COVERED | PARTIALLY COVERED | UNCOVERED |
|---|---|---|---|---|
| compute_fingerprint.py | 19 | 11 | 8 | 0 |
| validate_traceability.py | 20 | 14 | 6 | 0 |
| yaml_to_pytests.py | 20 | 7 | 13 | 0 |
| **Total** | **59** | **32** | **27** | **0** |

Every specification ID has at least one test (Gate 1 passes — see CI). The
COVERED rows are those whose test exercises the CLI surface (subprocess
invocation, exit codes, stdout/stderr, files on disk) the rule actually names.
PARTIALLY COVERED rows have helper-level evidence only; the named CLI surface
is reachable but not yet exercised end-to-end. Per Core Model §6.4 (Rule 9 —
when in doubt, downgrade), helper-level evidence is not promoted to COVERED.

Closing the helper-only gaps is a future-work item: each PARTIALLY COVERED
row above is reachable via a subprocess test that invokes the CLI with the
relevant flag and asserts on stdout/stderr/exit-code. Adding those tests
would not change behavior; it would only convert evidence currently produced
at the helper level into evidence at the surface the rule names.

For the strict definitions of the three coverage states, the multi-channel
rule, and the AI-agent discipline that applies when an AI assistant updates
this matrix, see [Core Model §6.4–§6.5](../docs/stdd-core-model.md).
