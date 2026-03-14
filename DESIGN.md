# Valid Guard — Design Decisions

## Core Philosophy
- **BDD-enhanced test design** — not just testing, but helping humans maintain control over AI-driven development through systematic test design intelligence layered on top of the Cucumber/Gherkin ecosystem
- AI writes code too fast for humans to review line-by-line; the human's role is: define goals → review plan → verify results
- Current AI coding agents write lazy tests — a few tests and done. Valid Guard enforces systematic test design using software testing theory
- **Scenario coverage > code coverage** — care about covering important scenarios and critical paths, weighted by risk

## Name: Valid Guard

## Architecture: Route C — BDD-Enhanced Test Design

Valid Guard is a **test design intelligence layer** that sits on top of the Cucumber BDD ecosystem:

```
YAML Plan (design layer)     →  Gherkin .feature (executable layer)  →  Cucumber Runner (execution)
Risk, techniques, coverage       Given/When/Then scenarios               behave, cucumber-js, etc.
```

### Why Route C?
- **YAML plan** = design-thinking layer — risk assessment, technique selection, coverage tracking, decision tables, state machines. Things that Gherkin syntax cannot express.
- **Gherkin .feature files** = executable specification layer — Given/When/Then scenarios readable by all stakeholders.
- **Cucumber runner** = test execution — delegates to the mature, multi-language Cucumber ecosystem instead of reinventing a test runner.

### What Valid Guard adds that BDD alone doesn't provide:
1. **Risk assessment** — 4-dimension scoring (impact, frequency, consequence, detectability) per scenario
2. **Technique selection** — systematic application of EP, BVA, DT, ST, PW, CE, EG
3. **Scenario completeness audit** — ensures all risk-relevant paths are covered, not just the obvious happy paths
4. **Design artifacts** — decision tables, state transition diagrams that Gherkin cannot represent
5. **Coverage gap analysis** — risk-weighted scenario coverage metrics

### What Valid Guard does NOT do:
- Replace Cucumber's test execution (use `behave`, `cucumber-js`, `cucumber-jvm`, etc.)
- Recreate Cucumber's reporting (`--format html`, `--format json`)
- Manage step definition implementations (that's the developer's job)

## Two Entry Points
1. **Greenfield** (`/vg plan`): From PRD/feature description → scenario analysis → YAML plan → Gherkin .feature files
2. **Brownfield** (`/vg analyze`): From existing code → reverse-engineer scenarios → find coverage gaps
   - Target Level 3 depth (cross-function call chains, data flow, state changes) up to context window limits

## Test Design Layer (Core Differentiator)
AI auto-selects appropriate testing techniques based on heuristics:
- **Equivalence Partitioning**: when inputs have clear valid/invalid ranges
- **Boundary Value Analysis**: when numeric ranges, length limits, time constraints exist
- **Decision Table**: when multiple condition combinations affect outcomes
- **State Transition**: when objects have lifecycle/state flow
- **Pairwise/Combinatorial**: when parameter combinations explode (>3 params, >2 values each)
- **Cause-Effect Graphing**: when complex logical dependencies exist between inputs and outputs
- **Error Guessing**: experience-based anticipation of likely defects
- Multiple techniques can apply to the same scenario

## Risk Assessment Dimensions
| Dimension | High (3) | Medium (2) | Low (1) |
|---|---|---|---|
| Impact scope | Core business, payments, security | Secondary features, UX | Display-only, cosmetic |
| Usage frequency | Every user daily | Some users occasionally | Rarely triggered |
| Failure consequence | Data loss, security breach, money | Functional but workaround exists | Minor inconvenience |
| Detectability | Silent failure (user won't notice) | User notices but not severe | Immediately visible |

Risk score = average of 4 dimensions. High >= 2.5, Medium >= 1.5, Low < 1.5.

## Scenario Coverage Metric
```
Feature PRD
  └─ Epic / User Story
       └─ Scenario (via Example Mapping)
            ├─ Rule 1
            │    ├─ Example 1.1 (happy path) → [risk: high] → feature::scenario ✅
            │    ├─ Example 1.2 (edge case)  → [risk: medium] → feature::scenario ✅
            │    └─ Example 1.3 (boundary)   → [risk: high] → ❌ uncovered
            └─ Rule 2 ...
```
- Scenario coverage = covered scenarios / total scenarios
- Weighted coverage uses risk levels (high=3, medium=2, low=1)

## Slash Commands
```
/vg plan <description>    # Greenfield: natural language → YAML test plan
/vg plan --prd <file>     # Greenfield: from PRD file
/vg analyze <path>        # Brownfield: analyze existing code
/vg review                # Interactive HTML report for human review
/vg generate              # Generate Gherkin .feature files + step stubs
/vg run                   # Execute via Cucumber runner, sync results
/vg report                # Coverage gap analysis (risk-weighted)
/vg status                # Quick scenario coverage status
```

## Test Plan Format: YAML (Design Layer)
```yaml
feature: User Authentication
risk_level: high
scenarios:
  - name: "Successful login with valid credentials"
    type: happy_path
    risk: high
    risk_rationale: "Impact: 3, Frequency: 3, Consequence: 3, Detectability: 1. Average: 2.50 → high."
    techniques: [equivalence_partitioning]
    gherkin_ref: "features/auth/user-authentication.feature::Successful login with valid credentials"
    status: covered
    tags: [smoke, critical-path]
```

The YAML plan is intentionally lightweight — no input/expected data (that lives in Gherkin), no test implementation details. It focuses on risk, techniques, and coverage tracking.

## Output & Review
- **Interactive HTML report** — coverage gap analysis, example mapping visualization, decision table display, state transition diagrams
- Human can: approve/reject scenarios, adjust risk levels, add missing scenarios, export decisions as JSON
- For pass/fail execution results, use Cucumber's built-in reporting

## Runtime File Structure (created in user's project)
```
user-project/
├── .claude/skills/valid-guard/   # Skill definition (copied from this repo)
├── valid-guard/
│   ├── plans/                    # YAML test plans (version-controlled)
│   ├── reports/                  # Coverage reports (gitignored)
│   └── config.yaml               # Valid Guard config
├── features/                     # Gherkin .feature files (generated by /vg generate)
│   ├── auth/
│   │   ├── login.feature
│   │   └── steps/               # Step definitions
│   └── checkout/
│       └── ...
```

## Language Support
- **BDD framework**: Cucumber (multi-language)
  - Python: behave
  - JavaScript/TypeScript: cucumber-js
  - Java/Kotlin: cucumber-jvm
  - Ruby: cucumber
  - Go: godog
- Language auto-detection via `pyproject.toml`, `package.json`, `go.mod`, `pom.xml`, `build.gradle`, `Cargo.toml`
- YAML plan layer is language-agnostic; only `/vg generate` step definitions are language-specific

## Eval Strategy
- 30 eval cases sourced from a 187-case library (extracted from testing articles and best practices)
- Each eval run as independent agent with and without SKILL.md context
- Grading: rubric-based regex pattern matching with weighted scoring
- See `evals/RESULTS.md` for methodology, results, and known limitations
