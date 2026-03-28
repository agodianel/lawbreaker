"""
Ollama connector — queries a local Ollama instance via its REST API.

No authentication needed. Targets ``http://localhost:11434/api/generate``.
"""

from __future__ import annotations
import requests
from lawbreaker.connectors.base import BaseConnector, SYSTEM_PROMPT


class OllamaConnector(BaseConnector):
    """Connector for locally-running Ollama models."""

    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        """Initialise the Ollama connector.

        Args:
            model: Ollama model tag, e.g. ``'llama3.2'``.
            base_url: Ollama server URL (default localhost:11434).
        """
        self._model = model
        self._base_url = base_url.rstrip("/")

    @property
    def model_name(self) -> str:
        """Return the model identifier."""
        return self._model

    def query(self, question_text: str, system_prompt: str = SYSTEM_PROMPT) -> str:
        """Query the local Ollama API.

        Args:
            question_text: The question to send.
            system_prompt: System prompt for formatting.

        Returns:
            The model's text response.

        Raises:
            RuntimeError: On API or connection failure.
        """
        try:
            resp = requests.post(
                f"{self._base_url}/api/generate",
                json={
                    "model": self._model,
                    "prompt": f"{system_prompt}\n\nQuestion: {question_text}\nAnswer:",
                    "stream": False,
                    "options": {"temperature": 0.0},
                },
                timeout=120,
            )
            resp.raise_for_status()
            return resp.json().get("response", "").strip()
        except Exception as exc:
            raise RuntimeError(f"Ollama API error: {exc}") from exc
