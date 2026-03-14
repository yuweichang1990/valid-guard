# Mock Strategy Guide — Detailed Reference

When Valid Guard generates test code (`/vg generate`), it must select the right test double strategy for each dependency. Wrong choices lead to tests that pass in isolation but fail in production, or tests so tightly coupled to implementation that any refactor breaks them.

---

## Test Double Hierarchy

Use the **least powerful double** that satisfies the test's goal:

| Double Type | What it does | When to use | Risk level |
|---|---|---|---|
| **Real** | Actual dependency | Fast, deterministic, no side effects | Lowest — most realistic |
| **Fake** | Simplified working implementation (e.g., in-memory DB) | Dependency is slow/external but logic must be exercised | Low |
| **Stub** | Returns pre-configured values, no behavior verification | Test needs controlled input from a dependency | Medium |
| **Spy** | Records calls for later assertion | Need to verify an interaction happened (e.g., email sent) | Medium-High |
| **Mock** | Pre-programmed expectations, fails if not met | Complex interaction protocols | Highest — most brittle |

**Default preference order:** Real > Fake > Stub > Spy > Mock

---

## Decision Framework: When to Mock

### MUST mock (external boundary)
- Network calls to third-party APIs (payment gateways, OAuth providers)
- File system operations that would create real artifacts
- Time-dependent logic (use clock injection, not `time.sleep`)
- Random/non-deterministic sources (seed or inject)
- Email/SMS/notification sending

### SHOULD mock (pragmatic choice)
- Database access in unit tests (but use real DB in integration tests)
- Heavy computational dependencies that slow tests (>1s per call)
- Dependencies with complex setup that dwarfs the test logic

### SHOULD NOT mock (test value loss)
- The module under test itself (obvious, but AI agents sometimes do this)
- Pure functions and value objects — just call them
- Data structures, DTOs, configuration objects
- Simple utility functions (string formatting, math, parsing)
- Anything where the mock would just mirror the implementation

### MUST NOT mock (test becomes meaningless)
- Logic you are trying to test — mocking the subject defeats the purpose
- Dependencies whose behavior IS the test (e.g., testing "does our SQL query return correct results" by mocking the database)
- Standard library primitives (list operations, string methods, math)

---

## Mock Boundary Principle

> **Mock at the boundary, not in the middle.**

Draw a clear line between "inside" (code you own and are testing) and "outside" (infrastructure, third-party services, I/O). Mock at this boundary only.

```
┌──────────────────────────────────┐
│         Code Under Test          │
│  ┌──────┐  ┌──────┐  ┌──────┐  │
│  │ Svc A │→│ Svc B │→│ Svc C │  │  ← Do NOT mock between these
│  └──────┘  └──────┘  └──────┘  │
│              │                   │
│         ┌────▼────┐              │
│         │  Port   │              │  ← Mock HERE (the boundary)
│         └────┬────┘              │
└──────────────┼───────────────────┘
          ┌────▼────┐
          │ External │  (DB, API, filesystem, network)
          └─────────┘
```

---

## Mock Patterns by Dependency Type

### Database
- **Unit tests:** Use repository pattern + in-memory fake, or stub the repository interface
- **Integration tests:** Use real database with transaction rollback or test containers
- **Never:** Mock individual SQL queries — if the query is wrong, the mock won't catch it

### HTTP/API Clients
- Stub at the HTTP client level (e.g., `responses` library in Python, `nock` in Node.js)
- Provide realistic response payloads, including error responses (400, 500, timeout)
- Test timeout and retry behavior separately

### Time
- Inject a clock/time provider rather than patching `datetime.now()` globally
- Provide a `FakeClock` that can be advanced programmatically
- Critical for testing: TTL expiration, rate limiting, scheduling, cron jobs

### File System
- Use temporary directories (`tmp_path` in pytest) for tests that need real files
- Stub only when testing logic that decides what to do, not the I/O itself
- Never mock `open()` — use `tmp_path` or `StringIO`/`BytesIO`

### Event/Message Systems
- Use an in-memory event bus fake that captures published events
- Assert on event contents and ordering, not on publish method calls
- Test consumers with real events, not by mocking the event handler

---

## Mock Anti-patterns to Avoid

| Anti-pattern | Why it's harmful | What to do instead |
|---|---|---|
| **Mock-and-mirror** | Mock returns exactly what the real implementation would — test proves nothing | Use the real implementation or write a meaningful fake |
| **Mock-the-world** | Every dependency is mocked — test is an implementation spec | Mock only at boundaries; use real objects internally |
| **Assert-on-internals** | Verifying private method calls or internal state | Assert on observable outputs and side effects only |
| **Setup-heavier-than-test** | 30 lines of mock setup, 3 lines of test | Redesign: extract interface, use fake, or rethink test scope |
| **Mock leak** | Mock set up in one test bleeds into another | Use fresh mocks per test; avoid global/module-level patching |
| **Fragile mock chains** | `mock.return_value.method.return_value.attr` chains | Simplify the interface or introduce an adapter |

---

## Generated Code Guidelines

When `/vg generate` creates test code:

1. **Declare mock strategy per scenario** — add a comment explaining why this double type was chosen
2. **Prefer dependency injection** — if the code under test doesn't support DI, suggest a refactor TODO
3. **Use framework-idiomatic patterns:**
   - Python: `unittest.mock.patch` for boundary mocking, `pytest.fixture` for fakes
   - TypeScript: jest mocking or dependency injection containers
   - Go: interface-based test doubles
4. **Generate realistic test data** — not `"test"`, `123`, `True`, but domain-realistic values
5. **Include cleanup** — ensure mocks are reset between tests (prefer per-test fixtures over global setup)
