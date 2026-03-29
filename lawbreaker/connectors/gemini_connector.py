"""
Google Gemini connector — queries the Gemini API via the Google GenAI SDK.

Supports ``api_key`` constructor param or ``GEMINI_API_KEY`` env var.
"""

from __future__ import annotations
import os
from lawbreaker.connectors.base import BaseConnector, SYSTEM_PROMPT


class GeminiConnector(BaseConnector):
    """Connector for Google Gemini models (Gemini 2.0 Flash, etc.)."""

    def __init__(self, model: str = "gemini-2.0-flash", api_key: str | None = None):
        """Initialise the Gemini connector.

        Args:
            model: Model identifier, e.g. ``'gemini-2.0-flash'``.
            api_key: Optional API key; falls back to ``GEMINI_API_KEY``.
        """
        self._model = model
        self._api_key = api_key or os.environ.get("GEMINI_API_KEY", "")

    @property
    def model_name(self) -> str:
        """Return the model identifier."""
        return self._model

    def query(self, question_text: str, system_prompt: str = SYSTEM_PROMPT) -> str:
        """Query the Google Gemini API.

        Args:
            question_text: The question to send.
            system_prompt: System prompt for formatting.

        Returns:
            The model's text response.

        Raises:
            RuntimeError: On API failure.
        """
        try:
            from google import genai

            client = genai.Client(api_key=self._api_key)
            response = client.models.generate_content(
                model=self._model,
                contents=f"{system_prompt}\n\nQuestion: {question_text}\nAnswer:",
                config={
                    "temperature": 0.0,
                    "max_output_tokens": 100,
                },
            )
            return response.text.strip()
        except Exception as exc:
            raise RuntimeError(f"Gemini API error: {exc}") from exc
