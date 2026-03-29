"""
Example: Run LawBreaker benchmark against Anthropic Claude.

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python examples/run_anthropic.py
"""

import os

from lawbreaker.connectors.anthropic_connector import AnthropicConnector
from lawbreaker.runner import BenchmarkRunner

MODEL = "claude-sonnet-4-20250514"


def main():
    """Run a benchmark against Claude and print results."""
    connector = AnthropicConnector(model=MODEL)
    runner = BenchmarkRunner(connector=connector, n_questions=5, seed=42)
    report = runner.run()

    print(report.summary())
    print(report.to_markdown_table())

    # Save results — filename derived from model name
    safe_name = MODEL.replace("/", "__")
    out_dir = "results/anthropic"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{safe_name}.json")
    with open(out_path, "w") as f:
        f.write(report.to_json())
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
