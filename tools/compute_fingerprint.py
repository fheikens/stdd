#!/usr/bin/env python3
"""Compute the specification fingerprint for an STDD project.

Usage:
    python compute_fingerprint.py --spec-dir features/ --test-dir tests/ --nfr-file features/nfr.md
    python compute_fingerprint.py --spec-dir features/ --test-dir tests/ --compare
    python compute_fingerprint.py --spec-dir features/ --test-dir tests/ --update

Exit codes:
    0  Fingerprint matches stored value, or update succeeded, or first run
    1  Fingerprint mismatch (knowledge layer changed)
"""

import argparse
import hashlib
import pathlib
import sys

FINGERPRINT_FILE = ".fingerprint"

# Directories and file extensions that are build artifacts, not knowledge layer
_SKIP_DIRS = {"__pycache__", ".pytest_cache", "node_modules", ".mypy_cache"}
_SKIP_SUFFIXES = {".pyc", ".pyo"}


def _is_knowledge_file(filepath: pathlib.Path) -> bool:
    """Return True if filepath is a knowledge-layer file (not a build artifact)."""
    if any(part in _SKIP_DIRS for part in filepath.parts):
        return False
    if filepath.suffix in _SKIP_SUFFIXES:
        return False
    if filepath.name.startswith("."):
        return False
    return filepath.is_file()


def compute_fingerprint(spec_dir: str, test_dir: str, nfr_file: str | None = None) -> str:
    """Hash all specification and test files to produce a fingerprint.

    Directory labels (SPEC_DIR, TEST_DIR, NFR_FILE) are written into the hash
    stream before each section to prevent theoretical path collisions between
    spec and test trees that happen to contain identically-named files.

    Build artifacts (__pycache__, .pyc, .pytest_cache, etc.) are excluded so
    the fingerprint remains stable across platforms and test runs.
    """
    hasher = hashlib.sha256()

    labels = {spec_dir: b"SPEC_DIR\n", test_dir: b"TEST_DIR\n"}
    for directory in [spec_dir, test_dir]:
        path = pathlib.Path(directory)
        if not path.exists():
            print(f"Warning: directory {directory} does not exist", file=sys.stderr)
            continue
        hasher.update(labels[directory])
        for filepath in sorted(path.rglob("*")):
            if _is_knowledge_file(filepath):
                hasher.update(str(filepath.relative_to(path)).encode())
                hasher.update(filepath.read_bytes())

    if nfr_file:
        nfr_path = pathlib.Path(nfr_file)
        if nfr_path.exists():
            hasher.update(b"NFR_FILE\n")
            hasher.update(nfr_path.read_bytes())

    return hasher.hexdigest()


def main():
    parser = argparse.ArgumentParser(description="STDD Specification Fingerprint")
    parser.add_argument("--spec-dir", required=True, help="Directory containing specifications")
    parser.add_argument("--test-dir", required=True, help="Directory containing tests")
    parser.add_argument("--nfr-file", default=None, help="Path to NFR file")
    parser.add_argument("--compare", action="store_true",
                        help="Compare against stored fingerprint, exit 1 on mismatch")
    parser.add_argument("--update", action="store_true",
                        help="Write new fingerprint to .fingerprint file")
    args = parser.parse_args()

    fingerprint = compute_fingerprint(args.spec_dir, args.test_dir, args.nfr_file)
    print(fingerprint)

    if args.compare:
        fp_path = pathlib.Path(FINGERPRINT_FILE)
        if not fp_path.exists():
            print("No .fingerprint file found. This appears to be the first run.",
                  file=sys.stderr)
            print("Run with --update to create the .fingerprint file.", file=sys.stderr)
            sys.exit(0)

        stored = fp_path.read_text().strip()
        if stored != fingerprint:
            print("MISMATCH: specification fingerprint has changed.", file=sys.stderr)
            print(f"  Stored:  {stored}", file=sys.stderr)
            print(f"  Current: {fingerprint}", file=sys.stderr)
            sys.exit(1)
        else:
            print("Fingerprint matches.", file=sys.stderr)

    if args.update:
        pathlib.Path(FINGERPRINT_FILE).write_text(fingerprint + "\n")
        print(f"Updated {FINGERPRINT_FILE}", file=sys.stderr)


if __name__ == "__main__":
    main()
