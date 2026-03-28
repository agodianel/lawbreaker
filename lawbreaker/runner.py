"""
BenchmarkRunner — orchestrates a full adversarial physics benchmark run.

Generates questions from all (or selected) laws, queries the LLM via a
connector, verifies answers symbolically, and produces a ``BenchmarkReport``.
"""

from __future__ import annotations

import random
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from lawbreaker.connectors.base import BaseConnector
from lawbreaker.core.question import Question
from lawbreaker.core.result import BenchmarkReport, QuestionResult
from lawbreaker.core.verifier import PhysicsVerifier
from lawbreaker.laws import ALL_LAWS, LAW_REGISTRY
from lawbreaker.laws.base import BaseLaw

console = Console()


class BenchmarkRunner:
    """Runs a full adversarial physics benchmark against an LLM.

    Args:
        connector: LLM connector to query.
        laws: Optional list of law short-names to test (default: all).
        n_questions: Number of questions to generate per law.
        seed: Optional seed for reproducible question generation.
    """

    def __init__(
        self,
        connector: BaseConnector,
        laws: list[str] | None = None,
        n_questions: int = 10,
        seed: Optional[int] = None,
    ):
        """Initialise the benchmark runner.

        Args:
            connector: The LLM connector to use.
            laws: List of law short-names, or None for all laws.
            n_questions: Questions per law.
            seed: Random seed for reproducibility.
        """
        self._connector = connector
        self._n_questions = n_questions
        self._seed = seed
        self._verifier = PhysicsVerifier()

        if laws:
            self._laws: list[BaseLaw] = []
            for name in laws:
                if name in LAW_REGISTRY:
                    self._laws.append(LAW_REGISTRY[name]())
                else:
                    console.print(f"[yellow]Warning: unknown law '{name}', skipping[/yellow]")
        else:
            self._laws = [cls() for cls in ALL_LAWS]

    def run(self) -> BenchmarkReport:
        """Execute the full benchmark and return an aggregated report.

        Generates ``n_questions`` for each selected law, queries the
        connector, verifies each answer, and aggregates results.

        Returns:
            A ``BenchmarkReport`` summarising the run.
        """
        results: list[QuestionResult] = []
        rng = random.Random(self._seed) if self._seed is not None else random.Random()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            for law in self._laws:
                task = progress.add_task(f"Testing {law.LAW_NAME}...", total=self._n_questions)
                for i in range(self._n_questions):
                    q_seed = rng.randint(0, 2**31) if self._seed is not None else None
                    difficulty = rng.choice(["easy", "medium", "hard"])
                    question = law.generate(difficulty=difficulty, seed=q_seed)
                    result = self.run_single(question)
                    results.append(result)
                    progress.advance(task)

        return BenchmarkReport.from_results(self._connector.model_name, results)

    def run_single(self, question: Question) -> QuestionResult:
        """Evaluate a single question against the LLM.

        Queries the connector, extracts the numeric answer, and verifies.
        API errors are caught and recorded as ``error`` status.

        Args:
            question: The question to evaluate.

        Returns:
            A ``QuestionResult`` with the verdict.
        """
        try:
            llm_response = self._connector.query(question.question_text)
        except Exception as exc:
            return QuestionResult(
                question=question,
                llm_response="",
                error=str(exc),
            )

        extracted = self._verifier.extract_numeric(llm_response)
        if extracted is None:
            return QuestionResult(
                question=question,
                llm_response=llm_response,
                extracted_answer=None,
                passed=False,
                error="Could not extract numeric answer from response",
            )

        passed = self._verifier.verify_numeric(
            extracted, question.correct_answer
        )
        return QuestionResult(
            question=question,
            llm_response=llm_response,
            extracted_answer=extracted,
            passed=passed,
        )
