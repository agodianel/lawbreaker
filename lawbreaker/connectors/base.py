"""
BaseConnector — abstract interface that all LLM connectors must implement.
"""

from abc import ABC, abstractmethod

SYSTEM_PROMPT = (
    "You are a physics expert. Answer the following question with ONLY the numerical "
    'answer and its unit. Format: "<number> <unit>". Do not show working.\n'
    'Example: "10.5 V" or "9.81 N" or "300 K"'
)


class BaseConnector(ABC):
    """Abstract base for LLM API connectors.

    Every connector must implement ``query`` (send question, get answer)
    and expose a ``model_name`` property.
    """

    @abstractmethod
    def query(self, question_text: str, system_prompt: str = SYSTEM_PROMPT) -> str:
        """Send a question to the LLM and return the raw text response.

        Args:
            question_text: The physics question to ask.
            system_prompt: System-level instruction for answer formatting.

        Returns:
            Raw string response from the model.
        """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the identifier of the model being queried.

        Examples: ``'gpt-4o'``, ``'claude-3-5-sonnet'``,
        ``'meta-llama/Llama-3.1-8B-Instruct'``.
        """
