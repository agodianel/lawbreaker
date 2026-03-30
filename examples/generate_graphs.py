"""
Generate comprehensive benchmark comparison graphs from LawBreaker results.

Produces publication-quality charts suitable for academic presentations
and social media (LinkedIn, Twitter).

Usage:
    python examples/generate_graphs.py
"""

import glob
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import seaborn as sns

# ── Config ──────────────────────────────────────────────────────────────
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results_v0.6")
OUT_DIR = os.path.join(os.path.dirname(__file__), "graphs")
os.makedirs(OUT_DIR, exist_ok=True)

# Visual identity
PROVIDER_COLORS = {
    "Anthropic": "#D4A574",
    "Google": "#4285F4",
    "OpenAI": "#10A37F",
}
MODEL_COLORS = {
    "claude-opus-4-6": "#C4956A",
    "claude-sonnet-4-6": "#E4B584",
    "gemini-3.1-flash-image-preview": "#2B6CC4",
    "gemini-3.1-flash-lite-preview": "#6AADFF",
    "gpt-5.4-mini": "#0D8A6A",
    "gpt-5.4-nano": "#5ED4B4",
}
PROVIDER_FOR_MODEL = {
    "claude-opus-4-6": "Anthropic",
    "claude-sonnet-4-6": "Anthropic",
    "gemini-3.1-flash-image-preview": "Google",
    "gemini-3.1-flash-lite-preview": "Google",
    "gpt-5.4-mini": "OpenAI",
    "gpt-5.4-nano": "OpenAI",
}

DPI = 200
sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "#FAFAFA",
    "font.family": "sans-serif",
})


# ── Data loading ────────────────────────────────────────────────────────
def load_all_results():
    results = {}
    for path in sorted(glob.glob(os.path.join(RESULTS_DIR, "**", "*.json"), recursive=True)):
        with open(path) as f:
            data = json.load(f)
        results[data["model_name"]] = data
    return results


# ── 1. Overall Leaderboard Bar Chart ────────────────────────────────────
def plot_overall_leaderboard(results):
    models = sorted(results.keys(), key=lambda m: results[m]["overall_score"], reverse=True)
    scores = [results[m]["overall_score"] * 100 for m in models]
    colors = [MODEL_COLORS.get(m, "#888") for m in models]

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(range(len(models)), scores, color=colors, edgecolor="white", height=0.6)

    for bar, score, model in zip(bars, scores, models):
        ci = results[model].get("per_law_ci", {})
        ax.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height() / 2,
                f"{score:.1f}%", va="center", fontweight="bold", fontsize=12)

    ax.set_yticks(range(len(models)))
    ax.set_yticklabels([_pretty(m) for m in models], fontsize=12)
    ax.set_xlabel("Overall Score (%)", fontsize=13)
    ax.set_title("LawBreaker Benchmark — Overall Leaderboard", fontsize=16, fontweight="bold", pad=15)
    ax.set_xlim(0, 105)
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(100))

    # Provider badges in label
    for i, m in enumerate(models):
        prov = PROVIDER_FOR_MODEL.get(m, "")
        color = PROVIDER_COLORS.get(prov, "#888")
        ax.annotate(f"  {prov}", xy=(0, i), fontsize=8,
                    color=color, fontweight="bold", va="center")

    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "01_overall_leaderboard.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  ✓ 01_overall_leaderboard.png")


# ── 2. Per-Law Heatmap ──────────────────────────────────────────────────
def plot_law_heatmap(results):
    models = sorted(results.keys(), key=lambda m: results[m]["overall_score"], reverse=True)
    all_laws = sorted({law for r in results.values() for law in r["per_law_scores"]})

    matrix = []
    for m in models:
        row = [results[m]["per_law_scores"].get(law, 0) * 100 for law in all_laws]
        matrix.append(row)

    fig, ax = plt.subplots(figsize=(22, 8))
    im = ax.imshow(matrix, cmap="RdYlGn", vmin=0, vmax=100, aspect="auto")

    ax.set_xticks(range(len(all_laws)))
    ax.set_xticklabels(all_laws, rotation=55, ha="right", fontsize=8)
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels([_pretty(m) for m in models], fontsize=11)

    for i in range(len(models)):
        for j in range(len(all_laws)):
            val = matrix[i][j]
            color = "white" if val < 40 or val > 85 else "black"
            ax.text(j, i, f"{val:.0f}", ha="center", va="center", fontsize=7, color=color)

    cbar = plt.colorbar(im, ax=ax, shrink=0.6, pad=0.02)
    cbar.set_label("Pass Rate (%)", fontsize=11)
    ax.set_title("Per-Law Score Heatmap — All Models", fontsize=16, fontweight="bold", pad=15)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "02_per_law_heatmap.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  ✓ 02_per_law_heatmap.png")


# ── 3. Trap Type Radar Chart ────────────────────────────────────────────
def plot_trap_radar(results):
    models = sorted(results.keys(), key=lambda m: results[m]["overall_score"], reverse=True)
    all_traps = sorted({t for r in results.values() for t in r["per_trap_scores"]})

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection="polar"))

    angles = np.linspace(0, 2 * np.pi, len(all_traps), endpoint=False).tolist()
    angles += angles[:1]

    for m in models:
        values = [results[m]["per_trap_scores"].get(t, 0) * 100 for t in all_traps]
        values += values[:1]
        ax.plot(angles, values, "o-", linewidth=2, label=_pretty(m),
                color=MODEL_COLORS.get(m, "#888"), markersize=4)
        ax.fill(angles, values, alpha=0.08, color=MODEL_COLORS.get(m, "#888"))

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([_pretty_trap(t) for t in all_traps], fontsize=7)
    ax.set_ylim(0, 110)
    ax.set_title("Trap Type Resilience — Radar", fontsize=15, fontweight="bold", pad=25)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.12), fontsize=9)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "03_trap_radar.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  ✓ 03_trap_radar.png")


# ── 4. Provider Comparison (grouped bar) ────────────────────────────────
def plot_provider_comparison(results):
    providers = {}
    for m, data in results.items():
        prov = PROVIDER_FOR_MODEL.get(m, "Unknown")
        providers.setdefault(prov, []).append(data["overall_score"] * 100)

    prov_names = sorted(providers.keys())
    best_scores = [max(providers[p]) for p in prov_names]
    avg_scores = [sum(providers[p]) / len(providers[p]) for p in prov_names]
    colors = [PROVIDER_COLORS.get(p, "#888") for p in prov_names]

    x = np.arange(len(prov_names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 6))
    bars1 = ax.bar(x - width / 2, best_scores, width, color=colors, edgecolor="white")
    bars2 = ax.bar(x + width / 2, avg_scores, width, color=colors, alpha=0.5, edgecolor="white")

    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{bar.get_height():.1f}%", ha="center", va="bottom", fontweight="bold", fontsize=11)
    for bar in bars2:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{bar.get_height():.1f}%", ha="center", va="bottom", fontsize=10)

    from matplotlib.patches import Patch
    legend_handles = [
        Patch(facecolor="#555", edgecolor="white", label="Best Model"),
        Patch(facecolor="#555", alpha=0.5, edgecolor="white", label="Average"),
    ]

    ax.set_xticks(x)
    ax.set_xticklabels(prov_names, fontsize=13)
    ax.set_ylabel("Score (%)", fontsize=13)
    ax.set_title("Provider Comparison — Best vs Average", fontsize=16, fontweight="bold", pad=15)
    ax.legend(handles=legend_handles, fontsize=11)
    ax.set_ylim(0, 110)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(100))
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "04_provider_comparison.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  ✓ 04_provider_comparison.png")


# ── 5. Confidence Intervals per Law (best model) ────────────────────────
def plot_confidence_intervals(results):
    best_model = max(results.keys(), key=lambda m: results[m]["overall_score"])
    data = results[best_model]
    ci_data = data.get("per_law_ci", {})
    scores = data["per_law_scores"]

    if not ci_data:
        print("  ⚠ Skipping CI plot (no CI data)")
        return

    laws = sorted(scores.keys(), key=lambda l: scores[l], reverse=True)
    y_pos = range(len(laws))
    mids = [scores[l] * 100 for l in laws]
    lowers = [(scores[l] - ci_data[l][0]) * 100 for l in laws]
    uppers = [(ci_data[l][1] - scores[l]) * 100 for l in laws]

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.barh(y_pos, mids, color=MODEL_COLORS.get(best_model, "#4285F4"),
            alpha=0.7, edgecolor="white", height=0.6)
    ax.errorbar(mids, y_pos, xerr=[lowers, uppers], fmt="none",
                ecolor="#333", elinewidth=1.5, capsize=3)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(laws, fontsize=9)
    ax.set_xlabel("Pass Rate (%)", fontsize=12)
    ax.set_title(f"Per-Law Scores with 95% CI — {_pretty(best_model)}",
                 fontsize=15, fontweight="bold", pad=15)
    ax.set_xlim(0, 115)
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(100))

    ax.axvline(x=data["overall_score"] * 100, color="red", linestyle="--",
               alpha=0.5, label=f"Overall: {data['overall_score']:.1%}")
    ax.legend(fontsize=10)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "05_confidence_intervals.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  ✓ 05_confidence_intervals.png")


# ── 6. Mean Relative Error Comparison ───────────────────────────────────
def plot_error_comparison(results):
    models = sorted(results.keys(), key=lambda m: results[m]["overall_score"], reverse=True)
    all_laws = sorted({l for r in results.values() for l in r.get("per_law_error_stats", {})})

    if not all_laws:
        print("  ⚠ Skipping error comparison (no error stats)")
        return

    fig, ax = plt.subplots(figsize=(14, 7))
    x = np.arange(len(all_laws))
    width = 0.8 / len(models)

    for i, m in enumerate(models):
        err_stats = results[m].get("per_law_error_stats", {})
        means = []
        for law in all_laws:
            stat = err_stats.get(law, {})
            val = stat.get("mean")
            means.append(val if val is not None else 0)
        # Cap for readability
        means_capped = [min(v, 5.0) for v in means]
        offset = (i - len(models) / 2 + 0.5) * width
        ax.bar(x + offset, means_capped, width, label=_pretty(m),
               color=MODEL_COLORS.get(m, "#888"), edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(all_laws, rotation=55, ha="right", fontsize=7)
    ax.set_ylabel("Mean Relative Error (capped at 5.0)", fontsize=11)
    ax.set_title("Mean Relative Error per Law — All Models", fontsize=15, fontweight="bold", pad=15)
    ax.legend(fontsize=8, ncol=2)
    ax.set_ylim(0)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "06_mean_relative_error.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  ✓ 06_mean_relative_error.png")


# ── 7. Worst Laws per Model ─────────────────────────────────────────────
def plot_worst_laws(results):
    models = sorted(results.keys(), key=lambda m: results[m]["overall_score"], reverse=True)

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()

    for idx, m in enumerate(models):
        ax = axes[idx]
        scores = results[m]["per_law_scores"]
        worst_5 = sorted(scores.items(), key=lambda x: x[1])[:5]
        best_5 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
        combined = worst_5 + best_5
        combined_sorted = sorted(combined, key=lambda x: x[1])

        laws_names = [c[0] for c in combined_sorted]
        vals = [c[1] * 100 for c in combined_sorted]
        bar_colors = ["#E74C3C" if v < 50 else "#F39C12" if v < 70 else "#2ECC71" for v in vals]

        ax.barh(range(len(laws_names)), vals, color=bar_colors, edgecolor="white", height=0.7)
        ax.set_yticks(range(len(laws_names)))
        ax.set_yticklabels(laws_names, fontsize=7)
        ax.set_xlim(0, 110)
        ax.set_title(_pretty(m), fontsize=12, fontweight="bold")
        ax.axvline(x=50, color="red", linestyle=":", alpha=0.4)
        for i, v in enumerate(vals):
            ax.text(v + 1, i, f"{v:.0f}%", va="center", fontsize=7)

    fig.suptitle("Best & Worst 5 Laws per Model", fontsize=17, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "07_worst_best_laws.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  ✓ 07_worst_best_laws.png")


# ── 8. Trap Type Grouped Bar Chart ──────────────────────────────────────
def plot_trap_bars(results):
    models = sorted(results.keys(), key=lambda m: results[m]["overall_score"], reverse=True)
    all_traps = sorted({t for r in results.values() for t in r["per_trap_scores"]})

    # Pick top 10 most differentiated traps
    trap_variance = {}
    for t in all_traps:
        vals = [results[m]["per_trap_scores"].get(t, 0) for m in models]
        trap_variance[t] = max(vals) - min(vals)
    top_traps = sorted(all_traps, key=lambda t: trap_variance[t], reverse=True)[:12]

    fig, ax = plt.subplots(figsize=(16, 7))
    x = np.arange(len(top_traps))
    width = 0.8 / len(models)

    for i, m in enumerate(models):
        vals = [results[m]["per_trap_scores"].get(t, 0) * 100 for t in top_traps]
        offset = (i - len(models) / 2 + 0.5) * width
        ax.bar(x + offset, vals, width, label=_pretty(m),
               color=MODEL_COLORS.get(m, "#888"), edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels([_pretty_trap(t) for t in top_traps], rotation=40, ha="right", fontsize=9)
    ax.set_ylabel("Pass Rate (%)", fontsize=12)
    ax.set_title("Most Differentiating Trap Types — Score Comparison",
                 fontsize=15, fontweight="bold", pad=15)
    ax.legend(fontsize=9, ncol=2)
    ax.set_ylim(0, 115)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(100))
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "08_trap_comparison.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  ✓ 08_trap_comparison.png")


# ── 9. Pass / Fail / Error Breakdown ────────────────────────────────────
def plot_pass_fail_breakdown(results):
    models = sorted(results.keys(), key=lambda m: results[m]["overall_score"], reverse=True)

    fig, ax = plt.subplots(figsize=(11, 6))

    pass_counts, fail_counts, error_counts = [], [], []
    for m in models:
        questions = results[m].get("questions", [])
        if questions:
            p = sum(1 for q in questions if q.get("passed"))
            e = sum(1 for q in questions if q.get("error"))
            f = len(questions) - p - e
        else:
            p = results[m]["total_passed"]
            f = results[m]["total_questions"] - p
            e = 0
        pass_counts.append(p)
        fail_counts.append(f)
        error_counts.append(e)

    y = np.arange(len(models))
    ax.barh(y, pass_counts, color="#2ECC71", label="Pass", edgecolor="white", height=0.6)
    ax.barh(y, fail_counts, left=pass_counts, color="#E74C3C", label="Fail", edgecolor="white", height=0.6)
    left2 = [p + f for p, f in zip(pass_counts, fail_counts)]
    ax.barh(y, error_counts, left=left2, color="#95A5A6", label="Error", edgecolor="white", height=0.6)

    ax.set_yticks(y)
    ax.set_yticklabels([_pretty(m) for m in models], fontsize=11)
    ax.set_xlabel("Number of Questions", fontsize=12)
    ax.set_title("Pass / Fail / Error Breakdown", fontsize=16, fontweight="bold", pad=15)
    ax.legend(fontsize=11)
    ax.invert_yaxis()
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "09_pass_fail_breakdown.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  ✓ 09_pass_fail_breakdown.png")


# ── 10. Law Category Performance (single vs chain) ─────────────────────
def plot_single_vs_chain(results):
    models = sorted(results.keys(), key=lambda m: results[m]["overall_score"], reverse=True)

    single_scores = []
    chain_scores = []
    for m in models:
        laws = results[m]["per_law_scores"]
        s_vals = [v for k, v in laws.items() if "→" not in k]
        c_vals = [v for k, v in laws.items() if "→" in k]
        single_scores.append(sum(s_vals) / len(s_vals) * 100 if s_vals else 0)
        chain_scores.append(sum(c_vals) / len(c_vals) * 100 if c_vals else 0)

    x = np.arange(len(models))
    width = 0.35

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.bar(x - width / 2, single_scores, width, label="Single-Step Laws",
           color="#3498DB", edgecolor="white")
    ax.bar(x + width / 2, chain_scores, width, label="Multi-Step (Chain) Laws",
           color="#E67E22", edgecolor="white")

    for i in range(len(models)):
        ax.text(i - width / 2, single_scores[i] + 1, f"{single_scores[i]:.0f}%",
                ha="center", fontsize=9, fontweight="bold")
        ax.text(i + width / 2, chain_scores[i] + 1, f"{chain_scores[i]:.0f}%",
                ha="center", fontsize=9, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([_pretty(m) for m in models], rotation=20, ha="right", fontsize=10)
    ax.set_ylabel("Average Pass Rate (%)", fontsize=12)
    ax.set_title("Single-Step vs Multi-Step Law Performance",
                 fontsize=15, fontweight="bold", pad=15)
    ax.legend(fontsize=11)
    ax.set_ylim(0, 115)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(100))
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "10_single_vs_chain.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  ✓ 10_single_vs_chain.png")


# ── 11. Score Distribution Violin Plot ──────────────────────────────────
def plot_score_distribution(results):
    models = sorted(results.keys(), key=lambda m: results[m]["overall_score"], reverse=True)

    fig, ax = plt.subplots(figsize=(12, 6))

    data_for_violin = []
    positions = []
    colors_list = []
    for i, m in enumerate(models):
        per_law = results[m]["per_law_scores"]
        vals = [v * 100 for v in per_law.values()]
        data_for_violin.append(vals)
        positions.append(i)
        colors_list.append(MODEL_COLORS.get(m, "#888"))

    parts = ax.violinplot(data_for_violin, positions=positions,
                          showmeans=True, showmedians=True, widths=0.7)

    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(colors_list[i])
        pc.set_alpha(0.7)
    for key in ("cmeans", "cmedians", "cbars", "cmins", "cmaxes"):
        if key in parts:
            parts[key].set_color("#333")

    ax.set_xticks(positions)
    ax.set_xticklabels([_pretty(m) for m in models], rotation=20, ha="right", fontsize=10)
    ax.set_ylabel("Per-Law Score (%)", fontsize=12)
    ax.set_title("Score Distribution Across Laws — Violin Plot",
                 fontsize=15, fontweight="bold", pad=15)
    ax.set_ylim(-5, 110)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(100))
    ax.axhline(y=50, color="red", linestyle=":", alpha=0.3)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "11_score_distribution.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  ✓ 11_score_distribution.png")


# ── 12. All Models CI Comparison (overall) ──────────────────────────────
def plot_overall_ci(results):
    from lawbreaker.core.uncertainty import wilson_ci

    models = sorted(results.keys(), key=lambda m: results[m]["overall_score"], reverse=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, m in enumerate(models):
        score = results[m]["overall_score"] * 100
        ci = wilson_ci(results[m]["total_passed"], results[m]["total_questions"])
        lo, hi = ci[0] * 100, ci[1] * 100
        color = MODEL_COLORS.get(m, "#888")
        ax.errorbar(score, i, xerr=[[score - lo], [hi - score]],
                    fmt="o", color=color, ecolor=color, elinewidth=2.5,
                    capsize=6, markersize=10, markeredgecolor="white", markeredgewidth=1.5)
        ax.text(hi + 1.5, i, f"{score:.1f}% [{lo:.0f}–{hi:.0f}%]",
                va="center", fontsize=10, color=color, fontweight="bold")

    ax.set_yticks(range(len(models)))
    ax.set_yticklabels([_pretty(m) for m in models], fontsize=11)
    ax.set_xlabel("Overall Score (%)", fontsize=12)
    ax.set_title("Overall Score with 95% Confidence Intervals",
                 fontsize=15, fontweight="bold", pad=15)
    ax.set_xlim(0, 110)
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(100))
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "12_overall_ci.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("  ✓ 12_overall_ci.png")


# ── Helpers ─────────────────────────────────────────────────────────────
def _pretty(model_name: str) -> str:
    """Make model names presentable."""
    return (model_name
            .replace("-preview", " (P)")
            .replace("-image", " Img")
            .replace("-lite", " Lite")
            .replace("gemini-3.1-", "Gemini 3.1 ")
            .replace("claude-opus-4-6", "Claude Opus 4.6")
            .replace("claude-sonnet-4-6", "Claude Sonnet 4.6")
            .replace("gpt-5.4-mini", "GPT-5.4 Mini")
            .replace("gpt-5.4-nano", "GPT-5.4 Nano"))


def _pretty_trap(trap: str) -> str:
    return trap.replace("_", " ").title()


# ── Main ────────────────────────────────────────────────────────────────
def main():
    results = load_all_results()
    print(f"\nLoaded {len(results)} model results. Generating graphs...\n")

    plot_overall_leaderboard(results)
    plot_law_heatmap(results)
    plot_trap_radar(results)
    plot_provider_comparison(results)
    plot_confidence_intervals(results)
    plot_error_comparison(results)
    plot_worst_laws(results)
    plot_trap_bars(results)
    plot_pass_fail_breakdown(results)
    plot_single_vs_chain(results)
    plot_score_distribution(results)
    plot_overall_ci(results)

    print(f"\n✅ All graphs saved to {OUT_DIR}/\n")


if __name__ == "__main__":
    main()
