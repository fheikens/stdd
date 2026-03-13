# STDD Quick Start
## Build Your First Feature in 90 Minutes

Author: Frank Heikens
Version: 1.0
Date: 2026

---

You have a feature to build. This guide gets you from zero to a regenerable, AI-verified implementation in six steps. All you need is a text editor, a test runner, and access to an AI coding assistant.

---

### Step 1: Define the Specification (~15 min)

Copy `templates/specification.md` into your project. Fill in every section: inputs, outputs, rules, invariants, and failure conditions.

Write one sentence per rule. If a rule takes a paragraph, your feature is too big -- decompose it into smaller features first.

A good specification answers: *What does this function accept? What does it return? What must always be true? What can go wrong?*

---

### Step 2: Write Acceptance Cases (~10 min)

Copy `templates/acceptance-cases.yaml`. Write one case per scenario: happy path, edge cases, and failures. Each case references a spec ID from Step 1.

Cover at least: one normal input, one boundary value, one invalid input, and one failure condition. If you can think of a case, write it now. You will not get another chance before generation.

---

### Step 3: Write Tests (~20 min)

Translate each acceptance case into a test. One test per case. Each test docstring references its spec ID:

```python
from decimal import Decimal

def test_group_discount_applied():
    """FEAT-01: Groups of 4+ receive 10% discount."""
    result = calculate_price("Orchestra", "E1", group_size=4)
    assert result.total == Decimal("360.00")
```

All tests fail -- no implementation exists yet. This is correct.

Copy `templates/traceability-matrix.md` and fill it in. Every spec ID must map to at least one test. Every test must map to a spec ID.

---

### Step 4: Generate with TFP (~15 min)

Copy `templates/tfp-prompt.md` and fill in your specification, tests, and constraints. Give the complete prompt to your AI assistant. Run the generated code against your tests.

Tests fail? Refine the prompt -- add the constraint the AI missed, or decompose further. **Never weaken the tests.** The tests are the specification. Expect 1--3 attempts for a well-specified function.

---

### Step 5: Verify (~10 min)

All tests pass. Now lock it down:

```
python tools/validate_traceability.py --spec-dir features/ --test-dir tests/
python tools/compute_fingerprint.py --spec-dir features/ --test-dir tests/ --update
```

The first command confirms every spec ID has a test. The second records a fingerprint of your knowledge layer.

Commit the specification, tests, traceability matrix, implementation, and `.fingerprint` together. They are one atomic unit.

---

### Step 6: Celebrate. Then Regenerate. (~5 min)

Delete the implementation file. Run TFP again with the same spec and tests. The new implementation passes all tests.

This is the regeneration model working. The spec and tests *are* the system. The code is disposable. You just proved it.

---

## What's Next?

- [Writing Specifications](writing-specifications.md) -- deeper guidance on precision, invariants, and failure conditions
- [Engineering Playbook](engineering-playbook.md) -- CI setup, fingerprinting, and team workflows
- [Adoption Guide](adoption-guide.md) -- rolling STDD out across a team
- [Order Cancellation Example](../examples/order-cancellation/) -- a complete worked example with spec, tests, and implementation
