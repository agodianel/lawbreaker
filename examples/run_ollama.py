"""
Example: Run LawBreaker benchmark against a local Ollama model.

Usage:
    ollama pull llama3.2
    python examples/run_ollama.py
"""

from lawbreaker.connectors.ollama_connector import OllamaConnector
from lawbreaker.runner import BenchmarkRunner


def main():
    """Run a benchmark against local llama3.2 via Ollama."""
    connector = OllamaConnector(model="llama3.2")
    runner = BenchmarkRunner(connector=connector, n_questions=5, seed=42)
    report = runner.run()

    print(report.summary())
    print(report.to_markdown_table())

    with open("results_ollama.json", "w") as f:
        f.write(report.to_json())
    print("\nResults saved to results_ollama.json")


if __name__ == "__main__":
    main()
