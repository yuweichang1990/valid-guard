# Test Anti-patterns — Detailed Reference

Valid Guard actively avoids these anti-patterns when generating test plans and test code. When analyzing existing tests (`/vg analyze`), flag any of these patterns as quality issues.

---

## Plan-level Anti-patterns

### 1. Happy Path Tunnel Vision
**What:** Only testing the golden path. No error cases, no boundaries, no invalid input.
**Why it's dangerous:** Real bugs live in the cracks — edge cases, error handling, unexpected input.
**Valid Guard rule:** Every scenario MUST have at least one negative/error example. The ratio of happy path to non-happy-path scenarios should be roughly 1:2 or higher for high-risk features.

### 2. Redundant Scenario Explosion
**What:** 50 test cases that all test the same equivalence class with slightly different values.
**Why it's dangerous:** Wastes execution time, maintenance burden, creates false confidence. 50 tests for "valid email" don't catch "email with Unicode domain."
**Valid Guard rule:** One representative value per equivalence class, plus boundary values. More classes > more values per class.

### 3. Risk-Blind Coverage
**What:** Equal testing effort across all features regardless of risk.
**Why it's dangerous:** Spending 20 tests on a cosmetic tooltip while the payment flow has 3 tests.
**Valid Guard rule:** Risk level determines coverage depth. High-risk scenarios get all applicable techniques. Low-risk scenarios get happy path coverage.

### 4. Requirement Gaps as Test Gaps
**What:** Not testing something because "the spec doesn't mention it."
**Why it's dangerous:** Specs are always incomplete. The absence of a requirement doesn't mean the absence of a bug.
**Valid Guard rule:** Use Error Guessing (EG) to go beyond stated requirements. Consider: what would a malicious user try? What would a confused user input?

---

## Code-level Anti-patterns

### 5. The Tautology Test
**What:** Test asserts that the code does what it does — mirrors the implementation.
```python
# BAD: This just repeats the implementation
def test_calculate_price():
    result = calculate_price(100, 0.1)
    assert result == 100 * (1 - 0.1)  # Just the formula again
```
**Fix:** Assert against independently derived expected values:
```python
# GOOD: Expected value is independently known
def test_calculate_price_10_percent_discount():
    assert calculate_price(100, 0.1) == 90.0
```

### 6. The Inspector Test
**What:** Test reaches into private state or internal implementation details.
**Why it's dangerous:** Any refactor breaks the test even if behavior is preserved. Tests become an anchor against improvement.
**Valid Guard rule:** Assert on **observable behavior** — return values, side effects, state changes visible through public API. Never assert on private methods, internal data structures, or the number of times an internal function was called.

### 7. The Flaky Setup
**What:** Test depends on external state: system time, file system layout, network availability, database contents from another test, random values without seed.
**Valid Guard rule:** Each test must be **self-contained**. Use fixtures for setup, use dependency injection for external dependencies, seed randomness, freeze time.

### 8. The Giant Test
**What:** Single test function that tests 15 things with 50+ lines.
**Why it's dangerous:** When it fails, you don't know which behavior broke. Difficult to maintain, hard to read.
**Valid Guard rule:** One assertion concept per test. Use parametrize for variations of the same concept. If a test needs >20 lines of assertions, split it.

### 9. The Test That Cried Wolf
**What:** Test assertions are so loose they always pass. `assert result is not None`, `assert len(items) > 0`.
**Why it's dangerous:** Returns any garbage? Test passes. Returns wrong items? Test passes.
**Valid Guard rule:** Assert on **specific expected values**, not existence checks. Compare exact counts, exact values, exact structures. When exact values aren't stable, assert on invariants that the correct answer satisfies.

### 10. Missing Teardown / Test Pollution
**What:** Tests modify shared state (global variables, database records, files) without cleanup. Test B passes when run alone but fails when Test A runs first.
**Valid Guard rule:** Use setup/teardown fixtures or fresh contexts per test. In database tests, use transactions with rollback. Run tests in random order periodically to catch order dependencies.

### 11. Logic in Tests
**What:** Tests contain loops, conditionals, try/catch, or computation to derive expected values.
```python
# BAD: Logic in the test
def test_sort():
    data = [3, 1, 2]
    result = sort(data)
    for i in range(len(result) - 1):
        assert result[i] <= result[i + 1]  # Reimplements is_sorted
```
**Valid Guard rule:** Tests should be **linear and declarative**. Input → action → expected output. If you need logic, the test is testing too much at once or the expected value should be pre-computed.

### 12. Invisible Failure
**What:** Test catches exceptions and swallows them, or only tests that no exception is raised, without verifying the actual output.
```python
# BAD: Exception hiding
def test_process():
    try:
        result = process(data)
    except Exception:
        pass  # "Test passes!"
```
**Valid Guard rule:** If testing error handling, assert on the specific exception type and message. If testing success, assert on the return value, not just the absence of errors.

---

## Test Naming Anti-patterns

### 13. Meaningless Names
**What:** `test_1`, `test_process`, `test_it_works`
**Valid Guard rule:** Test name must describe: **what** is being tested, **under what conditions**, and **what the expected outcome is**. Pattern: `test_<action>_<condition>_<expected>` (e.g., `test_login_with_expired_password_returns_403`).

### 14. Names That Lie
**What:** `test_successful_login` but the test actually verifies the error message format for failed logins.
**Valid Guard rule:** Test name must accurately reflect what the test asserts. When generating tests from scenarios, derive the name from the scenario name field.

---

## Detection Checklist for `/vg analyze`

When analyzing existing test code, scan for:

- [ ] Tests with no assertions (or only `assert True`)
- [ ] Tests with assertions on mocks that mirror the implementation
- [ ] Test files with no parameterization despite repetitive test logic
- [ ] Tests importing and accessing private members (prefix `_`)
- [ ] Global state modification without matching teardown
- [ ] Tests with `time.sleep()` calls (sign of race condition or flaky setup)
- [ ] Exception swallowing (`except: pass` or bare `except`)
- [ ] Test methods longer than 30 lines
- [ ] Test names that are just `test_1`, `test_2`, or auto-generated numbers
- [ ] No negative/error test cases in a test file
