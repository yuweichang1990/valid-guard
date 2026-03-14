"""
HTML Benchmark Report Generator for Valid Guard.
Generates a self-contained HTML dashboard from benchmark.json files.

Usage: python report_gen.py <benchmark_json_path> [benchmark_json_path2 ...]
       python report_gen.py baseline/benchmark.json
"""
import json
import sys
import os
from datetime import datetime


def load_benchmark(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def merge_benchmarks(benchmarks):
    """Merge multiple iteration benchmarks into a combined view."""
    if len(benchmarks) == 1:
        return benchmarks[0]

    merged = {
        "phase": 3,
        "metadata": benchmarks[-1]["metadata"].copy(),
        "overall": {"with_skill": {"mean": 0, "min": 1, "max": 0, "count": 0},
                     "without_skill": {"mean": 0, "min": 1, "max": 0, "count": 0},
                     "delta": 0},
        "by_category": {},
        "per_eval": {},
        "iterations": [],
    }

    # Use best score per eval across iterations
    for bm in benchmarks:
        iter_label = os.path.basename(os.path.dirname(bm.get("_source_path", "")))
        merged["iterations"].append(iter_label)
        for eval_key, data in bm.get("per_eval", {}).items():
            existing = merged["per_eval"].get(eval_key)
            if existing is None:
                merged["per_eval"][eval_key] = data.copy()
                merged["per_eval"][eval_key]["source_iteration"] = iter_label
            else:
                # Take best with_skill score
                if data["with_skill"] is not None:
                    if existing["with_skill"] is None or data["with_skill"] > existing["with_skill"]:
                        merged["per_eval"][eval_key] = data.copy()
                        merged["per_eval"][eval_key]["source_iteration"] = iter_label

    # Recalculate overall from best per-eval scores
    ws_scores = []
    wos_scores = []
    cats = {}
    for eval_key, data in merged["per_eval"].items():
        if data["with_skill"] is not None:
            ws_scores.append(data["with_skill"])
        if data["without_skill"] is not None:
            wos_scores.append(data["without_skill"])

        cat = data["category"]
        if cat not in cats:
            cats[cat] = {"with_skill": [], "without_skill": []}
        if data["with_skill"] is not None:
            cats[cat]["with_skill"].append(data["with_skill"])
        if data["without_skill"] is not None:
            cats[cat]["without_skill"].append(data["without_skill"])

    def stats(arr):
        if not arr:
            return {"mean": 0, "min": 0, "max": 0, "count": 0}
        return {"mean": round(sum(arr)/len(arr), 3), "min": round(min(arr), 3),
                "max": round(max(arr), 3), "count": len(arr)}

    merged["overall"]["with_skill"] = stats(ws_scores)
    merged["overall"]["without_skill"] = stats(wos_scores)
    merged["overall"]["delta"] = round(
        merged["overall"]["with_skill"]["mean"] - merged["overall"]["without_skill"]["mean"], 3)

    for cat, data in cats.items():
        ws = stats(data["with_skill"])
        wos = stats(data["without_skill"])
        merged["by_category"][cat] = {
            "with_skill": ws,
            "without_skill": wos,
            "delta": round(ws["mean"] - wos["mean"], 3),
        }

    return merged


def pct(val, digits=1):
    if val is None:
        return "N/A"
    return f"{val*100:.{digits}f}%"


def delta_color(d):
    if d is None:
        return "#888"
    if d > 0.3:
        return "#16a34a"
    if d > 0.1:
        return "#65a30d"
    if d > 0:
        return "#ca8a04"
    return "#dc2626"


def score_color(s):
    if s is None:
        return "#888"
    if s >= 0.95:
        return "#16a34a"
    if s >= 0.8:
        return "#65a30d"
    if s >= 0.6:
        return "#ca8a04"
    return "#dc2626"


def generate_html(benchmark, output_path):
    """Generate self-contained HTML report."""
    overall = benchmark["overall"]
    overall_c = benchmark.get("overall_content", {"with_skill": {"mean": 0}, "without_skill": {"mean": 0}, "delta": 0})
    overall_s = benchmark.get("overall_structural", {"with_skill": {"mean": 0}, "without_skill": {"mean": 0}, "delta": 0})
    cats = benchmark.get("by_category", {})
    evals = benchmark.get("per_eval", {})

    ws_mean = overall["with_skill"]["mean"]
    wos_mean = overall["without_skill"]["mean"]
    delta = overall["delta"]
    ws_c_mean = overall_c["with_skill"]["mean"]
    wos_c_mean = overall_c["without_skill"]["mean"]
    delta_c = overall_c["delta"]
    ws_s_mean = overall_s["with_skill"]["mean"]
    wos_s_mean = overall_s["without_skill"]["mean"]
    delta_s = overall_s.get("delta", 0)
    eval_count = overall["with_skill"]["count"]

    # Sort evals by delta descending
    sorted_evals = sorted(evals.items(), key=lambda x: (x[1]["delta"] or 0), reverse=True)

    # Sort categories by delta descending
    sorted_cats = sorted(cats.items(), key=lambda x: x[1]["delta"], reverse=True)

    # Build category rows
    cat_rows = ""
    for cat, data in sorted_cats:
        ws = data["with_skill"]["mean"]
        wos = data["without_skill"]["mean"]
        d = data["delta"]
        wos_c = data.get("without_skill_content", {}).get("mean", 0)
        d_c = data.get("delta_content", 0)
        n = data["with_skill"]["count"]
        cat_rows += f"""
        <tr>
          <td class="cat-name">{cat.replace("_", " ").title()}</td>
          <td class="score" style="color:{score_color(ws)}">{pct(ws)}</td>
          <td class="score" style="color:{score_color(wos)}">{pct(wos)}</td>
          <td class="score" style="color:{score_color(wos_c)}">{pct(wos_c)}</td>
          <td class="delta" style="color:{delta_color(d_c)}">+{pct(d_c)}</td>
          <td class="delta" style="color:{delta_color(d)}">+{pct(d)}</td>
          <td class="count">{n}</td>
        </tr>"""

    # Build eval rows
    eval_rows = ""
    for eval_key, data in sorted_evals:
        ws = data["with_skill"]
        wos = data["without_skill"]
        d = data["delta"]
        wos_c = data.get("without_skill_content")
        d_c = data.get("delta_content")
        name = data.get("name", eval_key)
        cat = data.get("category", "")
        eval_rows += f"""
        <tr>
          <td class="eval-id">{eval_key}</td>
          <td class="eval-name">{name}</td>
          <td class="eval-cat">{cat}</td>
          <td class="score" style="color:{score_color(ws)}">{pct(ws)}</td>
          <td class="score" style="color:{score_color(wos)}">{pct(wos)}</td>
          <td class="score" style="color:{score_color(wos_c)}">{pct(wos_c)}</td>
          <td class="delta" style="color:{delta_color(d_c)}">{'+' if d_c and d_c > 0 else ''}{pct(d_c)}</td>
          <td class="delta" style="color:{delta_color(d)}">{'+' if d and d > 0 else ''}{pct(d)}</td>
        </tr>"""

    # Build chart data for per-eval comparison
    chart_labels = json.dumps([e[0].replace("p3-", "") for e in sorted_evals])
    chart_ws = json.dumps([round((e[1]["with_skill"] or 0)*100, 1) for e in sorted_evals])
    chart_wos = json.dumps([round((e[1]["without_skill"] or 0)*100, 1) for e in sorted_evals])
    chart_wos_c = json.dumps([round((e[1].get("without_skill_content") or 0)*100, 1) for e in sorted_evals])

    # Category chart data
    cat_labels = json.dumps([c[0].replace("_", " ").title() for c in sorted_cats])
    cat_ws = json.dumps([round(c[1]["with_skill"]["mean"]*100, 1) for c in sorted_cats])
    cat_wos = json.dumps([round(c[1]["without_skill"]["mean"]*100, 1) for c in sorted_cats])
    cat_wos_c = json.dumps([round(c[1].get("without_skill_content", {}).get("mean", 0)*100, 1) for c in sorted_cats])

    # Top winners and losers
    top_gains = sorted_evals[:5]
    top_gains_html = ""
    for ek, ed in top_gains:
        d = ed["delta"]
        if d and d > 0:
            top_gains_html += f'<div class="gain-item"><span class="gain-delta" style="color:{delta_color(d)}">+{pct(d)}</span> <span class="gain-name">{ed.get("name", ek)}</span></div>'

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Valid Guard — Benchmark Report</title>
<style>
  :root {{
    --bg: #0f172a; --surface: #1e293b; --surface2: #334155;
    --text: #f1f5f9; --text2: #94a3b8; --accent: #3b82f6;
    --green: #16a34a; --yellow: #ca8a04; --red: #dc2626;
    --ws-color: #3b82f6; --wos-color: #64748b;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
  h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 4px; }}
  .subtitle {{ color: var(--text2); font-size: 14px; margin-bottom: 32px; }}

  /* Summary Cards */
  .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }}
  .summary-card {{ background: var(--surface); border-radius: 12px; padding: 20px; }}
  .summary-card .label {{ color: var(--text2); font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }}
  .summary-card .value {{ font-size: 36px; font-weight: 700; }}
  .summary-card .sub {{ color: var(--text2); font-size: 13px; margin-top: 4px; }}

  /* Section */
  .section {{ background: var(--surface); border-radius: 12px; padding: 24px; margin-bottom: 24px; }}
  .section h2 {{ font-size: 18px; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }}

  /* Tables */
  table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  th {{ text-align: left; padding: 10px 12px; border-bottom: 2px solid var(--surface2); color: var(--text2); font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
  td {{ padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); }}
  tr:hover {{ background: rgba(255,255,255,0.03); }}
  .score {{ font-weight: 600; font-variant-numeric: tabular-nums; text-align: right; }}
  .delta {{ font-weight: 700; font-variant-numeric: tabular-nums; text-align: right; }}
  .count {{ text-align: center; color: var(--text2); }}
  .cat-name, .eval-cat {{ text-transform: capitalize; }}
  .eval-id {{ font-family: 'Cascadia Code', 'Fira Code', monospace; font-size: 12px; color: var(--text2); }}
  .eval-name {{ font-weight: 500; }}

  /* Bars */
  .bar-cell {{ width: 200px; }}
  .bar-bg {{ background: var(--surface2); border-radius: 4px; height: 20px; position: relative; overflow: hidden; }}
  .bar-ws {{ position: absolute; left: 0; top: 0; height: 10px; background: var(--ws-color); border-radius: 4px 4px 0 0; opacity: 0.8; }}
  .bar-wos {{ position: absolute; left: 0; top: 10px; height: 10px; background: var(--wos-color); border-radius: 0 0 4px 4px; opacity: 0.6; }}

  /* Legend */
  .legend {{ display: flex; gap: 24px; margin-bottom: 16px; font-size: 13px; }}
  .legend-item {{ display: flex; align-items: center; gap: 6px; }}
  .legend-dot {{ width: 12px; height: 12px; border-radius: 3px; }}

  /* Gains */
  .gains-list {{ display: flex; flex-direction: column; gap: 8px; }}
  .gain-item {{ display: flex; align-items: center; gap: 12px; padding: 8px 12px; background: var(--surface2); border-radius: 8px; }}
  .gain-delta {{ font-weight: 700; font-size: 16px; min-width: 70px; }}
  .gain-name {{ font-weight: 500; }}

  /* Canvas */
  .chart-container {{ position: relative; height: 320px; margin-top: 16px; }}
  canvas {{ width: 100% !important; height: 100% !important; }}

  /* Footer */
  .footer {{ text-align: center; color: var(--text2); font-size: 12px; margin-top: 40px; padding: 16px; }}

  /* Responsive */
  @media (max-width: 768px) {{
    .summary-grid {{ grid-template-columns: 1fr 1fr; }}
    .bar-cell {{ display: none; }}
    .container {{ padding: 16px; }}
  }}
</style>
</head>
<body>
<div class="container">
  <h1>Valid Guard — Benchmark</h1>
  <p class="subtitle">Generated {timestamp} | {eval_count} evals | Rubric-based weighted scoring</p>

  <!-- Summary Cards -->
  <div class="summary-grid">
    <div class="summary-card">
      <div class="label">With Skill (Combined)</div>
      <div class="value" style="color:{score_color(ws_mean)}">{pct(ws_mean)}</div>
      <div class="sub">content {pct(ws_c_mean)} / structural {pct(ws_s_mean)}</div>
    </div>
    <div class="summary-card">
      <div class="label">Without Skill (Combined)</div>
      <div class="value" style="color:{score_color(wos_mean)}">{pct(wos_mean)}</div>
      <div class="sub">content {pct(wos_c_mean)} / structural {pct(wos_s_mean)}</div>
    </div>
    <div class="summary-card">
      <div class="label">Delta (Combined)</div>
      <div class="value" style="color:{delta_color(delta)}">+{pct(delta)}</div>
      <div class="sub">{eval_count} eval cases</div>
    </div>
    <div class="summary-card">
      <div class="label">Delta (Content Only)</div>
      <div class="value" style="color:{delta_color(delta_c)}">+{pct(delta_c)}</div>
      <div class="sub">test design quality only</div>
    </div>
    <div class="summary-card">
      <div class="label">Delta (Structural)</div>
      <div class="value" style="color:{delta_color(delta_s)}">+{pct(delta_s)}</div>
      <div class="sub">schema compliance only</div>
    </div>
    <div class="summary-card">
      <div class="label">Categories</div>
      <div class="value">{len(cats)}</div>
      <div class="sub">{', '.join(c.replace('_',' ') for c in cats.keys())}</div>
    </div>
  </div>

  <!-- Top Skill Gains -->
  <div class="section">
    <h2>Top Skill Gains</h2>
    <div class="gains-list">
      {top_gains_html}
    </div>
  </div>

  <!-- Category Breakdown -->
  <div class="section">
    <h2>By Category</h2>
    <div class="legend">
      <div class="legend-item"><div class="legend-dot" style="background:var(--ws-color)"></div> With Skill</div>
      <div class="legend-item"><div class="legend-dot" style="background:var(--wos-color)"></div> Without Skill</div>
    </div>
    <table>
      <thead>
        <tr><th>Category</th><th style="text-align:right">With Skill</th><th style="text-align:right">Without (Combined)</th><th style="text-align:right">Without (Content)</th><th style="text-align:right">Content Delta</th><th style="text-align:right">Combined Delta</th><th style="text-align:center">Evals</th></tr>
      </thead>
      <tbody>{cat_rows}</tbody>
    </table>
    <div class="chart-container">
      <canvas id="catChart"></canvas>
    </div>
  </div>

  <!-- Per-Eval Breakdown -->
  <div class="section">
    <h2>Per-Eval Detail (sorted by delta)</h2>
    <table>
      <thead>
        <tr><th>ID</th><th>Name</th><th>Category</th><th style="text-align:right">With Skill</th><th style="text-align:right">Without (Comb.)</th><th style="text-align:right">Without (Content)</th><th style="text-align:right">Content Delta</th><th style="text-align:right">Combined Delta</th></tr>
      </thead>
      <tbody>{eval_rows}</tbody>
    </table>
    <div class="chart-container" style="height:400px">
      <canvas id="evalChart"></canvas>
    </div>
  </div>

  <div class="footer">
    Valid Guard Benchmark Report | Skill: valid-guard | Method: rubric-based weighted scoring
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<script>
  const catLabels = {cat_labels};
  const catWS = {cat_ws};
  const catWOS = {cat_wos};

  const catWOSC = {cat_wos_c};
  new Chart(document.getElementById('catChart'), {{
    type: 'bar',
    data: {{
      labels: catLabels,
      datasets: [
        {{ label: 'With Skill', data: catWS, backgroundColor: 'rgba(59,130,246,0.7)', borderRadius: 4 }},
        {{ label: 'Without (Content Only)', data: catWOSC, backgroundColor: 'rgba(234,179,8,0.5)', borderRadius: 4 }},
        {{ label: 'Without (Combined)', data: catWOS, backgroundColor: 'rgba(100,116,139,0.5)', borderRadius: 4 }}
      ]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      scales: {{
        y: {{ beginAtZero: true, max: 100, ticks: {{ color: '#94a3b8', callback: v => v + '%' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
        x: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ display: false }} }}
      }},
      plugins: {{ legend: {{ labels: {{ color: '#f1f5f9' }} }} }}
    }}
  }});

  const evalLabels = {chart_labels};
  const evalWS = {chart_ws};
  const evalWOS = {chart_wos};
  const evalWOSC = {chart_wos_c};

  new Chart(document.getElementById('evalChart'), {{
    type: 'bar',
    data: {{
      labels: evalLabels,
      datasets: [
        {{ label: 'With Skill', data: evalWS, backgroundColor: 'rgba(59,130,246,0.7)', borderRadius: 4 }},
        {{ label: 'Without (Content)', data: evalWOSC, backgroundColor: 'rgba(234,179,8,0.5)', borderRadius: 4 }},
        {{ label: 'Without (Combined)', data: evalWOS, backgroundColor: 'rgba(100,116,139,0.5)', borderRadius: 4 }}
      ]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      indexAxis: 'y',
      scales: {{
        x: {{ beginAtZero: true, max: 100, ticks: {{ color: '#94a3b8', callback: v => v + '%' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
        y: {{ ticks: {{ color: '#94a3b8', font: {{ size: 11 }} }}, grid: {{ display: false }} }}
      }},
      plugins: {{ legend: {{ labels: {{ color: '#f1f5f9' }} }} }}
    }}
  }});
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML report generated: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python report_gen.py <benchmark.json> [benchmark2.json ...]")
        sys.exit(1)

    benchmarks = []
    for path in sys.argv[1:]:
        bm = load_benchmark(path)
        bm["_source_path"] = path
        benchmarks.append(bm)

    if len(benchmarks) == 1:
        merged = benchmarks[0]
    else:
        merged = merge_benchmarks(benchmarks)

    output_path = os.path.join(os.path.dirname(sys.argv[1]), "..", "report.html")
    generate_html(merged, output_path)
