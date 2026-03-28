"""
Anthropic connector — queries the Anthropic Messages API.

Supports ``api_key`` constructor param or ``ANTHROPIC_API_KEY`` env var.
"""

from __future__ import annotations
import os
from lawbreaker.connectors.base import BaseConnector, SYSTEM_PROMPT


class AnthropicConnector(BaseConnector):
    """Connector for Anthropic models (Claude 3.5 Sonnet, etc.)."""

    def __init__(self, model: str = "claude-3-5-sonnet-20241022", api_key: str | None = None):
        """Initialise the Anthropic connector.

        Args:
            model: Model identifier.
            api_key: Optional API key; falls back to ``ANTHROPIC_API_KEY``.
        """
        self._model = model
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")

    @property
    def model_name(self) -> str:
        """Return the model identifier."""
        return self._model

    def query(self, question_text: str, system_prompt: str = SYSTEM_PROMPT) -> str:
        """Query the Anthropic Messages API.

        Args:
            question_text: The question to send.
            system_prompt: System prompt for formatting.

        Returns:
            The model's text response.

        Raises:
            RuntimeError: On API failure.
        """
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self._api_key)
            message = client.messages.create(
                model=self._model,
                max_tokens=100,
                system=system_prompt,
                messages=[{"role": "user", "content": question_text}],
            )
            return message.content[0].text.strip()
        except Exception as exc:
            raise RuntimeError(f"Anthropic API error: {exc}") from exc
