"""Example: Run LawBreaker benchmark against recent HuggingFace models.

Benchmarks a curated list of recent open models on HF Inference API.
If a model returns an API error on a probe question, it is skipped.

Usage:
    export HF_TOKEN="hf_..."
    python examples/run_huggingface.py
"""

import os
import time

from lawbreaker.connectors.huggingface_connector import HuggingFaceConnector
from lawbreaker.runner import BenchmarkRunner

# Recent flagship open models
MODELS = [
    "meta-llama/Llama-3.1-8B-Instruct",
    "meta-llama/Llama-4-Scout-17B-16E-Instruct",
]
OUT_DIR = "results/huggingface"
N_QUESTIONS = 5
SEED = 42


def _probe_model(model: str) -> bool:
    """Send a trivial question to check if the model responds."""
    try:
        connector = HuggingFaceConnector(model=model)
        connector.query("What is 1+1?")
        return True
    except Exception:
        return False


def main():
    """Benchmark recent HuggingFace models."""
    os.makedirs(OUT_DIR, exist_ok=True)

    for i, model in enumerate(MODELS):
        safe_name = model.replace("/", "__")
        out_path = os.path.join(OUT_DIR, f"{safe_name}.json")

        print(f"[{i + 1}/{len(MODELS)}] Probing {model} ...")
        if not _probe_model(model):
            print(f"  !! {model} returned an error, skipping.\n")
            continue

        print(f"  Benchmarking {model} ...")
        try:
            connector = HuggingFaceConnector(model=model)
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

        if i < len(MODELS) - 1:
            time.sleep(2)

    print("Done.")


if __name__ == "__main__":
    main()
