# STDD Templates

Starter files for creating a new STDD feature. Copy these into your project's `features/` directory and fill in the placeholders.

## Files

| Template | Purpose |
|----------|---------|
| `specification.md` | Feature specification with inputs, outputs, rules, invariants, and failure conditions |
| `acceptance-cases.yaml` | Canonical acceptance cases in structured YAML (happy path, edge case, failure case) |
| `traceability-matrix.md` | Mapping from every spec ID to its corresponding test |
| `tfp-prompt.md` | Four-part Test-First Prompting prompt for AI code generation |

## Usage

1. Copy the templates into a new feature directory:
   ```
   cp -r templates/ features/my_feature/
   ```
2. Replace all `[PLACEHOLDER]` values with your feature's details.
3. Write the specification first, then the acceptance cases, then the traceability matrix.
4. Use the TFP prompt template when you are ready to generate an implementation.

## Structure

An STDD feature directory typically looks like this:

```
features/
  my_feature/
    specification.md
    acceptance_cases.yaml
    traceability-matrix.md
    tests/
      test_my_feature.py
```

For full guidance on writing specifications, see `docs/writing-specifications.md`. For the practical workflow, see `docs/engineering-playbook.md`.
