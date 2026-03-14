# Valid Guard — Design Decisions

## Core Philosophy
- **TDD + Validation-Driven Development** — not just testing, but helping humans maintain control over AI-driven development. Validation-Driven Development means: define goals → review structured plan → verify results, keeping humans in the loop as AI writes code
- AI writes code too fast for humans to review line-by-line; the human's role is: define goals → review plan → verify results
- Current AI coding agents write lazy tests — a few tests and done. Valid Guard enforces systematic test design using software testing theory
- **Scenario coverage > code coverage** — care about covering important scenarios and critical paths, weighted by risk

## Name: Valid Guard

## Two Entry Points
1. **Greenfield** (`/vg plan`): From PRD/feature description → scenario analysis → test plan → test code
2. **Brownfield** (`/vg analyze`): From existing code → reverse-engineer scenarios → find coverage gaps
   - Target Level 3 depth (cross-function call chains, data flow, state changes) up to context window limits

## Test Design Layer (Core Differentiator)
AI auto-selects appropriate testing techniques based on heuristics:
- **Equivalence Partitioning**: when inputs have clear valid/invalid ranges
- **Boundary Value Analysis**: when numeric ranges, length limits, time constraints exist
- **Decision Table**: when multiple condition combinations affect outcomes
- **State Transition**: when objects have lifecycle/state flow
- **Pairwise/Combinatorial**: when parameter combinations explode (>3 params, >2 values each)
- Multiple techniques can apply to the same scenario

## Risk Assessment Dimensions
| Dimension | High | Medium | Low |
|---|---|---|---|
| Impact scope | Core business, payments, security | Secondary features, UX | Display-only, cosmetic |
| Usage frequency | Every user daily | Some users occasionally | Rarely triggered |
| Failure consequence | Data loss, security breach, money | Functional but workaround exists | Minor inconvenience |
| Detectability | Silent failure (user won't notice) | User notices but not severe | Immediately visible |

## Scenario Coverage Metric
```
Feature PRD
  └─ Epic / User Story
       └─ Scenario (via Example Mapping)
            ├─ Rule 1
            │    ├─ Example 1.1 (happy path) → [risk: high] → test_xxx ✅
            │    ├─ Example 1.2 (edge case)  → [risk: medium] → test_yyy ✅
            │    └─ Example 1.3 (boundary)   → [risk: high] → ❌ uncovered
            └─ Rule 2 ...
```
- Scenario coverage = covered scenarios / total scenarios
- Weighted version uses risk levels
- Also track traditional line-of-code coverage

## Slash Commands
```
/vg plan <description>    # Greenfield: natural language → test plan
/vg plan --prd <file>     # Greenfield: from PRD file
/vg analyze <path>        # Brownfield: analyze existing code
/vg review                # Open interactive HTML report for test plan review
/vg generate              # Generate test code from test plan
/vg run                   # Execute tests
/vg report                # Final coverage report (scenario + line)
/vg status                # Quick scenario coverage status
```

## Test Plan Format: YAML
```yaml
feature: User Authentication
risk_level: high
scenarios:
  - name: "Successful login with valid credentials"
    type: happy_path
    risk: high
    techniques: [equivalence_partitioning]
    examples:
      - input: { email: "valid@test.com", password: "Valid123!" }
        expected: { status: 200, token: "non-empty" }
    test_ref: "tests/auth/test_login.py::test_successful_login"
    status: covered
```

## Output & Review
- **Interactive HTML report** (priority) — collapsible structure, links, human review
- Human can: approve/reject scenarios, adjust risk levels, add missing scenarios, set priority, link to test code
- **Interaction model (MVP)**: HTML with interactive elements (checkbox, dropdown), export to JSON, AI reads JSON to update (Plan B)
- Example Mapping and Decision Table visualization included

## Runtime File Structure (created in user's project)
```
user-project/
├── .claude/skills/valid-guard/   # Skill definition (copied from this repo)
├── valid-guard/
│   ├── plans/                    # YAML test plans (version-controlled)
│   ├── reports/                  # HTML reports (gitignored)
│   └── config.yaml               # Valid Guard config
└── tests/                        # Generated test code
```

## Core Features
- /vg plan (Greenfield)
- /vg analyze (Brownfield)
- Test technique auto-selection
- Risk level annotation
- YAML test plan output
- Interactive HTML report
- /vg generate (test code generation)
- /vg run (test execution)
- Scenario coverage calculation
- Line coverage integration
- Example Mapping visualization
- Decision Table visualization

## Language Support
- MVP: Python + pytest
- Architecture: language-agnostic test plan layer + language detection at code gen (no plugin system needed, just detect pyproject.toml/package.json/go.mod)

## Eval Strategy
- 30 eval cases sourced from a 187-case library (extracted from testing articles and best practices)
- Each eval run as independent agent with and without SKILL.md context
- Grading: rubric-based regex pattern matching with weighted scoring
- See `evals/RESULTS.md` for methodology, results, and known limitations
