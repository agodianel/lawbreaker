"""
Example: Run LawBreaker benchmark against HuggingFace Inference API.

Usage:
    export HF_TOKEN="hf_..."
    python examples/run_huggingface.py
"""

from lawbreaker.connectors.huggingface_connector import HuggingFaceConnector
from lawbreaker.runner import BenchmarkRunner


def main():
    """Run a benchmark against Llama 3.1 8B via HF Inference API."""
    connector = HuggingFaceConnector(
        model="meta-llama/Llama-3.1-8B-Instruct"
    )
    runner = BenchmarkRunner(connector=connector, n_questions=5, seed=42)
    report = runner.run()

    print(report.summary())
    print(report.to_markdown_table())

    with open("results_huggingface.json", "w") as f:
        f.write(report.to_json())
    print("\nResults saved to results_huggingface.json")


if __name__ == "__main__":
    main()
