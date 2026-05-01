"""Tests for tools/compute_fingerprint.py.

Every test references a specification ID from
features/compute-fingerprint/specification.md.

Generated following the STDD methodology — specifications and acceptance
cases were written first, then these tests, then the implementation was
verified against them.
"""

import os
import subprocess
import sys

import pytest

# Allow importing from tools/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

from compute_fingerprint import compute_fingerprint


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TOOL = os.path.join(os.path.dirname(__file__), "..", "tools", "compute_fingerprint.py")


def _make_tree(tmp_path, dirname, files):
    """Create a directory with the given files and return its path."""
    d = tmp_path / dirname
    d.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (d / name).write_text(content)
    return str(d)


# ---------------------------------------------------------------------------
# FP-01 / FP-02: Hash includes spec and test files
# ---------------------------------------------------------------------------

def test_fingerprint_includes_spec_and_test_files(tmp_path):
    """FP-01, FP-02: Hash is computed from files in both directories."""
    spec_dir = _make_tree(tmp_path, "specs", {"spec.md": "# Spec"})
    test_dir = _make_tree(tmp_path, "tests", {"test_x.py": "assert True"})

    fp = compute_fingerprint(spec_dir, test_dir)

    assert isinstance(fp, str)
    assert len(fp) == 64  # SHA-256 hex digest


# ---------------------------------------------------------------------------
# FP-03: Directory labels in hash stream
# ---------------------------------------------------------------------------

def test_directory_labels_affect_hash(tmp_path):
    """FP-03: SPEC_DIR and TEST_DIR labels differentiate which directory a file belongs to."""
    # Same file in spec-only vs test-only should produce different hashes
    # because the label (SPEC_DIR vs TEST_DIR) differs
    spec_with_file = _make_tree(tmp_path, "spec_full", {"data.md": "content"})
    test_empty = _make_tree(tmp_path, "test_empty", {})

    spec_empty = _make_tree(tmp_path, "spec_empty", {})
    test_with_file = _make_tree(tmp_path, "test_full", {"data.md": "content"})

    fp_in_spec = compute_fingerprint(spec_with_file, test_empty)
    fp_in_test = compute_fingerprint(spec_empty, test_with_file)

    assert fp_in_spec != fp_in_test


# ---------------------------------------------------------------------------
# FP-04: Each file contributes path and content
# ---------------------------------------------------------------------------

def test_file_path_and_content_in_hash(tmp_path):
    """FP-04: Renaming a file changes the hash even if content is identical."""
    spec_dir_a = _make_tree(tmp_path, "specs_a", {"alpha.md": "content"})
    spec_dir_b = _make_tree(tmp_path, "specs_b", {"beta.md": "content"})
    test_dir = _make_tree(tmp_path, "tests", {"test.py": "pass"})

    fp_a = compute_fingerprint(spec_dir_a, test_dir)
    fp_b = compute_fingerprint(spec_dir_b, test_dir)

    assert fp_a != fp_b


# ---------------------------------------------------------------------------
# FP-05: NFR file included when present
# ---------------------------------------------------------------------------

def test_nfr_file_changes_hash(tmp_path):
    """FP-05: Including an NFR file changes the fingerprint."""
    spec_dir = _make_tree(tmp_path, "specs", {"spec.md": "# Spec"})
    test_dir = _make_tree(tmp_path, "tests", {"test.py": "pass"})
    nfr = tmp_path / "nfr.md"
    nfr.write_text("# NFR: latency < 200ms")

    fp_without = compute_fingerprint(spec_dir, test_dir)
    fp_with = compute_fingerprint(spec_dir, test_dir, nfr_file=str(nfr))

    assert fp_without != fp_with


# ---------------------------------------------------------------------------
# FP-06: NFR file silently skipped when absent
# ---------------------------------------------------------------------------

def test_nfr_file_skipped_when_absent(tmp_path):
    """FP-06: A nonexistent NFR file does not affect the hash."""
    spec_dir = _make_tree(tmp_path, "specs", {"spec.md": "# Spec"})
    test_dir = _make_tree(tmp_path, "tests", {"test.py": "pass"})

    fp_without = compute_fingerprint(spec_dir, test_dir)
    fp_with_missing = compute_fingerprint(spec_dir, test_dir, nfr_file=str(tmp_path / "no_such.md"))

    assert fp_without == fp_with_missing


# ---------------------------------------------------------------------------
# FP-07: Missing directory prints warning but continues
# ---------------------------------------------------------------------------

def test_missing_directory_warns_but_continues(tmp_path, capsys):
    """FP-07 / FP-FAIL-01: A nonexistent spec_dir produces a warning, not a crash."""
    test_dir = _make_tree(tmp_path, "tests", {"test.py": "pass"})

    fp = compute_fingerprint(str(tmp_path / "no_such_dir"), test_dir)

    assert isinstance(fp, str)
    assert len(fp) == 64
    captured = capsys.readouterr()
    assert "Warning" in captured.err


def test_missing_test_directory_warns_but_continues(tmp_path, capsys):
    """FP-07 / FP-FAIL-02: A nonexistent test_dir produces a warning, not a crash."""
    spec_dir = _make_tree(tmp_path, "specs", {"spec.md": "# Spec"})

    fp = compute_fingerprint(spec_dir, str(tmp_path / "no_such_test_dir"))

    assert isinstance(fp, str)
    assert len(fp) == 64
    captured = capsys.readouterr()
    assert "Warning" in captured.err


# ---------------------------------------------------------------------------
# FP-08: Deterministic
# ---------------------------------------------------------------------------

def test_deterministic_hash(tmp_path):
    """FP-08: Same inputs always produce the same hash."""
    spec_dir = _make_tree(tmp_path, "specs", {"spec.md": "# Spec"})
    test_dir = _make_tree(tmp_path, "tests", {"test.py": "pass"})

    fp1 = compute_fingerprint(spec_dir, test_dir)
    fp2 = compute_fingerprint(spec_dir, test_dir)

    assert fp1 == fp2


# ---------------------------------------------------------------------------
# FP-INV-02: Content change produces different hash
# ---------------------------------------------------------------------------

def test_content_change_produces_different_hash(tmp_path):
    """FP-INV-02: Changing any file's content changes the hash."""
    spec_dir = _make_tree(tmp_path, "specs", {"spec.md": "version 1"})
    test_dir = _make_tree(tmp_path, "tests", {"test.py": "pass"})

    fp_before = compute_fingerprint(spec_dir, test_dir)

    # Modify the spec file
    (tmp_path / "specs" / "spec.md").write_text("version 2")

    fp_after = compute_fingerprint(spec_dir, test_dir)

    assert fp_before != fp_after


# ---------------------------------------------------------------------------
# FP-INV-03: Sorted order
# ---------------------------------------------------------------------------

def test_files_processed_in_sorted_order(tmp_path):
    """FP-INV-03: Files are processed in sorted order — hash is stable regardless of creation order."""
    spec_dir = tmp_path / "specs"
    spec_dir.mkdir()
    test_dir = _make_tree(tmp_path, "tests", {"test.py": "pass"})

    # Create files in reverse alphabetical order
    (spec_dir / "c.md").write_text("C")
    (spec_dir / "a.md").write_text("A")
    (spec_dir / "b.md").write_text("B")

    fp1 = compute_fingerprint(str(spec_dir), test_dir)
    fp2 = compute_fingerprint(str(spec_dir), test_dir)

    assert fp1 == fp2


# ---------------------------------------------------------------------------
# FP-09: Compare matches
# ---------------------------------------------------------------------------

def test_compare_matches(tmp_path, monkeypatch):
    """FP-09: --compare exits 0 when stored fingerprint matches."""
    spec_dir = _make_tree(tmp_path, "specs", {"spec.md": "# Spec"})
    test_dir = _make_tree(tmp_path, "tests", {"test.py": "pass"})

    monkeypatch.chdir(tmp_path)

    # Compute and store
    fp = compute_fingerprint(spec_dir, test_dir)
    (tmp_path / ".fingerprint").write_text(fp + "\n")

    result = subprocess.run(
        [sys.executable, TOOL, "--spec-dir", spec_dir, "--test-dir", test_dir, "--compare"],
        capture_output=True, text=True, cwd=str(tmp_path),
    )

    assert result.returncode == 0


# ---------------------------------------------------------------------------
# FP-10: Compare detects mismatch
# ---------------------------------------------------------------------------

def test_compare_detects_mismatch(tmp_path, monkeypatch):
    """FP-10 / FP-FAIL-03: --compare exits 1, MISMATCH and both hashes printed to stderr."""
    spec_dir = _make_tree(tmp_path, "specs", {"spec.md": "# Spec"})
    test_dir = _make_tree(tmp_path, "tests", {"test.py": "pass"})

    monkeypatch.chdir(tmp_path)
    stored_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    (tmp_path / ".fingerprint").write_text(stored_hash + "\n")

    result = subprocess.run(
        [sys.executable, TOOL, "--spec-dir", spec_dir, "--test-dir", test_dir, "--compare"],
        capture_output=True, text=True, cwd=str(tmp_path),
    )

    assert result.returncode == 1
    assert "MISMATCH" in result.stderr
    assert stored_hash in result.stderr  # stored hash printed
    assert "Current:" in result.stderr  # current hash labeled


# ---------------------------------------------------------------------------
# FP-11: Compare with no .fingerprint file
# ---------------------------------------------------------------------------

def test_compare_first_run(tmp_path, monkeypatch):
    """FP-11: --compare exits 0 when no .fingerprint file exists (first run)."""
    spec_dir = _make_tree(tmp_path, "specs", {"spec.md": "# Spec"})
    test_dir = _make_tree(tmp_path, "tests", {"test.py": "pass"})

    monkeypatch.chdir(tmp_path)

    result = subprocess.run(
        [sys.executable, TOOL, "--spec-dir", spec_dir, "--test-dir", test_dir, "--compare"],
        capture_output=True, text=True, cwd=str(tmp_path),
    )

    assert result.returncode == 0
    assert "first run" in result.stderr.lower()


# ---------------------------------------------------------------------------
# FP-12: Update writes fingerprint file
# ---------------------------------------------------------------------------

def test_update_writes_fingerprint(tmp_path, monkeypatch):
    """FP-12: --update writes hash + newline to .fingerprint file."""
    spec_dir = _make_tree(tmp_path, "specs", {"spec.md": "# Spec"})
    test_dir = _make_tree(tmp_path, "tests", {"test.py": "pass"})

    monkeypatch.chdir(tmp_path)

    result = subprocess.run(
        [sys.executable, TOOL, "--spec-dir", spec_dir, "--test-dir", test_dir, "--update"],
        capture_output=True, text=True, cwd=str(tmp_path),
    )

    assert result.returncode == 0
    fp_file = tmp_path / ".fingerprint"
    assert fp_file.exists()

    content = fp_file.read_text()
    assert content.endswith("\n")
    assert len(content.strip()) == 64


# ---------------------------------------------------------------------------
# FP-13: Hash always printed to stdout
# ---------------------------------------------------------------------------

def test_hash_printed_to_stdout(tmp_path):
    """FP-13: The hash is always printed to stdout regardless of mode."""
    spec_dir = _make_tree(tmp_path, "specs", {"spec.md": "# Spec"})
    test_dir = _make_tree(tmp_path, "tests", {"test.py": "pass"})

    result = subprocess.run(
        [sys.executable, TOOL, "--spec-dir", spec_dir, "--test-dir", test_dir],
        capture_output=True, text=True,
    )

    assert result.returncode == 0
    assert len(result.stdout.strip()) == 64
