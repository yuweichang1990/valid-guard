# Contributing to Valid Guard

Thank you for your interest in contributing to Valid Guard. This document covers the essentials for getting started.

## Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/valid-guard.git
   cd valid-guard
   ```

2. Install the skill locally in Claude Code:
   ```bash
   claude mcp add valid-guard -- cat valid-guard-workspace/skill.md
   ```

3. Verify the installation by running `/vg status` in Claude Code.

## Running the Eval Suite

The benchmark suite lives in `valid-guard-workspace/phase3/`. To run it:

```bash
cd valid-guard-workspace/phase3/
python grade_phase3.py iteration-3
```

All 30 eval cases must pass before submitting a PR.

## Adding New Eval Cases

1. Add your test scenario to `phase3_evals.json` with the appropriate category and expected outputs.
2. Add corresponding check logic to the `EVAL_CHECKS` dictionary in `grade_phase3.py`.
3. Run the full suite to confirm your new case passes and no existing cases regress.

## Code Conventions

- **YAML plans**: Use `kebab-case` for keys and filenames (e.g., `test-plan.yaml`, `risk-level`).
- **Test files**: Use `snake_case` for Python test functions and filenames (e.g., `test_login_flow.py`).
- **Risk levels**: Always use `high`, `medium`, or `low` (lowercase).
- **Test techniques**: Reference by abbreviation: EP, BVA, DT, ST, PW, CE, EG.
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
