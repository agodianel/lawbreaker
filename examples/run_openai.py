"""Example: Run LawBreaker benchmark against the 2 most recent OpenAI models.

Auto-discovers the latest GPT chat models via the OpenAI Models API,
probes each, and benchmarks all that respond.

Usage:
    export OPENAI_API_KEY="sk-..."
    python examples/run_openai.py
"""

import os
import time

from lawbreaker.connectors.openai_connector import OpenAIConnector
from lawbreaker.runner import BenchmarkRunner

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(_SCRIPT_DIR, "results", "openai")
N_QUESTIONS = 5
SEED = 42


def _probe_model(model: str) -> bool:
    """Send a trivial question to check if the model responds."""
    try:
        connector = OpenAIConnector(model=model)
        connector.query("What is 1+1?")
        return True
    except Exception as exc:
        print(f"  !! {model} probe failed: {exc}")
        return False


def main():
    """Discover and benchmark the 2 most recent OpenAI models."""
    os.makedirs(OUT_DIR, exist_ok=True)

    print("Discovering most recent OpenAI GPT models...")
    candidates = OpenAIConnector.discover_models(limit=10)
    if not candidates:
        print("No models found. Check your OPENAI_API_KEY.")
        return
    print(f"Found {len(candidates)} candidate(s), probing for working models...\n")

    # Probe candidates until we find enough working models
    models: list[str] = []
    for model in candidates:
        print(f"  Probing {model} ...")
        if _probe_model(model):
            print(f"  ✓ {model} is accessible")
            models.append(model)
            if len(models) >= 2:
                break
        print()

    if not models:
        print("\nNo accessible models found.")
        return
    print(f"\n{len(models)} working model(s): {', '.join(models)}\n")

    for i, model in enumerate(models):
        safe_name = model.replace("/", "__")
        out_path = os.path.join(OUT_DIR, f"{safe_name}.json")

        print(f"[{i + 1}/{len(models)}] Benchmarking {model} ...")
        try:
            connector = OpenAIConnector(model=model)
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
