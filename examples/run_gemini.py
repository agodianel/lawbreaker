"""
Example: Run LawBreaker benchmark against ALL available Google Gemini models.

Discovers models via the Gemini API and benchmarks each one.

Usage:
    export GEMINI_API_KEY="AIza..."
    python examples/run_gemini.py
"""

import os
import time

from lawbreaker.connectors.gemini_connector import GeminiConnector
from lawbreaker.runner import BenchmarkRunner

OUT_DIR = "results/gemini"
N_QUESTIONS = 5
SEED = 42
DELAY_BETWEEN_MODELS = 2  # seconds between models to avoid rate limits


def main():
    """Discover all Gemini models and run benchmarks against each."""
    print("Discovering available Gemini models...")
    models = GeminiConnector.discover_models()
    print(f"Found {len(models)} model(s): {', '.join(models)}\n")

    os.makedirs(OUT_DIR, exist_ok=True)

    for i, model in enumerate(models):
        safe_name = model.replace("/", "__")
        out_path = os.path.join(OUT_DIR, f"{safe_name}.json")

        print(f"[{i + 1}/{len(models)}] Benchmarking {model} ...")
        try:
            connector = GeminiConnector(model=model)
            runner = BenchmarkRunner(
                connector=connector, n_questions=N_QUESTIONS, seed=SEED
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
