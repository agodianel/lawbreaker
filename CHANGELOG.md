# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-03-29

### Added
- **Model auto-discovery** for all major providers via `discover_models()` classmethods:
  - **OpenAI**: Discovers latest GPT chat models via `client.models.list()`, filters for `gpt-*`, sorts by creation date
  - **Anthropic**: Discovers latest Claude models via `client.models.list()` with pagination, sorts by `created_at`
  - **Gemini**: Discovers recent Gemini model versions (already in v0.2.0, unchanged)
  - **HuggingFace**: Discovers all warm inference models (already in v0.2.0, unchanged)
- Example scripts (`run_openai.py`, `run_anthropic.py`) now use auto-discovery instead of hardcoded model lists
- All 4 provider run scripts (OpenAI, Anthropic, Gemini, HuggingFace) auto-discover models on launch

## [0.3.0] - 2026-03-29

### Added
- **6 multi-step combined law chains** — questions that chain two physics laws together, requiring intermediate calculations:
  - **Ohm → Power**: I = V/R then P = VI
  - **Force → Kinetic Energy**: a = F/m, v = at, KE = ½mv²
  - **PE → Speed**: mgh = ½mv², v = √(2gh) (mass cancels)
  - **Ohm → Kirchhoff Voltage**: series circuit voltage divider I = V/(R₁+R₂), V₂ = IR₂
  - **Spring → Speed**: ½kx² = ½mv², v = x√(k/m)
  - **Heat → Height**: Q = mcΔT, h = Q/(mg)
- Each chain has 3 trap types (unit confusion, intermediate anchoring, missing √, mass distractor, etc.)
- Total: **34 laws** (28 single-law + 6 multi-step chains), **194 tests** all passing

## [0.2.0] - 2025-03-29

### Added
- **Google Gemini connector** (`gemini_connector.py`) — supports Gemini 2.0 Flash and all Gemini models via `GEMINI_API_KEY`
- **`run-all` CLI command** — auto-discovers and benchmarks ALL available HuggingFace inference models with leaderboard comparison
- **`models` CLI command** — discovers and lists warm HuggingFace inference models available for benchmarking
- **`--delay` flag** for `run` command — configurable sleep between API calls to avoid rate limiting
- **Per-connector results directories** — results now saved to `results/openai/`, `results/anthropic/`, `results/gemini/`, `results/huggingface/`, `results/ollama/`
- **Model discovery** — `HuggingFaceConnector.discover_models()` finds canonical instruct/chat models with warm inference
- **Example scripts** for Anthropic Claude (`run_anthropic.py`) and Google Gemini (`run_gemini.py`)

### Changed
- Updated Anthropic connector default model to `claude-sonnet-4-20250514`
- CLI `--connector` option now accepts `gemini` in addition to existing connectors
- All example scripts updated to save results in connector-specific subdirectories
- `run-all` command now saves results to `results/<connector>/` subdirectory

## [0.1.0] - 2025-01-01

### Added
- **28 physics laws** with adversarial trap questions:
  - **Mechanics**: Newton's Second Law, Kinetic Energy, Energy Conservation, Hooke's Law, Centripetal Force, Conservation of Momentum, Work-Energy Theorem, Gravitational PE, Drag Force
  - **Electricity & Magnetism**: Ohm's Law, Kirchhoff's Current Law, Kirchhoff's Voltage Law, Electrical Power, Coulomb's Law, Capacitance, RC Time Constant, Magnetic Force
  - **Thermodynamics**: Ideal Gas Law, Boyle's Law, Specific Heat, Thermal Expansion, Stefan-Boltzmann Law
  - **Optics & Waves**: Snell's Law, Wave Speed, Thin Lens Equation, Pendulum Period
  - **Fluid Mechanics**: Bernoulli's Equation
  - **Gravitation**: Newton's Gravitational Force
- **4 LLM connectors**: OpenAI, Anthropic, HuggingFace, Ollama
- **Symbolic math grading** via sympy + pint — no LLM-as-judge
- **3 trap types per law**: anchoring bias, unit confusion, and law-specific traps
- **3 difficulty levels**: easy, medium, hard with scaled parameter ranges
- **Seed-based reproducibility** for all question generation
- **Click CLI** with commands: `run`, `leaderboard`, `laws`, `example`
- **Benchmark runner** with full report generation and JSON export
- **Leaderboard system** with HuggingFace Dataset integration
- **164+ pytest tests** covering all laws, connectors, and verifier
- **CI pipeline** via GitHub Actions (Python 3.10, 3.11, 3.12)
- **GitHub community files**: CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, issue templates, PR template
