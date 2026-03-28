"""
Core module — data structures and symbolic verification engine.
"""

from lawbreaker.core.question import Question
from lawbreaker.core.result import QuestionResult, BenchmarkReport
from lawbreaker.core.verifier import PhysicsVerifier

__all__ = ["Question", "QuestionResult", "BenchmarkReport", "PhysicsVerifier"]
