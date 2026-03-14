# Valid Guard — Developer Instructions

> This file is for **contributors and AI assistants working on the Valid Guard codebase**. For user-facing documentation, see [README.md](README.md).

## Project Overview

Valid Guard is a Claude Code skill that applies software testing theory (EP, BVA, DT, ST, pairwise) to generate risk-annotated YAML test plans before test code is written. The skill definition lives in `.claude/skills/valid-guard/SKILL.md`.

## Key Directories

```
.claude/skills/valid-guard/        — Skill definition (SKILL.md)
  ├── assets/                      — Report template, default config
  ├── references/                  — Techniques guide, YAML schema, anti-patterns
  └── examples/                    — 3 example YAML test plans
evals/                             — Eval suite (30 cases, grading scripts, reports)
demo/                              — End-to-end demo with sample YAML plan
DESIGN.md                          — Architecture and design rationale
```

Note: `valid-guard/plans/`, `valid-guard/reports/`, and `tests/` are created at runtime in the **user's project**, not in this repository.

## Coding Conventions

- **Test plans**: Always YAML. Follow the schema in `.claude/skills/valid-guard/references/test-plan-schema.yaml`. Every scenario must have `name`, `type`, `risk`, `techniques`, `status`, `test_ref`, `priority`, `tags`, `risk_rationale`, `technique_rationale`, `example_mapping`, and `metadata`.
- **HTML reports**: Must work offline. No external CDN dependencies. Inline all CSS/JS.
- **Python test code**: Idiomatic pytest. Descriptive function names matching scenario names. Group by feature in subdirectories.
- **File naming**: Plans use kebab-case (`user-auth.yaml`). Test files use snake_case (`test_user_auth.py`). YAML keys use snake_case (`risk_level`, `test_ref`).
- **Risk levels**: `high`, `medium`, `low` only.
- **Scenario types**: `happy_path`, `edge_case`, `error_handling`, `boundary`, `security`, `state_transition`, `combinatorial`, `performance`.
- **Technique tags**: `equivalence_partitioning`, `boundary_value`, `decision_table`, `state_transition`, `pairwise`, `cause_effect`, `error_guessing`.

## Working on the Eval Suite

The benchmark suite is in `evals/`:

```bash
# Grade all 30 evals
make grade

# Generate HTML report
make report

# Verify all output files exist
make verify
```

Or directly:
```bash
cd evals
python grade.py baseline          # Grade + produce benchmark.json
python report_gen.py baseline/benchmark.json  # HTML report
python run.py --grade-only            # Alternative: grade via run.py
```

### Adding new eval cases
1. Add entry to `evals.json` with id, category, prompt, rubric
2. Add check patterns to `EVAL_CHECKS` in `grade.py`
3. Run the full suite to confirm no regressions

## Important Rules

- `valid-guard/reports/` (in the user's project) is gitignored
- When modifying the YAML schema, update both the schema file and DESIGN.md examples
- The HTML report uses export-to-JSON for round-trip editing: human edits in HTML → export JSON → AI reads JSON → updates YAML plan
- The YAML plan layer is language-agnostic — do not introduce language-specific logic into it
- MVP targets Python + pytest; language detection uses `pyproject.toml`, `package.json`, `go.mod`
