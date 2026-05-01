"""Tests for tools/yaml_to_pytests.py.

Every test references a specification ID from
features/yaml-to-pytests/specification.md.

Generated following the STDD methodology — specifications and acceptance
cases were written first, then these tests, then the implementation was
verified against them.
"""

import ast
import os
import subprocess
import sys

import pytest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

from yaml_to_pytests import (
    slugify,
    generate_test_function,
    generate_module,
    generate_go_module,
    load_cases,
)


TOOL = os.path.join(os.path.dirname(__file__), "..", "tools", "yaml_to_pytests.py")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_yaml(tmp_path, content, filename="acceptance-cases.yaml"):
    """Write YAML content to a temp file and return its path."""
    f = tmp_path / filename
    if isinstance(content, dict):
        f.write_text(yaml.dump(content, default_flow_style=False))
    else:
        f.write_text(content)
    return str(f)


def _make_cases(cases_list):
    """Wrap a list of cases in the expected top-level dict."""
    return {"acceptance_cases": cases_list}


SIMPLE_CASE = {
    "name": "happy path",
    "spec_id": "FEAT-01",
    "given": {"input": "value"},
    "when": {"action": "do_thing"},
    "then": {"result": "expected"},
}

ERROR_CASE = {
    "name": "reject invalid input",
    "spec_id": "FEAT-03",
    "given": {"input": "bad"},
    "when": {"action": "validate"},
    "then": {"error": True, "error_code": "INVALID_INPUT"},
}


# ---------------------------------------------------------------------------
# GEN-01: One test function per acceptance case
# ---------------------------------------------------------------------------

def test_one_function_per_case():
    """GEN-01: Each acceptance case produces exactly one test function."""
    cases = [SIMPLE_CASE, ERROR_CASE]
    output = generate_module(cases)

    # Count function definitions
    func_count = output.count("\ndef test_")

    assert func_count == 2


# ---------------------------------------------------------------------------
# GEN-02: Test function name is slugified
# ---------------------------------------------------------------------------

def test_slugify_basic():
    """GEN-02: slugify converts names to valid Python identifiers."""
    assert slugify("cancel confirmed order -- refund triggered") == "cancel_confirmed_order_refund_triggered"


def test_slugify_special_chars():
    """GEN-14: slugify handles special characters."""
    result = slugify("Cancel Order -- with special chars! & stuff")
    assert result == "cancel_order_with_special_chars_stuff"
    assert result.isidentifier()


# ---------------------------------------------------------------------------
# GEN-03: Docstring references spec_id
# ---------------------------------------------------------------------------

def test_docstring_references_spec_id():
    """GEN-03: Each test function's docstring contains the spec_id."""
    output = generate_test_function(SIMPLE_CASE)

    assert "FEAT-01" in output
    assert "happy path" in output


# ---------------------------------------------------------------------------
# GEN-04: Error cases get pytest.raises skeleton
# ---------------------------------------------------------------------------

def test_error_case_gets_pytest_raises():
    """GEN-04: Error cases generate a pytest.raises skeleton."""
    output = generate_test_function(ERROR_CASE, target_function="validate")

    assert "pytest.raises" in output
    assert "INVALID_INPUT" in output


# ---------------------------------------------------------------------------
# GEN-05: Non-error cases get assertion placeholders
# ---------------------------------------------------------------------------

def test_non_error_case_gets_assertions():
    """GEN-05: Non-error cases generate assertion placeholders for each then key."""
    case = {
        "name": "success path",
        "spec_id": "FEAT-01",
        "given": {"x": 1},
        "when": {"action": "compute"},
        "then": {"total": 42, "status": "done"},
    }
    output = generate_test_function(case, target_function="compute")

    assert "assert result.total == 42" in output
    assert "assert result.status == 'done'" in output


# ---------------------------------------------------------------------------
# GEN-06: Module flag adds import statement
# ---------------------------------------------------------------------------

def test_module_flag_adds_import():
    """GEN-06: --module adds an import statement to the generated file."""
    output = generate_module([SIMPLE_CASE], target_module="myapp.orders", target_function="cancel_order")

    assert "from myapp.orders import cancel_order" in output


def test_module_only_without_function():
    """GEN-06: --module without --function adds a plain import."""
    output = generate_module([SIMPLE_CASE], target_module="myapp.orders")

    assert "import myapp.orders" in output


# ---------------------------------------------------------------------------
# GEN-07: Function flag merges given+when into kwargs
# ---------------------------------------------------------------------------

def test_function_merges_given_when():
    """GEN-07: --function merges given and when into keyword arguments."""
    case = {
        "name": "call with args",
        "spec_id": "FEAT-01",
        "given": {"order_id": "ORD-100"},
        "when": {"reason": "Changed my mind"},
        "then": {"status": "cancelled"},
    }
    output = generate_test_function(case, target_function="cancel_order")

    assert "cancel_order(order_id='ORD-100', reason='Changed my mind')" in output


# ---------------------------------------------------------------------------
# GEN-08: Given keys appear before when keys
# ---------------------------------------------------------------------------

def test_given_before_when_in_args():
    """GEN-08: In the merged argument list, given keys appear before when keys."""
    case = {
        "name": "ordered args",
        "spec_id": "FEAT-01",
        "given": {"a": 1, "b": 2},
        "when": {"c": 3, "d": 4},
        "then": {"result": 10},
    }
    output = generate_test_function(case, target_function="compute")

    assert "compute(a=1, b=2, c=3, d=4)" in output


# ---------------------------------------------------------------------------
# GEN-09: Go table-driven skeleton
# ---------------------------------------------------------------------------

def test_go_skeleton_generated():
    """GEN-09: --language go produces a Go table-driven test skeleton."""
    output = generate_go_module([SIMPLE_CASE])

    assert "func TestAcceptanceCases" in output
    assert "tests := []struct" in output
    assert "t.Run(tt.name" in output


# ---------------------------------------------------------------------------
# GEN-10: Output flag writes to file
# ---------------------------------------------------------------------------

def test_output_writes_to_file(tmp_path):
    """GEN-10: --output writes generated code to a file."""
    yaml_path = _write_yaml(tmp_path, _make_cases([SIMPLE_CASE]))
    out_file = str(tmp_path / "test_generated.py")

    result = subprocess.run(
        [sys.executable, TOOL, yaml_path, "--output", out_file],
        capture_output=True, text=True,
    )

    assert result.returncode == 0
    assert os.path.exists(out_file)
    content = open(out_file).read()
    assert "def test_happy_path" in content


# ---------------------------------------------------------------------------
# GEN-11: Accepts both YAML key variants
# ---------------------------------------------------------------------------

def test_accepts_underscore_key(tmp_path):
    """GEN-11: Accepts 'acceptance_cases' as the top-level key."""
    yaml_path = _write_yaml(tmp_path, "acceptance_cases:\n  - name: test\n    spec_id: X-01\n    given: {}\n    when: {}\n    then: {ok: true}")

    cases = load_cases(__import__("pathlib").Path(yaml_path))

    assert len(cases) == 1


def test_accepts_hyphen_key(tmp_path):
    """GEN-11: Accepts 'acceptance-cases' as the top-level key."""
    yaml_path = _write_yaml(tmp_path, "acceptance-cases:\n  - name: test\n    spec_id: X-01\n    given: {}\n    when: {}\n    then: {ok: true}")

    cases = load_cases(__import__("pathlib").Path(yaml_path))

    assert len(cases) == 1


# ---------------------------------------------------------------------------
# GEN-12: File not found exits 1
# ---------------------------------------------------------------------------

def test_file_not_found_exits_1():
    """GEN-12 / GEN-FAIL-01: Exit code 1 and error to stderr if the YAML file does not exist."""
    result = subprocess.run(
        [sys.executable, TOOL, "/nonexistent/path/cases.yaml"],
        capture_output=True, text=True,
    )

    assert result.returncode == 1
    assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()


# ---------------------------------------------------------------------------
# GEN-13: Invalid YAML structure exits 1
# ---------------------------------------------------------------------------

def test_invalid_yaml_structure_exits_1(tmp_path):
    """GEN-13 / GEN-FAIL-02: Exit code 1 and error to stderr if YAML is not a mapping."""
    yaml_path = _write_yaml(tmp_path, "- just a list\n- no mapping")

    result = subprocess.run(
        [sys.executable, TOOL, yaml_path],
        capture_output=True, text=True,
    )

    assert result.returncode == 1
    assert "Error" in result.stderr


def test_missing_key_exits_1(tmp_path):
    """GEN-13 / GEN-FAIL-03: Exit code 1 and error to stderr if YAML lacks the expected key."""
    yaml_path = _write_yaml(tmp_path, "wrong_key:\n  - name: test")

    result = subprocess.run(
        [sys.executable, TOOL, yaml_path],
        capture_output=True, text=True,
    )

    assert result.returncode == 1
    assert "Error" in result.stderr


# ---------------------------------------------------------------------------
# GEN-14: Slugify produces valid identifiers
# ---------------------------------------------------------------------------

def test_slugify_removes_leading_trailing_underscores():
    """GEN-14: slugify strips leading and trailing underscores."""
    result = slugify("--leading and trailing--")
    assert not result.startswith("_")
    assert not result.endswith("_")


# ---------------------------------------------------------------------------
# GEN-INV-01: Number of test functions equals number of cases
# ---------------------------------------------------------------------------

def test_function_count_equals_case_count():
    """GEN-INV-01: Number of generated test functions equals number of acceptance cases."""
    cases = [
        {"name": f"case {i}", "spec_id": f"X-{i:02d}", "given": {}, "when": {}, "then": {"ok": True}}
        for i in range(5)
    ]
    output = generate_module(cases)

    assert output.count("\ndef test_") == 5


# ---------------------------------------------------------------------------
# GEN-INV-02: Every test references exactly one spec_id
# ---------------------------------------------------------------------------

def test_every_test_references_spec_id():
    """GEN-INV-02: Every generated test has the spec_id in its docstring."""
    cases = [
        {"name": "first", "spec_id": "AA-01", "given": {}, "when": {}, "then": {"ok": True}},
        {"name": "second", "spec_id": "BB-02", "given": {}, "when": {}, "then": {"ok": True}},
    ]
    output = generate_module(cases)

    assert "AA-01" in output
    assert "BB-02" in output


# ---------------------------------------------------------------------------
# GEN-INV-03: Generated Python code is syntactically valid
# ---------------------------------------------------------------------------

def test_generated_code_parses():
    """GEN-INV-03: Generated Python code is parseable by ast.parse."""
    cases = [SIMPLE_CASE, ERROR_CASE]
    output = generate_module(cases)

    # This will raise SyntaxError if the code is invalid
    ast.parse(output)


def test_generated_code_with_function_parses():
    """GEN-INV-03: Generated code with --function flag is also valid Python."""
    case = {
        "name": "with function",
        "spec_id": "FEAT-01",
        "given": {"x": 1, "y": 2},
        "when": {"op": "add"},
        "then": {"result": 3},
    }
    output = generate_module([case], target_module="myapp", target_function="compute")

    ast.parse(output)
