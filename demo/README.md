# Valid Guard Demo — User Registration

This demo shows the end-to-end Valid Guard workflow for a simple user
registration feature: plan, review, and generate.

## Files in This Directory

| File | What it shows |
|------|---------------|
| `user-registration-plan.yaml` | The YAML test plan produced by `/vg plan` — 10 scenarios with risk scores, technique rationale, and example mapping. |
| `generated-tests-example.py` | A realistic example of the pytest code that `/vg generate` produces from the plan above. |
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
- **Technique rationale** explaining why each testing method was chosen

### Step 3 — Generate the Interactive Report

```
/vg review
```

Produces a self-contained HTML report with scenario coverage dashboard,
filterable table, example mapping cards, and approve/reject controls.

### Step 4 — Generate Test Code

```
/vg generate
```

Produces a pytest file with one test function per scenario. The included
`generated-tests-example.py` is what this step would output for the
user-registration plan. Key properties of the generated code:

- **1:1 scenario mapping** — every YAML scenario becomes a test function
- **`pytest.mark.parametrize`** — scenarios with multiple examples use parametrize
- **Arrange / Act / Assert** — consistent structure in every test
- **Docstrings with `test_ref`** — traceability back to the plan
- **TODO annotations** — clearly marks where real fixtures, clients, and assertions need to be wired up

## What's Next

- `/vg generate` — Generate test code from the plan
- `/vg run` — Execute generated tests and capture results
- `/vg report` — Produce a final coverage report with metrics
