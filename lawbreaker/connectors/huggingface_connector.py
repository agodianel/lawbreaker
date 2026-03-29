"""
HuggingFace connector — queries models via the HF Inference API.

Supports ``token`` constructor param or ``HF_TOKEN`` env var.
Targets free serverless inference models.
"""

from __future__ import annotations
import os
from lawbreaker.connectors.base import BaseConnector, SYSTEM_PROMPT

# Orgs whose models we consider canonical (skip community forks)
_CANONICAL_ORGS = {
    "meta-llama", "Qwen", "mistralai", "deepseek-ai", "google",
    "microsoft", "nvidia", "allenai", "openai", "moonshotai",
    "zai-org", "SakanaAI", "EssentialAI", "MiniMaxAI",
}


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

    @classmethod
    def discover_models(cls, token: str | None = None) -> list[str]:
        """Discover available chat/instruct models on HF Inference API.

        Queries the HuggingFace Hub for warm text-generation models,
        filters for canonical instruct/chat models, and returns them
        sorted by download count.

        Args:
            token: Optional API token; falls back to ``HF_TOKEN``.

        Returns:
            List of model identifiers available for inference.
        """
        from huggingface_hub import HfApi

        tok = token or os.environ.get("HF_TOKEN", "")
        api = HfApi(token=tok)

        models = list(api.list_models(
            pipeline_tag="text-generation",
            inference="warm",
            sort="downloads",
            limit=200,
        ))

        result = []
        for m in models:
            name = m.id
            org = name.split("/")[0] if "/" in name else ""

            # Only canonical orgs
            if org not in _CANONICAL_ORGS:
                continue

            name_lower = name.lower()

            # Must be an instruct/chat/reasoning model
            if not any(kw in name_lower for kw in ("instruct", "chat", "-r1")):
                continue

            # Skip code-specific / math-specific
            if any(skip in name_lower for skip in ("coder", "math", "code")):
                continue

            result.append(name)

        return result

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
            client = InferenceClient(
                model=self._model,
                token=self._token,
            )
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{question_text}\nAnswer:"}
            ]
            response = client.chat_completion(
                messages=messages,
                max_tokens=100,
                temperature=0.01,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            raise RuntimeError(f"HuggingFace API error: {exc}") from exc
