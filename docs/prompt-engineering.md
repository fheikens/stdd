
# AI Prompt Engineering for STDD
## Writing Specifications That AI Gets Right on the First Attempt

Author: Frank Heikens
Version: 1.1
Date: 2026

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. The TFP Prompt Structure](#2-the-tfp-prompt-structure)
- [3. Writing Specifications That AI Understands](#3-writing-specifications-that-ai-understands)
- [4. Common Specification Ambiguities](#4-common-specification-ambiguities)
- [5. Constraint Language](#5-constraint-language)
- [6. Context Window Management](#6-context-window-management)
- [7. Iterative Prompt Refinement](#7-iterative-prompt-refinement)
- [8. Prompt Anti-Patterns](#8-prompt-anti-patterns)
- [9. Multi-Model Strategy](#9-multi-model-strategy)
- [10. Specification Readiness Checklist](#10-specification-readiness-checklist)
- [11. Worked Examples](#11-worked-examples)
- [12. Conclusion](#12-conclusion)
- [13. AI-Agent Coverage Discipline](#13-ai-agent-coverage-discipline)

---

# 1. Introduction

Test-First Prompting (TFP) gives AI a specification and failing tests, then asks it to generate an implementation that passes the tests. The [Engineering Playbook](engineering-playbook.md), Section 3, defines the four-part prompt structure and provides worked examples at the unit, integration, and system levels.

This document goes deeper. It addresses the craft of prompt engineering within STDD — not the mechanical structure of the prompt, but the skills that determine whether AI generates correct code on the first attempt or the fifth.

The difference between a one-attempt success and a five-attempt struggle is almost never the AI model. It is the specification. A precise, unambiguous specification with explicit constraints produces correct code reliably. A vague specification with implicit rules forces the AI to guess — and guesses are wrong often enough to waste significant time.

This document teaches you to write specifications that eliminate guessing.

---

# 2. The TFP Prompt Structure

A TFP prompt has four parts:

1. **Specification** — the behavioral rules the implementation must satisfy
2. **Tests** — the failing test suite that defines correct behavior
3. **Constraints** — non-functional requirements, coding conventions, library restrictions
4. **Context** — related components, contracts, integration points

See [Engineering Playbook](engineering-playbook.md), Section 3, for the full template, worked examples, and cross-language guidance. See [Templates](../templates/tfp-prompt.md) for the copy-paste starter.

The rest of this document focuses on making each part as effective as possible.

---

# 3. Writing Specifications That AI Understands

AI models process specifications as text. They do not infer intent, read between the lines, or apply domain expertise. Every rule that is not explicitly stated is a rule that AI may violate.

## 3.1 Explicit Over Implicit

The most common cause of failed AI generation is implicit rules — behavior that the specification author considers obvious but does not write down.

**Weak:**
```
The shipping cost has a minimum charge of $5.00.
```

**Strong:**
```
After all calculations (rate × weight × express multiplier), if the result
is less than $5.00, the cost is set to $5.00. This minimum charge applies
regardless of weight, destination, or express status.
```

The weak version states the rule. The strong version states the rule, when it applies (after all calculations), how it applies (set to $5.00, not "add the difference"), and its scope (regardless of other factors).

This is the SC-8 lesson from the [Adoption Guide](adoption-guide.md), Section 5. The first AI generation failed because the specification stated the minimum charge as a note. The second generation succeeded because the specification stated it as a post-calculation constraint with explicit scope.

## 3.2 Procedural vs Declarative Rules

Some rules are best expressed as declarations of what must be true. Others are best expressed as procedures — step-by-step sequences that the implementation must follow.

**Declarative — when the outcome matters, not the process:**
```
The balance must never be negative.
An expired hold must not prevent a new hold on the same seat.
The hash must be deterministic for identical inputs.
```

**Procedural — when the order of operations matters:**
```
1. Calculate base cost: rate × weight
2. Apply express multiplier: base cost × 1.5 if express, × 1.0 otherwise
3. Apply minimum charge: if result < $5.00, set result to $5.00
4. Round to two decimal places
```

Use declarative rules for invariants and constraints. Use procedural rules when the specification defines a calculation with a specific order of operations. AI models follow procedures reliably because there is no ambiguity about what to do next.

## 3.3 Quantified Constraints

Vague quantifiers are a reliable source of AI misinterpretation. Words like "some," "a few," "several," "many," "quickly," and "efficiently" have no testable meaning.

**Vague:**
```
The function should handle large inputs efficiently.
The system should retry failed requests a few times.
The response should be fast.
```

**Quantified:**
```
The function must complete in under 200ms for inputs up to 10,000 elements.
The system retries failed requests exactly 3 times with exponential backoff
(1s, 2s, 4s) before returning an error.
Response time must be below 100ms at the 95th percentile under 500
concurrent connections.
```

If a constraint cannot be expressed as a number, it is not a constraint — it is a wish. Wishes are not testable. They do not belong in a specification.

## 3.4 Boundary Conditions

Every range has boundaries. Every list has a minimum and maximum length. Every numeric input has limits. If the specification does not state what happens at the boundaries, AI will invent behavior.

**Incomplete:**
```
The function accepts a list of items and returns the total price.
```

**Complete:**
```
The function accepts a list of items and returns the total price.
- An empty list returns 0.00.
- A list with a single item returns that item's price.
- The maximum list length is 1000 items. Lists exceeding 1000 items
  raise a ValueError with message "List exceeds maximum length of 1000".
- Each item price must be non-negative. Negative prices raise a ValueError
  with message "Item price must be non-negative".
```

Boundary conditions are where bugs live. State them explicitly, and the tests derived from them will catch boundary violations automatically.

## 3.5 One Rule, One Behavior

Compound rules — rules that describe multiple behaviors in a single statement — are harder for AI to implement correctly because they require the model to decompose the rule internally.

**Compound:**
```
If the user is not authenticated or the session has expired, redirect
to the login page and clear the session cookie, unless the request is
to a public endpoint.
```

**Decomposed:**
```
AUTH-01: If the user is not authenticated, redirect to /login with
         HTTP 302.
AUTH-02: If the session has expired, redirect to /login with HTTP 302.
AUTH-03: When redirecting to /login, clear the session cookie by setting
         its expiry to a past date.
AUTH-04: Requests to public endpoints (listed in PUBLIC_ENDPOINTS) bypass
         authentication checks entirely. No redirect, no cookie clearing.
```

Each decomposed rule is independently testable. Each test verifies one behavior. When a test fails, you know exactly which rule was violated.

---

# 4. Common Specification Ambiguities

Certain patterns in specification language reliably cause AI to generate incorrect code. Recognizing these patterns before generation saves time.

## 4.1 Vague Precedence

When a specification defines multiple rules that could apply to the same input, the order of evaluation matters. If the specification does not define precedence, AI will choose an order — and it may choose wrong.

**Ambiguous:**
```
Apply a 10% discount for orders over $100.
Apply a 15% loyalty discount for premium members.
```

Which discount applies first? Are they cumulative or does the larger one win? The specification does not say.

**Explicit:**
```
DISC-01: For orders over $100, apply a 10% discount to the subtotal.
DISC-02: For premium members, apply a 15% loyalty discount to the
         subtotal.
DISC-03: When both discounts apply, apply the order discount (DISC-01)
         first, then apply the loyalty discount (DISC-02) to the
         already-discounted amount. Discounts are cumulative, not
         exclusive.
```

The third rule resolves the ambiguity. Without it, both "apply the larger discount only" and "apply them cumulatively" are valid interpretations.

## 4.2 Implicit Defaults

When a specification describes behavior for certain inputs but says nothing about other inputs, AI must decide what to do with the unspecified cases. It may return null, raise an exception, use a default value, or ignore the input entirely.

**Ambiguous:**
```
If the user provides a currency, convert the price to that currency.
```

What happens when the user does not provide a currency? What happens when the currency is not recognized?

**Explicit:**
```
CONV-01: If the user provides a supported currency code (USD, EUR, GBP,
         JPY), convert the price to that currency using the current
         exchange rate.
CONV-02: If the user does not provide a currency, return the price in
         the system default currency (USD).
CONV-03: If the user provides an unsupported currency code, raise a
         ValueError with message "Unsupported currency: {code}".
```

Every branch is specified. AI has no decisions to make.

## 4.3 Ambiguous References

Pronouns and vague references in specifications create ambiguity. "The result," "the value," "it," and "the previous state" can refer to multiple things.

**Ambiguous:**
```
Calculate the discount and apply it to the total. If it exceeds the
maximum, cap it.
```

What does "it" refer to in each sentence? The discount? The total after discount? "Cap it" — cap the discount or cap the total?

**Explicit:**
```
CALC-01: Calculate the discount amount as subtotal × discount_rate.
CALC-02: If the discount amount exceeds max_discount, set the discount
         amount to max_discount.
CALC-03: Calculate the final total as subtotal - discount amount.
```

Name every value. Reference it by name, not by pronoun.

## 4.4 Conditional Nesting

Deeply nested conditions in specification language are difficult for AI to translate into correct code. Each level of nesting doubles the number of paths.

**Nested:**
```
If the order is domestic, apply standard shipping unless the order
weighs over 50kg, in which case use freight shipping, unless the
customer has a freight waiver, in which case use standard shipping
but with the freight rate.
```

**Flat:**
```
SHIP-01: Domestic orders under 50kg use standard shipping at the
         standard rate.
SHIP-02: Domestic orders of 50kg or more use freight shipping at the
         freight rate.
SHIP-03: Domestic orders of 50kg or more from customers with a freight
         waiver use standard shipping at the freight rate.
```

Three flat rules. Three tests. No nesting. AI implements each rule independently.

---

# 5. Constraint Language

Different types of constraints require different specification patterns. This section provides templates for the most common constraint categories.

## 5.1 Performance Constraints

Performance constraints must include a metric, a threshold, and the conditions under which the threshold applies.

**Template:**
```
[Metric] must be [below/above] [threshold] [under conditions].
```

**Examples:**
```
Response time must be below 200ms at the 95th percentile under 500
concurrent connections.

Memory usage must not exceed 256MB when processing a batch of 10,000
records.

Startup time must be below 3 seconds on a cold start with no cached data.
```

Without conditions, a performance constraint is untestable. "The API should be fast" is meaningless. "The API must respond in under 100ms for GET requests with a warm cache" is testable.

## 5.2 Security Constraints

Security constraints define what the system must prevent, not just what it must do.

**Template:**
```
[System] must [prevent/ensure] [security property] by [mechanism].
```

**Examples:**
```
All database queries must use parameterized statements. String
concatenation in SQL queries is forbidden.

User passwords must be hashed with bcrypt using a minimum cost factor
of 12. Plaintext passwords must never be stored or logged.

API endpoints requiring authentication must return HTTP 401 with body
{"error": "Authentication required"} when no valid token is provided.
The response must not include any information about why authentication
failed.
```

The mechanism matters. "The system must be secure" is not a specification. "All inputs must be validated against a whitelist before processing" is a specification.

## 5.3 Data Integrity Constraints

Data integrity constraints define what must always be true about the data, regardless of the operation.

**Template:**
```
[Data property] must [always/never] [condition]. When violated,
[specific response].
```

**Examples:**
```
Account balance must never be negative. When a withdrawal would result
in a negative balance, reject the withdrawal and return an error with
message "Insufficient funds". Do not clamp to zero.

Order total must equal the sum of line item totals plus tax plus
shipping. Any discrepancy must raise an IntegrityError.

A seat cannot be held by two customers simultaneously. When a second
hold is attempted on an already-held seat, return an error with message
"Seat is not available".
```

The phrase "do not clamp" in the first example prevents a common AI behavior: when told a value must not be negative, AI sometimes clamps to zero instead of rejecting the operation. The specification must distinguish between clamping and rejecting.

## 5.4 Concurrency Constraints

Concurrency constraints define what happens when multiple operations occur simultaneously.

**Template:**
```
When [N operations] occur [simultaneously/within window], exactly
[outcome]. All other operations must [specific failure behavior].
```

**Examples:**
```
When two concurrent hold requests target the same seat, exactly one
must succeed and return the hold confirmation. The other must fail with
error "Seat is not available". The order of success is not specified.

When a read and a write occur concurrently on the same record, the
read must return either the value before the write or the value after
the write. It must never return a partial or corrupted value.
```

Concurrency specifications must define both the success case and the failure case. "Only one should succeed" is incomplete without specifying what happens to the others.

---

# 6. Context Window Management

Every TFP prompt competes for space in the AI model's context window. Including too little context causes the AI to make assumptions. Including too much causes the AI to lose focus on the critical constraints.

## 6.1 What to Always Include

These elements are mandatory in every TFP prompt:

- **The specification** — all rules, invariants, and failure conditions for the target function
- **The test suite** — the complete set of failing tests the implementation must pass
- **Direct dependencies** — the contracts (method signatures, input/output types) of components the function calls
- **Error handling expectations** — what exceptions to raise, what error messages to return

## 6.2 What to Include When Relevant

These elements improve generation quality but are not always necessary:

- **Related specifications** — when the target function collaborates with other specified components
- **NFR constraints** — when non-functional requirements affect the implementation
- **Language-specific conventions** — when the target language has idioms that matter (e.g., Go error returns vs exceptions)
- **Library constraints** — when specific libraries must or must not be used

## 6.3 What to Omit

These elements rarely help and often hurt:

- **Implementation code of dependencies** — the AI needs to know what a dependency does (its contract), not how it does it
- **Historical context** — why the specification was written, what it replaced, what previous versions looked like
- **Unrelated specifications** — other features in the system that do not interact with the target function
- **Deployment or infrastructure details** — unless the function directly interacts with infrastructure

## 6.4 Context Budgets

As a practical guideline:

| Prompt Level | Typical Context Budget |
|-------------|----------------------|
| **Unit function** | Specification + tests + direct dependency contracts. Usually fits in 2,000–4,000 tokens. |
| **Component** | Specification + tests + all internal function specs + dependency contracts. Usually 4,000–8,000 tokens. |
| **Integration** | Specifications of all collaborating components + integration tests + contracts between them. Usually 8,000–15,000 tokens. |
| **System** | Full workflow specification + all component specs + system tests. Can reach 15,000–30,000 tokens. Decompose if possible. |

When a prompt exceeds the practical budget for its level, the specification is probably too large. Decompose the function into smaller units, each with its own specification and tests.

## 6.5 Dependency Contracts vs Full Implementations

When the target function depends on another component, include the contract — not the implementation.

**Too much (full implementation):**
```
Here is the PricingEngine class:
[200 lines of code]
```

**Just right (contract only):**
```
The function calls PricingEngine.calculate_price(seat_id: str) -> Decimal.
- Returns the current price for the given seat as a Decimal.
- Raises SeatNotFoundError if the seat does not exist.
- Raises PricingUnavailableError if the pricing service is down.
```

The contract tells the AI everything it needs to know to use the dependency correctly. The implementation details are irrelevant and consume context that could be used for the actual specification.

---

# 7. Iterative Prompt Refinement

When AI generates code that fails tests, the response is not to retry the same prompt. The response is to diagnose the failure and refine the prompt systematically.

## 7.1 Read the Failing Test

The test failure message is the most important signal. It tells you exactly which rule was violated and how.

```
FAILED test_minimum_charge_applied
AssertionError: assert 3.75 == 5.00
```

This tells you: the minimum charge rule (SC-8) was not applied. The AI calculated $3.75 but did not enforce the $5.00 minimum.

## 7.2 Classify the Failure

Every generation failure falls into one of four categories:

| Category | Symptom | Resolution |
|----------|---------|------------|
| **Ambiguous specification** | AI implemented a valid interpretation, but the wrong one | Rewrite the rule to eliminate the alternative interpretation |
| **Missing constraint** | AI did something reasonable but violated an unstated rule | Add the missing rule to the specification |
| **Excessive complexity** | AI got some rules right but lost track of others | Decompose into smaller functions |
| **Context insufficiency** | AI could not implement the function because it lacked information about dependencies | Add the missing contract or context |

## 7.3 Targeted Refinement Patterns

Based on the failure category, apply the appropriate refinement:

**Highlight** — When the AI missed a specific rule, move that rule to a more prominent position in the specification. Place it immediately before the test suite, or add a separate "Critical Constraints" section that lists the rules the AI must not miss.

```
CRITICAL CONSTRAINTS (the implementation MUST satisfy these):
- After all calculations, if the result is less than $5.00, set it to $5.00.
- Use Decimal arithmetic, never float.
```

**Decompose** — When the function is too complex for a single generation, split it. If a function has 15 rules, consider splitting it into three functions with 5 rules each. Each sub-function gets its own specification, tests, and TFP prompt.

**Reorder** — When the AI misses ordering constraints, make the order explicit by numbering the steps. Instead of describing rules as a set, describe them as a sequence.

**Seed with examples** — When the AI misinterprets a rule despite clear language, add a concrete input-output example directly in the specification:

```
Example: calculate_shipping(weight=2.0, rate=1.50, express=True)
Step 1: base = 2.0 × 1.50 = 3.00
Step 2: express = 3.00 × 1.5 = 4.50
Step 3: minimum check: 4.50 < 5.00, so result = 5.00
Returns: 5.00
```

## 7.4 When to Stop Refining the Prompt

If the same function fails after three targeted refinements, the problem is usually not the prompt. It is the specification.

At this point:

1. Review the specification for completeness. Are there missing rules? Implicit assumptions?
2. Review the decomposition. Is the function too large? Does it have too many responsibilities?
3. Review the tests. Do the tests accurately represent the specification? Could a test be wrong?

The [Engineering Playbook](engineering-playbook.md), Section 7, provides a full escalation procedure with timeboxes for each attempt.

---

# 8. Prompt Anti-Patterns

These patterns reliably produce poor AI generation results. Avoid them.

## 8.1 Subjective Quality Instructions

```
Write clean, maintainable, well-structured code.
```

This instruction is untestable. The AI cannot verify whether its output is "clean" or "maintainable." These words mean different things to different people. They add noise to the prompt without constraining the output.

Instead, express quality through testable constraints:

```
Each function must have a single responsibility.
No function may exceed 50 lines.
All public functions must include a docstring.
```

## 8.2 Implementation Hints

```
Use a dictionary to store the lookup table.
Implement this with a recursive approach.
Use the Strategy pattern.
```

Implementation hints bias the AI toward a specific approach, which may not be the best one. Worse, they shift the specification from WHAT to HOW. If the specification says "use a dictionary," the AI will use a dictionary even when a different data structure would be more correct.

Let the specification define the behavior. Let the AI choose the implementation. The tests verify correctness regardless of the approach chosen.

The one exception: when a specific library or data structure is required for compatibility, state it as a constraint:

```
Use the shopspring/decimal library for all monetary calculations.
```

This is not an implementation hint — it is a compatibility constraint.

## 8.3 Omitting Failure Conditions

A specification that only describes the happy path produces code that only handles the happy path.

```
The function takes a user ID and returns the user's profile.
```

What happens when the user ID does not exist? When it is null? When it is an empty string? When the database is unreachable?

Every input has valid and invalid forms. Every external dependency can fail. Every state has transitions that are not allowed. If the specification does not define these cases, the AI will not handle them — or will handle them inconsistently.

## 8.4 Retrying Without Change

Running the same prompt a second time rarely produces different results. AI models are largely deterministic at low temperature settings. If the first generation failed, the same prompt will produce the same failure.

Change the prompt before retrying:
- Add the failing test output to the prompt
- Highlight the constraint that was violated
- Add an example of the expected behavior
- Decompose the function

## 8.5 Weakening Tests

When AI generates code that almost passes but fails one test, it is tempting to relax the test to match the AI's output.

This is the most dangerous anti-pattern in STDD.

The test represents the specification. If the AI's output disagrees with the test, the AI is wrong. Weakening the test means changing the specification to match a flawed implementation — the opposite of specification-driven development.

If a test seems wrong, review the specification. If the specification is correct, the test is correct. Fix the prompt or decompose the function. Never weaken the test.

## 8.6 Promoting Coverage Without Test Evidence

When AI is asked to update a traceability matrix or assess coverage, a common failure mode is to mark a requirement COVERED on the strength of plausible reasoning — "the implementation does X, therefore X is covered" — or on the strength of a helper-level test that does not exercise the surface the requirement names.

This is not coverage. It is inference dressed up as evidence. Section 13 of this document and Section 6.5 of the [Core Model](stdd-core-model.md) define the discipline AI agents must apply when reasoning about coverage. The short form: a COVERED claim must point to a specific test that asserts the specific behavior, on the specific surface, that the requirement names. If any part is missing, the requirement is PARTIALLY COVERED or UNCOVERED.

This anti-pattern is dangerous precisely because the matrix looks complete. The defense is procedural, not conversational: require an evidence block on every COVERED row, and refuse to promote without one.

## 8.7 Over-Specifying the Implementation

```
Create a class named ShippingCalculator with a private method
_apply_discount that takes a float and returns a float. Use a
class variable DEFAULT_RATE set to 1.50. Initialize with a
constructor that accepts weight and destination.
```

This is not a specification. This is an implementation. The specification should define behavior — what the function does, not what the code looks like.

```
The shipping calculator accepts a weight (positive float) and a
destination (one of "domestic", "international"). It returns the
shipping cost as a Decimal with two decimal places.
```

The AI may implement this as a class, a function, a module, or a closure. As long as the tests pass, the implementation choice does not matter.

---

# 9. Multi-Model Strategy

STDD specifications are model-independent. The specification defines behavior in human-readable language. The tests verify behavior through executable assertions. Neither depends on any specific AI model.

However, AI models differ in their strengths, and prompt phrasing that works well with one model may be less effective with another.

## 9.1 What Stays Constant

- **The specification** — behavioral rules, invariants, failure conditions
- **The tests** — executable verification of the specification
- **The constraints** — NFRs, library requirements, coding conventions
- **The contracts** — interfaces between components

These are properties of the system, not properties of the AI model. They do not change when you switch models.

## 9.2 What May Adapt

- **Prompt phrasing** — some models respond better to numbered lists, others to prose. Some handle markdown well, others prefer plain text.
- **Context ordering** — placing the most critical constraints first vs last. Different models may have different attention patterns across long prompts.
- **Example density** — some models need worked examples to understand complex rules. Others interpret rules correctly from specification language alone.

## 9.3 Cross-Model Regeneration as Quality Test

One of the strongest tests of specification quality is regenerating the same function with different AI models. If both models produce implementations that pass all tests, the specification is precise enough to be model-independent.

If one model passes and another fails, the failure reveals a specification ambiguity — something the first model guessed correctly but the second did not. Fixing that ambiguity strengthens the specification for all future models.

This is the Regeneration Confidence metric from [Metrics & Measurement](metrics.md), Section 6, applied across models.

---

# 10. Specification Readiness Checklist

Before giving a specification and tests to AI for generation, verify readiness using this checklist.

## Rules

- [ ] Every rule has a unique ID (e.g., SC-01, AUTH-03)
- [ ] Every rule describes one behavior (no compound rules)
- [ ] Every rule uses quantified language (no "a few," "quickly," "efficiently")
- [ ] Every rule defines its scope (what inputs, what conditions)

## Invariants

- [ ] Every invariant is a universal constraint (holds in all scenarios)
- [ ] Every invariant is testable with a concrete assertion
- [ ] Invariants define both what must be true and what must never be true

## Failure Conditions

- [ ] Every invalid input has a defined response (exception type, error message)
- [ ] Every external dependency failure has a defined response
- [ ] Every state violation has a defined response
- [ ] The specification does not rely on implicit "reasonable" behavior for error cases

## Non-Functional Requirements

- [ ] Performance constraints include metric, threshold, and conditions
- [ ] Security constraints include mechanism, not just intent
- [ ] Data integrity constraints define the violation response (reject vs clamp vs log)

## Boundaries

- [ ] Empty inputs are handled (empty list, empty string, null)
- [ ] Maximum inputs are defined (list length limits, string length limits)
- [ ] Numeric ranges are bounded (minimum, maximum, precision)
- [ ] The specification explicitly addresses zero, one, and many cases

## Language

- [ ] No ambiguous pronouns ("it," "the result," "the value")
- [ ] No implicit defaults (every unspecified case has an explicit rule)
- [ ] No vague precedence (rule ordering is explicit when multiple rules could apply)
- [ ] No conditional nesting deeper than one level (flatten nested conditions into separate rules)

If any item on this checklist is unchecked, the specification is likely to cause at least one failed generation attempt. Fix the specification before generating.

---

# 11. Worked Examples

These examples demonstrate how specification refinement improves AI generation results.

## 11.1 Example: The Missing Minimum Charge

**Initial specification:**

```
SC-05: Express shipping multiplies the base cost by 1.5.
SC-06: Standard shipping has no multiplier.
SC-07: The final cost is rounded to two decimal places.
SC-08: The minimum shipping charge is $5.00.
```

**Test that fails:**

```python
def test_minimum_charge_applied():
    """SC-08: Minimum charge overrides low calculated cost."""
    result = calculate_shipping(weight=0.5, rate=1.00, express=False)
    assert result == Decimal("5.00")
```

**AI's output:** Returns `Decimal("0.50")`. The AI calculated 0.5 × 1.00 = 0.50 and rounded it, but did not apply the minimum charge.

**Diagnosis:** SC-08 says "the minimum shipping charge is $5.00" but does not say when or how to apply it. The AI treated it as a constraint on the input (minimum rate) rather than a constraint on the output (minimum result).

**Refined specification:**

```
SC-08: After all calculations (rate × weight × express multiplier ×
       rounding), if the final cost is less than $5.00, set the final
       cost to $5.00. This minimum applies regardless of weight,
       destination, or express status.
```

**Result:** AI generates correct code. The test passes.

**Lesson:** State when the rule applies (after all calculations), how it applies (set to $5.00), and its scope (regardless of other factors).

## 11.2 Example: The Implicit Ordering

**Initial specification:**

```
PRICE-01: Apply the volume discount based on quantity.
PRICE-02: Apply the loyalty discount for premium members.
PRICE-03: Apply tax at the regional rate.
PRICE-04: Round the final amount to two decimal places.
```

**Test that fails:**

```python
def test_discount_ordering():
    """PRICE-01, PRICE-02: Volume then loyalty, cumulative."""
    result = calculate_price(
        unit_price=Decimal("100.00"),
        quantity=20,           # 10% volume discount
        is_premium=True,       # 5% loyalty discount
        tax_rate=Decimal("0.08")
    )
    # Expected: 100 × 20 = 2000 → -10% = 1800 → -5% = 1710 → +8% = 1846.80
    assert result == Decimal("1846.80")
```

**AI's output:** Returns `Decimal("1857.60")`. The AI applied the loyalty discount first, then the volume discount.

**Diagnosis:** PRICE-01 and PRICE-02 do not specify order. The AI applied them in a different sequence, producing a different result because the discounts are applied to progressively smaller amounts.

**Refined specification:**

```
PRICE-01: Calculate the subtotal as unit_price × quantity.
PRICE-02: Apply the volume discount: if quantity ≥ 10, reduce the
          subtotal by 10%. This produces the discounted subtotal.
PRICE-03: Apply the loyalty discount: if the customer is premium,
          reduce the discounted subtotal by 5%. This produces the
          final subtotal.
PRICE-04: Apply tax: multiply the final subtotal by (1 + tax_rate).
          This produces the total.
PRICE-05: Round the total to two decimal places.
```

**Result:** AI generates correct code. Discounts are applied in the specified order.

**Lesson:** When the order of operations affects the result, number the steps sequentially. Do not assume AI will choose the intended order.

---

# 12. Conclusion

Prompt engineering in STDD is not about crafting clever prompts. It is about writing clear specifications.

A specification that is explicit, quantified, and unambiguous produces correct AI-generated code reliably — often on the first attempt. A specification that is vague, implicit, or compound forces the AI to guess, and incorrect guesses waste time in iterative refinement.

The skills in this document reduce generation attempts by eliminating the ambiguities that cause failures:

- Make every rule explicit — no implicit behavior
- Quantify every constraint — no vague language
- Define every boundary — no undefined inputs
- Flatten every conditional — no nested logic
- Name every value — no ambiguous references

These are specification skills, not AI skills. They make specifications better for human readers too. A specification that AI can implement on the first attempt is a specification that any developer can understand without asking questions.

The quality of the prompt follows from the quality of the specification. Invest in the specification, and the prompt takes care of itself.

---

# 13. AI-Agent Coverage Discipline

This section is written for AI agents (Claude, Codex, and equivalents) operating on STDD artifacts. It restates the binding rules from [Core Model](stdd-core-model.md), Section 6.5, in directive form so they can be quoted or linked into an agent prompt.

**An AI agent must not promote coverage status based on plausible reasoning, implementation inspection, or helper-level tests.**

For every requirement an AI agent marks or accepts as COVERED, the agent must explicitly identify:

1. The exact observable behavior the requirement claims.
2. The exact test that proves it (file path and test name).
3. The exact surface that test exercises.
4. The surfaces named by the requirement that are not covered by that test, if any.

If item 4 is non-empty, the requirement is **not** COVERED. It is PARTIALLY COVERED, with the missing surfaces listed explicitly under "Evidence not yet verified," or UNCOVERED if the existing evidence does not match the claim at all.

**Specifically forbidden:**

- Marking a requirement COVERED because the implementation appears to satisfy it.
- Marking a requirement COVERED because a helper, parser, or formatter the implementation calls has its own unit test.
- Marking a multi-channel requirement (log, stderr, stdout, argv, files, network, TLS, backup/restore, environment, command-line) COVERED on the strength of a test against one channel.
- Marking a security, backup, or restore claim COVERED without at least one integration or channel-level test.
- Marking compatibility with an upstream system COVERED because constants, filenames, or function signatures are unchanged.
- Inferring coverage from the presence of similar tests for adjacent requirements.

**Required output when updating a traceability matrix:** every COVERED row must include the evidence block defined in [Templates › Traceability Matrix](../templates/traceability-matrix.md) — test file, test name, behavior verified, surface verified, and any "Evidence not yet verified" entries. A row without that block is not a COVERED row.

**When uncertain, downgrade.** Rule 9 in the Core Model is the default. If the evidence might cover the claim but the agent cannot demonstrate that it does, the row is PARTIALLY COVERED. The cost of an honest PARTIALLY COVERED is a known gap that gets closed; the cost of a false COVERED is a guarantee the system does not provide.

For the categorical definitions and the multi-channel rule, see [Core Model](stdd-core-model.md), Sections 6.4 and 6.1 (Rule 8). For the brownfield/fork-specific application of these rules, see Section 6.6 of the Core Model and Section 7 of the [Adoption Guide](adoption-guide.md).

---

For the TFP prompt template, see [Templates](../templates/tfp-prompt.md).

For TFP examples at unit, integration, and system levels, see [Engineering Playbook](engineering-playbook.md), Section 3.

For failure escalation procedures, see [Engineering Playbook](engineering-playbook.md), Section 7.

For measuring specification quality, see [Metrics & Measurement](metrics.md).

For writing specifications in general, see [Writing Specifications](writing-specifications.md).
