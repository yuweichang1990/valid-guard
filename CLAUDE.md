# Valid Guard — Developer Instructions

> This file is for **contributors and AI assistants working on the Valid Guard codebase**. For user-facing documentation, see [README.md](README.md).

## Project Overview

Valid Guard is a Claude Code skill that applies software testing theory (EP, BVA, DT, ST, pairwise) to generate risk-annotated YAML test plans before test code is written. The skill definition lives in `.claude/skills/valid-guard/skill.md`.

## Key Directories

```
.claude/skills/valid-guard/   — Skill definition (SKILL.md)
valid-guard/plans/             — YAML test plans (version-controlled)
valid-guard/reports/           — Generated HTML reports (gitignored)
valid-guard/templates/         — HTML report templates (version-controlled)
valid-guard/schema/            — YAML schema definitions
valid-guard/examples/          — Example test plans and reference guides
valid-guard/config.yaml        — Runtime configuration
valid-guard-workspace/phase3/  — Eval suite (30 cases, grading scripts, reports)
demo/                          — End-to-end demo with sample YAML plan
DESIGN.md                      — Architecture and design rationale
```

## Coding Conventions

- **Test plans**: Always YAML. Follow the schema in `valid-guard/schema/`. Every scenario must have `name`, `type`, `risk`, `techniques`, `status`, `test_ref`, `priority`, `tags`, `risk_rationale`, `technique_rationale`, `example_mapping`, and `metadata`.
- **HTML reports**: Must work offline. No external CDN dependencies. Inline all CSS/JS.
- **Python test code**: Idiomatic pytest. Descriptive function names matching scenario names. Group by feature in subdirectories.
- **File naming**: Plans use kebab-case (`user-auth.yaml`). Test files use snake_case (`test_user_auth.py`).
- **Risk levels**: `high`, `medium`, `low` only.
- **Scenario types**: `happy_path`, `edge_case`, `error_case`, `boundary`, `security`.
- **Technique tags**: Snake_case: `equivalence_partitioning`, `boundary_value_analysis`, `decision_table`, `state_transition`, `pairwise`.

## Working on the Eval Suite

The benchmark suite is in `valid-guard-workspace/phase3/`:

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
cd valid-guard-workspace/phase3
python grade_phase3.py iteration-3          # Grade + produce benchmark.json
python generate_report.py iteration-3/benchmark.json  # HTML report
python run_evals.py --grade-only            # Alternative: grade via run_evals.py
```

### Adding new eval cases
1. Add entry to `phase3_evals.json` with id, category, prompt, rubric
2. Add check patterns to `EVAL_CHECKS` in `grade_phase3.py`
3. Run the full suite to confirm no regressions

## Important Rules

- `valid-guard/reports/` is gitignored — keep a `.gitkeep` there
- `valid-guard/plans/` and `valid-guard/templates/` are tracked in git
- When modifying the YAML schema, update both the schema file and DESIGN.md examples
- The HTML report uses export-to-JSON for round-trip editing: human edits in HTML → export JSON → AI reads JSON → updates YAML plan
- The YAML plan layer is language-agnostic — do not introduce language-specific logic into it
- MVP targets Python + pytest; language detection uses `pyproject.toml`, `package.json`, `go.mod`
