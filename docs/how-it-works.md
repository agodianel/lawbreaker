# How It Works

## Architecture

LawBreaker is a physics adversarial benchmark that **generates** trap questions
and **grades** answers using symbolic math — no LLM-as-judge required.

```
┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│  28 Physics  │────▶│   Benchmark   │────▶│   LLM API    │
│    Laws      │     │    Runner     │     │  Connector   │
└──────────────┘     └───────┬───────┘     └──────┬───────┘
                             │                     │
                     ┌───────▼───────┐     ┌──────▼───────┐
                     │   Symbolic    │◀────│   Model      │
                     │   Verifier    │     │   Response   │
                     └───────┬───────┘     └──────────────┘
                             │
                     ┌───────▼───────┐
                     │   Report &    │
                     │  Leaderboard  │
                     └───────────────┘
```

## Key Components

### Laws (`lawbreaker/laws/`)
Each law is a Python class that:
- Inherits from `BaseLaw`
- Defines parameter ranges for 3 difficulty levels (easy/medium/hard)
- Implements `generate()` to produce a `Question` with embedded traps
- Implements `verify()` to check answers using sympy/pint

### Connectors (`lawbreaker/connectors/`)
Thin wrappers around LLM APIs that:
- Accept a physics question as text
- Return the model's answer as a string
- Support OpenAI, Anthropic, HuggingFace, and Ollama

### Verifier (`lawbreaker/core/verifier.py`)
The grading engine that:
- Parses numeric answers from model responses
- Compares against the correct answer with configurable tolerance
- Uses symbolic math (sympy) for exact verification
- Handles unit conversions via pint

### Runner (`lawbreaker/runner.py`)
The orchestrator that:
- Generates N questions across all laws
- Sends each question to the LLM connector
- Grades responses via the verifier
- Produces a structured report with per-law and per-trap breakdowns

## Design Principles

1. **Procedural generation** — No static question bank. Every run creates fresh questions.
2. **Seed-based reproducibility** — Same seed = same questions for fair comparisons.
3. **Symbolic grading** — No subjective evaluation. Math is the judge.
4. **Adversarial by design** — Every question has a trap that exploits known LLM weaknesses.
5. **Zero GPU** — Runs on any machine, grades without GPU.
