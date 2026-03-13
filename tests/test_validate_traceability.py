"""Tests for tools/validate_traceability.py.

Every test references a specification ID from
features/validate-traceability/specification.md.

Generated following the STDD methodology — specifications and acceptance
cases were written first, then these tests, then the implementation was
verified against them.
"""

import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

from validate_traceability import find_spec_ids, find_tested_ids, DEFAULT_SPEC_ID_PATTERN


TOOL = os.path.join(os.path.dirname(__file__), "..", "tools", "validate_traceability.py")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_spec_dir(tmp_path, dirname, content):
    """Create a spec directory with one .md file."""
    d = tmp_path / dirname
    d.mkdir(parents=True, exist_ok=True)
    (d / "spec.md").write_text(content)
    return str(d)


def _make_test_dir(tmp_path, dirname, files):
    """Create a test directory with named files."""
    d = tmp_path / dirname
    d.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (d / name).write_text(content)
    return str(d)


# ---------------------------------------------------------------------------
# TR-01: Scans .md files for spec IDs
# ---------------------------------------------------------------------------

def test_scans_md_files_for_spec_ids(tmp_path):
    """TR-01: Finds spec IDs in .md files within spec directory."""
    spec_dir = _make_spec_dir(tmp_path, "specs", "| FEAT-01 | Rule one |\n| FEAT-02 | Rule two |")

    ids = find_spec_ids([spec_dir], DEFAULT_SPEC_ID_PATTERN)

    assert "FEAT-01" in ids
    assert "FEAT-02" in ids


# ---------------------------------------------------------------------------
# TR-02: Detect spec ID in table row
# ---------------------------------------------------------------------------

def test_detect_spec_id_in_table_row(tmp_path):
    """TR-02: Spec IDs in markdown table rows are detected."""
    spec_dir = _make_spec_dir(tmp_path, "specs", "| FEAT-01 | Pending orders can be cancelled |")

    ids = find_spec_ids([spec_dir], DEFAULT_SPEC_ID_PATTERN)

    assert "FEAT-01" in ids


# ---------------------------------------------------------------------------
# TR-03: Detect spec ID in heading
# ---------------------------------------------------------------------------

def test_detect_spec_id_in_heading(tmp_path):
    """TR-03: Spec IDs in markdown headings are detected."""
    spec_dir = _make_spec_dir(tmp_path, "specs", "## FEAT-01 Rule description")

    ids = find_spec_ids([spec_dir], DEFAULT_SPEC_ID_PATTERN)

    assert "FEAT-01" in ids


# ---------------------------------------------------------------------------
# TR-04: Detect spec ID in hash comment
# ---------------------------------------------------------------------------

def test_detect_spec_id_in_hash_comment(tmp_path):
    """TR-04: Spec IDs in hash comments are detected."""
    spec_dir = _make_spec_dir(tmp_path, "specs", "# FEAT-01")

    ids = find_spec_ids([spec_dir], DEFAULT_SPEC_ID_PATTERN)

    assert "FEAT-01" in ids


# ---------------------------------------------------------------------------
# TR-05: Detect spec ID in slash comment
# ---------------------------------------------------------------------------

def test_detect_spec_id_in_slash_comment(tmp_path):
    """TR-05: Spec IDs in slash comments are detected."""
    spec_dir = _make_spec_dir(tmp_path, "specs", "// FEAT-01")

    ids = find_spec_ids([spec_dir], DEFAULT_SPEC_ID_PATTERN)

    assert "FEAT-01" in ids


# ---------------------------------------------------------------------------
# TR-06: Scans test files matching naming patterns
# ---------------------------------------------------------------------------

def test_scans_test_files_by_name_pattern(tmp_path):
    """TR-06: Test files matching test_*.py, *_test.py patterns are scanned."""
    test_dir = _make_test_dir(tmp_path, "tests", {
        "test_feature.py": '"""FEAT-01: tested."""',
        "other.py": "FEAT-02",  # Should NOT be scanned (wrong name pattern)
    })

    tested = find_tested_ids(test_dir, DEFAULT_SPEC_ID_PATTERN)

    assert "FEAT-01" in tested
    assert "FEAT-02" not in tested  # other.py doesn't match test file pattern


# ---------------------------------------------------------------------------
# TR-07: All specifications covered — exit 0
# ---------------------------------------------------------------------------

def test_all_specs_covered_exits_0(tmp_path):
    """TR-07: Exit code 0 when every spec ID has at least one test reference."""
    spec_dir = _make_spec_dir(tmp_path, "specs", "| FEAT-01 | Rule |\n| FEAT-02 | Rule |")
    test_dir = _make_test_dir(tmp_path, "tests", {
        "test_all.py": "# FEAT-01\n# FEAT-02",
    })

    result = subprocess.run(
        [sys.executable, TOOL, "--spec-dir", spec_dir, "--test-dir", test_dir],
        capture_output=True, text=True,
    )

    assert result.returncode == 0


# ---------------------------------------------------------------------------
# TR-08: Untested specification — exit 1
# ---------------------------------------------------------------------------

def test_untested_spec_exits_1(tmp_path):
    """TR-08: Exit code 1 when any spec ID has no test reference."""
    spec_dir = _make_spec_dir(tmp_path, "specs", "| FEAT-01 | tested |\n| FEAT-02 | untested |")
    test_dir = _make_test_dir(tmp_path, "tests", {
        "test_partial.py": "# FEAT-01 only",
    })

    result = subprocess.run(
        [sys.executable, TOOL, "--spec-dir", spec_dir, "--test-dir", test_dir],
        capture_output=True, text=True,
    )

    assert result.returncode == 1
    assert "FEAT-02" in result.stdout


# ---------------------------------------------------------------------------
# TR-09: Non-existent spec directory — exit 1
# ---------------------------------------------------------------------------

def test_nonexistent_spec_dir_exits_1(tmp_path):
    """TR-09: Exit code 1 if spec_dir does not exist."""
    test_dir = _make_test_dir(tmp_path, "tests", {"test.py": "pass"})

    result = subprocess.run(
        [sys.executable, TOOL, "--spec-dir", str(tmp_path / "no_such"), "--test-dir", test_dir],
        capture_output=True, text=True,
    )

    assert result.returncode == 1


# ---------------------------------------------------------------------------
# TR-10: Non-existent test directory — exit 1
# ---------------------------------------------------------------------------

def test_nonexistent_test_dir_exits_1(tmp_path):
    """TR-10: Exit code 1 if test_dir does not exist."""
    spec_dir = _make_spec_dir(tmp_path, "specs", "| FEAT-01 | Rule |")

    result = subprocess.run(
        [sys.executable, TOOL, "--spec-dir", spec_dir, "--test-dir", str(tmp_path / "no_such")],
        capture_output=True, text=True,
    )

    assert result.returncode == 1


# ---------------------------------------------------------------------------
# TR-11: Multiple spec directories
# ---------------------------------------------------------------------------

def test_multiple_spec_dirs(tmp_path):
    """TR-11: Multiple --spec-dir values are all scanned."""
    spec_dir_a = _make_spec_dir(tmp_path, "specs_a", "| MODA-01 | From dir A |")
    spec_dir_b = _make_spec_dir(tmp_path, "specs_b", "| MODB-01 | From dir B |")
    test_dir = _make_test_dir(tmp_path, "tests", {
        "test_all.py": "# MODA-01\n# MODB-01",
    })

    result = subprocess.run(
        [sys.executable, TOOL,
         "--spec-dir", spec_dir_a,
         "--spec-dir", spec_dir_b,
         "--test-dir", test_dir],
        capture_output=True, text=True,
    )

    assert result.returncode == 0
    assert "Specifications found: 2" in result.stdout


# ---------------------------------------------------------------------------
# TR-12: Custom spec pattern
# ---------------------------------------------------------------------------

def test_custom_spec_pattern(tmp_path):
    """TR-12: A custom --spec-pattern overrides the default ID detection."""
    spec_dir = _make_spec_dir(tmp_path, "specs", "| REQ-123 | Custom requirement |")
    test_dir = _make_test_dir(tmp_path, "tests", {
        "test_reqs.py": "# REQ-123",
    })

    result = subprocess.run(
        [sys.executable, TOOL,
         "--spec-dir", spec_dir,
         "--test-dir", test_dir,
         "--spec-pattern", r"REQ-\d+"],
        capture_output=True, text=True,
    )

    assert result.returncode == 0


# ---------------------------------------------------------------------------
# TR-13: Report shows counts
# ---------------------------------------------------------------------------

def test_report_shows_counts(tmp_path):
    """TR-13: Report includes total, covered, and missing counts."""
    spec_dir = _make_spec_dir(tmp_path, "specs", "| FEAT-01 | tested |\n| FEAT-02 | untested |")
    test_dir = _make_test_dir(tmp_path, "tests", {
        "test_partial.py": "# FEAT-01",
    })

    result = subprocess.run(
        [sys.executable, TOOL, "--spec-dir", spec_dir, "--test-dir", test_dir],
        capture_output=True, text=True,
    )

    assert "Specifications found: 2" in result.stdout
    assert "Covered by tests:     1" in result.stdout
    assert "Missing tests:        1" in result.stdout


# ---------------------------------------------------------------------------
# TR-INV-01: Every spec ID found appears in report
# ---------------------------------------------------------------------------

def test_every_spec_id_appears_in_report(tmp_path):
    """TR-INV-01: A spec ID found in any .md file appears in the coverage report."""
    spec_dir = _make_spec_dir(tmp_path, "specs", "| ALPHA-01 | First |\n## BETA-02 Second rule")
    test_dir = _make_test_dir(tmp_path, "tests", {
        "test_both.py": "# ALPHA-01\n# BETA-02",
    })

    result = subprocess.run(
        [sys.executable, TOOL, "--spec-dir", spec_dir, "--test-dir", test_dir],
        capture_output=True, text=True,
    )

    assert "ALPHA-01" in result.stdout
    assert "BETA-02" in result.stdout


# ---------------------------------------------------------------------------
# TR-INV-02 / TR-INV-03: Exit code matches missing count
# ---------------------------------------------------------------------------

def test_exit_0_implies_zero_missing(tmp_path):
    """TR-INV-02: Exit code 0 implies missing count is zero."""
    spec_dir = _make_spec_dir(tmp_path, "specs", "| FEAT-01 | Rule |")
    test_dir = _make_test_dir(tmp_path, "tests", {
        "test_feat.py": "# FEAT-01",
    })

    result = subprocess.run(
        [sys.executable, TOOL, "--spec-dir", spec_dir, "--test-dir", test_dir],
        capture_output=True, text=True,
    )

    assert result.returncode == 0
    assert "Missing tests:        0" in result.stdout


def test_exit_1_implies_nonzero_missing(tmp_path):
    """TR-INV-03: Exit code 1 implies missing count is greater than zero."""
    spec_dir = _make_spec_dir(tmp_path, "specs", "| FEAT-01 | untested |")
    test_dir = _make_test_dir(tmp_path, "tests", {
        "test_empty.py": "# nothing here",
    })

    result = subprocess.run(
        [sys.executable, TOOL, "--spec-dir", spec_dir, "--test-dir", test_dir],
        capture_output=True, text=True,
    )

    assert result.returncode == 1
    assert "Missing tests:        1" in result.stdout
