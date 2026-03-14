# Valid Guard Demo — User Registration

This demo shows the output of `/vg plan` for a simple user registration feature.
See `user-registration-plan.yaml` for the complete test plan.

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
- **Technique rationale** explaining why each testing method was chosen

### Step 3 — Generate the Interactive Report

```
/vg review
```

Produces a self-contained HTML report with scenario coverage dashboard,
filterable table, example mapping cards, and approve/reject controls.

## What's Next

- `/vg generate` — Generate test code from the plan
- `/vg run` — Execute generated tests and capture results
- `/vg report` — Produce a final coverage report with metrics
