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

    @classmethod
    def discover_models(
        cls,
        api_key: str | None = None,
        recent_only: bool = True,
    ) -> list[str]:
        """Return available Gemini model names that support content generation.

        Args:
            api_key: Optional API key; falls back to ``GEMINI_API_KEY``.
            recent_only: If *True* (default), keep only the most recent
                major version (e.g. 3.1).  Set to *False* to
                return every Gemini model.

        Returns:
            Sorted list of model name strings (e.g. ``'gemini-2.0-flash'``).
        """
        import re
        from google import genai

        key = api_key or os.environ.get("GEMINI_API_KEY", "")
        client = genai.Client(api_key=key)
        models: list[str] = []
        for m in client.models.list():
            # Only models that support generateContent
            if not m.supported_actions or "generateContent" not in m.supported_actions:
                continue
            name = m.name or ""
            # Strip the "models/" prefix if present
            if name.startswith("models/"):
                name = name[len("models/"):]
            # Keep only gemini models, skip tuned/legacy
            if not name.startswith("gemini"):
                continue
            models.append(name)

        if recent_only and models:
            # Extract major versions (e.g. "3.1" from "gemini-3.1-flash")
            version_pat = re.compile(r"^gemini-(\d+\.\d+)")
            versions: set[str] = set()
            for name in models:
                match = version_pat.match(name)
                if match:
                    versions.add(match.group(1))
            if versions:
                top2 = sorted(versions, key=lambda v: tuple(map(int, v.split("."))), reverse=True)[:1]
                models = [n for n in models if any(f"gemini-{v}" in n for v in top2)]

        return sorted(models)

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
