# LLM Connectors

LawBreaker supports 4 LLM connectors out of the box. All connectors implement
the `BaseConnector` interface.

## OpenAI

```python
from lawbreaker.connectors.openai_connector import OpenAIConnector

connector = OpenAIConnector(model="gpt-4o")
```

**Requirements**: Set `OPENAI_API_KEY` environment variable.

**Supported models**: Any model available via the OpenAI Chat Completions API
(gpt-4o, gpt-4-turbo, gpt-3.5-turbo, etc.).

## Anthropic

```python
from lawbreaker.connectors.anthropic_connector import AnthropicConnector

connector = AnthropicConnector(model="claude-sonnet-4-20250514")
```

**Requirements**: Set `ANTHROPIC_API_KEY` environment variable.

**Supported models**: Any model available via the Anthropic Messages API
(claude-sonnet-4-20250514, claude-3-haiku, etc.).

## HuggingFace

```python
from lawbreaker.connectors.huggingface_connector import HuggingFaceConnector

connector = HuggingFaceConnector(model="meta-llama/Llama-3.1-8B-Instruct")
```

**Requirements**: Set `HF_TOKEN` environment variable (free tier works).

**Supported models**: Any model available via the HuggingFace Inference API.

## Ollama (Local)

```python
from lawbreaker.connectors.ollama_connector import OllamaConnector

connector = OllamaConnector(model="llama3.2")
```

**Requirements**: [Ollama](https://ollama.ai/) installed and running locally.

**Supported models**: Any model pulled via `ollama pull <model>`.

## Adding a Custom Connector

Subclass `BaseConnector`:

```python
from lawbreaker.connectors.base import BaseConnector

class MyConnector(BaseConnector):
    def __init__(self, model: str, **kwargs):
        super().__init__(model)
        # Setup your client

    def query(self, prompt: str) -> str:
        # Send prompt to your LLM and return the response text
        return response_text
```

Then use it:

```python
from lawbreaker.runner import BenchmarkRunner

connector = MyConnector(model="my-model")
runner = BenchmarkRunner(connector=connector, n_questions=10, seed=42)
report = runner.run()
```
