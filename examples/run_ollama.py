"""
Example: Run LawBreaker benchmark against a local Ollama model.

Usage:
    ollama pull llama3.2
    python examples/run_ollama.py
"""

import os

from lawbreaker.connectors.ollama_connector import OllamaConnector
from lawbreaker.runner import BenchmarkRunner

MODEL = "llama3.2"


def main():
    """Run a benchmark against local llama3.2 via Ollama."""
    connector = OllamaConnector(model=MODEL)
    runner = BenchmarkRunner(connector=connector, n_questions=5, seed=42)
    report = runner.run()

    print(report.summary())
    print(report.to_markdown_table())

    # Save results — filename derived from model name
    safe_name = MODEL.replace("/", "__")
    out_dir = "results/ollama"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{safe_name}.json")
    with open(out_path, "w") as f:
        f.write(report.to_json())
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
