"""
Example: Run LawBreaker benchmark against OpenAI GPT-4o.

Usage:
    export OPENAI_API_KEY="sk-..."
    python examples/run_openai.py
"""

from lawbreaker.connectors.openai_connector import OpenAIConnector
from lawbreaker.runner import BenchmarkRunner


def main():
    """Run a benchmark against GPT-4o and print results."""
    connector = OpenAIConnector(model="gpt-4o")
    runner = BenchmarkRunner(connector=connector, n_questions=5, seed=42)
    report = runner.run()

    print(report.summary())
    print(report.to_markdown_table())

    # Save results to connector-specific directory
    import os
    os.makedirs("results/openai", exist_ok=True)
    with open("results/openai/gpt-4o.json", "w") as f:
        f.write(report.to_json())
    print("\nResults saved to results/openai/gpt-4o.json")


if __name__ == "__main__":
    main()
