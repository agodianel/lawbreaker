"""
OpenAI connector — queries OpenAI chat completion API.

Supports ``api_key`` constructor param or ``OPENAI_API_KEY`` env var.
"""

from __future__ import annotations
import os
from lawbreaker.connectors.base import BaseConnector, SYSTEM_PROMPT


class OpenAIConnector(BaseConnector):
    """Connector for OpenAI models (GPT-4o, etc.)."""

    def __init__(self, model: str = "gpt-4o", api_key: str | None = None):
        """Initialise the OpenAI connector.

        Args:
            model: Model identifier, e.g. ``'gpt-4o'``.
            api_key: Optional API key; falls back to ``OPENAI_API_KEY``.
        """
        self._model = model
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "")

    @property
    def model_name(self) -> str:
        """Return the model identifier."""
        return self._model

    def query(self, question_text: str, system_prompt: str = SYSTEM_PROMPT) -> str:
        """Query the OpenAI chat completions API.

        Args:
            question_text: The question to send.
            system_prompt: System prompt for formatting.

        Returns:
            The model's text response.

        Raises:
            RuntimeError: On API failure.
        """
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self._api_key)
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question_text},
                ],
                temperature=0.0,
                max_tokens=100,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            raise RuntimeError(f"OpenAI API error: {exc}") from exc
