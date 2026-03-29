"""
Example: Run LawBreaker benchmark against Google Gemini.

Usage:
    export GEMINI_API_KEY="AIza..."
    python examples/run_gemini.py
"""

from lawbreaker.connectors.gemini_connector import GeminiConnector
from lawbreaker.runner import BenchmarkRunner


def main():
    """Run a benchmark against Gemini 2.0 Flash and print results."""
    connector = GeminiConnector(model="gemini-2.0-flash")
    runner = BenchmarkRunner(connector=connector, n_questions=5, seed=42)
    report = runner.run()

    print(report.summary())
    print(report.to_markdown_table())

    # Save results to connector-specific directory
    import os
    os.makedirs("results/gemini", exist_ok=True)
    with open("results/gemini/gemini-2.0-flash.json", "w") as f:
        f.write(report.to_json())
    print("\nResults saved to results/gemini/gemini-2.0-flash.json")


if __name__ == "__main__":
    main()
