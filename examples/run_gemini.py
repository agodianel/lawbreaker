"""Example: Run LawBreaker benchmark against the 2 most recent Gemini models.

Auto-discovers the latest Gemini model versions via the API,
probes each, and benchmarks all that respond.

Usage:
    export GEMINI_API_KEY="AIza..."
    python examples/run_gemini.py
"""

import os
import time

from lawbreaker.connectors.gemini_connector import GeminiConnector
from lawbreaker.runner import BenchmarkRunner

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(_SCRIPT_DIR, "results", "gemini")
N_QUESTIONS = 5
SEED = 42
DELAY = 2.5


def _probe_model(model: str) -> bool:
    """Send a trivial question to check if the model responds."""
    try:
        connector = GeminiConnector(model=model)
        connector.query("What is 1+1?")
        return True
    except Exception as exc:
        print(f"  !! {model} probe failed: {exc}")
        return False


def main():
    """Discover and benchmark the 2 most recent Gemini models."""
    os.makedirs(OUT_DIR, exist_ok=True)

    print("Discovering most recent Gemini models...")
    candidates = GeminiConnector.discover_models(recent_only=True)
    if not candidates:
        print("No models found. Check your GEMINI_API_KEY.")
        return
    print(f"Found {len(candidates)} candidate(s), probing for working models...\n")

    # Probe all candidates and keep the ones that respond
    models: list[str] = []
    for model in candidates:
        print(f"  Probing {model} ...")
        if _probe_model(model):
            print(f"  ✓ {model} is accessible")
            models.append(model)
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
            connector = GeminiConnector(model=model)
            runner = BenchmarkRunner(
                connector=connector, n_questions=N_QUESTIONS, seed=SEED,
                delay=DELAY,
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
