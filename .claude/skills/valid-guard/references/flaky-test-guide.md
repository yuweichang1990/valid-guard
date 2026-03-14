# Flaky Test Management — Detailed Reference

Flaky tests — tests that sometimes pass and sometimes fail without code changes — are one of the biggest threats to test suite trust. A flaky test suite is worse than no tests: developers stop believing failures and start ignoring red builds. Valid Guard includes flaky test detection and management as a core concern.

---

## Root Cause Classification

Every flaky test has a root cause. Classify first, then remediate.

### Category 1: Timing & Concurrency
**Symptoms:** Fails under load, in CI but not locally, inconsistently on slower machines.
**Common causes:**
- Race conditions between threads/processes
- `time.sleep()` used instead of proper waiting/polling
- Timeouts too tight for CI environments
- Non-atomic operations assumed to be atomic
- Clock drift between test start and assertion time

**Remediation:**
- Replace `sleep()` with explicit wait conditions (poll for expected state)
- Use deterministic synchronization (locks, barriers, events)
- Inject time dependencies (freeze time, use fake clocks)
- Add retries ONLY at the infrastructure level, never in the test logic itself

### Category 2: Test Order Dependency
**Symptoms:** Passes in isolation, fails when run with other tests. Fails when test order is randomized.
**Common causes:**
- Shared mutable state (global variables, class-level attributes, module state)
- Database records created by Test A expected by Test B
- File system artifacts not cleaned up
- Cached values persisting between tests

**Remediation:**
- Enforce test isolation: each test creates its own data, cleans up after itself
- Use fresh fixtures per test (not per session or per module for mutable state)
- Run test suite with randomized order regularly (`pytest-randomly`)
- Add setup/teardown that resets shared state

### Category 3: Environmental Sensitivity
**Symptoms:** Passes on developer machines, fails in CI. Passes on Linux, fails on Windows. Passes Monday, fails on the first of the month.
**Common causes:**
- Locale/timezone differences (`en_US` vs `en_GB`, UTC vs local)
- File path separators (`/` vs `\`)
- Floating-point precision differences across architectures
- DNS resolution, network availability assumptions
- Disk space, memory limits, file descriptor limits

**Remediation:**
- Pin locale and timezone in test setup
- Use `os.path.join()` or `pathlib` instead of string concatenation for paths
- Use approximate comparisons for floating-point (`pytest.approx`)
- Mock all network dependencies
- Document minimum resource requirements

### Category 4: Non-deterministic Data
**Symptoms:** Random, unpredictable failures. Fails with certain randomly generated inputs but not others.
**Common causes:**
- Unseeded random number generators
- UUIDs or timestamps in expected output
- Dictionary/set iteration order (Python <3.7, or current in other languages)
- Reliance on database auto-increment IDs being sequential

**Remediation:**
- Seed all random generators in tests
- Use deterministic ID generators in test fixtures
- Sort collections before comparison when order doesn't matter
- Use pattern matching instead of exact string comparison for timestamps/UUIDs

### Category 5: Resource Leaks
**Symptoms:** Passes when run alone, fails when run as part of the full suite. Fails more consistently the longer the suite runs.
**Common causes:**
- Open file handles, database connections not closed
- Thread pool exhaustion
- Memory leaks making later tests OOM
- Port conflicts (test server from previous test still binding)

**Remediation:**
- Use context managers (`with` statements) for all resources
- Implement proper fixture teardown
- Use unique ports per test or wait for port availability
- Monitor resource consumption in CI

---

## Flaky Test Detection

### During `/vg run`

When test results include failures, Valid Guard should:

1. **Check for known flaky patterns** in the test code:
   - `time.sleep()` calls → likely Category 1
   - Global state access → likely Category 2
   - Platform-specific paths → likely Category 3
   - `random.` calls without seed → likely Category 4

2. **Compare with previous runs** (if `valid-guard/reports/results.xml` history exists):
   - Test that passed before and fails now without code change → suspect flaky
   - Test that alternates pass/fail across runs → confirmed flaky

3. **Report flaky suspects** separately from genuine failures:
   ```
   Failing tests: 3
     ✗ test_payment_processing (genuine — new code)
     ✗ test_timeout_handling (likely flaky — Category 1: uses sleep())
     ✗ test_user_list_order (likely flaky — Category 4: no sort before compare)
   ```

### During `/vg analyze`

When analyzing existing tests, scan for flaky test indicators:
- `time.sleep()` in test code
- Missing teardown for shared resources
- Platform-specific path strings
- Unseeded `random` usage
- Global variable mutation
- Missing `@pytest.fixture` teardown (yield fixtures without cleanup)

---

## Quarantine Strategy

When a test is confirmed flaky:

1. **Mark it** — add a tag/marker in the test plan YAML: `tags: [flaky, category_1_timing]`
2. **Isolate it** — suggest moving to a separate test suite or marking with `@pytest.mark.flaky`
3. **Track it** — record in the test plan with status `flaky` and the root cause category
4. **Fix it** — provide specific remediation guidance based on the root cause category
5. **Time-box it** — flaky tests not fixed within 2 weeks should be either fixed or removed

**Important:** Quarantine is a temporary measure, not a permanent solution. A quarantined test represents a coverage gap.

---

## Prevention in `/vg generate`

When generating new tests, Valid Guard applies these rules to prevent flaky tests from being created:

1. **No `time.sleep()`** — use explicit wait conditions or mock time
2. **No unseeded randomness** — seed all generators, or use fixed test data
3. **No implicit ordering** — sort before comparing collections
4. **No shared mutable state** — use fresh fixtures per test
5. **No hardcoded paths** — use `tmp_path`, `os.path.join`, or path injection
6. **No network calls** — mock all HTTP, use test containers for databases
7. **Explicit cleanup** — yield fixtures with teardown, context managers for resources
8. **Deterministic IDs** — use factory patterns with sequential or fixed IDs
9. **Timezone-safe** — all datetime tests use UTC or explicitly set timezone
10. **Platform-agnostic** — use `pathlib`, avoid OS-specific commands
