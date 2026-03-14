# Eval Results — Valid Guard

## What This Benchmark Measures

This benchmark evaluates two dimensions of value:

1. **Content improvement** (with_skill vs without_skill): Does the skill cause the LLM to include more testing concepts (techniques, edge cases, risk analysis)? Measured by keyword and pattern matching against rubric criteria. A high content score means the output mentions relevant terms — it does not guarantee depth of analysis or practical usefulness.

2. **Structured, human-readable output** (schema compliance): Does the skill reliably produce test plans in its own YAML schema (risk_rationale, technique_rationale, test_ref, status, priority, tags, example_mapping, metadata)? This is an internal quality metric — it confirms the skill produces reviewable, structured output that humans can inspect before code generation. It is NOT compared against bare LLM output (which has no knowledge of the schema).

- **What this benchmark does NOT measure**:
  - Actual test code quality or correctness (generated code is not executed)
  - Bug-finding effectiveness in real codebases
  - Developer time savings or productivity impact
  - Comparison to alternative prompting approaches or competing tools
  - Semantic understanding of test design (only pattern presence)

## Summary (30 evals, 11 categories)

### Content Score: with_skill vs without_skill

| Metric | with_skill | without_skill | Delta |
|---|---|---|---|
| **Content** (keyword/concept presence) | **100.0%** | **89.9%** | **+10.1%** |

> The bare LLM already scores ~90% on test design content. The skill adds +10.1% improvement, concentrated in security (+45.5%), brownfield (+25.4%), and adversarial (+15.5%) categories.
>
> The 100% with_skill content score across all evals suggests the rubric patterns are lenient. These scores indicate keyword/concept presence, not depth of analysis. A more rigorous evaluation would require human expert review.

### Schema Compliance: Internal Quality Metric

Schema compliance measures whether the skill reliably produces output conforming to its own YAML schema. This is an **internal self-check**, not a comparative benchmark — the bare LLM has no knowledge of the Valid Guard schema, so comparing against it would be circular.

| Metric | Score |
|---|---|
| Schema compliance rate (22 plan-type evals) | **99.2%** |

> 21 of 22 plan-type evals achieved 100% schema compliance. The single exception (P3-02) scored 92% due to a missing field. Guidance evals (adversarial, risk_assessment, security, brownfield-redundancy) have no schema checks — their content score is the total score.

## Content Score by Category

| Category | with_skill | without_skill | Content Delta | Evals |
|---|---|---|---|---|
| Security | 100.0% | 54.5% | **+45.5%** | P3-27 |
| Brownfield | 100.0% | 74.6% | **+25.4%** | P3-05, P3-06 |
| Adversarial | 100.0% | 84.5% | **+15.5%** | P3-09, P3-10, P3-20 |
| Code Gen | 100.0% | 87.3% | **+12.7%** | P3-07, P3-08 |
| Concurrency | 100.0% | 90.9% | **+9.1%** | P3-25, P3-26 |
| TDD Best Practices | 100.0% | 90.9% | **+9.1%** | P3-17 |
| Risk Assessment | 100.0% | 90.9% | **+9.1%** | P3-23, P3-24, P3-29 |
| State Transition | 100.0% | 92.4% | **+7.6%** | P3-11, P3-12, P3-13, P3-21, P3-22 |
| Domain Specific | 100.0% | 92.7% | **+7.3%** | P3-14, P3-15, P3-16, P3-28, P3-30 |
| Correctness | 100.0% | 98.2% | **+1.8%** | P3-01, P3-02, P3-18, P3-19 |
| Completeness | 100.0% | 100.0% | **+0.0%** | P3-03, P3-04 |


## Per-Eval Detail (sorted by content delta)

| Eval | Category | Content (w/wo) | Content Delta |
|---|---|---|---|
| P3-27 Security Payloads | security | 100% / 55% | **+45.5%** |
| P3-06 Redundancy | brownfield | 100% / 67% | **+33.3%** |
| P3-10 Misconception | adversarial | 100% / 73% | **+27.3%** |
| P3-08 Fix Weak Assert | codegen | 100% / 80% | **+20.0%** |
| P3-11 ATM PIN ST | state_transition | 100% / 80% | **+20.0%** |
| P3-12 Order Lifecycle | state_transition | 100% / 82% | **+18.2%** |
| P3-25 Inventory Race | concurrency | 100% / 82% | **+18.2%** |
| P3-28 Payment Recovery | domain_specific | 100% / 82% | **+18.2%** |
| P3-30 Multi-currency | domain_specific | 100% / 82% | **+18.2%** |
| P3-24 Tax Filing Risk | risk_assessment | 100% / 82% | **+18.2%** |
| P3-05 Brownfield Gap | brownfield | 100% / 82% | **+17.6%** |
| P3-20 AI Trust | adversarial | 100% / 90% | **+10.0%** |
| P3-09 Anti-pattern | adversarial | 100% / 91% | **+9.1%** |
| P3-17 Throttle TDD | tdd_best_practices | 100% / 91% | **+9.1%** |
| P3-29 Regression Prio | risk_assessment | 100% / 91% | **+9.1%** |
| P3-02 BVA Correctness | correctness | 100% / 93% | **+7.1%** |
| P3-07 Codegen Runnable | codegen | 100% / 95% | **+5.3%** |
| P3-01 DT Correctness | correctness | 100% / 100% | **+0.0%** |
| P3-03 Conway Complete | completeness | 100% / 100% | **+0.0%** |
| P3-04 Amigos Complete | completeness | 100% / 100% | **+0.0%** |
| P3-13 Ticket Booking | state_transition | 100% / 100% | **+0.0%** |
| P3-14 Double Payment | domain_specific | 100% / 100% | **+0.0%** |
| P3-15 Login Lockout | domain_specific | 100% / 100% | **+0.0%** |
| P3-16 OTP Verification | domain_specific | 100% / 100% | **+0.0%** |
| P3-18 Loan Approval DT | correctness | 100% / 100% | **+0.0%** |
| P3-19 Vending Machine | correctness | 100% / 100% | **+0.0%** |
| P3-21 Shopping Cart | state_transition | 100% / 100% | **+0.0%** |
| P3-22 Airport Kiosk | state_transition | 100% / 100% | **+0.0%** |
| P3-26 Payment GW Load | concurrency | 100% / 100% | **+0.0%** |
| P3-23 Insurance FMEA | risk_assessment | 100% / 100% | **+0.0%** |

## Key Findings

### Where skill adds most content value

Categories ranked by content delta (keyword/concept presence improvement):
1. **Security** (+45.5%): The skill enforces systematic attack payload specification structure that the bare LLM omits.
2. **Brownfield** (+25.4%): Gap detection and redundancy analysis benefit from the skill's structured analysis framework.
3. **Adversarial** (+15.5%): Anti-pattern detection and misconception identification improve with explicit technique guidance.
4. **Code Gen** (+12.7%): Generated test code includes more testing concepts when guided by the skill.

### Where bare LLM already performs well

- **Completeness** (+0.0%): The bare LLM naturally produces comprehensive test plans for well-scoped problems.
- **Correctness** (+1.8%): Decision table and BVA correctness are near-equal with or without the skill.
- **Risk Assessment** (+9.1%): FMEA and risk prioritization are areas where the bare LLM already excels — these evals use guidance mode with no schema requirements.

### The skill's primary value: human-readable test design

The +10.1% content improvement is modest — the bare LLM already knows most testing concepts. The skill's greater contribution is **structured, human-readable output**: every test plan includes risk rationale (4 dimensions), technique rationale, example mapping, decision tables, status tracking, and priority — in a consistent YAML format that humans can review before code generation.

This structured format (99.2% schema compliance across 22 plan-type evals) enables workflows that unstructured LLM output cannot support:
- **Pre-code review**: Teams inspect and approve test scenarios before any code is written
- **Risk-based prioritization**: Scenarios are annotated with risk levels, enabling informed tradeoffs
- **Traceability**: Each scenario links to its generated test via `test_ref`, maintaining plan-to-code mapping
- **Version control**: YAML test plans are diffable, reviewable in PRs, and machine-parseable

## SKILL.md Refinements During Eval Development

- Added **Advisory Mode** section for review/evaluation questions.
- Added **Rule #10**: All schema fields mandatory.
- Updated `test_ref` schema comment.
- Broadened grading patterns for p3-15 (login lockout), p3-27 (SQL injection), p3-29 (regression priority) to reduce false negatives.

## Methodology

- 30 eval cases across 11 categories
- 28 sourced from 187-case eval library, 2 custom (P3-05 brownfield with real code, P3-20 adversarial AI trust)
- 11 categories: correctness, completeness, brownfield, codegen, adversarial, state_transition, domain_specific, tdd_best_practices, risk_assessment, concurrency, security
- Grading: rubric-based pattern matching with weighted scoring (content checks + schema compliance checks)
- Each eval run as independent agent with (with_skill) or without (without_skill) SKILL.md context
- Content/schema compliance score separation: content = test design keyword/concept presence, schema compliance = Valid Guard YAML field presence
- HTML report: `report.html`

## Known Limitations

- **Single run per eval (no variance)**: Results are from a single execution, not averaged. LLM non-determinism may cause scores to vary by several percentage points across runs. Without multiple runs, statistical confidence cannot be established.
- **Pattern-matching grading (not semantic)**: Rubric checks use regex patterns, not human expert review. This risks false negatives (valid content missed by patterns) and false positives (superficial keyword matches credited as understanding). A pattern match for "boundary value" does not confirm the output actually applies BVA correctly.
- **Self-evaluated**: The benchmark was designed, implemented, and graded by the skill's authors. There is no independent verification. Independent evaluation is a goal for future releases.
- **Comparison is "skill vs no instructions" (not "skill vs alternative prompts")**: The without_skill baseline uses a bare LLM with no special prompting. A fairer comparison would be against alternative prompting strategies (e.g., "generate a test plan in YAML with risk analysis") or competing tools. The current comparison overstates the skill's unique value.
- **Schema compliance is a self-check**: The skill defines the YAML schema, so outputs produced with the skill naturally conform to it. The 99.2% schema compliance rate confirms the skill reliably produces its own format — it is not a comparative quality signal against bare LLM output.
- **Code generation not validated**: Only 2 of 30 evals (P3-07, P3-08) test `/vg generate`. Generated code was not executed for correctness. Code generation quality is essentially unmeasured.
- **Content score ceiling effect**: 100% content scores across all 30 evals with the skill suggests rubric criteria are too easy to satisfy. This limits the benchmark's ability to differentiate between adequate and excellent outputs.
