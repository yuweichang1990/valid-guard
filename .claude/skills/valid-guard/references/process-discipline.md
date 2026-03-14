# Process Discipline — Detailed Reference

Valid Guard is a test *design* engine, but good design is worthless if the AI undermines it during execution. This reference defines the process guardrails that prevent lazy, hallucinatory, or rationalizing behavior during test generation and execution.

---

## Anti-rationalization Catalog

When generating or executing tests, the AI will be tempted to cut corners. These rationalizations are **pre-rejected** — if you catch yourself thinking any of these, stop and follow the correct procedure instead.

| Rationalization | Why it's rejected | Correct behavior |
|---|---|---|
| "This function is too simple to test" | Simple functions break in integration. Boundary cases exist in every function. | Test it. Use BVA at minimum. |
| "I'll add edge case tests later" | Later never comes. Coverage debt compounds. | Add them now as part of the scenario plan. |
| "The happy path test is sufficient" | Happy paths are the least likely place for bugs. | Every happy path needs >=1 error path companion. |
| "Mocking everything will be faster" | Over-mocked tests prove nothing about real behavior. | Mock only at boundaries (see `mock-strategy.md`). |
| "This test is just checking the implementation" | Tautology tests are anti-patterns. | Test observable behavior and independently-derived expected values. |
| "100% coverage means the code is correct" | Coverage measures execution, not correctness. | Scenario coverage > line coverage. Always. |
| "These tests are essentially the same" | Each equivalence class exists for a reason. | If they're truly redundant, remove one. If not, keep both. |
| "The user didn't ask for negative tests" | Users rarely ask for what prevents bugs. | Always include negative tests for high/medium risk scenarios. |
| "Error guessing is just guessing" | EG catches real-world defects that formal techniques miss. | Apply EG to every high-risk scenario. Document rationale. |

---

## Verify-Red / Verify-Green Protocol

When `/vg run` executes tests, apply this two-gate verification:

### Gate 1: Verify-Red (for newly generated tests before implementation)

Before claiming a test is meaningful:
1. The test must **fail** because the feature is missing, NOT because of syntax errors or import failures.
2. The failure message must match the expected behavior gap.
3. A test that passes immediately is testing existing behavior — it does not count as new coverage. Either:
   - The scenario was already covered (update plan status to `covered`)
   - The test is a tautology (rewrite it)

### Gate 2: Verify-Green (after implementation)

After a test passes:
1. All other tests must still pass (no regression).
2. The implementation must be the minimum code needed — no speculative features.
3. If a previously-passing test now fails, fix the code, never the test.

---

## Incremental Generation Mode

Valid Guard's default `/vg generate` produces all tests at once (batch mode). For high-risk features or complex code, use **incremental mode** instead:

### When to use incremental mode
- The feature has >10 scenarios
- Multiple scenarios have complex setup requirements
- The codebase has no existing test infrastructure
- The team prefers red-green-refactor rhythm

### How incremental mode works

1. Sort scenarios by priority (risk-weighted, highest first).
2. For each scenario, in order:
   a. Generate ONE test function.
   b. Run it — verify it fails for the right reason (Gate 1).
   c. If generating implementation too: write minimum code to pass.
   d. Run full suite — verify all pass (Gate 2).
   e. Self-audit the test (see checklist below).
   f. Proceed to next scenario.

### Self-Audit Checklist (per test)

After generating each test, verify:

- [ ] **Behavior, not implementation**: Does this test assert on observable outputs, not internal mechanics?
- [ ] **Public interface only**: Does this test access only the public API?
- [ ] **Refactor-resistant**: Would this test survive an internal rename/restructure unchanged?
- [ ] **Minimum implementation**: Does the code contain only what this test requires?
- [ ] **No speculation**: Are there any features added "while we're here"?
- [ ] **Independent**: Does this test depend on any other test's side effects?
- [ ] **Deterministic**: Will this test produce the same result every time?

If any check fails, rewrite the test from scratch — do not patch.

---

## Quality Escalation Policy

When test quality is below standard, escalate rather than patch:

### Level 1: Fix (minor issues)
- Missing assertion detail → add specific assertion
- Weak test name → rename to describe behavior
- Missing cleanup → add teardown

### Level 2: Rewrite (structural issues)
- Tautology test → delete and regenerate with independent expected values
- Inspector test → rewrite to test observable behavior only
- Giant test → split into focused test functions

### Level 3: Re-plan (design issues)
- Missing entire scenario category → return to `/vg plan` or `/vg analyze`
- Wrong techniques applied → re-evaluate technique selection
- Risk assessment incorrect → re-score with updated understanding

**Never patch a fundamentally flawed test.** If the approach is wrong, the correct action is to go back to the appropriate level and redo, not to add workarounds.

---

## Preventing Lazy Generation

These rules apply whenever `/vg generate` creates test code:

1. **No placeholder assertions**: `assert True`, `pass`, `# TODO: add assertion` are never acceptable in generated output. Every test must have at least one meaningful assertion.

2. **No copy-paste tests**: If multiple tests share >80% of their code, extract the common logic into a parametrized test or shared fixture. But each test must still have a unique, descriptive name.

3. **No mock-the-subject**: Never mock the function/class being tested. If you're testing `PaymentProcessor.process()`, `PaymentProcessor` must be real.

4. **No assert-only-not-None**: `assert result is not None` is almost never sufficient. Assert the specific expected value, type, structure, or behavior.

5. **No silent exception swallowing**: Never use `try/except: pass` in test code. If testing error handling, assert on the specific exception type and message.

6. **Domain-realistic data**: Use values that look like real data. Not `"test"`, `123`, `True`, but `"john.doe@company.com"`, `42599` (a realistic order ID), `Decimal("149.99")`.
