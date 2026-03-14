# Changelog

## [0.2.0] - 2026-03-14

### Changed — BDD-Enhanced Architecture (Route C)
- **Architecture pivot**: Valid Guard is now a test design intelligence layer on top of the Cucumber/BDD ecosystem
- YAML plan is the design-thinking layer (risk, techniques, coverage tracking); Gherkin `.feature` files carry executable Given/When/Then details
- BDD framework changed from pytest-bdd to Cucumber for multi-language support (behave, cucumber-js, cucumber-jvm, cucumber, godog)
- `/vg generate` now produces Gherkin `.feature` files with `@risk:` and `@technique:` tags, plus step definition stubs
- `/vg run` delegates to the project's Cucumber-compatible runner instead of constructing pytest commands
- `/vg report` focuses on coverage gap analysis — does not recreate Cucumber's pass/fail reporting

### Simplified
- YAML schema simplified: removed `priority`, `technique_rationale`, `preconditions`, `examples` (input/expected) from scenarios
- Renamed `test_ref` → `gherkin_ref` (points to `.feature` file + scenario name)
- Each scenario is now ~6 lines in YAML (name, type, risk, risk_rationale, techniques, gherkin_ref, status, tags)
- `state_transition` and `decision_table` kept as design artifacts that Gherkin cannot express

### Added
- Gherkin `.feature` example files for all 3 example plans (user-auth, e-commerce, file-upload)
- `questions` field at top level and in `example_mapping` for capturing ambiguities
- `bdd_framework` field in metadata
- `risk_rationale` numeric format: "Impact: X, Frequency: X, Consequence: X, Detectability: X. Average: X.XX → level."
- SECURITY.md with vulnerability reporting instructions

### Updated
- All documentation (README, DESIGN, CLAUDE, CONTRIBUTING) aligned with BDD-enhanced architecture
- Example YAML plans simplified from 200-500+ lines to ~100-130 lines each
- HTML report spec focused on coverage gap analysis

## [0.1.0] - 2026-03-14

### Added
- Initial release of Valid Guard skill for Claude Code
- `/vg plan` -- Greenfield test plan generation from natural language or PRD
- `/vg analyze` -- Brownfield code analysis with gap detection
- `/vg review` -- Interactive HTML report generation
- `/vg generate` -- Test code generation (Python + pytest)
- `/vg run` -- Test execution with result tracking
- `/vg report` -- Combined scenario + line coverage reporting
- `/vg status` -- Quick coverage summary
- Risk assessment with 4-dimension scoring (impact, frequency, consequence, detectability)
- 7 test design techniques: EP, BVA, DT, ST, PW, CE, EG
- Example Mapping and Decision Table visualization
- 3 example test plans (e-commerce, file-upload, auth)
- 6 reference guides (techniques, anti-patterns, flaky tests, mocking, process discipline, HTML report spec)
- Benchmark: 30 evals across 11 categories (pattern-matching rubric, single run, self-evaluated)
  - Content improvement: +10.1% average (100% with skill vs 89.9% without)
  - Structured output: 99.2% schema compliance (internal quality metric)
  - See evals/RESULTS.md for methodology, limitations, and honest framing of these numbers
