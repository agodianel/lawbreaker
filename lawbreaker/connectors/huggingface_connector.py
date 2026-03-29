"""
HuggingFace connector — queries models via the HF Inference API.

Supports ``token`` constructor param or ``HF_TOKEN`` env var.
Targets free serverless inference models.
"""

from __future__ import annotations
import os
import re
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

            result.append(m)

        # Keep only the latest version per model family+size
        return cls._latest_per_family(result)

    @staticmethod
    def _latest_per_family(model_infos) -> list[str]:
        """Keep only the latest version of each model family+size.

        Groups models by (org, architecture, parameter_count) and keeps
        the most recently created one.  E.g. Qwen2.5-7B wins over
        Qwen2-7B; Llama-3.3-70B wins over Llama-3.1-70B.
        """

        def _family_key(model_id: str) -> str:
            org = model_id.split("/")[0] if "/" in model_id else ""
            name = model_id.split("/")[-1].lower()

            # Architecture family
            if "deepseek-r1-distill-llama" in name:
                arch = "dr1-distill-llama"
            elif "deepseek-r1-distill-qwen" in name:
                arch = "dr1-distill-qwen"
            elif "deepseek-r1" in name:
                arch = "deepseek-r1"
            elif "llama" in name:
                arch = "llama"
            elif "qwen" in name:
                arch = "qwen"
            elif "mistral" in name:
                arch = "mistral"
            elif "olmo" in name:
                arch = "olmo"
            elif "kimi" in name:
                arch = "kimi"
            else:
                arch = re.split(r"[-_]", name)[0]

            # Parameter size — check MoE A-notation first
            moe = re.search(r"(\d+)b-a(\d+)b", name)
            if moe:
                size = f"{moe.group(1)}b-a{moe.group(2)}b"
            else:
                sz = re.search(r"(\d+\.?\d*)b", name)
                size = sz.group(0) if sz else "base"

            return f"{org}/{arch}/{size}"

        groups: dict[str, object] = {}
        for m in model_infos:
            key = _family_key(m.id)
            if key not in groups:
                groups[key] = m
            elif (
                hasattr(m, "created_at")
                and m.created_at
                and hasattr(groups[key], "created_at")
                and groups[key].created_at
                and m.created_at > groups[key].created_at
            ):
                groups[key] = m

        kept = {m.id for m in groups.values()}
        return [m.id for m in model_infos if m.id in kept]

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
