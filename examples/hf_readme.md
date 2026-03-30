---
language:
  - en
license: mit
task_categories:
  - question-answering
tags:
  - physics
  - benchmark
  - adversarial
  - evaluation
  - llm
  - science
  - uncertainty
size_categories:
  - 1K<n<10K
pretty_name: LLM Physics Law-Breaker — Adversarial Evaluation Results
---

# ⚖️ LLM Physics Law-Breaker — Adversarial Evaluation Results

An adversarial evaluation framework for LLMs & AI agents — grounded in physics.

This dataset contains benchmark results from [LawBreaker](https://github.com/agodianel/lawbreaker) — a framework that procedurally generates trap questions exploiting common LLM failure modes and grades answers using symbolic math (SymPy + Pint). No LLM-as-judge, no human review, zero GPU required.

## 🆕 What's New in v0.6

| Feature | Description |
|---------|-------------|
| **Wilson Score CI** | Every pass rate now includes a 95% confidence interval — no more point estimates |
| **Relative Error Tracking** | Per-law error stats (mean, median, max, std) quantify *how wrong* a model is, not just pass/fail |
| **Regression Detection** | `lawbreaker compare` runs two-proportion z-tests across all 34 laws with Benjamini-Hochberg FDR correction |
| **Graph Generator** | `generate_graphs.py` produces 12 publication-quality charts (leaderboard, heatmap, radar, CI, etc.) |
| **Zero Dependencies** | Uncertainty module uses `math.erf` — no scipy or statsmodels needed |

---

## 🏆 Leaderboard v0.6 — 6 Models, 3 Providers (with Uncertainty)

> 34 laws · 5 questions each · 170 total · seed 42 · deterministic · **Wilson score 95% CI**

| Rank | Model | Provider | Score | Passed | 95% CI | Worst Law | Worst Trap |
|------|-------|----------|-------|--------|--------|-----------|------------|
| 1 | gemini-3.1-flash-image-preview | Google | **83.5%** | 142/170 | 77.1 – 88.5% | Bernoulli's Equation | pressure_unit_confusion |
| 2 | gemini-3.1-flash-lite-preview | Google | **72.9%** | 124/170 | 65.9 – 79.1% | Gravitational Force | pressure_unit_confusion |
| 3 | claude-sonnet-4-6 | Anthropic | **64.7%** | 110/170 | 57.2 – 71.6% | Coulomb's Law | pressure_unit_confusion |
| 4 | claude-opus-4-6 | Anthropic | **62.4%** | 106/170 | 54.8 – 69.3% | Coulomb's Law | pressure_unit_confusion |
| 5 | gpt-5.4-mini | OpenAI | **58.2%** | 99/170 | 50.6 – 65.5% | Ideal Gas Law | pressure_unit_confusion |
| 6 | gpt-5.4-nano | OpenAI | **25.3%** | 43/170 | 19.2 – 32.4% | KCL | missing_branch |

### v0.6 Key Findings

- **Google Gemini leads** — Gemini 3.1 flash image-preview takes #1 at 83.5%, outperforming all Claude and GPT models
- **Unit confusion is universal** — `pressure_unit_confusion` is the worst trap for 5 out of 6 models
- **Chain laws expose gaps** — multi-step reasoning (e.g., Force → KE, Spring → Speed) separates strong from weak models
- **Coulomb's Law trips Claude** — both Opus and Sonnet score 0% on Coulomb's Law (r vs r² confusion)
- **Small models collapse** — GPT-5.4 Nano (25.3%) fails on nearly 3 out of 4 adversarial questions

---

## 🏆 Leaderboard v0.5 — 21 Models, 4 Providers

> 34 laws · 5 questions each · 170 total · seed 42 · deterministic

| Rank | Model | Provider | Score | Passed | Worst Law | Worst Trap |
|------|-------|----------|-------|--------|-----------|------------|
| 1 | gemini-3.1-flash-image-preview | Google | **83.5%** | 142/170 | Bernoulli's Equation | pressure_unit_confusion |
| 2 | gemini-3.1-flash-lite-preview | Google | **72.9%** | 124/170 | Gravitational Force | pressure_unit_confusion |
| 3 | claude-sonnet-4-6 | Anthropic | **65.3%** | 111/170 | Coulomb's Law | pressure_unit_confusion |
| 4 | gpt-5.4-mini | OpenAI | **58.8%** | 100/170 | Coulomb's Law | pressure_unit_confusion |
| 5 | gemini-2.5-flash-image | Google | **58.8%** | 100/170 | Coulomb's Law | wrong_k_constant |
| 6 | claude-opus-4-6 | Anthropic | **54.7%** | 93/170 | Coulomb's Law | pressure_unit_confusion |
| 7 | Kimi-K2-Instruct-0905 | HuggingFace | **54.1%** | 92/170 | Gravitational Force | pressure_unit_confusion |
| 8 | Qwen3-235B-A22B-Instruct-2507 | HuggingFace | **51.2%** | 87/170 | Ideal Gas Law | pressure_unit_confusion |
| 9 | Qwen3-Next-80B-A3B-Instruct | HuggingFace | **44.1%** | 75/170 | KCL | missing_branch |
| 10 | gemini-2.5-flash-lite | Google | **31.2%** | 53/170 | KCL | missing_branch |
| 11 | Qwen2.5-72B-Instruct | HuggingFace | **30.0%** | 51/170 | KCL | missing_branch |
| 12 | gpt-5.4-nano | OpenAI | **27.6%** | 47/170 | KCL | missing_branch |
| 13 | rnj-1-instruct | HuggingFace | **25.9%** | 43/166 | KCL | missing_branch |
| 14 | gemini-2.5-flash | Google | **23.5%** | 40/170 | Coulomb's Law | missing_branch |
| 15 | Qwen3-4B-Instruct-2507 | HuggingFace | **21.8%** | 37/170 | Ideal Gas Law | missing_branch |
| 16 | gemini-3.1-pro-preview | Google | **21.2%** | 36/170 | Ohm's Law | reversed_question |
| 17 | Llama-3.3-70B-Instruct | HuggingFace | **20.6%** | 35/170 | KCL | missing_branch |
| 18 | Olmo-3.1-32B-Instruct | HuggingFace | **20.0%** | 34/170 | KCL | missing_branch |
| 19 | Llama-3.1-8B-Instruct | HuggingFace | **7.1%** | 12/170 | KCL | reversed_question |
| 20 | Olmo-3-7B-Instruct | HuggingFace | **5.9%** | 10/170 | KCL | missing_branch |
| 21 | Llama-3.2-1B-Instruct | HuggingFace | **1.2%** | 2/170 | KCL | unit_confusion |

### v0.5 Key Findings

- **Top performers cluster around 55-85%** — no model achieves 90%+, showing adversarial traps remain effective even for frontier models
- **Coulomb's Law and KCL** are the two hardest laws across all models
- **pressure_unit_confusion** (atm vs Pa) and **missing_branch** (forgetting a current path) are the deadliest traps
- **Model size matters but isn't decisive** — Qwen3-235B (51.2%) beats Qwen2.5-72B (30.0%), but Kimi-K2 (54.1%) beats claude-opus-4 (54.7%) with orders of magnitude fewer parameters
- **Small models collapse** — below ~8B parameters, models score under 10%

---

## 📊 v0.5 → v0.6 Score Changes

Models re-evaluated in v0.6 (with improved grading and uncertainty scoring):

| Model | v0.5 Score | v0.6 Score | Δ | Notes |
|-------|-----------|-----------|---|-------|
| gemini-3.1-flash-image-preview | 83.5% | 83.5% | 0.0% | Stable |
| gemini-3.1-flash-lite-preview | 72.9% | 72.9% | 0.0% | Stable |
| claude-sonnet-4-6 | 65.3% | 64.7% | −0.6% | Minor scoring variance |
| claude-opus-4-6 | 54.7% | 62.4% | +7.7% | Improved with deterministic seed |
| gpt-5.4-mini | 58.8% | 58.2% | −0.6% | Minor scoring variance |
| gpt-5.4-nano | 27.6% | 25.3% | −2.3% | Small variance |

---

## 📐 34 Physics Laws Tested

### Single-Law Challenges (28)

Ohm's Law · Kirchhoff's Current Law · Kirchhoff's Voltage Law · Newton's Second Law · Kinetic Energy · Energy Conservation · Ideal Gas Law · Power · Coulomb's Law · Hooke's Law · Gravitational Force · Snell's Law · Bernoulli's Equation · Centripetal Force · Conservation of Momentum · Capacitance · Wave Speed · Pendulum Period · Thermal Expansion · Stefan-Boltzmann Law · Drag Force · Thin Lens Equation · Boyle's Law · RC Time Constant · Magnetic Force · Work-Energy Theorem · Specific Heat · Gravitational PE

### Multi-Step Combined Chains (6)

Ohm → Power · Force → Kinetic Energy · PE → Speed · Ohm → Kirchhoff Voltage · Spring → Speed · Heat → Height

These chains require solving an intermediate step before reaching the final answer.

---

## 🪤 Adversarial Trap Types

Each law has 3 adversarial trap types designed to exploit common LLM failure modes:

| Trap Category | Example | Why It Works |
|---------------|---------|--------------|
| Anchoring bias | "My colleague says the answer is 35V" | LLMs repeat a plausible-sounding wrong answer |
| Unit confusion | mA vs A, °C vs K, atm vs Pa, cm vs m | LLMs skip unit conversion |
| Formula errors | Forgetting ½ in KE, using r instead of r² | LLMs misremember formulas |
| Missing components | Forgetting a branch current, a voltage drop | LLMs overlook terms |
| Reversed questions | "What resistance gives this current?" | LLMs solve the forward problem instead |

---

## 📁 Dataset Structure

```
results_v0.5/                          # Pre-uncertainty scoring (21 models)
├── anthropic/
│   ├── claude-opus-4-6.json
│   └── claude-sonnet-4-6.json
├── gemini/
│   ├── gemini-2.5-flash.json
│   ├── gemini-2.5-flash-image.json
│   ├── gemini-2.5-flash-lite.json
│   ├── gemini-3.1-flash-image-preview.json
│   ├── gemini-3.1-flash-lite-preview.json
│   └── gemini-3.1-pro-preview.json
├── huggingface/
│   ├── EssentialAI__rnj-1-instruct.json
│   ├── Qwen__Qwen2.5-72B-Instruct.json
│   ├── Qwen__Qwen3-235B-A22B-Instruct-2507.json
│   ├── Qwen__Qwen3-4B-Instruct-2507.json
│   ├── Qwen__Qwen3-Next-80B-A3B-Instruct.json
│   ├── allenai__Olmo-3-7B-Instruct.json
│   ├── allenai__Olmo-3.1-32B-Instruct.json
│   ├── meta-llama__Llama-3.1-8B-Instruct.json
│   ├── meta-llama__Llama-3.2-1B-Instruct.json
│   ├── meta-llama__Llama-3.3-70B-Instruct.json
│   └── moonshotai__Kimi-K2-Instruct-0905.json
└── openai/
    ├── gpt-5.4-mini.json
    └── gpt-5.4-nano.json

results_v0.6/                          # With confidence intervals & error stats (6 models)
├── anthropic/
│   ├── claude-opus-4-6.json
│   └── claude-sonnet-4-6.json
├── gemini/
│   ├── gemini-3.1-flash-image-preview.json
│   └── gemini-3.1-flash-lite-preview.json
└── openai/
    ├── gpt-5.4-mini.json
    └── gpt-5.4-nano.json
```

---

## 📄 Data Format

### v0.5 Schema

Each JSON file contains the full benchmark result for one model:

```json
{
  "model_name": "claude-sonnet-4-6",
  "timestamp": "2026-03-29T21:44:45.593222+00:00",
  "total_questions": 170,
  "total_passed": 111,
  "overall_score": 0.6529,
  "per_law_scores": { "Ohm's Law": 1.0, "...": "..." },
  "per_trap_scores": { "unit_confusion": 0.641, "...": "..." },
  "worst_law": "Coulomb's Law",
  "worst_trap": "pressure_unit_confusion",
  "questions": [ ... ]
}
```

### v0.6 Schema (extends v0.5)

v0.6 results include everything from v0.5 **plus** three new fields:

```json
{
  "...all v0.5 fields...",
  "per_law_ci": {
    "Ohm's Law": [0.5655, 1.0],
    "Kirchhoff's Current Law": [0.3755, 0.9638],
    "...": "..."
  },
  "per_trap_ci": {
    "unit_confusion": [0.512, 0.756],
    "...": "..."
  },
  "per_law_error_stats": {
    "Ohm's Law": { "mean": 0.00007, "median": 0.0, "max": 0.00034, "std": 0.00014 },
    "Kirchhoff's Current Law": { "mean": 0.4, "median": 0.0, "max": 2.0, "std": 0.8 },
    "...": "..."
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `per_law_ci` | dict → [low, high] | Wilson score 95% confidence interval per law |
| `per_trap_ci` | dict → [low, high] | Wilson score 95% confidence interval per trap |
| `per_law_error_stats` | dict → {mean, median, max, std} | Relative error statistics per law (quantifies *how wrong* the model is) |

### Question Record Fields

| Field | Type | Description |
|-------|------|-------------|
| question.law | string | Physics law being tested |
| question.trap_type | string | Adversarial trap applied |
| question.question_text | string | The full question presented to the LLM |
| question.correct_answer | float | Ground-truth numerical answer |
| question.correct_unit | string | Expected unit (V, N, J, Pa, etc.) |
| question.variables | dict | Input parameters used for generation |
| question.difficulty | string | easy / medium / hard |
| question.explanation | string | Why the trap works and how to solve it |
| llm_response | string | Raw LLM output |
| extracted_answer | float/null | Number extracted from the response |
| passed | bool | Whether the answer matched within tolerance |
| status | string | "correct", "incorrect", or "error" |
| relative_error | float/null | *(v0.6 only)* Relative error between extracted and correct answer |

---

## 🔬 Grading Methodology

Answers are graded using symbolic math, not string matching or LLM-as-judge:

1. **Numeric extraction** — A two-phase extractor: (a) if the first line starts with a number, use it; (b) otherwise, find the last number in the response
2. **Tolerance matching** — Extracted answer is compared to the ground truth with 5% relative tolerance (handles floating-point and rounding)
3. **Overflow guards** — Values exceeding 10¹⁵ are rejected as likely unit-confusion errors

This ensures reproducible, deterministic grading with zero false positives.

---

## 📤 Submit Your Own Results

```bash
git clone https://github.com/agodianel/lawbreaker.git
cd lawbreaker && pip install -e ".[dev]"

# Run against any model
export HF_TOKEN="hf_..."
lawbreaker run --model <MODEL> --connector <CONNECTOR> --questions 5 --push

# Compare two runs for regressions (new in v0.6)
lawbreaker compare results/baseline.json results/candidate.json --alpha 0.05
```

Supported connectors: `openai`, `anthropic`, `gemini`, `huggingface`, `ollama`

---

## 🔗 Links

- Source code & docs: [github.com/agodianel/lawbreaker](https://github.com/agodianel/lawbreaker)
- Kaggle dataset: [kaggle.com/datasets/dianelago/llm-physics-law-breaker-benchmark-results](https://www.kaggle.com/datasets/dianelago/llm-physics-law-breaker-benchmark-results)
- Wiki: [github.com/agodianel/lawbreaker/wiki](https://github.com/agodianel/lawbreaker/wiki)
- How it works: Questions are generated procedurally with adversarial traps. Answers are graded symbolically using SymPy and Pint. Zero GPU, zero LLM-as-judge, fully reproducible.

## 📄 License

[MIT](https://opensource.org/licenses/MIT) — use it, fork it, break more laws.

## Citation

```bibtex
@misc{lawbreaker2026,
  title={LawBreaker: An Adversarial Evaluation Framework for LLMs and AI Agents},
  author={Dianel Ago},
  year={2026},
  url={https://github.com/agodianel/lawbreaker},
  note={HuggingFace Dataset: diago01/llm-physics-law-breaker}
}
```
