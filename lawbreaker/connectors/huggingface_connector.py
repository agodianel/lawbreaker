"""
HuggingFace connector — queries models via the HF Inference API.

Supports ``token`` constructor param or ``HF_TOKEN`` env var.
Targets free serverless inference models.
"""

from __future__ import annotations
import os
from lawbreaker.connectors.base import BaseConnector, SYSTEM_PROMPT


class HuggingFaceConnector(BaseConnector):
    """Connector for HuggingFace Inference API models."""

    def __init__(self, model: str = "meta-llama/Llama-3.1-8B-Instruct", token: str | None = None):
        """Initialise the HuggingFace connector.

        Args:
            model: HF model identifier.
            token: Optional API token; falls back to ``HF_TOKEN``.
        """
        self._model = model
        self._token = token or os.environ.get("HF_TOKEN", "")

    @property
    def model_name(self) -> str:
        """Return the model identifier."""
        return self._model

    def query(self, question_text: str, system_prompt: str = SYSTEM_PROMPT) -> str:
        """Query the HuggingFace Inference API.

        Args:
            question_text: The question to send.
            system_prompt: System prompt for formatting.

        Returns:
            The model's text response.

        Raises:
            RuntimeError: On API failure.
        """
        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(model=self._model, token=self._token)
            response = client.text_generation(
                f"{system_prompt}\n\nQuestion: {question_text}\nAnswer:",
                max_new_tokens=100,
                temperature=0.01,
            )
            return response.strip()
        except Exception as exc:
            raise RuntimeError(f"HuggingFace API error: {exc}") from exc
