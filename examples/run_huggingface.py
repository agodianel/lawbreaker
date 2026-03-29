"""
Example: Run LawBreaker benchmark against HuggingFace Inference API.

Usage:
    export HF_TOKEN="hf_..."
    python examples/run_huggingface.py
"""

import os

from lawbreaker.connectors.huggingface_connector import HuggingFaceConnector
from lawbreaker.runner import BenchmarkRunner

MODEL = "meta-llama/Llama-3.1-8B-Instruct"


def main():
    """Run a benchmark against Llama 3.1 8B via HF Inference API."""
    connector = HuggingFaceConnector(model=MODEL)
    runner = BenchmarkRunner(connector=connector, n_questions=5, seed=42)
    report = runner.run()

    print(report.summary())
    print(report.to_markdown_table())

    # Save results — filename derived from model name
    safe_name = MODEL.replace("/", "__")
    out_dir = "results/huggingface"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{safe_name}.json")
    with open(out_path, "w") as f:
        f.write(report.to_json())
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
