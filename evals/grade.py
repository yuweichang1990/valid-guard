"""
Grading script for Valid Guard evals.
Uses rubric-based scoring on 5 quality dimensions (1-5 scale)
plus binary pass/fail checks for specific criteria.

Usage: python grade.py <iteration-dir>
       python grade.py baseline
"""
import json
import sys
import os
import re
from pathlib import Path


# ── Quality dimension weights ──
DIMENSIONS = {
    "correctness": 0.25,
    "completeness": 0.25,
    "structure": 0.20,
    "actionability": 0.15,
    "insight": 0.15,
}

# ── Eval definitions with automated checks ──
EVAL_CHECKS = {
    "p3-01-dt-correctness": {
        "name": "Decision Table for max(x,y,z)",
        "category": "correctness",
        "checks": [
            {"text": "Contains decision_table section", "patterns": [r"(?i)decision.{0,5}table"], "weight": 1},
            {"text": "Lists conditions c1-c9 or equivalent", "patterns": [r"(?i)(c[1-9]|x\s*>=?\s*1|x\s*<=?\s*300|y\s*>=?\s*1|y\s*<=?\s*300|z\s*>=?\s*1|z\s*<=?\s*300|x\s*>\s*y|x\s*>\s*z|y\s*>\s*z)"], "min_matches_from_output": 6, "weight": 2},
            {"text": "Actions include x_largest/y_largest/z_largest", "patterns": [r"(?i)x.{0,5}largest", r"(?i)y.{0,5}largest", r"(?i)z.{0,5}largest"], "min_matches": 3, "weight": 2},
            {"text": "Includes invalid_input action", "patterns": [r"(?i)(invalid|out.of.range|validation.fail)"], "weight": 1},
            {"text": "Has at least 10 rules", "patterns": [r"(?i)(rule|scenario|case)"], "count_min": 10, "weight": 2},
            {"text": "Handles equal values", "patterns": [r"(?i)(equal|same|tie|x\s*=\s*y|x\s*==\s*y)"], "weight": 1},
            {"text": "Includes boundary values 1 and 300", "patterns": [r"\b1\b.*\b300\b|\b300\b.*\b1\b", r"(?i)boundary"], "weight": 1},
            {"text": "Has concrete numeric examples", "patterns": [r"\b\d{2,3}\b"], "count_min": 5, "weight": 1},
        ],
        "structural_checks": True,
    },
    "p3-02-bva-correctness": {
        "name": "BVA for isEligible(age, income)",
        "category": "correctness",
        "checks": [
            {"text": "Tests age=17 (below boundary)", "patterns": [r"\b17\b"], "weight": 2},
            {"text": "Tests age=18 (exact boundary)", "patterns": [r"\b18\b"], "weight": 2},
            {"text": "Tests income=30000 (boundary where > fails)", "patterns": [r"30000"], "weight": 2},
            {"text": "Tests income=30001 (just above boundary)", "patterns": [r"30001"], "weight": 2},
            {"text": "Uses equivalence partitioning", "patterns": [r"(?i)(equivalence.{0,5}partition|EP\b)"], "weight": 1},
            {"text": "Uses boundary value analysis", "patterns": [r"(?i)(boundary.{0,5}value|BVA\b)"], "weight": 1},
            {"text": "Tests both conditions independently", "patterns": [r"(?i)(independen|isolat|each.{0,10}condition|condition.{0,10}separately)"], "weight": 1},
            {"text": "Identifies >= vs > distinction", "patterns": [r"(?i)(>=\s*.*>\s|greater.{0,10}equal.*greater|>=.*differs.*>)"], "weight": 2},
            {"text": "Has 4+ equivalence partitions", "patterns": [r"(?i)(partition|class|category|group)"], "count_min": 4, "weight": 1},
        ],
        "structural_checks": True,
    },
    "p3-03-conway-completeness": {
        "name": "Conway's Game of Life completeness",
        "category": "completeness",
        "checks": [
            {"text": "Alive + 2 neighbors → survives", "patterns": [r"(?i)(alive|living).{0,30}2.{0,20}(surviv|stay|live)"], "weight": 2},
            {"text": "Alive + 3 neighbors → survives", "patterns": [r"(?i)(alive|living).{0,30}3.{0,20}(surviv|stay|live)"], "weight": 2},
            {"text": "Alive + 0-1 neighbors → dies (underpopulation)", "patterns": [r"(?i)(underpopulation|under.population|loneli|isolat|0.{0,10}neighbor|1.{0,10}neighbor.{0,20}die)"], "weight": 2},
            {"text": "Alive + 4+ neighbors → dies (overcrowding)", "patterns": [r"(?i)(overcrowd|over.crowd|overpopulat|4.{0,20}(die|dead)|too.many)"], "weight": 2},
            {"text": "Dead + 3 neighbors → becomes alive", "patterns": [r"(?i)(dead|empty).{0,30}3.{0,20}(alive|born|reproduc|birth)"], "weight": 2},
            {"text": "Dead + non-3 neighbors → stays dead", "patterns": [r"(?i)(dead.{0,30}(stay|remain)|not.{0,10}3.{0,20}(stay|remain).{0,10}dead)"], "weight": 1},
            {"text": "Uses decision table for state x count", "patterns": [r"(?i)decision.{0,5}table"], "weight": 1},
            {"text": "Uses BVA on neighbor count", "patterns": [r"(?i)(boundary|BVA)"], "weight": 1},
            {"text": "Tests all neighbor counts 0-8", "patterns": [r"\b0\b", r"\b1\b", r"\b2\b", r"\b3\b", r"\b4\b", r"\b8\b"], "min_matches": 5, "weight": 2},
            {"text": "Includes edge cases: 0 (isolation) and 8 (max)", "patterns": [r"\b0\b.{0,50}(isol|lone|no.neigh)", r"\b8\b.{0,50}(max|all|overcrowd)"], "weight": 1},
        ],
        "structural_checks": True,
    },
    "p3-04-amigos-completeness": {
        "name": "Three Amigos purchase order",
        "category": "completeness",
        "checks": [
            {"text": "Example mapping with story/rules/examples", "patterns": [r"(?i)example.{0,5}mapping", r"(?i)(story|user.story):", r"(?i)rule"], "min_matches": 2, "weight": 2},
            {"text": "Approval threshold with dollar amounts", "patterns": [r"\$\d+|\d+.{0,5}(dollar|USD|amount|threshold)"], "weight": 2},
            {"text": "Multi-level approval for high-value orders", "patterns": [r"(?i)(multi.{0,5}level|dual|two.{0,10}approv|escalat|senior|manager)"], "weight": 2},
            {"text": "Given-When-Then scenarios", "patterns": [r"(?i)(given|when|then)"], "count_min": 3, "weight": 1},
            {"text": "Vendor notification verification", "patterns": [r"(?i)(vendor|supplier).{0,20}(notif|email|alert)"], "weight": 2},
            {"text": "Accounting queue/processing", "patterns": [r"(?i)(account|payment).{0,20}(queue|process|trigger)"], "weight": 1},
            {"text": "Rejection flow", "patterns": [r"(?i)(reject|deny|decline|disapprov)"], "weight": 1},
            {"text": "Questions/ambiguities identified", "patterns": [r"(?i)(question|ambigu|unclear|clarif|what.if|what.happen)"], "count_min": 2, "weight": 2},
            {"text": "Edge cases: zero-value, partial, concurrent", "patterns": [r"(?i)(zero|partial|concurrent|simultaneous|duplicate)"], "weight": 1},
        ],
        "structural_checks": True,
    },
    "p3-05-brownfield-gap": {
        "name": "Brownfield gap analysis on order_processor",
        "category": "brownfield",
        "checks": [
            {"text": "Identifies existing 7 tests", "patterns": [r"(?i)(existing|current|covered).{0,20}(7|seven|test)"], "weight": 1},
            {"text": "Gap: tax calculation not verified", "patterns": [r"(?i)tax.{0,30}(not|miss|gap|untest|uncover|never|verif|assert|calculat)"], "weight": 2},
            {"text": "Gap: shipping threshold boundary ($50)", "patterns": [r"(?i)(shipping|free.ship|threshold).{0,30}(50|boundary|miss|gap|untest)"], "weight": 2},
            {"text": "Gap: request_refund untested", "patterns": [r"(?i)(refund|request_refund).{0,30}(not|miss|gap|untest|uncover|no.test)"], "weight": 2},
            {"text": "Gap: inventory restoration on cancel", "patterns": [r"(?i)(inventory|stock).{0,30}(restor|cancel|return|revert)"], "weight": 2},
            {"text": "Gap: MAX_ITEMS boundary (100/101)", "patterns": [r"(?i)(max.item|100|101).{0,30}(boundary|limit|miss|gap)"], "weight": 1},
            {"text": "Gap: discount boundaries (0%, 100%)", "patterns": [r"(?i)discount.{0,30}(0|100|boundar|edge|miss)"], "weight": 1},
            {"text": "Gap: unknown item validation", "patterns": [r"(?i)(unknown|invalid).{0,20}item"], "weight": 1},
            {"text": "Gap: zero/negative quantity", "patterns": [r"(?i)(zero|negative|<=\s*0).{0,20}(quantit|qty)"], "weight": 1},
            {"text": "Gap: full state transition coverage", "patterns": [r"(?i)state.{0,10}transition.{0,30}(miss|gap|incomplete|partial|not.all|full|chain|all.valid|lifecycle)"], "weight": 2},
            {"text": "Marks scenarios as covered/uncovered", "patterns": [r"(?i)(status:\s*(un)?covered|covered.*uncovered)"], "weight": 1},
            {"text": "Risk prioritization of gaps", "patterns": [r"(?i)(high.{0,10}risk|critical|priorit)"], "weight": 1},
        ],
        "structural_checks": True,
    },
    "p3-06-brownfield-redundancy": {
        "name": "Test suite redundancy analysis",
        "category": "brownfield",
        "is_guidance": True,
        "checks": [
            {"text": "Addresses both redundancy AND gap discovery", "patterns": [r"(?i)redundan", r"(?i)(gap|miss|untest|edge.case)"], "min_matches": 2, "weight": 2},
            {"text": "References EP for identifying same-partition tests", "patterns": [r"(?i)(equivalence|partition|same.{0,10}class|same.{0,10}partition)"], "weight": 2},
            {"text": "References BVA for finding missing edge cases", "patterns": [r"(?i)(boundary|BVA|edge.{0,10}case)"], "weight": 1},
            {"text": "Recommends test-to-scenario mapping", "patterns": [r"(?i)(map|trac|link).{0,20}(scenario|requirement|story)"], "weight": 2},
            {"text": "Mentions risk-based prioritization", "patterns": [r"(?i)risk.{0,10}(based|priorit|driven|weight)"], "weight": 2},
            {"text": "Suggests mutation testing", "patterns": [r"(?i)(mutation|mutant).{0,10}test"], "weight": 1},
            {"text": "Addresses path/branch coverage gaps", "patterns": [r"(?i)(path|branch|decision).{0,10}(coverage|cover|analys)"], "weight": 1},
            {"text": "Notes maintainability benefit of removing redundancy", "patterns": [r"(?i)(maintain|speed|CI|pipeline|execution.time|feedback)"], "weight": 1},
        ],
        "structural_checks": False,
    },
    "p3-07-codegen-runnable": {
        "name": "Generate runnable pytest code",
        "category": "codegen",
        "checks": [
            {"text": "Valid Python imports", "patterns": [r"import pytest", r"from.{0,50}(order_processor|OrderProcessor)"], "min_matches": 2, "weight": 2},
            {"text": "Has pytest fixture for processor", "patterns": [r"@pytest\.fixture"], "weight": 1},
            {"text": "Has 15+ test functions", "patterns": [r"def test_"], "count_min": 15, "weight": 2},
            {"text": "Tests create_order happy path", "patterns": [r"def test_.*create.*order|def test_.*simple.*order"], "weight": 1},
            {"text": "Tests boundary: MAX_ITEMS", "patterns": [r"100|MAX_ITEMS|max_items"], "weight": 1},
            {"text": "Tests boundary: FREE_SHIPPING_THRESHOLD", "patterns": [r"50\.00|FREE_SHIPPING|shipping.*threshold"], "weight": 2},
            {"text": "Tests state transitions", "patterns": [r"(?i)(transition|CONFIRMED|PROCESSING|SHIPPED|DELIVERED)"], "count_min": 3, "weight": 2},
            {"text": "Tests request_refund", "patterns": [r"(?i)(refund|request_refund)"], "weight": 2},
            {"text": "Tests apply_discount boundaries", "patterns": [r"(?i)(discount.*0|discount.*100|Decimal.*0|Decimal.*100)"], "weight": 1},
            {"text": "Tests inventory side effects", "patterns": [r"(?i)(inventory|stock).{0,30}(assert|check|verify|==)"], "weight": 2},
            {"text": "Uses pytest.raises for error cases", "patterns": [r"pytest\.raises"], "count_min": 3, "weight": 1},
            {"text": "Uses Decimal for numeric assertions", "patterns": [r"Decimal\("], "count_min": 3, "weight": 1},
            {"text": "Uses parametrize", "patterns": [r"@pytest\.mark\.parametrize|parametrize"], "weight": 1},
        ],
        "structural_checks": False,
    },
    "p3-08-codegen-fix": {
        "name": "Weak assertion detection and fix",
        "category": "codegen",
        "is_guidance": True,
        "checks": [
            {"text": "Identifies assertTrue(result != null) as weak/tautological", "patterns": [r"(?i)(weak|tautolog|meaningless|ineffective|poor).{0,30}assert"], "weight": 2},
            {"text": "Explains mutations would survive", "patterns": [r"(?i)(mutation|mutant|surviv|\+\s*to\s*-|arithmetic)"], "weight": 2},
            {"text": "Provides assertEquals(5, result) or equivalent", "patterns": [r"(?i)(assertEqual|assertEquals|assert_equal|==\s*5|expect.*5|result.*5)"], "weight": 2},
            {"text": "Provides additional test cases beyond add(2,3)", "patterns": [r"(?i)(add\(0|add\(-|add\(.*,\s*0\)|negative|zero|edge)"], "weight": 2},
            {"text": "Explains coverage vs quality distinction", "patterns": [r"(?i)(coverage.{0,30}(not|doesn.t|does not).{0,20}(guarantee|ensure|mean)|quality.{0,10}(vs|versus|not.{0,10}same))"], "weight": 1},
            {"text": "References mutation testing", "patterns": [r"(?i)mutation.{0,10}test"], "weight": 1},
        ],
        "structural_checks": False,
    },
    "p3-09-adversarial-antipattern": {
        "name": "Adversarial: testing trivial code",
        "category": "adversarial",
        "is_guidance": True,
        "checks": [
            {"text": "Explicitly says approach is WRONG", "patterns": [r"(?i)(no|wrong|incorrect|misguided|not.{0,10}(correct|right|recommend|advisab))"], "weight": 2},
            {"text": "Identifies anti-pattern: trivial over critical", "patterns": [r"(?i)(trivial|getter|setter).{0,30}(instead|while|but|ignor|neglect).{0,30}(critical|payment|important)"], "weight": 2},
            {"text": "Prioritizes payment processing", "patterns": [r"(?i)payment.{0,30}(first|priorit|critical|high.risk|most.important)"], "weight": 2},
            {"text": "Says getters/setters provide minimal value", "patterns": [r"(?i)(getter|setter).{0,60}(minimal|little|no|low|zero|trivial|near.zero|already.guarantee).{0,20}(value|benefit|worth|capabilit|defect)"], "weight": 1},
            {"text": "Suggests specific payment scenarios", "patterns": [r"(?i)(invalid.{0,10}amount|declined|timeout|insuffici|refund|concurrent)"], "count_min": 2, "weight": 2},
            {"text": "References risk-based or Pareto testing", "patterns": [r"(?i)(risk.{0,10}(based|driven)|pareto|80.{0,5}20|critical.{0,10}first)"], "weight": 1},
            {"text": "Addresses coverage metric misconception", "patterns": [r"(?i)(100%|coverage).{0,40}(not|doesn.t|does not|mislead|false|inflat|theater|illusion).{0,30}(guarantee|quality|mean|security|confidence|sense|metric)"], "weight": 1},
        ],
        "structural_checks": False,
    },
    "p3-10-adversarial-misconception": {
        "name": "Adversarial: 100% coverage misconception",
        "category": "adversarial",
        "is_guidance": True,
        "checks": [
            {"text": "Says NO, coverage != quality", "patterns": [r"(?i)(no|not.{0,10}(good|enough|sufficient)|coverage.{0,30}(not|doesn.t).{0,20}(guarantee|ensure|mean))"], "weight": 2},
            {"text": "Identifies missing price=0 boundary", "patterns": [r"(?i)(price\s*=\s*0|price.*zero|boundary.*0|0.*boundary)"], "weight": 2},
            {"text": "Identifies missing discountPercent boundaries (0, 100)", "patterns": [r"(?i)(discount.{0,15}(0|100|boundar)|0.{0,10}percent|100.{0,10}percent)"], "weight": 2},
            {"text": "Mentions conditional boundary mutations (<= to <)", "patterns": [r"(?i)(<=\s*(to|→|->)\s*<|boundary.{0,10}mutation|conditional.{0,10}mutation|off.by.one)"], "weight": 2},
            {"text": "References mutation testing", "patterns": [r"(?i)mutation.{0,10}test"], "weight": 1},
            {"text": "Provides concrete test recommendations", "patterns": [r"(?i)(add.{0,10}test|recommend|should.{0,10}test|missing.{0,10}test)"], "weight": 1},
            {"text": "Mentions string mutation / exception message verification", "patterns": [r"(?i)(string.{0,10}mutat|exception.{0,10}message|error.{0,10}message|verif.{0,20}message)"], "weight": 1},
        ],
        "structural_checks": False,
    },
    "p3-11-st-atm-pin": {
        "name": "ATM PIN entry state machine",
        "category": "state_transition",
        "checks": [
            {"text": "States: idle, waiting_for_pin, account_access, card_retained", "patterns": [r"(?i)idle", r"(?i)waiting.{0,5}pin", r"(?i)account.{0,5}access", r"(?i)(card.{0,5}retain|locked|blocked)"], "min_matches": 3, "weight": 2},
            {"text": "Transition: incorrect PIN → retry (up to 3)", "patterns": [r"(?i)(3|three).{0,20}(attempt|tries|incorrect|fail)"], "weight": 2},
            {"text": "Transition: 3rd failure → card retained/locked", "patterns": [r"(?i)(3|third).{0,20}(retain|lock|block|swallow)"], "weight": 2},
            {"text": "Guard condition on PIN attempts counter", "patterns": [r"(?i)(guard|counter|attempt.{0,10}count|increment)"], "weight": 1},
            {"text": "Uses state_transition technique", "patterns": [r"(?i)state.{0,5}transition"], "weight": 1},
            {"text": "Tests timeout/card ejection", "patterns": [r"(?i)(timeout|eject|inactiv|cancel)"], "weight": 1},
            {"text": "Has state transition diagram/table", "patterns": [r"(?i)(states:|transitions:|from:|to:|trigger:)"], "count_min": 3, "weight": 1},
        ],
        "structural_checks": True,
    },
    "p3-12-st-order-lifecycle": {
        "name": "Order lifecycle with time guards",
        "category": "state_transition",
        "checks": [
            {"text": "Models 7+ order states", "patterns": [r"(?i)(cart|pending.payment|payment.processing|confirmed|preparing|shipped|delivered|cancel|refund)"], "count_min": 5, "weight": 2},
            {"text": "Cancellation within 30-minute window", "patterns": [r"(?i)(30.{0,5}minute|cancel.{0,30}(time|window|within))"], "weight": 2},
            {"text": "Refund from delivered state", "patterns": [r"(?i)(delivered|refund).{0,30}(refund|delivered)"], "weight": 1},
            {"text": "Time-based guards on transitions", "patterns": [r"(?i)(time|timer|guard|window|expir|deadline)"], "count_min": 2, "weight": 2},
            {"text": "Terminal states (delivered, cancelled, refunded)", "patterns": [r"(?i)(terminal|final|end.{0,5}state|no.{0,10}transition)"], "weight": 1},
            {"text": "BVA on time boundaries", "patterns": [r"(?i)(boundary|29|30|31|minute)"], "count_min": 2, "weight": 1},
            {"text": "Uses state_transition + decision_table", "patterns": [r"(?i)state.{0,5}transition", r"(?i)decision.{0,5}table"], "min_matches": 2, "weight": 2},
        ],
        "structural_checks": True,
    },
    "p3-13-st-ticket-booking": {
        "name": "Ticket booking with timer and refund rules",
        "category": "state_transition",
        "checks": [
            {"text": "States: available, reserved, booked, cancelled", "patterns": [r"(?i)available", r"(?i)reserved", r"(?i)booked", r"(?i)cancel"], "min_matches": 4, "weight": 2},
            {"text": "10-minute reservation timer", "patterns": [r"(?i)(10.{0,5}minute|timer|reserv.{0,20}expir)"], "weight": 2},
            {"text": "Timer expiry returns to available", "patterns": [r"(?i)(expir|timeout).{0,30}(available|release)"], "weight": 2},
            {"text": "Refund rules: >24h before event", "patterns": [r"(?i)(24.{0,5}hour|refund.{0,30}(before|event|cancel))"], "weight": 2},
            {"text": "Concurrent booking handling", "patterns": [r"(?i)(concurrent|simultaneous|race|conflict|lock)"], "weight": 1},
            {"text": "BVA on timer and refund window", "patterns": [r"(?i)(boundary|BVA|9.{0,3}min|10.{0,3}min|11.{0,3}min|23.{0,3}hour|24.{0,3}hour|25.{0,3}hour)"], "weight": 1},
        ],
        "structural_checks": True,
    },
    "p3-14-domain-double-payment": {
        "name": "Double payment prevention",
        "category": "domain_specific",
        "checks": [
            {"text": "Button disabling after first click", "patterns": [r"(?i)(disable|disabl).{0,20}(button|click|submit)"], "weight": 2},
            {"text": "Idempotency key/token", "patterns": [r"(?i)(idempoten|token|nonce|dedup|unique.{0,10}(key|id|token))"], "weight": 2},
            {"text": "Server-side duplicate rejection", "patterns": [r"(?i)(server|backend).{0,30}(reject|duplic|prevent|idempoten)"], "weight": 2},
            {"text": "Loading/spinner indicator", "patterns": [r"(?i)(loading|spinner|indicator|progress|processing)"], "weight": 1},
            {"text": "Network retry handling", "patterns": [r"(?i)(retry|timeout|network.{0,20}(fail|error|interrupt))"], "weight": 1},
            {"text": "Concurrent session protection", "patterns": [r"(?i)(concurrent|session|multiple.{0,10}(tab|window|device))"], "weight": 1},
            {"text": "Only one transaction in database", "patterns": [r"(?i)(one|single|exactly).{0,20}(transaction|charge|payment|record)"], "weight": 2},
        ],
        "structural_checks": True,
    },
    "p3-15-domain-login-lockout": {
        "name": "Login authentication with lockout",
        "category": "domain_specific",
        "checks": [
            {"text": "Valid login redirects to dashboard", "patterns": [r"(?i)(valid|correct|success).{0,40}(login|auth|credential)", r"(?i)(redirect|dashboard|home.{0,5}page)"], "min_matches": 2, "weight": 1},
            {"text": "Generic error message (no enumeration)", "patterns": [r"(?i)(generic|same|identical|indistinguish).{0,30}(error|message)", r"(?i)(enumerat|reveal|distinguish|disclose)"], "min_matches": 2, "weight": 2},
            {"text": "Account lockout after N failures", "patterns": [r"(?i)(lock|block).{0,20}(after|attempt|\d+.{0,5}fail)"], "weight": 2},
            {"text": "Lockout duration/reset mechanism", "patterns": [r"(?i)(unlock|reset|duration|cool.?down|minute|temporary)"], "weight": 1},
            {"text": "SQL injection prevention", "patterns": [r"(?i)(sql.{0,5}inject|injection|sanitiz|parameteriz)"], "weight": 1},
            {"text": "Brute force protection", "patterns": [r"(?i)(brute.{0,5}force|rate.{0,5}limit|captcha|throttl)"], "weight": 2},
            {"text": "Session management", "patterns": [r"(?i)(session|token|cookie|jwt)"], "weight": 1},
        ],
        "structural_checks": True,
    },
    "p3-16-domain-otp": {
        "name": "OTP verification for payment",
        "category": "domain_specific",
        "checks": [
            {"text": "OTP delivery verification", "patterns": [r"(?i)(deliver|send|receiv).{0,20}(otp|code|sms)"], "weight": 1},
            {"text": "OTP expiration handling", "patterns": [r"(?i)(expir|timeout|window).{0,20}(otp|code)"], "weight": 2},
            {"text": "Brute-force protection (max attempts)", "patterns": [r"(?i)(brute|max|limit).{0,20}(attempt|tries|otp)"], "weight": 2},
            {"text": "Invalid OTP rejection", "patterns": [r"(?i)(invalid|incorrect|wrong).{0,20}(otp|code)"], "weight": 1},
            {"text": "OTP reuse prevention", "patterns": [r"(?i)(reuse|replay|used|same.{0,10}(otp|code))"], "weight": 2},
            {"text": "Resend OTP flow", "patterns": [r"(?i)(resend|re-send|new.{0,10}(otp|code))"], "weight": 1},
            {"text": "BVA on expiration time", "patterns": [r"(?i)(boundary|just.{0,5}(before|after)|BVA|second)"], "weight": 1},
        ],
        "structural_checks": True,
    },
    "p3-17-tdd-throttle": {
        "name": "Throttle function TDD with state + BVA",
        "category": "tdd_best_practices",
        "checks": [
            {"text": "Immediate first call execution", "patterns": [r"(?i)(first|initial|immediate).{0,20}(call|execut|fire|invoke)"], "weight": 2},
            {"text": "Subsequent calls ignored during delay", "patterns": [r"(?i)(ignore|suppress|skip|discard|block).{0,20}(call|during|until)"], "weight": 2},
            {"text": "After delay, next call executes", "patterns": [r"(?i)(after|expir|elaps).{0,20}(delay|timer|period).{0,30}(execut|fire|call)"], "weight": 2},
            {"text": "State model: ready/throttled", "patterns": [r"(?i)(ready|throttled|idle|waiting|cooldown)"], "count_min": 2, "weight": 1},
            {"text": "BVA on delay parameter", "patterns": [r"(?i)(zero|negative|0|delay.{0,20}(0|zero|negat|bound))"], "weight": 2},
            {"text": "Uses state_transition technique", "patterns": [r"(?i)state.{0,5}transition"], "weight": 1},
            {"text": "Timer precision/edge cases", "patterns": [r"(?i)(precision|edge|exact|millisecond|timer)"], "weight": 1},
        ],
        "structural_checks": True,
    },
    "p3-18-dt-loan-approval": {
        "name": "Loan approval multi-condition DT",
        "category": "correctness",
        "checks": [
            {"text": "Three conditions: credit, income, debts", "patterns": [r"(?i)credit", r"(?i)income", r"(?i)debt"], "min_matches": 3, "weight": 2},
            {"text": "Correct outcomes: Approved, Rejected, Further Review", "patterns": [r"(?i)approved", r"(?i)rejected", r"(?i)(further|review|manual)"], "min_matches": 3, "weight": 2},
            {"text": "Decision table with 8 rules (2^3)", "patterns": [r"(?i)(rule|decision)"], "count_min": 4, "weight": 2},
            {"text": "Good+High+No → Approved", "patterns": [r"(?i)(good|high).{0,30}(no.{0,10}debt|debt.{0,5}no).{0,30}approved"], "weight": 1},
            {"text": "EP for each condition (Good/Poor, High/Low, Yes/No)", "patterns": [r"(?i)(good|poor|high|low|yes|no)"], "count_min": 4, "weight": 1},
            {"text": "Has concrete examples with all 3 inputs", "patterns": [r"(?i)(credit.{0,5}(good|poor|score)|income.{0,5}(high|low|\d))"], "count_min": 3, "weight": 1},
        ],
        "structural_checks": True,
    },
    "p3-19-st-vending-machine": {
        "name": "Vending machine state transitions",
        "category": "correctness",
        "checks": [
            {"text": "States: idle, accepting_coins, dispensing, returning_change, out_of_stock", "patterns": [r"(?i)idle", r"(?i)accepting.{0,5}coin", r"(?i)dispensing", r"(?i)return.{0,5}change", r"(?i)out.of.stock"], "min_matches": 4, "weight": 2},
            {"text": "Guard: amount >= item_price", "patterns": [r"(?i)(amount|total|coin).{0,20}(>=|enough|sufficient|price)"], "weight": 2},
            {"text": "Change calculation", "patterns": [r"(?i)(change|return|difference|overpay)"], "weight": 1},
            {"text": "Out-of-stock handling", "patterns": [r"(?i)out.of.stock.{0,30}(refund|return|reject|cannot)"], "weight": 1},
            {"text": "Coin denominations", "patterns": [r"(?i)(coin|denomination|quarter|dime|nickel|dollar|\$[0-9])"], "count_min": 2, "weight": 1},
            {"text": "Multiple items / price variations", "patterns": [r"(?i)(item|product|select|price)"], "count_min": 3, "weight": 1},
            {"text": "Cancel/coin return from accepting_coins", "patterns": [r"(?i)(cancel|coin.{0,10}return|eject|abort)"], "weight": 1},
        ],
        "structural_checks": True,
    },
    "p3-20-adversarial-ai-trust": {
        "name": "Adversarial: AI tests all pass, should I ship?",
        "category": "adversarial",
        "is_guidance": True,
        "checks": [
            {"text": "Says NO, passing tests != ready to ship", "patterns": [r"(?i)(no|not|shouldn.t|don.t|cannot).{0,30}(ship|deploy|trust|sufficient|ready)"], "weight": 2},
            {"text": "Warns about AI test quality issues", "patterns": [r"(?i)(ai|llm|generated).{0,30}(weak|shallow|tautolog|happy.path|quality)"], "weight": 2},
            {"text": "Recommends mutation testing", "patterns": [r"(?i)mutation.{0,10}test"], "weight": 2},
            {"text": "Suggests manual review of test assertions", "patterns": [r"(?i)(review|inspect|audit).{0,20}(assert|test|quality)"], "weight": 1},
            {"text": "Warns about coverage without quality", "patterns": [r"(?i)coverage.{0,30}(not|doesn.t|without).{0,20}(quality|guarantee|mean)"], "weight": 1},
            {"text": "Recommends boundary/edge case verification", "patterns": [r"(?i)(boundary|edge.case|negative|error).{0,20}(test|cover|miss|verif)"], "weight": 1},
            {"text": "Warns about false confidence from all-green", "patterns": [r"(?i)(false|mislead).{0,20}(confidence|security|assurance)"], "weight": 1},
        ],
        "structural_checks": False,
    },
    "p3-21-st-shopping-cart": {
        "name": "Shopping cart state machine",
        "category": "state_transition",
        "checks": [
            {"text": "States: empty_cart, items_added, checkout, payment_processing, order_confirmed", "patterns": [r"(?i)empty.{0,5}cart", r"(?i)items?.{0,5}added", r"(?i)checkout", r"(?i)payment.{0,5}process", r"(?i)(order.{0,5}confirm|confirmed)"], "min_matches": 4, "weight": 2},
            {"text": "Events: add_product, update_quantity, remove_all, click_checkout, submit_payment", "patterns": [r"(?i)add.{0,5}(product|item)", r"(?i)update.{0,5}quantit", r"(?i)remove.{0,10}(all|item)", r"(?i)(checkout|submit.{0,5}payment)"], "min_matches": 3, "weight": 2},
            {"text": "Guard: cart not empty and items in stock", "patterns": [r"(?i)(guard|condition).{0,30}(not.{0,5}empty|in.{0,5}stock|inventory)"], "weight": 2},
            {"text": "Payment success/failure branches", "patterns": [r"(?i)payment.{0,20}(success|fail|error|decline)"], "weight": 2},
            {"text": "Remove all items returns to empty_cart", "patterns": [r"(?i)remove.{0,30}(empty|initial|start)"], "weight": 1},
            {"text": "State transition table/diagram", "patterns": [r"(?i)(states:|transitions:|from:|to:|trigger:)"], "count_min": 3, "weight": 1},
            {"text": "Concurrent modification handling", "patterns": [r"(?i)(concurrent|simultaneous|race|parallel|session)"], "weight": 1},
        ],
        "structural_checks": True,
    },
    "p3-22-st-airport-kiosk": {
        "name": "Airport self-service kiosk workflow",
        "category": "state_transition",
        "checks": [
            {"text": "States: airline_selection, enter_pnr, confirm_print, printing, exit", "patterns": [r"(?i)airline.{0,5}select", r"(?i)(enter|input).{0,5}(pnr|booking)", r"(?i)(confirm|print)", r"(?i)exit"], "min_matches": 3, "weight": 2},
            {"text": "Invalid PNR error handling", "patterns": [r"(?i)(invalid|wrong|not.found).{0,20}(pnr|booking|code)"], "weight": 2},
            {"text": "Cancel at any point → exit screen", "patterns": [r"(?i)cancel.{0,30}(any|every|each|all).{0,10}(point|state|step|screen)"], "weight": 2},
            {"text": "Timeout handling", "patterns": [r"(?i)(timeout|inactiv|idle).{0,20}(return|reset|exit)"], "weight": 2},
            {"text": "Return to airline selection after print", "patterns": [r"(?i)(return|back|loop).{0,20}(airline|start|initial|select)"], "weight": 1},
            {"text": "State transition diagram", "patterns": [r"(?i)state.{0,5}transition"], "weight": 1},
            {"text": "Error recovery path", "patterns": [r"(?i)(error|recovery|retry|re.enter)"], "weight": 1},
        ],
        "structural_checks": True,
    },
    "p3-23-risk-insurance-fmea": {
        "name": "Insurance claims FMEA analysis",
        "category": "risk_assessment",
        "is_guidance": True,
        "checks": [
            {"text": "Addresses claim calculation engine", "patterns": [r"(?i)claim.{0,15}(calculat|amount|engine)"], "weight": 2},
            {"text": "Addresses document upload", "patterns": [r"(?i)document.{0,15}(upload|evidence|attach)"], "weight": 1},
            {"text": "Addresses fraud detection", "patterns": [r"(?i)fraud.{0,15}(detect|algorithm|flag|prevent)"], "weight": 2},
            {"text": "Addresses claims dashboard", "patterns": [r"(?i)(claims?.{0,5}dashboard|status.{0,5}filter)"], "weight": 1},
            {"text": "Addresses notification emails", "patterns": [r"(?i)(notif|email).{0,20}(claim|send|deliver)"], "weight": 1},
            {"text": "FMEA methodology applied", "patterns": [r"(?i)(fmea|failure.{0,5}mode|severity|occurrence|detection|RPN)"], "count_min": 2, "weight": 2},
            {"text": "Risk prioritization of components", "patterns": [r"(?i)(priorit|highest.{0,10}risk|critical|ranking)"], "weight": 2},
            {"text": "Failure cascade identification", "patterns": [r"(?i)(cascade|downstream|ripple|depend|impact.{0,10}other)"], "weight": 1},
        ],
        "structural_checks": False,
    },
    "p3-24-risk-tax-filing": {
        "name": "Government tax filing risk matrix",
        "category": "risk_assessment",
        "is_guidance": True,
        "checks": [
            {"text": "Tax calculation engine = high risk", "patterns": [r"(?i)tax.{0,15}(calculat|engine).{0,30}(high|critical|highest)"], "weight": 2},
            {"text": "Data encryption = high risk", "patterns": [r"(?i)(encrypt|data.{0,5}protect).{0,30}(high|critical)"], "weight": 2},
            {"text": "Decorative banner = low risk", "patterns": [r"(?i)(banner|decorat|seasonal).{0,30}(low|minimal|negligible)"], "weight": 2},
            {"text": "Accessibility (WCAG) assessed", "patterns": [r"(?i)(accessib|WCAG|screen.reader)"], "weight": 1},
            {"text": "E-signature compliance", "patterns": [r"(?i)(e.?sign|digital.{0,5}sign|signature)"], "weight": 1},
            {"text": "Uses risk matrix (probability x impact)", "patterns": [r"(?i)(risk.{0,5}matrix|probability.{0,10}impact|likelihood.{0,10}impact|3x3)"], "weight": 2},
            {"text": "Recommends test investment based on risk", "patterns": [r"(?i)(test.{0,10}(invest|effort|priorit)|allocat|coverage.{0,10}(high|most))"], "weight": 1},
        ],
        "structural_checks": False,
    },
    "p3-25-concurrency-inventory": {
        "name": "Inventory race condition prevention",
        "category": "concurrency",
        "checks": [
            {"text": "Last unit race condition scenario", "patterns": [r"(?i)(last|final|single).{0,15}(unit|item|stock|quantit).{0,30}(race|concurrent|simultaneous)"], "weight": 2},
            {"text": "Overselling prevention", "patterns": [r"(?i)(oversell|over.sell|negative.{0,5}stock|below.{0,5}zero|exceed)"], "weight": 2},
            {"text": "Locking strategy (pessimistic/optimistic)", "patterns": [r"(?i)(pessimist|optimist|lock|mutex|semaphore|compare.and.swap|CAS|atomic)"], "weight": 2},
            {"text": "Cart-inventory consistency check", "patterns": [r"(?i)(cart|basket).{0,20}(inventory|stock|consisten|sync|valid)"], "weight": 2},
            {"text": "Database transaction isolation", "patterns": [r"(?i)(transaction|isolation|atomic|serializ|commit|rollback)"], "weight": 1},
            {"text": "Multiple user simulation", "patterns": [r"(?i)(multiple|two|concurrent|parallel).{0,15}(user|buyer|customer|request)"], "weight": 1},
            {"text": "Stock deduction atomicity", "patterns": [r"(?i)(atomic|deduct|decrement).{0,20}(stock|inventory|quantity)"], "weight": 1},
        ],
        "structural_checks": True,
    },
    "p3-26-concurrency-payment-gw": {
        "name": "Concurrent payment gateway load",
        "category": "concurrency",
        "checks": [
            {"text": "Concurrent user simulation (hundreds)", "patterns": [r"(?i)(hundred|concurrent|simultaneous|parallel).{0,20}(user|request|transaction|payment)"], "weight": 2},
            {"text": "Data consistency under load", "patterns": [r"(?i)(data.{0,10}consisten|integrity|corrupt|inconsisten)"], "weight": 2},
            {"text": "Response time degradation", "patterns": [r"(?i)(response.{0,5}time|latency|timeout|degrad|slow|SLA)"], "weight": 2},
            {"text": "Transaction isolation", "patterns": [r"(?i)(transaction|isolation|atomic|race.{0,5}condition)"], "weight": 2},
            {"text": "Connection pool / resource exhaustion", "patterns": [r"(?i)(connection.{0,5}pool|resource.{0,10}exhaust|thread.{0,5}pool|limit|capacity)"], "weight": 1},
            {"text": "Deadlock detection", "patterns": [r"(?i)(deadlock|dead.lock|circular.{0,5}wait|lock.{0,5}contention)"], "weight": 1},
            {"text": "Graceful degradation / circuit breaker", "patterns": [r"(?i)(graceful|circuit.{0,5}break|fallback|degrad|throttl|backpressure)"], "weight": 1},
        ],
        "structural_checks": True,
    },
    "p3-27-security-attack-payloads": {
        "name": "Security attack payload testing",
        "category": "security",
        "is_guidance": True,
        "checks": [
            {"text": "XSS payloads with specific examples", "patterns": [r"(?i)(xss|cross.site.script).{0,30}(<script|alert|onerror|javascript:)"], "weight": 2},
            {"text": "SQL injection payloads", "patterns": [r"(?i)sql.{0,5}inject", r"(?i)(UNION.{0,5}SELECT|OR\s+'?1'?\s*=\s*'?1|authentication.{0,10}bypass|tautology|blind.{0,5}inject)"], "min_matches": 2, "weight": 2},
            {"text": "CSRF token manipulation", "patterns": [r"(?i)(csrf|cross.site.request|token.{0,10}manipulat|forger)"], "weight": 2},
            {"text": "Input sanitization bypass", "patterns": [r"(?i)(sanitiz|escap|encod).{0,20}(bypass|circumvent|evade)"], "weight": 2},
            {"text": "Null byte injection", "patterns": [r"(?i)(null.{0,3}byte|%00|\\0|\\x00)"], "weight": 1},
            {"text": "Expected defensive responses specified", "patterns": [r"(?i)(400|403|reject|block|sanitiz|escap|encode).{0,20}(response|status|expect|return)"], "weight": 1},
            {"text": "Multiple attack vectors (3+)", "patterns": [r"(?i)(xss|sql|csrf|null.byte|command.inject|path.travers)"], "count_min": 3, "weight": 1},
        ],
        "structural_checks": False,
    },
    "p3-28-domain-payment-recovery": {
        "name": "Payment failure recovery flow",
        "category": "domain_specific",
        "checks": [
            {"text": "Insufficient funds scenario", "patterns": [r"(?i)insufficient.{0,10}(fund|balance)"], "weight": 2},
            {"text": "Declined card scenario", "patterns": [r"(?i)(decline|reject).{0,10}card"], "weight": 2},
            {"text": "Gateway error/timeout scenario", "patterns": [r"(?i)(gateway|network).{0,15}(error|timeout|fail|unavailab)"], "weight": 2},
            {"text": "User guidance to resolve", "patterns": [r"(?i)(guide|instruct|suggest|prompt|redirect).{0,20}(user|customer|resolv|fix|retry|alternative)"], "weight": 2},
            {"text": "Retry/alternative payment method", "patterns": [r"(?i)(retry|alternative|different|another).{0,15}(payment|method|card)"], "weight": 1},
            {"text": "Transaction rollback/compensation", "patterns": [r"(?i)(rollback|compensat|revert|undo|cancel.{0,10}transaction)"], "weight": 1},
            {"text": "Notification of failure", "patterns": [r"(?i)(notif|email|alert|message).{0,20}(fail|error|decline|unsuccessful)"], "weight": 1},
        ],
        "structural_checks": True,
    },
    "p3-29-risk-regression-priority": {
        "name": "Microservices regression prioritization",
        "category": "risk_assessment",
        "is_guidance": True,
        "checks": [
            {"text": "Payment service = highest priority", "patterns": [r"(?i)payment.{0,5}service", r"(?i)(tier.{0,3}1|priority.{0,5}1|full.{0,5}regress|highest.{0,10}(priority|risk))"], "min_matches": 2, "weight": 2},
            {"text": "Order fulfillment = high priority", "patterns": [r"(?i)(order|fulfillment).{0,5}(service)?", r"(?i)(tier.{0,3}1|priority.{0,5}[12]|full.{0,5}regress|high.{0,10}(priority|risk)|code.{0,5}change)"], "min_matches": 2, "weight": 2},
            {"text": "Catalog = medium priority (no code change)", "patterns": [r"(?i)(catalog|product).{0,30}(medium|moderate|no.{0,5}(code.{0,5})?change)"], "weight": 2},
            {"text": "Dashboard = low priority", "patterns": [r"(?i)(dashboard|analytics|report).{0,20}(low|lowest|minimal|last)"], "weight": 2},
            {"text": "Code change as primary risk indicator", "patterns": [r"(?i)(code.{0,5}change|changed.{0,10}code).{0,30}(risk|indicator|factor|primary|strongest)"], "weight": 1},
            {"text": "External dependency risk factor", "patterns": [r"(?i)(external|third.party|carrier|vendor).{0,20}(depend|integrat|risk)"], "weight": 1},
            {"text": "Financial impact considered", "patterns": [r"(?i)(\$|dollar|financial|money|revenue|million).{0,20}(impact|risk|loss)"], "weight": 1},
        ],
        "structural_checks": False,
    },
    "p3-30-domain-multicurrency": {
        "name": "Multi-currency payment API edge cases",
        "category": "domain_specific",
        "checks": [
            {"text": "Invalid currency codes (XXX, ZZZ)", "patterns": [r"(?i)(invalid|unknown|non.exist).{0,15}(currency|code).{0,20}(XXX|ZZZ|reject|error)"], "weight": 2},
            {"text": "Negative payment amounts", "patterns": [r"(?i)negativ.{0,10}(amount|payment|value)"], "weight": 2},
            {"text": "Decimal precision per currency (USD=2, JPY=0)", "patterns": [r"(?i)(decimal|precision|places).{0,30}(USD|JPY|currenc)"], "weight": 2},
            {"text": "Integer overflow / extremely large amounts", "patterns": [r"(?i)(overflow|extremely.{0,5}large|max|9999|limit|huge)"], "weight": 2},
            {"text": "Zero-amount transaction", "patterns": [r"(?i)zero.{0,10}(amount|payment|transaction|value)"], "weight": 1},
            {"text": "Currency conversion rate change mid-transaction", "patterns": [r"(?i)(rate.{0,10}change|conversion.{0,20}(during|mid)|exchange.{0,10}(lock|fluctuat))"], "weight": 1},
            {"text": "Specific HTTP status codes or API responses", "patterns": [r"(?i)(400|422|status|response.{0,10}code|error.{0,10}message)"], "weight": 1},
        ],
        "structural_checks": True,
    },
}

# ── Valid Guard structural checks (for plan-type evals) ──
STRUCTURAL_CHECKS = [
    {"text": "[Structure] YAML schema: feature, risk_level, entry_point, scenarios",
     "patterns": [r"feature:", r"risk_level:", r"entry_point:", r"scenarios:"],
     "min_matches": 3, "weight": 1},
    {"text": "[Structure] risk_rationale with 4 dimensions",
     "patterns": [r"(?i)impact", r"(?i)frequency", r"(?i)consequence", r"(?i)detectability"],
     "min_matches": 3, "weight": 2},
    {"text": "[Structure] technique_rationale field",
     "patterns": [r"technique_rationale:"], "weight": 1},
    {"text": "[Structure] status field (uncovered/covered)",
     "patterns": [r"status:\s*(uncovered|covered|failing|skipped)"], "weight": 1},
    {"text": "[Structure] priority field (1-5)",
     "patterns": [r"priority:\s*[1-5]"], "weight": 1},
    {"text": "[Structure] test_ref field",
     "patterns": [r"test_ref:"], "weight": 1},
    {"text": "[Structure] Valid Guard type enum",
     "patterns": [r"type:\s*(happy_path|edge_case|boundary|error_handling|state_transition|combinatorial|security|performance)"],
     "weight": 1},
    {"text": "[Structure] Multiple techniques used (>=2)",
     "patterns": [r"equivalence_partitioning", r"boundary_value", r"decision_table", r"state_transition", r"pairwise", r"cause_effect", r"error_guessing"],
     "min_matches": 2, "weight": 2},
    {"text": "[Structure] example_mapping section",
     "patterns": [r"example_mapping:"], "weight": 1},
    {"text": "[Structure] metadata section",
     "patterns": [r"metadata:", r"(created_at|language|test_framework):"],
     "min_matches": 2, "weight": 1},
]


def count_pattern_matches(pattern, text):
    """Count occurrences of a pattern in text."""
    return len(re.findall(pattern, text, re.MULTILINE | re.IGNORECASE))


def evaluate_check(check, text):
    """Evaluate a single check against the output text."""
    patterns = check.get("patterns", [])
    min_matches = check.get("min_matches", 1)
    count_min = check.get("count_min", 0)

    pattern_hits = 0
    total_count = 0
    evidence = ""

    for p in patterns:
        matches = re.findall(p, text, re.MULTILINE | re.IGNORECASE)
        if matches:
            pattern_hits += 1
            total_count += len(matches)
            if not evidence:
                match_str = matches[0] if isinstance(matches[0], str) else str(matches[0])
                evidence = f"Found: {match_str[:80]}"

    passed = False
    if count_min > 0:
        # Need at least count_min total occurrences across any pattern
        passed = total_count >= count_min
        if not passed:
            evidence = f"Found {total_count}/{count_min} required occurrences"
    elif min_matches > 1:
        passed = pattern_hits >= min_matches
        if not passed:
            evidence = f"Found {pattern_hits}/{min_matches} required patterns"
    else:
        passed = pattern_hits > 0

    if not passed and not evidence:
        evidence = f"Not found (checked {len(patterns)} patterns)"

    return {
        "text": check["text"],
        "passed": passed,
        "weight": check.get("weight", 1),
        "evidence": evidence,
    }


def grade_eval(eval_key, text):
    """Grade a single eval output."""
    config = EVAL_CHECKS[eval_key]
    results = []

    # Content checks
    for check in config["checks"]:
        results.append(evaluate_check(check, text))

    # Structural checks (only for plan-type evals)
    if config.get("structural_checks", False):
        for check in STRUCTURAL_CHECKS:
            results.append(evaluate_check(check, text))

    # Calculate weighted score
    total_weight = sum(r["weight"] for r in results)
    passed_weight = sum(r["weight"] for r in results if r["passed"])
    weighted_score = round(passed_weight / total_weight, 3) if total_weight > 0 else 0

    # Simple pass rate
    passed_count = sum(1 for r in results if r["passed"])
    total = len(results)

    # Separate content vs structural
    content_results = [r for r in results if not r["text"].startswith("[Structure]")]
    struct_results = [r for r in results if r["text"].startswith("[Structure]")]

    content_weight = sum(r["weight"] for r in content_results)
    content_passed_weight = sum(r["weight"] for r in content_results if r["passed"])
    struct_weight = sum(r["weight"] for r in struct_results)
    struct_passed_weight = sum(r["weight"] for r in struct_results if r["passed"])

    return {
        "eval_key": eval_key,
        "eval_name": config["name"],
        "category": config["category"],
        "is_guidance": config.get("is_guidance", False),
        "checks": results,
        "summary": {
            "passed": passed_count,
            "total": total,
            "pass_rate": round(passed_count / total, 3) if total > 0 else 0,
            "weighted_score": weighted_score,
            "content_score": round(content_passed_weight / content_weight, 3) if content_weight > 0 else 0,
            "structural_score": round(struct_passed_weight / struct_weight, 3) if struct_weight > 0 else 0,
        },
    }


def grade_iteration(iteration_dir):
    """Grade all evals in an iteration directory."""
    all_results = {}
    categories = {}

    for eval_key, config in EVAL_CHECKS.items():
        eval_path = os.path.join(iteration_dir, eval_key)
        if not os.path.exists(eval_path):
            continue

        for config_name in ["with_skill", "without_skill"]:
            output_path = os.path.join(eval_path, config_name, "output.yaml")
            if not os.path.exists(output_path):
                print(f"  SKIP {eval_key}/{config_name} — no output found")
                continue

            with open(output_path, "r", encoding="utf-8") as f:
                text = f.read()

            grading = grade_eval(eval_key, text)
            result_key = f"{eval_key}/{config_name}"
            all_results[result_key] = grading

            # Save grading
            grading_path = os.path.join(eval_path, config_name, "grading.json")
            with open(grading_path, "w", encoding="utf-8") as f:
                json.dump(grading, f, indent=2, ensure_ascii=False)

            s = grading["summary"]
            print(f"  {eval_key}/{config_name}: {s['passed']}/{s['total']} checks, weighted={s['weighted_score']:.0%}, content={s['content_score']:.0%}")

            # Track by category
            cat = config["category"]
            if cat not in categories:
                categories[cat] = {"with_skill": [], "without_skill": [],
                                   "with_skill_content": [], "without_skill_content": [],
                                   "with_skill_structural": [], "without_skill_structural": []}
            categories[cat][config_name].append(s["weighted_score"])
            categories[cat][f"{config_name}_content"].append(s["content_score"])
            if s["structural_score"] > 0 or config.get("structural_checks", False):
                categories[cat][f"{config_name}_structural"].append(s["structural_score"])

    return all_results, categories


def create_benchmark(iteration_dir, all_results, categories):
    """Create benchmark comparing with_skill vs without_skill."""
    with_scores = []
    without_scores = []
    with_content = []
    without_content = []
    with_structural = []
    without_structural = []

    for key, grading in all_results.items():
        s = grading["summary"]
        if "with_skill" in key:
            with_scores.append(s["weighted_score"])
            with_content.append(s["content_score"])
            if s["structural_score"] > 0:
                with_structural.append(s["structural_score"])
        else:
            without_scores.append(s["weighted_score"])
            without_content.append(s["content_score"])
            if s["structural_score"] > 0:
                without_structural.append(s["structural_score"])

    def stats(arr):
        if not arr:
            return {"mean": 0, "min": 0, "max": 0, "count": 0}
        mean = sum(arr) / len(arr)
        return {
            "mean": round(mean, 3),
            "min": round(min(arr), 3),
            "max": round(max(arr), 3),
            "count": len(arr),
        }

    ws = stats(with_scores)
    wos = stats(without_scores)
    ws_c = stats(with_content)
    wos_c = stats(without_content)
    ws_s = stats(with_structural)
    wos_s = stats(without_structural)

    # Per-category breakdown
    category_summary = {}
    for cat, data in categories.items():
        ws_cat = stats(data["with_skill"])
        wos_cat = stats(data["without_skill"])
        ws_cat_c = stats(data["with_skill_content"])
        wos_cat_c = stats(data["without_skill_content"])
        ws_cat_s = stats(data.get("with_skill_structural", []))
        wos_cat_s = stats(data.get("without_skill_structural", []))
        delta = round(ws_cat["mean"] - wos_cat["mean"], 3) if ws_cat["count"] > 0 and wos_cat["count"] > 0 else 0
        delta_c = round(ws_cat_c["mean"] - wos_cat_c["mean"], 3) if ws_cat_c["count"] > 0 and wos_cat_c["count"] > 0 else 0
        category_summary[cat] = {
            "with_skill": ws_cat,
            "without_skill": wos_cat,
            "delta": delta,
            "with_skill_content": ws_cat_c,
            "without_skill_content": wos_cat_c,
            "delta_content": delta_c,
        }

    benchmark = {
        "phase": 3,
        "metadata": {
            "skill_name": "valid-guard",
            "grading_method": "rubric-based (automated pattern checks + weighted scoring)",
            "evals_run": list(EVAL_CHECKS.keys()),
            "dimensions": list(DIMENSIONS.keys()),
        },
        "overall": {
            "with_skill": ws,
            "without_skill": wos,
            "delta": round(ws["mean"] - wos["mean"], 3),
        },
        "overall_content": {
            "with_skill": ws_c,
            "without_skill": wos_c,
            "delta": round(ws_c["mean"] - wos_c["mean"], 3),
        },
        "overall_structural": {
            "with_skill": ws_s,
            "without_skill": wos_s,
            "delta": round(ws_s["mean"] - wos_s["mean"], 3) if ws_s["count"] > 0 and wos_s["count"] > 0 else 0,
        },
        "by_category": category_summary,
        "per_eval": {},
    }

    # Per-eval comparison
    eval_keys = set()
    for key in all_results:
        eval_key = key.split("/")[0]
        eval_keys.add(eval_key)

    for eval_key in sorted(eval_keys):
        ws_key = f"{eval_key}/with_skill"
        wos_key = f"{eval_key}/without_skill"
        ws_sum = all_results[ws_key]["summary"] if ws_key in all_results else {}
        wos_sum = all_results[wos_key]["summary"] if wos_key in all_results else {}
        ws_score = ws_sum.get("weighted_score")
        wos_score = wos_sum.get("weighted_score")
        ws_content = ws_sum.get("content_score")
        wos_content = wos_sum.get("content_score")
        ws_struct = ws_sum.get("structural_score")
        wos_struct = wos_sum.get("structural_score")
        delta = round(ws_score - wos_score, 3) if ws_score is not None and wos_score is not None else None
        delta_c = round(ws_content - wos_content, 3) if ws_content is not None and wos_content is not None else None

        benchmark["per_eval"][eval_key] = {
            "name": EVAL_CHECKS[eval_key]["name"],
            "category": EVAL_CHECKS[eval_key]["category"],
            "with_skill": ws_score,
            "without_skill": wos_score,
            "delta": delta,
            "with_skill_content": ws_content,
            "without_skill_content": wos_content,
            "delta_content": delta_c,
            "with_skill_structural": ws_struct,
            "without_skill_structural": wos_struct,
        }

    benchmark_path = os.path.join(iteration_dir, "benchmark.json")
    with open(benchmark_path, "w", encoding="utf-8") as f:
        json.dump(benchmark, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"\n{'='*80}")
    print(f"  Benchmark — {iteration_dir}")
    print(f"{'='*80}")
    print(f"  {'':30s} {'Combined':>10s}  {'Content':>10s}  {'Structural':>10s}")
    print(f"  {'with_skill':30s} {ws['mean']:>9.1%}   {ws_c['mean']:>9.1%}   {ws_s['mean']:>9.1%}")
    print(f"  {'without_skill':30s} {wos['mean']:>9.1%}   {wos_c['mean']:>9.1%}   {wos_s['mean']:>9.1%}")
    print(f"  {'delta':30s} {ws['mean']-wos['mean']:>+9.1%}   {ws_c['mean']-wos_c['mean']:>+9.1%}   {ws_s['mean']-wos_s['mean']:>+9.1%}")
    print(f"{'─'*80}")
    print(f"  {'Category':20s} {'Combined':>10s} {'Cont.Delta':>11s} {'Comb.Delta':>11s}")
    for cat, data in category_summary.items():
        print(f"  {cat:20s} {data['with_skill']['mean']:>4.0%}/{data['without_skill']['mean']:<5.0%}  {data['delta_content']:>+10.1%}  {data['delta']:>+10.1%}")
    print(f"{'─'*80}")
    print(f"  {'Eval':40s} {'Combined':>9s} {'Content':>9s} {'Delta(C)':>9s} {'Delta':>9s}")
    for eval_key, data in benchmark["per_eval"].items():
        ws_v = f"{data['with_skill']:.0%}" if data['with_skill'] is not None else "N/A"
        wos_v = f"{data['without_skill']:.0%}" if data['without_skill'] is not None else "N/A"
        wos_c_v = f"{data['without_skill_content']:.0%}" if data.get('without_skill_content') is not None else "N/A"
        d_c = f"{data['delta_content']:+.1%}" if data.get('delta_content') is not None else "N/A"
        d_v = f"{data['delta']:+.1%}" if data['delta'] is not None else "N/A"
        print(f"    {eval_key:40s} {ws_v:>3}/{wos_v:<4} {wos_c_v:>8}  {d_c:>8}  {d_v:>8}")
    print(f"{'='*80}")

    return benchmark


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python grade.py <iteration-dir>")
        sys.exit(1)

    iteration_dir = sys.argv[1]
    print(f"Grading: {iteration_dir}")
    print(f"{'─'*60}")
    results, categories = grade_iteration(iteration_dir)
    if results:
        create_benchmark(iteration_dir, results, categories)
    else:
        print("No results to grade.")
