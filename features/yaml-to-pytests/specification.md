# Feature: Test Skeleton Generator

Version: 1.0
Type: behavioral
Status: ACTIVE

## Description

Generates test skeletons from an STDD acceptance-cases.yaml file. Each acceptance case becomes a test function with a docstring referencing the spec ID. Supports Python (pytest) and Go (table-driven) output formats.

## Inputs

| ID | Name | Type | Constraints |
|----|------|------|-------------|
| GEN-IN-01 | yaml_file | string | Required. Path to the acceptance-cases.yaml file. |
| GEN-IN-02 | --output | string | Optional. Write generated code to file instead of stdout. |
| GEN-IN-03 | --module | string | Optional. Python module to import from. |
| GEN-IN-04 | --function | string | Optional. Target function name for call stubs. |
| GEN-IN-05 | --language | string | Optional. `python` (default) or `go`. |

## Outputs

| ID | Name | Type |
|----|------|------|
| GEN-OUT-01 | generated_code | text | Test skeleton code printed to stdout or written to file. |
| GEN-OUT-02 | exit_code | integer | 0 on success; 1 on error. |

## Behavioral Scenarios

### Scenario: generate Python test skeletons
  Given: a valid acceptance-cases.yaml with mixed success and error cases
  When: yaml_to_pytests is run with default settings
  Then: one test function per case is generated, printed to stdout

### Scenario: generate with function call stubs
  Given: a valid acceptance-cases.yaml
  When: --module and --function are specified
  Then: import statement and function call stubs with keyword arguments are generated

### Scenario: generate Go table-driven tests
  Given: a valid acceptance-cases.yaml
  When: --language go is specified
  Then: a Go table-driven test skeleton is generated

### Scenario: write to output file
  Given: a valid acceptance-cases.yaml
  When: --output path is specified
  Then: generated code is written to the file, count printed to stderr

### Scenario: invalid YAML file
  Given: a YAML file path that does not exist
  When: yaml_to_pytests is run
  Then: exit code is 1, error printed to stderr

## Rules

| ID | Description |
|----|-------------|
| GEN-01 | Each acceptance case produces exactly one test function (Python) or sub-test entry (Go). |
| GEN-02 | Python test function name is `test_` followed by the slugified case name. |
| GEN-03 | Each test function's docstring contains the spec_id and case name. |
| GEN-04 | Error cases (then.error is true) generate a `pytest.raises` skeleton with error_code comment. |
| GEN-05 | Non-error cases generate assertion placeholders for each key in `then`. |
| GEN-06 | When --module is specified, a `from MODULE import FUNCTION` (or `import MODULE`) statement is added. |
| GEN-07 | When --function is specified, `given` and `when` keys are merged into keyword arguments for the call stub. |
| GEN-08 | In the merged argument list, `given` keys appear before `when` keys. |
| GEN-09 | When --language go is specified, a Go table-driven test skeleton is generated instead of Python. |
| GEN-10 | When --output is specified, generated code is written to the file and a summary is printed to stderr. |
| GEN-11 | Accepts both `acceptance_cases` and `acceptance-cases` as the top-level YAML key. |
| GEN-12 | Exits with code 1 if the YAML file does not exist. |
| GEN-13 | Exits with code 1 if the YAML structure is invalid (not a mapping or missing the expected key). |
| GEN-14 | slugify converts names to valid Python identifiers: lowercase, non-alphanumeric replaced with underscores, stripped of leading/trailing underscores. |

## Invariants

| ID | Description |
|----|-------------|
| GEN-INV-01 | Number of generated test functions equals number of acceptance cases. |
| GEN-INV-02 | Every generated test references exactly one spec_id. |
| GEN-INV-03 | Generated Python code is syntactically valid (parseable by ast.parse). |

## Failure Conditions

| ID | Trigger | Response |
|----|---------|----------|
| GEN-FAIL-01 | YAML file does not exist | Error printed to stderr, exit code 1. |
| GEN-FAIL-02 | YAML content is not a mapping | Error printed to stderr, exit code 1. |
| GEN-FAIL-03 | YAML mapping lacks `acceptance_cases` or `acceptance-cases` key | Error printed to stderr, exit code 1. |

## Constraints

- Requires PyYAML (`pip install pyyaml`).
- Go output always uses `package TODO_test` — the developer must rename it.
- Generated code contains `raise NotImplementedError` or `# TODO` placeholders where the developer must fill in implementation.

## Acceptance Cases

See: acceptance-cases.yaml

## Technologies

Python 3.10+, PyYAML

## Domain

Developer tooling / code generation

## NFR Overrides

None
