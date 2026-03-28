"""
Result dataclasses — QuestionResult and BenchmarkReport.

QuestionResult wraps a single question + LLM answer + pass/fail verdict.
BenchmarkReport aggregates all results for a full benchmark run with
per-law and per-trap scoring breakdowns.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from lawbreaker.core.question import Question


@dataclass
class QuestionResult:
    """Result of evaluating a single question against an LLM.

    Attributes:
        question: The original Question object.
        llm_response: Raw string returned by the LLM.
        extracted_answer: Numeric value parsed from llm_response, or None.
        passed: Whether the LLM answered correctly within tolerance.
        error: If an API or parsing error occurred, the message.
    """

    question: Question
    llm_response: str = ""
    extracted_answer: Optional[float] = None
    passed: bool = False
    error: Optional[str] = None

    @property
    def status(self) -> str:
        """Return human-readable status: 'pass', 'fail', or 'error'."""
        if self.error:
            return "error"
        return "pass" if self.passed else "fail"

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "question": self.question.to_dict(),
            "llm_response": self.llm_response,
            "extracted_answer": self.extracted_answer,
            "passed": self.passed,
            "error": self.error,
            "status": self.status,
        }


@dataclass
class BenchmarkReport:
    """Aggregated results of a complete benchmark run.

    Attributes:
        model_name: Identifier of the model tested.
        timestamp: ISO 8601 timestamp of when the run completed.
        total_questions: Number of questions asked.
        total_passed: Number of questions answered correctly.
        overall_score: Pass rate as a float 0.0–1.0.
        per_law_scores: Mapping of law name → pass rate.
        per_trap_scores: Mapping of trap type → pass rate.
        worst_law: The law with the lowest pass rate.
        worst_trap: The trap type with the lowest pass rate.
        questions: Full list of individual QuestionResult objects.
    """

    model_name: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    total_questions: int = 0
    total_passed: int = 0
    overall_score: float = 0.0
    per_law_scores: dict[str, float] = field(default_factory=dict)
    per_trap_scores: dict[str, float] = field(default_factory=dict)
    worst_law: str = ""
    worst_trap: str = ""
    questions: list[QuestionResult] = field(default_factory=list)

    @classmethod
    def from_results(
        cls, model_name: str, results: list[QuestionResult]
    ) -> "BenchmarkReport":
        """Build a BenchmarkReport by aggregating a list of QuestionResults.

        Computes per-law scores, per-trap scores, identifies worst performers,
        and calculates overall pass rate.
        """
        total = len(results)
        passed = sum(1 for r in results if r.passed)

        # Per-law aggregation
        law_totals: dict[str, int] = defaultdict(int)
        law_passed: dict[str, int] = defaultdict(int)
        for r in results:
            law_totals[r.question.law] += 1
            if r.passed:
                law_passed[r.question.law] += 1
        per_law = {
            law: (law_passed[law] / law_totals[law]) if law_totals[law] else 0.0
            for law in law_totals
        }

        # Per-trap aggregation
        trap_totals: dict[str, int] = defaultdict(int)
        trap_passed: dict[str, int] = defaultdict(int)
        for r in results:
            trap_totals[r.question.trap_type] += 1
            if r.passed:
                trap_passed[r.question.trap_type] += 1
        per_trap = {
            trap: (trap_passed[trap] / trap_totals[trap]) if trap_totals[trap] else 0.0
            for trap in trap_totals
        }

        worst_law = min(per_law, key=per_law.get) if per_law else ""
        worst_trap = min(per_trap, key=per_trap.get) if per_trap else ""
        best_law = max(per_law, key=per_law.get) if per_law else ""

        report = cls(
            model_name=model_name,
            total_questions=total,
            total_passed=passed,
            overall_score=passed / total if total else 0.0,
            per_law_scores=per_law,
            per_trap_scores=per_trap,
            worst_law=worst_law,
            worst_trap=worst_trap,
            questions=results,
        )
        report._best_law = best_law
        return report

    def to_json(self) -> str:
        """Serialize the full report to a JSON string."""
        data = {
            "model_name": self.model_name,
            "timestamp": self.timestamp,
            "total_questions": self.total_questions,
            "total_passed": self.total_passed,
            "overall_score": self.overall_score,
            "per_law_scores": self.per_law_scores,
            "per_trap_scores": self.per_trap_scores,
            "worst_law": self.worst_law,
            "worst_trap": self.worst_trap,
            "questions": [q.to_dict() for q in self.questions],
        }
        return json.dumps(data, indent=2)

    def to_markdown_table(self) -> str:
        """Render a markdown table of per-law and per-trap scores."""
        lines = [
            f"# LawBreaker Benchmark — {self.model_name}",
            "",
            f"**Overall Score:** {self.overall_score:.1%} "
            f"({self.total_passed}/{self.total_questions})",
            "",
            "## Per-Law Scores",
            "",
            "| Law | Score |",
            "| --- | ----- |",
        ]
        for law, score in sorted(
            self.per_law_scores.items(), key=lambda x: x[1], reverse=True
        ):
            lines.append(f"| {law} | {score:.1%} |")

        lines += [
            "",
            "## Per-Trap Scores",
            "",
            "| Trap Type | Score |",
            "| --------- | ----- |",
        ]
        for trap, score in sorted(
            self.per_trap_scores.items(), key=lambda x: x[1], reverse=True
        ):
            lines.append(f"| {trap} | {score:.1%} |")

        return "\n".join(lines)

    def summary(self) -> str:
        """One-line human-readable summary of the benchmark run."""
        best_law = getattr(self, "_best_law", "")
        if not best_law and self.per_law_scores:
            best_law = max(self.per_law_scores, key=self.per_law_scores.get)

        worst_law_score = self.per_law_scores.get(self.worst_law, 0.0)
        worst_trap_score = self.per_trap_scores.get(self.worst_trap, 0.0)
        best_law_score = self.per_law_scores.get(best_law, 0.0)

        return (
            f"{self.model_name} scored {self.overall_score:.1%} overall. "
            f"Worst law: {self.worst_law} ({worst_law_score:.0%}). "
            f"Worst trap: {self.worst_trap} ({worst_trap_score:.0%}). "
            f"Best law: {best_law} ({best_law_score:.0%})."
        )
