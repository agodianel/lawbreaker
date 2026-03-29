"""
Anthropic connector — queries the Anthropic Messages API.

Supports ``api_key`` constructor param or ``ANTHROPIC_API_KEY`` env var.
"""

from __future__ import annotations
import os
from lawbreaker.connectors.base import BaseConnector, SYSTEM_PROMPT


class AnthropicConnector(BaseConnector):
    """Connector for Anthropic models (Claude 3.5 Sonnet, etc.)."""

    def __init__(self, model: str = "claude-sonnet-4-20250514", api_key: str | None = None):
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

    @classmethod
    def discover_models(
        cls,
        api_key: str | None = None,
        limit: int = 2,
    ) -> list[str]:
        """Discover the most recent Anthropic Claude models.

        Queries the Anthropic Models API and returns the *limit*
        most recently created models.

        Args:
            api_key: Optional API key; falls back to ``ANTHROPIC_API_KEY``.
            limit: Number of most-recent models to return (default 2).

        Returns:
            List of model ID strings, newest first.
        """
        import anthropic
        from datetime import datetime

        key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        client = anthropic.Anthropic(api_key=key)

        all_models = []
        page = client.models.list(limit=100)
        all_models.extend(page.data)
        # Follow pagination if needed
        while page.has_more:
            page = client.models.list(limit=100, after_id=all_models[-1].id)
            all_models.extend(page.data)

        # Sort by created_at descending
        def _parse_ts(m):
            ts = getattr(m, "created_at", None)
            if isinstance(ts, str):
                return datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if isinstance(ts, datetime):
                return ts
            return datetime.min

        all_models.sort(key=_parse_ts, reverse=True)
        return [m.id for m in all_models[:limit]]

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
