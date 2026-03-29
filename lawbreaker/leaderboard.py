"""
Leaderboard — push and pull benchmark results to/from a HuggingFace Dataset.

Results are stored as JSON files under ``results/`` in the HF dataset repo.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from lawbreaker.core.result import BenchmarkReport


class Leaderboard:
    """HuggingFace Dataset-backed leaderboard for LawBreaker results."""

    DATASET_REPO = "diago01/llm-physics-law-breaker"

    def push_result(self, report: BenchmarkReport, token: str) -> str:
        """Push a benchmark report to the HuggingFace Dataset.

        Args:
            report: The benchmark report to upload.
            token: HuggingFace API token with write access.

        Returns:
            The remote file path of the uploaded result.

        Raises:
            RuntimeError: On upload failure.
        """
        try:
            from huggingface_hub import HfApi

            api = HfApi(token=token)
            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", report.model_name)
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
            remote_path = f"results/{safe_name}_{ts}.json"

            api.upload_file(
                path_or_fileobj=report.to_json().encode("utf-8"),
                path_in_repo=remote_path,
                repo_id=self.DATASET_REPO,
                repo_type="dataset",
            )
            return remote_path
        except Exception as exc:
            raise RuntimeError(f"Failed to push result: {exc}") from exc

    def pull_results(self) -> list[BenchmarkReport]:
        """Download all result JSONs from the HuggingFace Dataset.

        Returns:
            List of ``BenchmarkReport`` objects parsed from JSON.
        """
        try:
            from huggingface_hub import HfApi

            api = HfApi()
            files = api.list_repo_files(self.DATASET_REPO, repo_type="dataset")
            json_files = [f for f in files if f.startswith("results/") and f.endswith(".json")]

            reports: list[BenchmarkReport] = []
            for path in json_files:
                url = f"https://huggingface.co/datasets/{self.DATASET_REPO}/resolve/main/{path}"
                import requests
                resp = requests.get(url, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                report = BenchmarkReport(
                    model_name=data.get("model_name", ""),
                    timestamp=data.get("timestamp", ""),
                    total_questions=data.get("total_questions", 0),
                    total_passed=data.get("total_passed", 0),
                    overall_score=data.get("overall_score", 0.0),
                    per_law_scores=data.get("per_law_scores", {}),
                    per_trap_scores=data.get("per_trap_scores", {}),
                    worst_law=data.get("worst_law", ""),
                    worst_trap=data.get("worst_trap", ""),
                )
                reports.append(report)
            return reports
        except Exception:
            return []

    def render_table(self, reports: list[BenchmarkReport]) -> str:
        """Render a markdown leaderboard table sorted by overall score.

        Args:
            reports: List of benchmark reports.

        Returns:
            Markdown-formatted table string.
        """
        sorted_reports = sorted(reports, key=lambda r: r.overall_score, reverse=True)
        lines = [
            "# 🏆 LawBreaker Leaderboard",
            "",
            "| Rank | Model | Score | Questions | Worst Law | Worst Trap |",
            "| ---- | ----- | ----- | --------- | --------- | ---------- |",
        ]
        for i, r in enumerate(sorted_reports, 1):
            lines.append(
                f"| {i} | {r.model_name} | {r.overall_score:.1%} | "
                f"{r.total_questions} | {r.worst_law} | {r.worst_trap} |"
            )
        return "\n".join(lines)
