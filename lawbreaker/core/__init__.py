"""
Core module — data structures and symbolic verification engine.
"""

from lawbreaker.core.question import Question
from lawbreaker.core.result import QuestionResult, BenchmarkReport
from lawbreaker.core.uncertainty import (
    benjamini_hochberg,
    compute_error_stats,
    compute_relative_error,
    two_proportion_z_test,
    wilson_ci,
)
from lawbreaker.core.verifier import PhysicsVerifier

__all__ = [
    "Question",
    "QuestionResult",
    "BenchmarkReport",
    "PhysicsVerifier",
    "wilson_ci",
    "compute_relative_error",
    "compute_error_stats",
    "two_proportion_z_test",
    "benjamini_hochberg",
]
