#!/usr/bin/env python3
"""Validate that every specification ID has at least one corresponding test.

Usage:
    python validate_traceability.py --spec-dir features/ --test-dir tests/
    python validate_traceability.py --spec-dir features/ --spec-dir modules/ --test-dir tests/
    python validate_traceability.py --spec-dir features/ --test-dir tests/ --spec-pattern "REQ-\\d+"

Scans all .md files in each spec-dir for spec IDs. By default, IDs are
detected using the pattern WORD-NUMBER in the following locations:
  - Markdown table rows:   | WORD-NUMBER ...
  - Markdown headings:     ## ... WORD-NUMBER ...
  - Code fence comments:   # WORD-NUMBER   or   // WORD-NUMBER

A custom spec ID pattern can be supplied via --spec-pattern (default:
\\w+(?:-\\w+)*-\\d+, which matches multi-segment IDs like FP-INV-01 and
FP-FAIL-01 in addition to single-segment IDs like FEAT-01).
Multiple --spec-dir values are supported to scan several specification trees.

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

DEFAULT_SPEC_ID_PATTERN = r"\w+(?:-\w+)*-\d+"
TEST_FILE_PATTERNS = ["test_*.py", "*_test.py", "*_test.go", "test_*.go"]


def _build_spec_id_patterns(spec_pattern: str) -> list[re.Pattern]:
    """Build the list of compiled regexes used to detect spec IDs."""
    return [
        # Table rows: | SPEC-123 ...
        re.compile(rf"^\|\s*({spec_pattern})", re.MULTILINE),
        # Markdown headings: ## ... SPEC-123 ...
        re.compile(rf"^#+.*\b({spec_pattern})\b", re.MULTILINE),
        # Hash comment: # SPEC-123
        re.compile(rf"#\s+({spec_pattern})"),
        # Slash comment: // SPEC-123
        re.compile(rf"//\s+({spec_pattern})"),
    ]


def find_spec_ids(spec_dirs: list[str], spec_pattern: str) -> dict[str, str]:
    """Find all spec IDs in .md files. Returns {id: source_file}."""
    spec_ids: dict[str, str] = {}
    patterns = _build_spec_id_patterns(spec_pattern)

    for spec_dir in spec_dirs:
        spec_path = pathlib.Path(spec_dir)
        if not spec_path.exists():
            print(f"Error: spec directory {spec_dir} does not exist", file=sys.stderr)
            sys.exit(1)

        for md_file in sorted(spec_path.rglob("*.md")):
            content = md_file.read_text()
            for pattern in patterns:
                for match in pattern.finditer(content):
                    spec_ids[match.group(1)] = str(md_file)
    return spec_ids


def find_tested_ids(test_dir: str, spec_pattern: str) -> set[str]:
    """Scan test files for spec ID references."""
    tested: set[str] = set()
    test_path = pathlib.Path(test_dir)
    if not test_path.exists():
        print(f"Error: test directory {test_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    id_re = re.compile(rf"\b({spec_pattern})\b")
    for pattern in TEST_FILE_PATTERNS:
        for test_file in sorted(test_path.rglob(pattern)):
            content = test_file.read_text()
            for match in id_re.finditer(content):
                tested.add(match.group(1))
    return tested


def main():
    parser = argparse.ArgumentParser(description="STDD Traceability Validator")
    parser.add_argument("--spec-dir", required=True, action="append",
                        help="Directory containing specifications (may be repeated)")
    parser.add_argument("--test-dir", required=True, help="Directory containing tests")
    parser.add_argument("--spec-pattern", default=DEFAULT_SPEC_ID_PATTERN,
                        help="Regex pattern for spec IDs (default: %(default)s)")
    args = parser.parse_args()

    spec_ids = find_spec_ids(args.spec_dir, args.spec_pattern)
    tested_ids = find_tested_ids(args.test_dir, args.spec_pattern)

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
