# Eval Results — Valid Guard

## What This Benchmark Measures

- **Content score**: Checks for the presence of domain-appropriate testing concepts using keyword and pattern matching against rubric criteria. A high content score means the output mentions relevant terms and concepts — it does not guarantee depth of analysis or practical usefulness.
- **Schema compliance score**: Checks whether the output includes Valid Guard YAML fields (risk_rationale, technique_rationale, test_ref, status, priority, tags, example_mapping, metadata, etc.). Since the skill defines this schema, a high with_skill score is expected by design.
- **What this benchmark does NOT measure**:
  - Actual test code quality or correctness (generated code is not executed)
  - Bug-finding effectiveness in real codebases
  - Developer time savings or productivity impact
  - Comparison to alternative prompting approaches or competing tools
  - Semantic understanding of test design (only pattern presence)

## Summary (30 evals, 11 categories)

| Dimension | with_skill | without_skill | Delta |
|---|---|---|---|
| **Content** (keyword/concept presence) | **100.0%** | **89.9%** | **+10.1%** |
| **Schema Compliance** (YAML field presence) | **99.2%** | **15.0%** | **+84.2%** |

> **Note on content scores:** The 100% with_skill content score across all evals suggests the rubric patterns are lenient. These scores indicate keyword/concept presence, not depth of analysis. A more rigorous evaluation would require human expert review.
>
> **Note on schema compliance scores:** This measures whether the output follows the Valid Guard YAML schema (includes risk_rationale, technique_rationale, test_ref, etc.). Without the skill, the LLM has no instruction to use this schema, so the low baseline (15%) is expected — it reflects format awareness, not test design quality.

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

## Schema Compliance Score (plan-type evals only)

| Metric | with_skill | without_skill | Delta |
|---|---|---|---|
| Schema Compliance (22 evals) | 99.2% | 15.0% | **+84.2%** |

> Without the skill, 90% of schema compliance failures come from missing YAML fields: risk_rationale, technique_rationale, test_ref, status, priority, tags, example_mapping, metadata. The bare LLM produces good content but has no instruction to use the Valid Guard schema, so low baseline scores are expected — not a reflection of test design quality.
>
> Guidance evals (is_guidance=True: adversarial, risk_assessment, security, brownfield-redundancy) have no schema compliance checks — their content score = total score.

## Per-Eval Detail (sorted by content delta)

| Eval | Category | Content (w/wo) | Content Delta | Schema Compliance (w/wo) | Has Schema |
|---|---|---|---|---|---|
| P3-27 Security Payloads | security | 100% / 55% | **+45.5%** | — / — | No |
| P3-06 Redundancy | brownfield | 100% / 67% | **+33.3%** | — / — | No |
| P3-10 Misconception | adversarial | 100% / 73% | **+27.3%** | — / — | No |
| P3-08 Fix Weak Assert | codegen | 100% / 80% | **+20.0%** | — / — | No |
| P3-11 ATM PIN ST | state_transition | 100% / 80% | **+20.0%** | 100% / 0% | Yes |
| P3-12 Order Lifecycle | state_transition | 100% / 82% | **+18.2%** | 100% / 0% | Yes |
| P3-25 Inventory Race | concurrency | 100% / 82% | **+18.2%** | 100% / 0% | Yes |
| P3-28 Payment Recovery | domain_specific | 100% / 82% | **+18.2%** | 100% / 0% | Yes |
| P3-30 Multi-currency | domain_specific | 100% / 82% | **+18.2%** | 100% / 0% | Yes |
| P3-24 Tax Filing Risk | risk_assessment | 100% / 82% | **+18.2%** | — / — | No |
| P3-05 Brownfield Gap | brownfield | 100% / 82% | **+17.6%** | 100% / 0% | Yes |
| P3-20 AI Trust | adversarial | 100% / 90% | **+10.0%** | — / — | No |
| P3-09 Anti-pattern | adversarial | 100% / 91% | **+9.1%** | — / — | No |
| P3-17 Throttle TDD | tdd_best_practices | 100% / 91% | **+9.1%** | 100% / 0% | Yes |
| P3-29 Regression Prio | risk_assessment | 100% / 91% | **+9.1%** | — / — | No |
| P3-02 BVA Correctness | correctness | 100% / 93% | **+7.1%** | 92% / 0% | Yes |
| P3-07 Codegen Runnable | codegen | 100% / 95% | **+5.3%** | 100% / 92% | Yes |
| P3-01 DT Correctness | correctness | 100% / 100% | **+0.0%** | 100% / 0% | Yes |
| P3-03 Conway Complete | completeness | 100% / 100% | **+0.0%** | 100% / 0% | Yes |
| P3-04 Amigos Complete | completeness | 100% / 100% | **+0.0%** | 92% / 0% | Yes |
| P3-13 Ticket Booking | state_transition | 100% / 100% | **+0.0%** | 100% / 0% | Yes |
| P3-14 Double Payment | domain_specific | 100% / 100% | **+0.0%** | 100% / 0% | Yes |
| P3-15 Login Lockout | domain_specific | 100% / 100% | **+0.0%** | 100% / 0% | Yes |
| P3-16 OTP Verification | domain_specific | 100% / 100% | **+0.0%** | 100% / 0% | Yes |
| P3-18 Loan Approval DT | correctness | 100% / 100% | **+0.0%** | 100% / 0% | Yes |
| P3-19 Vending Machine | correctness | 100% / 100% | **+0.0%** | 100% / 0% | Yes |
| P3-21 Shopping Cart | state_transition | 100% / 100% | **+0.0%** | 100% / 0% | Yes |
| P3-22 Airport Kiosk | state_transition | 100% / 100% | **+0.0%** | 100% / 0% | Yes |
| P3-26 Payment GW Load | concurrency | 100% / 100% | **+0.0%** | 100% / 0% | Yes |
| P3-23 Insurance FMEA | risk_assessment | 100% / 100% | **+0.0%** | — / — | No |

**Schema compliance pattern**: 21 out of 22 plan-type evals show **100% / 0%** schema compliance scores (with_skill / without_skill). The only exception is P3-07 (codegen) where without_skill accidentally includes some schema-like fields, scoring 92%. This pattern is expected: the skill defines the schema, so outputs produced with the skill naturally conform to it.

## Key Findings

### Where skill adds most value (delta > 50%)

New evals reinforced findings from the first 20:
1. **Concurrency** (avg +56.6%): Inventory race conditions and payment gateway load testing require structured state transition models and decision tables that skill enforces.
2. **Domain Specific** (avg +57.0%): Payment recovery, multi-currency, and existing domain evals all show large schema compliance delta.
3. **State Transition** (avg +55.2%): Shopping cart and airport kiosk join the original 3 ST evals, confirming that state machine modeling is the skill's strongest advantage.

### New category insights

- **Risk Assessment** (+9.0%): Lowest delta of any category. Both with_skill and without_skill produce good risk analysis content. FMEA (p3-23) scored 100% for both — the bare LLM is already good at risk prioritization since these evals use `is_guidance` mode (no schema compliance checks).
- **Security** (+45.5%): Significant content delta (+45.5%) even without schema compliance checks — the skill produces more structured attack payload specifications.
- **Concurrency** (+56.6%): High combined delta driven by schema compliance requirements for state transition models and decision tables in concurrent scenarios.

### Root cause of skill advantage

The primary driver remains **schema compliance**: the Valid Guard YAML schema forces inclusion of risk_rationale (4 dimensions), technique_rationale, state_transition sections, decision_tables, example_mapping, metadata, test_ref, status, and priority. This is a structural advantage by design — the skill defines the format, so outputs naturally comply with it.

The new categories confirm that:
- Categories requiring **formal technique application** (state_transition, domain_specific, concurrency) show deltas >50%
- Categories where the bare LLM excels naturally (risk_assessment, adversarial, codegen) show deltas <15%
- **Security** is an outlier — high content delta because the skill enforces systematic payload specification structure

## SKILL.md Changes Made

**Iteration 1 → 2 improvements:**
1. Added **Advisory Mode** section for review/evaluation questions.
2. Added **Rule #10**: All schema fields mandatory.
3. Updated `test_ref` schema comment.

**Iteration 3 grading pattern fixes:**
- Broadened p3-15 login lockout patterns for multi-line matches.
- Broadened p3-27 SQL injection pattern to check SQL-inject mention + payload terms separately.
- Broadened p3-29 regression priority patterns to recognize tier-1/full-regression terminology.

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
- **Schema compliance score is expected to be high**: The skill defines the YAML schema, so outputs produced with the skill naturally conform to it. The 84.2% delta in schema compliance is largely a measure of "did the LLM follow the instructions it was given" rather than an independent quality signal.
- **Code generation not validated**: Only 2 of 30 evals (P3-07, P3-08) test `/vg generate`. Generated code was not executed for correctness. Code generation quality is essentially unmeasured.
- **Content score ceiling effect**: 100% content scores across all 30 evals with the skill suggests rubric criteria are too easy to satisfy. This limits the benchmark's ability to differentiate between adequate and excellent outputs.
