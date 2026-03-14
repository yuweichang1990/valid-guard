# Valid Guard

**AI-age test design intelligence for Claude Code**

---

## The Problem

AI writes code fast --- but tests are lazy.

When an AI coding agent generates a feature, it typically throws in a handful of tests and calls it done. There is no systematic test design, no risk-weighted coverage analysis, and no structured plan a human can review before test code is generated. The result: humans lose visibility into what is actually being tested, edge cases slip through, and "100% line coverage" masks gaping scenario gaps.

Current TDD-focused skills enforce a red-green-refactor *process*, but they do not address the *design* of the tests themselves. Writing tests first does not help if the tests are shallow.

## The Solution

Valid Guard brings **software testing theory** into AI-assisted development. It applies established techniques --- equivalence partitioning, boundary value analysis, decision tables, state transition testing, and pairwise combinatorics --- to systematically derive test scenarios before any test code is written.

The workflow is:

1. **Define** --- describe the feature or point at existing code
2. **Plan** --- Valid Guard produces a structured YAML test plan with risk-annotated scenarios
3. **Review** --- inspect and adjust via an interactive HTML report
4. **Generate** --- produce test code that maps 1:1 to the plan
5. **Verify** --- run tests and get a combined scenario + line coverage report

## Key Differentiators

| Aspect | Typical TDD Skill | Valid Guard |
|---|---|---|
| Focus | Process (red-green-refactor) | Test *design* (scenario completeness) |
| Coverage metric | Line/branch coverage | **Scenario coverage** weighted by risk |
| Test planning | None --- jumps straight to code | YAML test plan with risk levels and technique tags |
| Human review | Code review only | Interactive HTML report *before* code generation |
| Testing theory | Not applied | Equivalence partitioning, boundary value, decision tables, state transition, pairwise |
| Entry points | Greenfield only | Greenfield (`/vg plan`) **and** brownfield (`/vg analyze`) |

## Features

- **Greenfield planning** (`/vg plan`) --- from a natural-language description or PRD file, generate a comprehensive test plan using Example Mapping
- **Brownfield analysis** (`/vg analyze`) --- reverse-engineer scenarios from existing code, tracing cross-function call chains, data flow, and state changes up to Level 3 depth
- **Test technique auto-selection** --- AI picks the right technique(s) per scenario based on heuristics (ranges -> boundary value, multiple conditions -> decision table, lifecycle -> state transition, etc.)
- **Risk assessment** --- every scenario is annotated with a risk level (high/medium/low) across four dimensions: impact scope, usage frequency, failure consequence, and detectability
- **YAML test plans** --- machine-readable, version-controllable, human-reviewable test plan artifacts
- **Interactive HTML reports** --- collapsible scenario trees, approve/reject checkboxes, risk-level dropdowns, links to test code, Example Mapping and Decision Table visualizations
- **Test code generation** (`/vg generate`) --- produces test code (Python + pytest for MVP) with 1:1 mapping to plan scenarios
- **Test execution** (`/vg run`) --- runs the generated tests and collects results
- **Scenario coverage** (`/vg report`) --- combined metric: scenario coverage (weighted by risk) alongside traditional line coverage
- **Quick status** (`/vg status`) --- at-a-glance coverage summary without generating a full report

## Quick Start

### Installation

Valid Guard is a Claude Code skill. To install it in your project:

```bash
# Clone the repository into your Claude Code skills directory
git clone https://github.com/user/valid-guard.git .claude/skills/valid-guard
```

Or, if you are using [Skills MP](https://skillsmp.com) or another skills marketplace:

```bash
npx skills add valid-guard
```

After installation, restart Claude Code. The `/vg` commands will be available in your session.

### Prerequisites

- Claude Code v2.1.3 or later (skills support required)
- Python 3.10+ and pytest (for MVP test execution)

## Usage

### Greenfield: Create a test plan from a description

```
/vg plan "User authentication with email and password, including login, logout, password reset, and account lockout after 5 failed attempts"
```

Or from a PRD file:

```
/vg plan --prd docs/auth-feature.md
```

This produces a YAML test plan in `valid-guard/plans/` and opens an interactive HTML report.

### Brownfield: Analyze existing code

```
/vg analyze src/services/payment.py
```

Valid Guard reverse-engineers scenarios from the existing code, identifies coverage gaps, and generates a test plan for uncovered paths.

### Review the test plan

```
/vg review
```

Opens the interactive HTML report where you can:
- Approve or reject individual scenarios
- Adjust risk levels
- Add missing scenarios
- Link scenarios to existing test code

### Generate test code

```
/vg generate
```

Produces pytest test files in your project's `tests/` directory, with each test function mapped to a plan scenario via `test_ref`.

### Run tests

```
/vg run
```

Executes the generated tests and collects pass/fail results.

### Full coverage report

```
/vg report
```

Generates a combined report showing:
- Scenario coverage (covered / total, weighted by risk)
- Line-of-code coverage
- Uncovered high-risk scenarios highlighted

### Quick status check

```
/vg status
```

Prints a one-line summary: `Scenario coverage: 18/23 (78%) | High-risk uncovered: 2 | Line coverage: 85%`

## Architecture

```mermaid
flowchart TD
    subgraph "User Input"
        A[Natural Language / PRD]
        B[Existing Code]
    end

    subgraph "Valid Guard Core"
        C["/vg plan (Greenfield)"]
        D["/vg analyze (Brownfield)"]
        E["Test Design Engine"]
        F["Risk Assessor"]
        G["YAML Test Plan"]
    end

    subgraph "Test Design Techniques"
        T1["Equivalence Partitioning"]
        T2["Boundary Value Analysis"]
        T3["Decision Table"]
        T4["State Transition"]
        T5["Pairwise / Combinatorial"]
    end

    subgraph "Output & Review"
        H["Interactive HTML Report"]
        I["/vg generate → Test Code"]
        J["/vg run → Execution"]
        K["/vg report → Coverage"]
    end

    A --> C
    B --> D
    C --> E
    D --> E
    E --> T1 & T2 & T3 & T4 & T5
    T1 & T2 & T3 & T4 & T5 --> F
    F --> G
    G --> H
    G --> I
    I --> J
    J --> K
    H -.->|"human edits"| G
```

## Test Plan YAML Format

Test plans are stored in `valid-guard/plans/` as YAML files. Each plan follows this structure:

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

  - name: "Login fails after 5 consecutive bad passwords"
    type: edge_case
    risk: high
    techniques: [boundary_value_analysis, state_transition]
    examples:
      - input: { email: "user@test.com", attempts: 5 }
        expected: { status: 423, locked: true }
    test_ref: null
    status: uncovered
```

### Fields

| Field | Description |
|---|---|
| `feature` | Feature name |
| `risk_level` | Overall feature risk (`high`, `medium`, `low`) |
| `scenarios[].name` | Human-readable scenario description |
| `scenarios[].type` | `happy_path`, `edge_case`, `error_case`, `boundary`, `security` |
| `scenarios[].risk` | Scenario-level risk |
| `scenarios[].techniques` | Testing techniques applied |
| `scenarios[].examples` | Concrete input/expected pairs |
| `scenarios[].test_ref` | Link to generated test function (null if uncovered) |
| `scenarios[].status` | `covered`, `uncovered`, `approved`, `rejected` |

## Scenario Coverage Metric

Valid Guard introduces **scenario coverage** as a first-class metric:

```
Feature PRD
  └── Epic / User Story
       └── Scenario (via Example Mapping)
            ├── Rule 1
            │    ├── Example 1.1 (happy path)  → [risk: high]   → test_xxx ✓
            │    ├── Example 1.2 (edge case)   → [risk: medium] → test_yyy ✓
            │    └── Example 1.3 (boundary)    → [risk: high]   → ✗ uncovered
            └── Rule 2 ...
```

- **Scenario coverage** = covered scenarios / total scenarios
- **Weighted scenario coverage** = sum of covered risk weights / sum of total risk weights
- Both metrics are reported alongside traditional line coverage

## Interactive HTML Report

The HTML report provides a visual, interactive view of the test plan:

- Collapsible scenario tree organized by feature and rule
- Approve/reject toggles per scenario
- Risk level dropdowns for adjustment
- Example Mapping visualization
- Decision Table visualization
- Links to generated test code
- Export to JSON for AI round-trip updates

For a complete end-to-end example, see the [demo/](demo/) directory which includes a sample YAML test plan for a user registration feature.

## Risk Assessment

Every scenario is assessed across four dimensions:

| Dimension | High | Medium | Low |
|---|---|---|---|
| Impact scope | Core business, payments, security | Secondary features, UX | Display-only, cosmetic |
| Usage frequency | Every user daily | Some users occasionally | Rarely triggered |
| Failure consequence | Data loss, security breach, money | Functional but workaround exists | Minor inconvenience |
| Detectability | Silent failure (user won't notice) | User notices but not severe | Immediately visible |

## File Structure

```
project-root/
├── .claude/
│   └── skills/
│       └── valid-guard/        # Skill definition (SKILL.md)
├── .github/                    # Issue templates, PR template, CI workflow
├── valid-guard/
│   ├── plans/                  # Test plans (YAML) — version controlled
│   ├── reports/                # Interactive HTML reports — gitignored
│   ├── templates/              # Report templates — version controlled
│   ├── schema/                 # YAML schema definitions
│   ├── examples/               # Example test plans
│   └── config.yaml             # Valid Guard configuration
├── evals/                      # Eval suite (30 cases, grading, reports)
├── demo/                       # End-to-end demo with sample YAML plan
├── tests/                      # Generated test code (project's test dir)
├── DESIGN.md                   # Design decisions document
├── CONTRIBUTING.md             # Contributor guide
├── CHANGELOG.md                # Release history
└── README.md                   # This file
```

## Benchmark Results

Valid Guard was evaluated on **30 eval cases** across 11 categories, comparing outputs **with skill** (SKILL.md loaded) vs **without skill** (bare LLM).

### Accuracy (30 evals, 11 categories)

| Dimension | with_skill | without_skill | Delta | What it measures |
|---|---|---|---|---|
| **Content** (test design quality) | **100.0%** | **89.9%** | **+10.1%** | Domain knowledge, technique application, scenario completeness |
| **Structural** (schema compliance) | **99.2%** | **15.0%** | **+84.2%** | Valid Guard YAML schema fields (risk_rationale, test_ref, metadata, etc.) |

> The bare LLM already scores ~90% on test design content. The skill's primary value is **structural enforcement** --- ensuring every plan includes risk rationale (4 dimensions), technique rationale, state transitions, decision tables, example mapping, and full traceability metadata.

#### Content Score by Category

| Category | with_skill | without_skill | Content Delta |
|---|---|---|---|
| Security | 100.0% | 54.5% | **+45.5%** |
| Brownfield | 100.0% | 74.6% | **+25.4%** |
| Adversarial | 100.0% | 84.5% | **+15.5%** |
| Code Gen | 100.0% | 87.3% | **+12.7%** |
| Concurrency | 100.0% | 90.9% | **+9.1%** |
| TDD Best Practices | 100.0% | 90.9% | **+9.1%** |
| Risk Assessment | 100.0% | 90.9% | **+9.1%** |
| State Transition | 100.0% | 92.4% | **+7.6%** |
| Domain Specific | 100.0% | 92.7% | **+7.3%** |
| Correctness | 100.0% | 98.2% | **+1.8%** |
| Completeness | 100.0% | 100.0% | **+0.0%** |

#### Structural Score by Category (plan-type evals only)

| Category | with_skill | without_skill | Structural Delta |
|---|---|---|---|
| All plan-type evals (22) | 99.2% | 15.0% | **+84.2%** |

> Without the skill, 90% of structural check failures come from missing schema fields (risk_rationale, technique_rationale, test_ref, status, priority, tags, example_mapping, metadata). The bare LLM produces good content but does not know the Valid Guard schema.

### Token Efficiency

| Metric | with_skill | without_skill | Ratio |
|---|---|---|---|
| Avg tokens / eval | ~50,000 | ~23,000 | 2.1x |
| Avg duration / eval | ~4 min | ~2 min | 2.1x |
| Content accuracy | 100.0% | 89.9% | --- |
| Structural accuracy | 99.2% | 15.0% | --- |

**Analysis**: The skill uses **2.1x more tokens** than bare LLM, primarily for reading SKILL.md (~500 lines) and generating structured YAML output with all mandatory schema fields. The token overhead is structural --- it reflects the completeness of the output (risk rationale with 4 dimensions, technique rationale, state transition tables, decision tables, example mapping, metadata), not inefficiency.

**Key insight**: The bare LLM already scores ~90% on content (test design quality), but only 15% on structural compliance. The skill's primary value is enforcing the Valid Guard schema --- ensuring traceability, risk assessment, and formal technique application in every test plan. The content delta (+10.1%) is modest; the structural delta (+84.2%) is where the skill earns its token investment.

### Methodology

- 30 eval cases: 28 from a 187-case eval library, 2 custom with real Python code fixtures
- 11 categories: correctness, completeness, brownfield, codegen, adversarial, state_transition, domain_specific, tdd_best_practices, risk_assessment, concurrency, security
- Grading: rubric-based pattern matching with weighted scoring (content checks + structural checks)
- Content/structural score separation: content = test design quality, structural = Valid Guard YAML schema compliance
- Each eval run as independent agent with or without SKILL.md context
- Full results: [`evals/RESULTS.md`](evals/RESULTS.md)
- Interactive report: [`evals/report.html`](evals/report.html)

### Limitations and Caveats

- **Single run**: Each eval was run once, not averaged over multiple runs. LLM outputs are non-deterministic, so scores may vary by a few percentage points across runs.
- **Pattern-matching grading**: Scores are based on regex pattern matching against rubric criteria, not human expert judgment. This can both miss valid content (false negative) and over-credit superficial matches (false positive).
- **Code generation coverage**: Only 2 of 30 evals test `/vg generate` output. Generated test code was not executed for correctness verification. Code generation quality is an area for future evaluation.
- **Self-evaluated**: The benchmark was designed and graded by the same team that built the skill. Independent third-party evaluation is a goal for future releases.

## Language Support

- **MVP**: Python + pytest
- **Architecture**: The test plan layer is language-agnostic. Code generation detects your project's language by checking for `pyproject.toml`, `package.json`, `go.mod`, etc.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, eval suite instructions, code conventions, and the pull request process.

## License

[MIT](LICENSE) --- Copyright 2026
