# Traceability Matrix: STDD Tools

## Specification Fingerprint (compute_fingerprint.py)

| Spec ID | Test | Status |
|---------|------|--------|
| FP-01 | test_fingerprint_includes_spec_and_test_files | passing |
| FP-02 | test_fingerprint_includes_spec_and_test_files | passing |
| FP-03 | test_directory_labels_affect_hash | passing |
| FP-04 | test_file_path_and_content_in_hash | passing |
| FP-05 | test_nfr_file_changes_hash | passing |
| FP-06 | test_nfr_file_skipped_when_absent | passing |
| FP-07 | test_missing_directory_warns_but_continues | passing |
| FP-08 | test_deterministic_hash | passing |
| FP-09 | test_compare_matches | passing |
| FP-10 | test_compare_detects_mismatch | passing |
| FP-11 | test_compare_first_run | passing |
| FP-12 | test_update_writes_fingerprint | passing |
| FP-13 | test_hash_printed_to_stdout | passing |
| FP-INV-01 | test_deterministic_hash | passing |
| FP-INV-02 | test_content_change_produces_different_hash | passing |
| FP-INV-03 | test_files_processed_in_sorted_order | passing |

## Traceability Validation (validate_traceability.py)

| Spec ID | Test | Status |
|---------|------|--------|
| TR-01 | test_scans_md_files_for_spec_ids | passing |
| TR-02 | test_detect_spec_id_in_table_row | passing |
| TR-03 | test_detect_spec_id_in_heading | passing |
| TR-04 | test_detect_spec_id_in_hash_comment | passing |
| TR-05 | test_detect_spec_id_in_slash_comment | passing |
| TR-06 | test_scans_test_files_by_name_pattern | passing |
| TR-07 | test_all_specs_covered_exits_0 | passing |
| TR-08 | test_untested_spec_exits_1 | passing |
| TR-09 | test_nonexistent_spec_dir_exits_1 | passing |
| TR-10 | test_nonexistent_test_dir_exits_1 | passing |
| TR-11 | test_multiple_spec_dirs | passing |
| TR-12 | test_custom_spec_pattern | passing |
| TR-13 | test_report_shows_counts | passing |
| TR-INV-01 | test_every_spec_id_appears_in_report | passing |
| TR-INV-02 | test_exit_0_implies_zero_missing | passing |
| TR-INV-03 | test_exit_1_implies_nonzero_missing | passing |

## Test Skeleton Generator (yaml_to_pytests.py)

| Spec ID | Test | Status |
|---------|------|--------|
| GEN-01 | test_one_function_per_case | passing |
| GEN-02 | test_slugify_basic | passing |
| GEN-03 | test_docstring_references_spec_id | passing |
| GEN-04 | test_error_case_gets_pytest_raises | passing |
| GEN-05 | test_non_error_case_gets_assertions | passing |
| GEN-06 | test_module_flag_adds_import, test_module_only_without_function | passing |
| GEN-07 | test_function_merges_given_when | passing |
| GEN-08 | test_given_before_when_in_args | passing |
| GEN-09 | test_go_skeleton_generated | passing |
| GEN-10 | test_output_writes_to_file | passing |
| GEN-11 | test_accepts_underscore_key, test_accepts_hyphen_key | passing |
| GEN-12 | test_file_not_found_exits_1 | passing |
| GEN-13 | test_invalid_yaml_structure_exits_1, test_missing_key_exits_1 | passing |
| GEN-14 | test_slugify_special_chars, test_slugify_removes_leading_trailing_underscores | passing |
| GEN-INV-01 | test_function_count_equals_case_count | passing |
| GEN-INV-02 | test_every_test_references_spec_id | passing |
| GEN-INV-03 | test_generated_code_parses, test_generated_code_with_function_parses | passing |

## Summary

| Tool | Specifications | Covered | Missing |
|------|---------------|---------|---------|
| compute_fingerprint.py | 16 | 16 | 0 |
| validate_traceability.py | 16 | 16 | 0 |
| yaml_to_pytests.py | 17 | 17 | 0 |
| **Total** | **49** | **49** | **0** |

Every specification ID has at least one test.
Every test references a specification ID.
