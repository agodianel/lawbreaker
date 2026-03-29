"""Example: Run LawBreaker benchmark against the 2 most recent Anthropic models.

Auto-discovers the latest Claude models via the Anthropic Models API,
probes each, and benchmarks all that respond.

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python examples/run_anthropic.py
"""

import os
import time

from lawbreaker.connectors.anthropic_connector import AnthropicConnector
from lawbreaker.runner import BenchmarkRunner

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(_SCRIPT_DIR, "results", "anthropic")
N_QUESTIONS = 5
SEED = 42


def _probe_model(model: str) -> bool:
    """Send a trivial question to check if the model responds."""
    try:
        connector = AnthropicConnector(model=model)
        connector.query("What is 1+1?")
        return True
    except Exception:
        return False


def main():
    """Discover and benchmark the 2 most recent Anthropic models."""
    os.makedirs(OUT_DIR, exist_ok=True)

    print("Discovering most recent Anthropic Claude models...")
    models = AnthropicConnector.discover_models(limit=2)
    if not models:
        print("No models found. Check your ANTHROPIC_API_KEY.")
        return
    print(f"Found {len(models)} model(s): {', '.join(models)}\n")

    for i, model in enumerate(models):
        safe_name = model.replace("/", "__")
        out_path = os.path.join(OUT_DIR, f"{safe_name}.json")

        print(f"[{i + 1}/{len(models)}] Probing {model} ...")
        if not _probe_model(model):
            print(f"  !! {model} returned an error, skipping.\n")
            continue

        print(f"  Benchmarking {model} ...")
        try:
            connector = AnthropicConnector(model=model)
            runner = BenchmarkRunner(
                connector=connector, n_questions=N_QUESTIONS, seed=SEED
            )
            report = runner.run()

            print(report.summary())
            print(report.to_markdown_table())

            with open(out_path, "w") as f:
                f.write(report.to_json())
            print(f"  -> Saved to {out_path}\n")
        except Exception as exc:
            print(f"  !! Failed: {exc}\n")

        if i < len(models) - 1:
            time.sleep(2)

    print("Done.")


if __name__ == "__main__":
    main()
