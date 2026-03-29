"""Example: Run LawBreaker benchmark against ALL available HuggingFace models.

Auto-discovers warm inference models on HuggingFace, probes each,
and benchmarks all that respond. Uses a 5s delay between API calls.

Usage:
    export HF_TOKEN="hf_..."
    python examples/run_huggingface.py
"""

import os
import time

from lawbreaker.connectors.huggingface_connector import HuggingFaceConnector
from lawbreaker.runner import BenchmarkRunner

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(_SCRIPT_DIR, "results", "huggingface")
N_QUESTIONS = 5
SEED = 42
DELAY = 5.0


def _probe_model(model: str) -> bool:
    """Send a trivial question to check if the model responds."""
    try:
        connector = HuggingFaceConnector(model=model)
        connector.query("What is 1+1?")
        return True
    except Exception:
        return False


def main():
    """Discover and benchmark all available HuggingFace models."""
    os.makedirs(OUT_DIR, exist_ok=True)

    print("Discovering available HuggingFace inference models...")
    models = HuggingFaceConnector.discover_models()
    if not models:
        print("No models found. Check your HF_TOKEN.")
        return
    print(f"Found {len(models)} models.\n")

    for i, model in enumerate(models):
        safe_name = model.replace("/", "__")
        out_path = os.path.join(OUT_DIR, f"{safe_name}.json")

        print(f"[{i + 1}/{len(models)}] Probing {model} ...")
        if not _probe_model(model):
            print(f"  !! {model} returned an error, skipping.\n")
            continue

        print(f"  Benchmarking {model} ...")
        try:
            connector = HuggingFaceConnector(model=model)
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
