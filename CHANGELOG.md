# Changelog

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
- Benchmark: 30 evals across 11 categories
  - Content accuracy: 100% with skill vs 89.9% without (+10.1%)
  - Structural accuracy: 99.2% with skill vs 15.0% without (+84.2%)
