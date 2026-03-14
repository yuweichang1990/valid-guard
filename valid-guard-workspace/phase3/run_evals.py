"""
Eval automation for Valid Guard Phase 3.

Prints prompts for manual Claude Code execution, grades outputs,
and generates summary reports.

Usage:
  python run_evals.py --eval p3-21 --config with_skill
  python run_evals.py --all
  python run_evals.py --grade-only --iteration iteration-3
  python run_evals.py --report --iteration iteration-3
"""
import argparse
import json
import os
import sys
from pathlib import Path

PHASE3_DIR = Path(__file__).parent
EVALS_JSON = PHASE3_DIR / "phase3_evals.json"
DEFAULT_ITERATION = "iteration-3"
SKILL_MD_REL = "../../SKILL.md"


def load_evals():
    with open(EVALS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)["evals"]


def find_eval(evals, eval_id):
    """Find eval by id (e.g. 'p3-21') or dir_name (e.g. 'p3-21-st-shopping-cart')."""
    for e in evals:
        if e["id"] == eval_id or e["dir_name"] == eval_id:
            return e
    return None


def print_prompt(ev, config):
    """Print the prompt for manual execution."""
    prompt = ev["prompt"]
    print(f"\n{'='*70}")
    print(f"  {ev['id']} | {ev['name']} | config={config}")
    print(f"{'='*70}")
    if config == "with_skill":
        skill_path = os.path.abspath(PHASE3_DIR / SKILL_MD_REL)
        print(f"  [Include SKILL.md from: {skill_path}]")
    print()
    print(prompt)
    print(f"\n{'─'*70}")
    print(f"  Save output to: <iteration>/{ev['dir_name']}/{config}/output.yaml")
    print(f"{'─'*70}\n")


def grade_single(eval_key, iteration_dir):
    """Grade a single eval's outputs and return results."""
    import grade_phase3

    results = {}
    eval_path = PHASE3_DIR / iteration_dir / eval_key
    if not eval_path.exists():
        print(f"  SKIP {eval_key} — directory not found")
        return results

    for config in ["with_skill", "without_skill"]:
        output_path = eval_path / config / "output.yaml"
        if not output_path.exists():
            print(f"  SKIP {eval_key}/{config} — no output.yaml")
            continue
        text = output_path.read_text(encoding="utf-8")
        grading = grade_phase3.grade_eval(eval_key, text)
        results[f"{eval_key}/{config}"] = grading

        # Save grading.json alongside output
        grading_path = eval_path / config / "grading.json"
        with open(grading_path, "w", encoding="utf-8") as f:
            json.dump(grading, f, indent=2, ensure_ascii=False)

        s = grading["summary"]
        print(f"  {eval_key}/{config}: "
              f"{s['passed']}/{s['total']} checks, "
              f"weighted={s['weighted_score']:.0%}, "
              f"content={s['content_score']:.0%}")
    return results


def print_summary_table(all_results):
    """Print a summary table of all graded evals."""
    if not all_results:
        print("\nNo results to summarize.")
        return

    # Group by eval_key
    evals = {}
    for key, grading in all_results.items():
        eval_key, config = key.rsplit("/", 1)
        if eval_key not in evals:
            evals[eval_key] = {}
        evals[eval_key][config] = grading["summary"]["weighted_score"]

    print(f"\n{'='*65}")
    print(f"  {'Eval':<35s} {'With Skill':>12s} {'Without':>12s} {'Delta':>8s}")
    print(f"{'─'*65}")
    for eval_key in sorted(evals.keys()):
        scores = evals[eval_key]
        ws = scores.get("with_skill")
        wos = scores.get("without_skill")
        ws_str = f"{ws:.0%}" if ws is not None else "N/A"
        wos_str = f"{wos:.0%}" if wos is not None else "N/A"
        if ws is not None and wos is not None:
            delta_str = f"{ws - wos:+.1%}"
        else:
            delta_str = "N/A"
        print(f"  {eval_key:<35s} {ws_str:>12s} {wos_str:>12s} {delta_str:>8s}")
    print(f"{'='*65}")

    # Overall averages
    ws_all = [v for e in evals.values() for k, v in e.items() if k == "with_skill"]
    wos_all = [v for e in evals.values() for k, v in e.items() if k == "without_skill"]
    if ws_all:
        print(f"  {'MEAN with_skill':<35s} {sum(ws_all)/len(ws_all):>11.1%}")
    if wos_all:
        print(f"  {'MEAN without_skill':<35s} {'':>12s} {sum(wos_all)/len(wos_all):>11.1%}")
    print()


def run_report(iteration_dir):
    """Run generate_report.py on the benchmark.json."""
    benchmark_path = PHASE3_DIR / iteration_dir / "benchmark.json"
    if not benchmark_path.exists():
        print(f"Error: {benchmark_path} not found. Run grading first.")
        sys.exit(1)
    import subprocess
    report_script = PHASE3_DIR / "generate_report.py"
    subprocess.run([sys.executable, str(report_script), str(benchmark_path)], check=True)


def main():
    parser = argparse.ArgumentParser(description="Valid Guard Phase 3 eval automation")
    parser.add_argument("--eval", help="Eval ID (e.g. p3-21 or p3-21-st-shopping-cart)")
    parser.add_argument("--config", choices=["with_skill", "without_skill"],
                        default="with_skill", help="Config to use (default: with_skill)")
    parser.add_argument("--all", action="store_true", help="Print prompts for all evals")
    parser.add_argument("--grade-only", action="store_true",
                        help="Grade existing outputs without printing prompts")
    parser.add_argument("--report", action="store_true", help="Generate HTML report")
    parser.add_argument("--iteration", default=DEFAULT_ITERATION,
                        help=f"Iteration directory (default: {DEFAULT_ITERATION})")
    args = parser.parse_args()

    evals = load_evals()

    if args.report:
        run_report(args.iteration)
        return

    if args.grade_only:
        print(f"Grading outputs in {args.iteration}/...")
        import grade_phase3
        all_results = {}
        for ev in evals:
            results = grade_single(ev["dir_name"], args.iteration)
            all_results.update(results)
        print_summary_table(all_results)

        # Also produce benchmark.json via the main grading script
        results, categories = grade_phase3.grade_iteration(
            str(PHASE3_DIR / args.iteration))
        if results:
            grade_phase3.create_benchmark(str(PHASE3_DIR / args.iteration),
                                          results, categories)
        return

    if args.all:
        for ev in evals:
            for config in ["with_skill", "without_skill"]:
                print_prompt(ev, config)
        print(f"\nTotal: {len(evals)} evals x 2 configs = {len(evals)*2} runs")
        print(f"After running, grade with: python run_evals.py --grade-only")
        return

    if args.eval:
        ev = find_eval(evals, args.eval)
        if not ev:
            print(f"Error: eval '{args.eval}' not found.")
            print(f"Available: {', '.join(e['id'] for e in evals)}")
            sys.exit(1)
        print_prompt(ev, args.config)
        print(f"After running, grade with:")
        print(f"  python run_evals.py --grade-only --iteration {args.iteration}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
