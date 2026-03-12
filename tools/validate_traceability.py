#!/usr/bin/env python3
"""Validate that every specification ID has at least one corresponding test.

Usage:
    python validate_traceability.py --spec-dir features/ --test-dir tests/

Scans all .md files in spec-dir for spec IDs (pattern: | WORD-NUMBER in tables).
Scans all test files in test-dir for references to those IDs in docstrings,
comments, or test names.

Exit codes:
    0  All specifications have tests
    1  One or more specifications are untested
"""

import argparse
import pathlib
import re
import sys

SPEC_ID_PATTERN = re.compile(r"^\|\s*(\w+-\d+)", re.MULTILINE)
TEST_FILE_PATTERNS = ["test_*.py", "*_test.py", "*_test.go", "test_*.go"]


def find_spec_ids(spec_dir: str) -> dict[str, str]:
    """Find all spec IDs in .md files. Returns {id: source_file}."""
    spec_ids = {}
    spec_path = pathlib.Path(spec_dir)
    if not spec_path.exists():
        print(f"Error: spec directory {spec_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    for md_file in sorted(spec_path.rglob("*.md")):
        for match in SPEC_ID_PATTERN.finditer(md_file.read_text()):
            spec_ids[match.group(1)] = str(md_file)
    return spec_ids


def find_tested_ids(test_dir: str) -> set[str]:
    """Scan test files for spec ID references."""
    tested = set()
    test_path = pathlib.Path(test_dir)
    if not test_path.exists():
        print(f"Error: test directory {test_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    for pattern in TEST_FILE_PATTERNS:
        for test_file in sorted(test_path.rglob(pattern)):
            content = test_file.read_text()
            for match in re.finditer(r"\b(\w+-\d+)\b", content):
                tested.add(match.group(1))
    return tested


def main():
    parser = argparse.ArgumentParser(description="STDD Traceability Validator")
    parser.add_argument("--spec-dir", required=True, help="Directory containing specifications")
    parser.add_argument("--test-dir", required=True, help="Directory containing tests")
    args = parser.parse_args()

    spec_ids = find_spec_ids(args.spec_dir)
    tested_ids = find_tested_ids(args.test_dir)

    covered = []
    missing = []

    for spec_id, source in sorted(spec_ids.items()):
        if spec_id in tested_ids:
            covered.append((spec_id, source))
        else:
            missing.append((spec_id, source))

    print(f"Specifications found: {len(spec_ids)}")
    print(f"Covered by tests:     {len(covered)}")
    print(f"Missing tests:        {len(missing)}")
    print()

    if covered:
        print("COVERED:")
        for spec_id, source in covered:
            print(f"  {spec_id}  ({source})")
        print()

    if missing:
        print("MISSING TESTS:")
        for spec_id, source in missing:
            print(f"  {spec_id}  ({source})")
        print()
        print("FAILED: untested specifications found.", file=sys.stderr)
        sys.exit(1)
    else:
        print("All specifications have corresponding tests.")


if __name__ == "__main__":
    main()
