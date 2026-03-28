"""
Question dataclass — represents a single adversarial physics question.

Each question embeds a trap designed to mislead LLMs (anchoring bias,
unit confusion, Celsius vs Kelvin, sign errors, etc.).
"""

from dataclasses import dataclass, field
from typing import Any
import uuid


@dataclass
class Question:
    """A single adversarial physics question with embedded trap.

    Attributes:
        id: Unique identifier (UUID4).
        law: Human-readable law name, e.g. "Ohm's Law".
        trap_type: Category of adversarial trap embedded in the question.
        question_text: The full question string shown to the LLM.
        correct_answer: The numerically correct answer computed via sympy.
        correct_unit: Expected unit string, e.g. "V", "N", "J".
        variables: Dictionary of variable names to values used in generation.
        difficulty: One of "easy", "medium", "hard".
        explanation: Human-readable explanation of why this is a trap.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    law: str = ""
    trap_type: str = ""
    question_text: str = ""
    correct_answer: float = 0.0
    correct_unit: str = ""
    variables: dict[str, Any] = field(default_factory=dict)
    difficulty: str = "medium"
    explanation: str = ""

    def to_dict(self) -> dict:
        """Serialize the question to a plain dictionary."""
        return {
            "id": self.id,
            "law": self.law,
            "trap_type": self.trap_type,
            "question_text": self.question_text,
            "correct_answer": self.correct_answer,
            "correct_unit": self.correct_unit,
            "variables": self.variables,
            "difficulty": self.difficulty,
            "explanation": self.explanation,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Question":
        """Deserialize a question from a dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
