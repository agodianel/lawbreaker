"""Example: Run LawBreaker benchmark against recent local Ollama models.

Benchmarks a curated list of recent models via Ollama.  If a model
returns an error on a probe question, it is skipped immediately.

Usage:
    ollama pull llama3.2
    ollama pull gemma3
    python examples/run_ollama.py
"""

import os
import time

from lawbreaker.connectors.ollama_connector import OllamaConnector
from lawbreaker.runner import BenchmarkRunner

# Recent models to benchmark
MODELS = [
    "llama3.2",
    "gemma3",
]
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(_SCRIPT_DIR, "results", "ollama")
N_QUESTIONS = 5
SEED = 42


def _probe_model(model: str) -> bool:
    """Send a trivial question to check if the model responds."""
    try:
        connector = OllamaConnector(model=model)
        connector.query("What is 1+1?")
        return True
    except Exception:
        return False


def main():
    """Benchmark recent Ollama models."""
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
            connector = OllamaConnector(model=model)
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
