"""
Example: Run LawBreaker benchmark against Anthropic Claude.

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python examples/run_anthropic.py
"""

from lawbreaker.connectors.anthropic_connector import AnthropicConnector
from lawbreaker.runner import BenchmarkRunner


def main():
    """Run a benchmark against Claude and print results."""
    connector = AnthropicConnector(model="claude-sonnet-4-20250514")
    runner = BenchmarkRunner(connector=connector, n_questions=5, seed=42)
    report = runner.run()

    print(report.summary())
    print(report.to_markdown_table())

    # Save results to connector-specific directory
    import os
    os.makedirs("results/anthropic", exist_ok=True)
    with open("results/anthropic/claude-sonnet-4.json", "w") as f:
        f.write(report.to_json())
    print("\nResults saved to results/anthropic/claude-sonnet-4.json")


if __name__ == "__main__":
    main()
