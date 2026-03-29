"""
Example: Run LawBreaker benchmark against OpenAI GPT-4o.

Usage:
    export OPENAI_API_KEY="sk-..."
    python examples/run_openai.py
"""

import os

from lawbreaker.connectors.openai_connector import OpenAIConnector
from lawbreaker.runner import BenchmarkRunner

MODEL = "gpt-4o"


def main():
    """Run a benchmark against GPT-4o and print results."""
    connector = OpenAIConnector(model=MODEL)
    runner = BenchmarkRunner(connector=connector, n_questions=5, seed=42)
    report = runner.run()

    print(report.summary())
    print(report.to_markdown_table())

    # Save results — filename derived from model name
    safe_name = MODEL.replace("/", "__")
    out_dir = "results/openai"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{safe_name}.json")
    with open(out_path, "w") as f:
        f.write(report.to_json())
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
