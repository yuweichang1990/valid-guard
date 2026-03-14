# Test Design Techniques — Detailed Reference

This document contains detailed heuristics and application guidance for all 7 testing techniques used by Valid Guard. Referenced from SKILL.md Step 2 — Test Technique Selection.

---

## Equivalence Partitioning (EP)

**When to apply:** The input domain can be divided into classes where all values in a class are expected to produce equivalent behavior.

**Heuristics for detection:**
- Function accepts parameters with defined types (string, int, enum, etc.)
- Input has valid and invalid ranges
- Documentation mentions categories, types, or groups of input
- Parameters accept structured values (email, phone, URL, date)

**How to apply:**
1. Identify each input parameter.
2. For each parameter, define equivalence classes: valid classes (at least 2 if possible — e.g., short valid string, long valid string) and invalid classes (null/empty, wrong type, out of range, malformed format).
3. Generate at least one test example per equivalence class.
4. For combinations, ensure at least one test where all inputs are from valid classes (happy path).

---

## Boundary Value Analysis (BVA)

**When to apply:** Inputs have numeric ranges, length limits, size constraints, time constraints, or any ordered domain with defined edges.

**Heuristics for detection:**
- Min/max values mentioned in requirements or code (e.g., `0 <= age <= 150`)
- String length limits (e.g., `username max 32 chars`)
- Array/collection size bounds
- Date/time ranges or deadlines
- Pagination limits
- Rate limits, quotas, thresholds

**How to apply:**
1. For each boundary, generate test values at: the boundary value, one below the boundary (boundary - 1), and one above the boundary (boundary + 1).
2. For two-sided ranges [min, max], test: min-1, min, min+1, typical/nominal, max-1, max, max+1.
3. For length constraints, test: empty (0), 1, max-1, max, max+1.
4. Annotate each boundary test with which boundary it is testing.

---

## Decision Table (DT)

**When to apply:** Multiple conditions combine to determine the outcome, and different combinations produce different results.

**Heuristics for detection:**
- Business rules with AND/OR logic across multiple conditions
- If/else chains or switch statements with multiple branching conditions
- Pricing tiers, permission matrices, feature flags
- Requirements using words like "if... and... then", "when both", "unless"
- More than 2 boolean conditions affecting output

**How to apply:**
1. List all conditions (inputs/states that affect the decision).
2. List all possible actions/outcomes.
3. Build a decision table: each column is a rule (unique combination of conditions), each row is a condition or action.
4. For N boolean conditions, there are 2^N combinations. If N > 5, apply **pairwise reduction** (see Pairwise section) instead of full enumeration.
5. Mark "don't care" conditions where a condition is irrelevant to the outcome.
6. Generate one test per rule (column).

---

## State Transition (ST)

**When to apply:** The system under test has distinct states and transitions between them triggered by events, with behavior depending on current state.

**Heuristics for detection:**
- Entities with lifecycle (e.g., Order: created -> paid -> shipped -> delivered -> returned)
- Status fields or enums (PENDING, ACTIVE, SUSPENDED, CLOSED)
- Workflows with approval/rejection steps
- Session management (logged in, logged out, expired)
- Connection states (connected, disconnected, reconnecting)
- Feature toggles, flags that change behavior over time

**How to apply:**
1. Identify all states.
2. Identify all events/triggers that cause transitions.
3. Build a state transition table: rows = (current state, event), columns = next state and action.
4. Generate tests for:
   - Every valid transition (0-switch coverage minimum).
   - Invalid transitions — what happens when an event fires in a state that should not accept it (e.g., "ship" an order that is not yet "paid").
   - Transition sequences that cover common paths (1-switch coverage for critical paths): e.g., created->paid->shipped->delivered.
5. For complex state machines, visualize the state diagram in the HTML report.

---

## Pairwise / Combinatorial (PW)

**When to apply:** There are more than 3 input parameters with more than 2 possible values each, and full combinatorial testing is impractical.

**Heuristics for detection:**
- Configuration with multiple options (e.g., OS x browser x language x theme)
- API endpoints with many optional parameters
- Feature matrices (plan x region x currency)
- Any scenario where full decision table exceeds 32 combinations

**How to apply:**
1. List all parameters and their possible values.
2. Generate a pairwise covering array — every pair of parameter values appears in at least one test case.
3. For parameters with high-risk interactions, extend to 3-wise coverage.
4. Annotate which pairs each test case covers.
5. Prioritize test cases that cover the most uncovered pairs first.

---

## Cause-Effect Graphing (CE)

**When to apply:** Complex input-output relationships exist with logical dependencies (AND/OR/NOT) between conditions and effects.

**Heuristics for detection:**
- Requirements with compound boolean logic: "if A and (B or C) then X"
- Eligibility or access rules that combine multiple conditions
- Pricing or discount engines where multiple factors interact logically
- Workflow triggers that depend on combinations of input states
- Any specification where the outcome depends on the logical combination of two or more causes

**How to apply:**
1. Identify **causes** — distinct input conditions or states (e.g., "user is a member", "order exceeds $50", "has valid coupon").
2. Identify **effects** — distinct output behaviors or results (e.g., "discount applied", "free shipping granted").
3. Map logical relationships between causes and effects using AND, OR, and NOT connectors.
4. Derive a cause-effect graph and convert it into a decision table.
5. Generate test cases that cover each feasible combination in the graph, paying attention to constraint annotations (e.g., mutually exclusive causes).
6. Example: "discount eligibility depends on (member AND (order > $50 OR has_coupon))" — derive tests for member with large order, member with coupon, member with neither, non-member with both, etc.

---

## Error Guessing (EG)

**When to apply:** Based on testing experience and domain knowledge, anticipate likely defects that formal techniques may not systematically uncover.

**Heuristics for detection:**
- Areas with historically high defect rates or known fragility
- Code handling external inputs (user input, API payloads, file uploads)
- Complex data transformations, serialization/deserialization boundaries
- Date/time handling, timezone conversions, locale-dependent formatting
- Concurrency, caching, retry logic, and eventual consistency
- Integration points with third-party services or legacy systems

**How to apply:**
1. Consider common programming mistakes: off-by-one errors, null/undefined handling, integer overflow, floating-point precision, race conditions, encoding issues (UTF-8, emoji, RTL text).
2. Consider domain-specific pitfalls: what happens with Unicode in usernames, timezone edge cases (DST transitions), leap year dates, currency rounding, negative quantities, duplicate submissions.
3. Consider environmental failures: network timeouts, partial writes, disk full, permission denied, connection pool exhaustion.
4. For each guessed error scenario, define the input that would trigger it and the expected system behavior (graceful degradation, specific error message, rollback).
5. Prioritize guesses by the severity of the failure and the likelihood based on the technology stack and architecture.
