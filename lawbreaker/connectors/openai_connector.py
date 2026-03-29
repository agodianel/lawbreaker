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

    @classmethod
    def discover_models(
        cls,
        api_key: str | None = None,
        limit: int = 2,
    ) -> list[str]:
        """Discover the most recent OpenAI GPT chat models.

        Queries the OpenAI Models API, filters for GPT chat models,
        and returns the *limit* most recently created ones.

        Args:
            api_key: Optional API key; falls back to ``OPENAI_API_KEY``.
            limit: Number of most-recent models to return (default 2).

        Returns:
            List of model ID strings, newest first.
        """
        from openai import OpenAI
        import re

        key = api_key or os.environ.get("OPENAI_API_KEY", "")
        client = OpenAI(api_key=key)

        all_models = list(client.models.list())

        # Keep only gpt-* chat models, exclude non-chat variants
        skip = {"instruct", "audio", "realtime", "search", "transcribe", "tts", "dall-e", "whisper", "embedding", "codex", "-pro"}
        chat_models = []
        for m in all_models:
            mid = m.id.lower()
            if not mid.startswith("gpt-"):
                continue
            if any(s in mid for s in skip):
                continue
            chat_models.append(m)

        # Sort by creation date descending, take the most recent
        chat_models.sort(key=lambda m: m.created, reverse=True)

        # De-duplicate: skip dated snapshots (e.g. gpt-4o-2024-08-06)
        # when the non-dated alias (gpt-4o) is also present
        _dated = re.compile(r"-\d{4}-\d{2}-\d{2}$")
        ids = [m.id for m in chat_models]
        alias_set = {mid for mid in ids if not _dated.search(mid)}
        deduped: list[str] = []
        for mid in ids:
            base = _dated.sub("", mid)
            # Keep if it's the alias itself, or no alias exists
            if mid in alias_set or base not in alias_set:
                if mid not in deduped:
                    deduped.append(mid)

        return deduped[:limit]

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
                max_completion_tokens=100,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            raise RuntimeError(f"OpenAI API error: {exc}") from exc
