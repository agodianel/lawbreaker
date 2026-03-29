"""
CLI — Click-based command-line interface for LawBreaker.

Commands:
  - ``run``: execute a benchmark against an LLM
  - ``leaderboard``: show the HuggingFace leaderboard
  - ``laws``: list all available physics laws
  - ``example``: show an example question for a specific law
"""

from __future__ import annotations

import json
import sys

import click
from rich.console import Console
from rich.table import Table

from lawbreaker.laws import LAW_REGISTRY

console = Console()


@click.group()
@click.version_option(package_name="lawbreaker")
def main():
    """🧪 LawBreaker — Physics Adversarial Benchmark for LLMs."""


@main.command()
@click.option("--model", required=True, help="Model name/identifier")
@click.option("--connector", required=True,
              type=click.Choice(["openai", "anthropic", "huggingface", "ollama", "gemini"]))
@click.option("--questions", default=10, help="Questions per law")
@click.option("--output", default=None, help="Output JSON file path")
@click.option("--seed", default=None, type=int, help="Random seed")
@click.option("--laws", default=None, help="Comma-separated law names")
@click.option("--delay", default=0.0, type=float, help="Seconds between API calls (rate-limit avoidance)")
@click.option("--push/--no-push", default=False, help="Push to HF leaderboard")
def run(model, connector, questions, output, seed, laws, delay, push):
    """Run the adversarial physics benchmark against an LLM."""
    from lawbreaker.runner import BenchmarkRunner

    conn = _make_connector(connector, model)
    law_list = laws.split(",") if laws else None

    runner = BenchmarkRunner(
        connector=conn, laws=law_list, n_questions=questions, seed=seed,
        delay=delay,
    )
    console.print(f"\n[bold cyan]🧪 LawBreaker Benchmark[/bold cyan]")
    console.print(f"   Model: [green]{model}[/green]")
    console.print(f"   Questions/law: {questions}")
    console.print(f"   Seed: {seed or 'random'}\n")

    report = runner.run()

    # Results table
    table = Table(title="📊 Results by Law", show_lines=True)
    table.add_column("Law", style="cyan")
    table.add_column("Score", justify="right")
    for law_name, score in sorted(
        report.per_law_scores.items(), key=lambda x: x[1], reverse=True
    ):
        color = "green" if score >= 0.7 else "yellow" if score >= 0.4 else "red"
        table.add_row(law_name, f"[{color}]{score:.1%}[/{color}]")
    console.print(table)

    # Trap table
    trap_table = Table(title="🪤 Results by Trap Type", show_lines=True)
    trap_table.add_column("Trap", style="magenta")
    trap_table.add_column("Score", justify="right")
    for trap, score in sorted(
        report.per_trap_scores.items(), key=lambda x: x[1], reverse=True
    ):
        color = "green" if score >= 0.7 else "yellow" if score >= 0.4 else "red"
        trap_table.add_row(trap, f"[{color}]{score:.1%}[/{color}]")
    console.print(trap_table)

    console.print(f"\n[bold]{report.summary()}[/bold]\n")

    if output:
        import os
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        with open(output, "w") as f:
            f.write(report.to_json())
        console.print(f"[green]Results saved to {output}[/green]")

    if push:
        import os
        token = os.environ.get("HF_TOKEN", "")
        if not token:
            console.print("[red]Error: HF_TOKEN env var required for --push[/red]")
            sys.exit(1)
        from lawbreaker.leaderboard import Leaderboard
        lb = Leaderboard()
        path = lb.push_result(report, token)
        console.print(f"[green]Pushed to HuggingFace: {path}[/green]")


@main.command()
def leaderboard():
    """Show the public HuggingFace leaderboard."""
    from lawbreaker.leaderboard import Leaderboard

    lb = Leaderboard()
    console.print("\n[bold cyan]Fetching leaderboard...[/bold cyan]\n")
    reports = lb.pull_results()
    if not reports:
        console.print("[yellow]No results found on leaderboard yet.[/yellow]")
        return
    console.print(lb.render_table(reports))


@main.command("laws")
def list_laws():
    """List all available physics laws."""
    table = Table(title="⚡ Available Physics Laws")
    table.add_column("Short Name", style="cyan")
    table.add_column("Full Name", style="white")
    for name, cls in LAW_REGISTRY.items():
        table.add_row(name, cls.LAW_NAME)
    console.print(table)


@main.command("models")
def list_models():
    """Discover available HuggingFace inference models."""
    from lawbreaker.connectors.huggingface_connector import HuggingFaceConnector

    console.print("\n[bold cyan]🔍 Discovering HuggingFace inference models...[/bold cyan]\n")
    models = HuggingFaceConnector.discover_models()
    if not models:
        console.print("[yellow]No models found. Check your HF_TOKEN.[/yellow]")
        return
    table = Table(title=f"🤖 Available Models ({len(models)})")
    table.add_column("#", style="dim", justify="right")
    table.add_column("Model", style="cyan")
    for i, m in enumerate(models, 1):
        table.add_row(str(i), m)
    console.print(table)


@main.command("run-all")
@click.option("--questions", default=5, help="Questions per law")
@click.option("--output-dir", default="results", help="Base directory for result files")
@click.option("--seed", default=42, type=int, help="Random seed")
@click.option("--laws", default=None, help="Comma-separated law names")
@click.option("--delay", default=5.0, type=float, help="Seconds between API calls (rate-limit avoidance)")
@click.option("--connector", default="huggingface",
              type=click.Choice(["openai", "anthropic", "huggingface", "ollama", "gemini"]),
              help="Connector type for model discovery (default: huggingface)")
@click.option("--push/--no-push", default=False, help="Push to HF leaderboard")
def run_all(questions, output_dir, seed, laws, delay, connector, push):
    """Run benchmark against ALL available HuggingFace inference models."""
    import os
    from lawbreaker.connectors.huggingface_connector import HuggingFaceConnector
    from lawbreaker.runner import BenchmarkRunner

    console.print("\n[bold cyan]🔍 Discovering HuggingFace inference models...[/bold cyan]")
    models = HuggingFaceConnector.discover_models()
    if not models:
        console.print("[red]No models found. Check your HF_TOKEN.[/red]")
        sys.exit(1)

    console.print(f"[green]Found {len(models)} models[/green]\n")
    for i, m in enumerate(models, 1):
        console.print(f"  {i:2d}. {m}")
    console.print()

    # Use connector-specific subdirectory
    connector_dir = os.path.join(output_dir, connector)
    os.makedirs(connector_dir, exist_ok=True)
    law_list = laws.split(",") if laws else None
    summaries = []

    for idx, model in enumerate(models, 1):
        console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
        console.print(f"[bold cyan]  [{idx}/{len(models)}] {model}[/bold cyan]")
        console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")

        conn = HuggingFaceConnector(model=model)
        runner = BenchmarkRunner(
            connector=conn, laws=law_list, n_questions=questions,
            seed=seed, delay=delay,
        )

        try:
            report = runner.run()
        except Exception as exc:
            console.print(f"[red]  ✗ {model} failed: {exc}[/red]\n")
            summaries.append({"model": model, "score": None, "error": str(exc)})
            continue

        # Per-model results table
        table = Table(title=f"📊 {model}", show_lines=True)
        table.add_column("Law", style="cyan")
        table.add_column("Score", justify="right")
        for law_name, score in sorted(
            report.per_law_scores.items(), key=lambda x: x[1], reverse=True
        ):
            color = "green" if score >= 0.7 else "yellow" if score >= 0.4 else "red"
            table.add_row(law_name, f"[{color}]{score:.1%}[/{color}]")
        console.print(table)
        console.print(f"  [bold]{report.summary()}[/bold]\n")

        # Save individual result
        safe_name = model.replace("/", "__")
        out_path = os.path.join(connector_dir, f"{safe_name}.json")
        with open(out_path, "w") as f:
            f.write(report.to_json())
        console.print(f"  [dim]Saved → {out_path}[/dim]")

        summaries.append({
            "model": model,
            "score": report.overall_score,
            "passed": report.total_passed,
            "total": report.total_questions,
        })

        if push:
            token = os.environ.get("HF_TOKEN", "")
            if token:
                from lawbreaker.leaderboard import Leaderboard
                try:
                    lb = Leaderboard()
                    path = lb.push_result(report, token)
                    console.print(f"  [green]Pushed → {path}[/green]")
                except Exception as exc:
                    console.print(f"  [yellow]Push failed: {exc}[/yellow]")

    # Final comparison table
    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold cyan]  🏆 Final Leaderboard[/bold cyan]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")

    comp_table = Table(title="🏆 Model Comparison", show_lines=True)
    comp_table.add_column("#", style="dim", justify="right")
    comp_table.add_column("Model", style="cyan")
    comp_table.add_column("Score", justify="right")
    comp_table.add_column("Passed", justify="right")

    ranked = sorted(
        [s for s in summaries if s.get("score") is not None],
        key=lambda x: x["score"], reverse=True
    )
    for i, s in enumerate(ranked, 1):
        pct = s["score"] * 100
        color = "green" if pct >= 70 else "yellow" if pct >= 40 else "red"
        comp_table.add_row(
            str(i), s["model"],
            f"[{color}]{pct:.1f}%[/{color}]",
            f"{s['passed']}/{s['total']}"
        )

    failed = [s for s in summaries if s.get("score") is None]
    for s in failed:
        comp_table.add_row("—", s["model"], "[red]ERROR[/red]", "—")

    console.print(comp_table)

    # Save combined summary
    summary_path = os.path.join(connector_dir, "_leaderboard.json")
    with open(summary_path, "w") as f:
        json.dump(summaries, f, indent=2)
    console.print(f"\n[green]Leaderboard saved to {summary_path}[/green]\n")


@main.command()
@click.option("--law", required=True, help="Law short name")
@click.option("--trap", default=None, help="Trap type (optional)")
@click.option("--difficulty", default="medium", type=click.Choice(["easy", "medium", "hard"]))
@click.option("--seed", default=42, type=int, help="Seed for reproducibility")
def example(law, trap, difficulty, seed):
    """Show an example adversarial question for a specific law."""
    if law not in LAW_REGISTRY:
        console.print(f"[red]Unknown law: {law}[/red]")
        console.print(f"Available: {', '.join(LAW_REGISTRY.keys())}")
        sys.exit(1)

    law_instance = LAW_REGISTRY[law]()
    q = law_instance.generate(difficulty=difficulty, seed=seed)
    console.print(f"\n[bold cyan]📝 Example: {law_instance.LAW_NAME}[/bold cyan]")
    console.print(f"[dim]Trap type:[/dim] {q.trap_type}")
    console.print(f"[dim]Difficulty:[/dim] {q.difficulty}")
    console.print(f"\n[white]{q.question_text}[/white]")
    console.print(f"\n[green]✅ Correct answer:[/green] {q.correct_answer} {q.correct_unit}")
    console.print(f"[yellow]💡 Explanation:[/yellow] {q.explanation}\n")


def _make_connector(connector_type: str, model: str):
    """Factory to create the appropriate connector instance.

    Args:
        connector_type: One of 'openai', 'anthropic', 'huggingface', 'ollama', 'gemini'.
        model: Model identifier string.

    Returns:
        An instantiated connector.
    """
    if connector_type == "openai":
        from lawbreaker.connectors.openai_connector import OpenAIConnector
        return OpenAIConnector(model=model)
    elif connector_type == "anthropic":
        from lawbreaker.connectors.anthropic_connector import AnthropicConnector
        return AnthropicConnector(model=model)
    elif connector_type == "huggingface":
        from lawbreaker.connectors.huggingface_connector import HuggingFaceConnector
        return HuggingFaceConnector(model=model)
    elif connector_type == "ollama":
        from lawbreaker.connectors.ollama_connector import OllamaConnector
        return OllamaConnector(model=model)
    elif connector_type == "gemini":
        from lawbreaker.connectors.gemini_connector import GeminiConnector
        return GeminiConnector(model=model)
    else:
        console.print(f"[red]Unknown connector: {connector_type}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
