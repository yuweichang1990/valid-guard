# Valid Guard Demo — User Registration

This demo shows the end-to-end Valid Guard workflow for a simple user
registration feature: plan, review, and generate.

## Files in This Directory

| File | What it shows |
|------|---------------|
| `user-registration-plan.yaml` | The YAML test plan produced by `/vg plan` — 10 scenarios with risk scores, techniques, state machines, and example mapping. This is the **design layer**. |
| `user-registration.feature` | The Gherkin feature file produced by `/vg generate` — executable Given/When/Then scenarios with `@risk:` and `@technique:` tags. This is the **executable layer**. |
| `README.md` | This walkthrough. |

## Walkthrough

### Step 1 — Generate the Plan

```
/vg plan "User registration with email verification"
```

Valid Guard analyzes the feature, applies risk-based test design techniques,
and produces a YAML test plan at `valid-guard/plans/user-registration.yaml`.

### Step 2 — Review the YAML Test Plan

The included `user-registration-plan.yaml` is a reference copy containing:

- **10 scenarios** — happy paths, error handling, boundaries, security, state transitions
- **Risk scores** with 4-dimension rationale (Impact, Frequency, Consequence, Detectability)
- **Example mapping** linking business rules to concrete test examples
- **State transition** and other design artifacts that Gherkin cannot express
- **Questions** capturing ambiguities for human review

### Step 3 — Generate the Interactive Report

```
/vg review
```

Produces a self-contained HTML report with scenario coverage dashboard,
filterable table, example mapping cards, and approve/reject controls.

### Step 4 — Generate Gherkin Feature Files

```
/vg generate
```

Produces Gherkin `.feature` files with:

- **1:1 scenario mapping** — every YAML scenario becomes a Gherkin Scenario
- **Risk and technique tags** — `@risk:high @technique:ep @technique:bva`
- **Scenario Outlines** — boundary and combinatorial scenarios use Examples tables
- **Step definition stubs** — behave (Python), cucumber-js (JS), etc.

The included `user-registration.feature` shows what this step outputs.

### Step 5 — Run Tests

```
/vg run
```

Delegates to the project's Cucumber-compatible runner (behave, cucumber-js, etc.)
and syncs results back to the YAML plan.

### Step 6 — Coverage Gap Analysis

```
/vg report
```

Analyzes risk-weighted scenario coverage — the unique insight that Cucumber
alone does not provide.
