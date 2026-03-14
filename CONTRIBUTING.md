# Contributing to Valid Guard

Thank you for your interest in contributing to Valid Guard. This document covers the essentials for getting started.

## Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yuweichang1990/valid-guard.git
   cd valid-guard
   ```

2. Open Claude Code in the cloned directory. The skill is auto-discovered from `.claude/skills/valid-guard/SKILL.md` --- no additional installation is needed.

3. Verify by typing `/vg status` in the Claude Code chat interface.

## Running the Eval Suite

The benchmark suite lives in `evals/`. To grade pre-recorded eval outputs:

```bash
cd evals/
python grade.py baseline
```

This re-grades the 30 eval outputs in `evals/baseline/` (30 evals x 2 configs = 60 output files). All cases must pass before submitting a PR. No third-party Python dependencies are required --- the grading scripts use only the standard library.

## Adding New Eval Cases

1. Add your test scenario to `evals.json` with the appropriate category and expected outputs.
2. Add corresponding check logic to the `EVAL_CHECKS` dictionary in `grade.py`.
3. Run the full suite to confirm your new case passes and no existing cases regress.

## Code Conventions

- **YAML plans**: Use `snake_case` for keys (e.g., `risk_level`, `gherkin_ref`, `risk_rationale`). Use `kebab-case` for filenames (e.g., `user-auth.yaml`).
- **Gherkin files**: Use `kebab-case` filenames (e.g., `user-authentication.feature`). Tag scenarios with `@risk:<level>` and `@technique:<abbrev>` (e.g., `@risk:high @technique:ep`).
- **Step definitions**: Follow the conventions of the target BDD framework (behave for Python, cucumber-js for JS, etc.).
- **Risk levels**: Always use `high`, `medium`, or `low` (lowercase).
- **Risk rationale**: Always include all 4 dimensions with numeric scores: `"Impact: X, Frequency: X, Consequence: X, Detectability: X. Average: X.XX → level."`
- **Test techniques**: Reference by abbreviation: EP, BVA, DT, ST, PW, CE (Cause-Effect), EG (Error Guessing).
- **Commit messages**: Use imperative mood (e.g., "Add eval case for boundary analysis").

## Pull Request Process

1. Fork the repository and create a feature branch from `main`.
2. Make your changes following the conventions above.
3. Run the eval suite and confirm all cases pass.
4. Open a pull request using the provided PR template.
5. Wait for review. Address any feedback promptly.

## Reporting Issues

Use the GitHub issue templates for bug reports and feature requests. Include as much context as possible.

## License

By contributing, you agree that your contributions will be licensed under the project's existing license.
