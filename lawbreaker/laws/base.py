"""
BaseLaw — abstract base class for all physics law implementations.

Every law must be able to generate adversarial questions and verify
answers symbolically.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.core.verifier import PhysicsVerifier


class BaseLaw(ABC):
    """Abstract base for physics law question generators.

    Subclasses implement ``generate`` to produce adversarial questions
    and ``verify`` to check LLM answers using symbolic math.

    Class Attributes:
        LAW_NAME: Human-readable law name.
        TOLERANCE: Relative tolerance for answer verification (default 1%).
    """

    LAW_NAME: str = ""
    TOLERANCE: float = 0.01

    def __init__(self) -> None:
        """Initialise the law with a shared verifier instance."""
        self._verifier = PhysicsVerifier()

    @abstractmethod
    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate a single adversarial question.

        Args:
            difficulty: One of ``"easy"``, ``"medium"``, ``"hard"``.
            seed: Optional random seed for reproducibility.

        Returns:
            A fully populated ``Question`` object.
        """

    def verify(self, answer: float, question: Question) -> bool:
        """Check whether the given answer is correct for the question.

        Uses the shared PhysicsVerifier with this law's tolerance.

        Args:
            answer: Numeric answer to check.
            question: The Question containing the correct answer.

        Returns:
            True if the answer is within ``TOLERANCE`` of the correct value.
        """
        return self._verifier.verify_numeric(
            answer, question.correct_answer, self.TOLERANCE
        )

    def _rng(self, seed: Optional[int] = None) -> random.Random:
        """Return a seeded Random instance for reproducible generation.

        Args:
            seed: Optional seed value. If None, uses system entropy.

        Returns:
            A ``random.Random`` instance.
        """
        return random.Random(seed)
