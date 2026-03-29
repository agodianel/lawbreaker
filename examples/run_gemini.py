"""
Example: Run LawBreaker benchmark against recent Google Gemini models.

Discovers the two most recent Gemini model versions via the API
and benchmarks each one.  If a model returns an API error on its
first question, it is skipped immediately to save quota.

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
DELAY = 1.0
DELAY_BETWEEN_MODELS = 5  # seconds between models to avoid rate limits


def _probe_model(model: str) -> bool:
    """Send a single trivial question to check if the model responds."""
    try:
        connector = GeminiConnector(model=model)
        connector.query("What is 1+1?")
        return True
    except Exception:
        return False


def main():
    """Discover recent Gemini models and benchmark each one."""
    print("Discovering available Gemini models (recent versions only)...")
    models = GeminiConnector.discover_models(recent_only=True)
    print(f"Found {len(models)} model(s): {', '.join(models)}\n")

    os.makedirs(OUT_DIR, exist_ok=True)

    for i, model in enumerate(models):
        safe_name = model.replace("/", "__")
        out_path = os.path.join(OUT_DIR, f"{safe_name}.json")

        # Quick probe — skip immediately if the model errors out
        print(f"[{i + 1}/{len(models)}] Probing {model} ...")
        if not _probe_model(model):
            print(f"  !! {model} returned an error, skipping.\n")
            continue

        print(f"  Benchmarking {model} ...")
        try:
            connector = GeminiConnector(model=model)
            runner = BenchmarkRunner(
                connector=connector, n_questions=N_QUESTIONS, seed=SEED,
                delay=DELAY,
            )
            report = runner.run()

            print(report.summary())

            with open(out_path, "w") as f:
                f.write(report.to_json())
            print(f"  -> Saved to {out_path}\n")
        except Exception as exc:
            print(f"  !! Failed: {exc}\n")

        if i < len(models) - 1:
            time.sleep(DELAY_BETWEEN_MODELS)

    print("Done.")


if __name__ == "__main__":
    main()
