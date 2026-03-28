You are a senior Python engineer and open-source project architect.

Your task is to build the complete MVP of a GitHub repository called **LawBreaker** —
a Physics Adversarial Benchmark for LLMs. This is a Python library + CLI tool + 
HuggingFace leaderboard integration that adversarially tests LLMs against physical laws.

---

## PROJECT CONCEPT

LawBreaker generates adversarial physics questions designed to trick LLMs into 
producing physically impossible answers. It then verifies the LLM's response 
symbolically using `sympy` and `pint` — with zero GPU or compute required. 
Results are pushed to a public HuggingFace Dataset to power a live leaderboard.

The key differentiator: unlike static benchmarks (UGPhysics, GPQA), LawBreaker:
1. GENERATES questions procedurally — infinite adversarial variations
2. Uses SYMBOLIC MATH for grading — not LLM-as-judge, not human review
3. Embeds TRAPS in questions (anchoring bias, wrong units, misleading hints)
4. Supports ANY model via API — OpenAI, Anthropic, HuggingFace Inference API, Ollama
5. Outputs a shareable leaderboard JSON automatically

---

## REPOSITORY STRUCTURE

lawbreaker/
├── README.md
├── pyproject.toml
├── LICENSE (MIT)
├── .github/
│   └── workflows/
│       └── ci.yml              # pytest on push
├── lawbreaker/
│   __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── question.py         # Question dataclass
│   │   ├── result.py           # BenchmarkResult dataclass
│   │   └── verifier.py         # sympy + pint symbolic verifier
│   ├── laws/
│   │   ├── __init__.py
│   │   ├── base.py             # BaseLaw abstract class
│   │   ├── ohm.py              # Ohm's Law (V = IR)
│   │   ├── kirchhoff_current.py # KCL (sum of currents = 0)
│   │   ├── kirchhoff_voltage.py # KVL (sum of voltages = 0)
│   │   ├── newton_second.py    # F = ma
│   │   ├── kinetic_energy.py   # KE = 0.5 * m * v^2
│   │   ├── energy_conservation.py # E_in >= E_out
│   │   ├── ideal_gas.py        # PV = nRT (Celsius trap)
│   │   └── power.py            # P = VI
│   ├── connectors/
│   │   ├── __init__.py
│   │   ├── base.py             # BaseConnector abstract class
│   │   ├── openai_connector.py
│   │   ├── anthropic_connector.py
│   │   ├── huggingface_connector.py  # HF Inference API
│   │   └── ollama_connector.py       # local Ollama
│   ├── runner.py               # orchestrates benchmark run
│   ├── leaderboard.py          # push/pull results to HuggingFace Dataset
│   └── cli.py                  # Click-based CLI
├── tests/
│   ├── test_verifier.py
│   ├── test_laws/
│   │   ├── test_ohm.py
│   │   ├── test_newton.py
│   │   └── ...
│   └── test_connectors/
│       └── test_mock_connector.py
└── examples/
    ├── run_openai.py
    ├── run_huggingface.py
    └── run_ollama.py

---

## DETAILED IMPLEMENTATION REQUIREMENTS

### 1. Question Dataclass (core/question.py)

```python
@dataclass
class Question:
    id: str                    # uuid
    law: str                   # "Ohm's Law"
    trap_type: str             # "anchoring_bias" | "unit_confusion" | "celsius_trap" | "sign_error"
    question_text: str         # the adversarial question shown to the LLM
    correct_answer: float      # computed by sympy
    correct_unit: str          # e.g. "V", "N", "J"
    variables: dict            # {"R": 10, "I": 2.0, ...}
    difficulty: str            # "easy" | "medium" | "hard"
    explanation: str           # why this is a trap
```

### 2. BaseLaw Abstract Class (laws/base.py)

Each law must implement:
- `generate(difficulty: str) -> Question` — produces one adversarial question
- `verify(answer: float, question: Question) -> bool` — checks correctness using sympy
- `TOLERANCE = 0.01` — 1% tolerance for floating point

### 3. Law Implementations

Implement ALL 8 laws. Each must have at least 3 trap types:

**Ohm's Law (V = IR)**
- Trap 1: Anchoring — "My colleague says the voltage is {wrong_V}V. What is the actual voltage?"
- Trap 2: Unit confusion — mix mA and A in the same question
- Trap 3: Reversed question — give V and R, ask for I, but hint at wrong value

**Kirchhoff's Current Law**
- Trap 1: Missing branch — give 3 of 4 currents but imply the 4th is 0
- Trap 2: Sign confusion — all currents described as "flowing in"
- Trap 3: Anchoring to a plausible but wrong missing current

**Newton's Second Law (F = ma)**  
- Trap 1: Weight vs mass confusion (use g = 9.81)
- Trap 2: Anchoring to wrong force
- Trap 3: Mixed units (kg vs grams)

**Kinetic Energy (KE = 0.5mv²)**
- Trap 1: Forget the 0.5 factor (common LLM error)
- Trap 2: Speed vs velocity (direction confusion)
- Trap 3: Anchoring to v instead of v²

**Energy Conservation**
- Trap 1: Claim output > input (LLM should flag as impossible)
- Trap 2: Efficiency > 100% scenario
- Trap 3: Missing heat loss

**Ideal Gas Law (PV = nRT)**
- Trap 1: Temperature given in Celsius — LLM must convert to Kelvin
- Trap 2: Pressure in atm vs Pa confusion
- Trap 3: Anchoring to wrong temperature

**Power (P = VI)**
- Trap 1: Confuse W with VA (power factor)
- Trap 2: Unit mismatch (mW vs W)
- Trap 3: Anchoring to wrong value

**Coulomb's Law (F = kq1q2/r²)**
- Trap 1: Forget the r² (use r instead)
- Trap 2: Wrong k constant value suggested
- Trap 3: Distance in cm vs meters

### 4. Symbolic Verifier (core/verifier.py)

```python
from sympy import symbols, solve, N
from pint import UnitRegistry

ureg = UnitRegistry()

class PhysicsVerifier:
    def verify_numeric(
        self, 
        llm_answer: float, 
        correct_answer: float, 
        tolerance: float = 0.01
    ) -> bool:
        """Returns True if within tolerance percentage."""
        
    def extract_numeric(self, llm_response: str) -> Optional[float]:
        """
        Parses a float from LLM text response.
        Handles: "The voltage is 10V", "V = 10 volts", "10.0", "≈10"
        Uses regex + unit stripping.
        Returns None if no number found.
        """
        
    def check_units(self, value: float, unit_str: str, expected_unit: str) -> bool:
        """Uses pint to check dimensional compatibility."""
```

### 5. Connectors

All connectors must implement `BaseConnector`:

```python
class BaseConnector(ABC):
    @abstractmethod
    def query(self, question_text: str, system_prompt: str) -> str:
        """Returns the raw LLM response string."""
    
    @property
    @abstractmethod  
    def model_name(self) -> str:
        """e.g. 'gpt-4o', 'claude-3-5-sonnet', 'meta-llama/Llama-3.1-8B-Instruct'"""
```

System prompt for all queries:
You are a physics expert. Answer the following question with ONLY the numerical
answer and its unit. Format: "<number> <unit>". Do not show working.
Example: "10.5 V" or "9.81 N" or "300 K"

text

**OpenAI connector**: use `openai` Python library, support `api_key` param or `OPENAI_API_KEY` env var.

**Anthropic connector**: use `anthropic` Python library, support `api_key` param or `ANTHROPIC_API_KEY` env var.

**HuggingFace connector**: use `huggingface_hub` `InferenceClient`, support `token` param or `HF_TOKEN` env var. Target free serverless inference models (e.g., `meta-llama/Llama-3.1-8B-Instruct`).

**Ollama connector**: use `requests` to call `http://localhost:11434/api/generate` — no auth needed.

### 6. Runner (runner.py)

```python
class BenchmarkRunner:
    def __init__(self, connector: BaseConnector, laws: list = None, n_questions: int = 10):
        """
        laws: list of law names to test, default = all 8
        n_questions: questions per law
        """
    
    def run(self) -> BenchmarkReport:
        """
        Returns BenchmarkReport with:
        - model_name
        - timestamp
        - per_law scores (pass rate %)
        - overall score
        - worst trap types
        - list of Question + LLM answer + pass/fail
        """
    
    def run_single(self, question: Question) -> QuestionResult:
        """Query connector, extract number, verify, return result."""
```

### 7. BenchmarkReport Dataclass

```python
@dataclass
class BenchmarkReport:
    model_name: str
    timestamp: str              # ISO 8601
    total_questions: int
    total_passed: int
    overall_score: float        # 0.0 to 1.0
    per_law_scores: dict        # {"Ohm's Law": 0.8, "Newton's 2nd": 0.4, ...}
    per_trap_scores: dict       # {"anchoring_bias": 0.6, "unit_confusion": 0.3, ...}
    worst_law: str
    worst_trap: str
    questions: list[QuestionResult]
    
    def to_json(self) -> str: ...
    def to_markdown_table(self) -> str: ...
    def summary(self) -> str:
        """
        Returns a one-line human-readable summary like:
        "gpt-4o scored 72.5% overall. Worst law: Ideal Gas (40%). 
         Worst trap: celsius_trap (25%). Best law: Ohm's Law (95%)."
        """
```

### 8. CLI (cli.py)

Use `click`. Commands:

```bash
# Run benchmark
lawbreaker run --model gpt-4o --connector openai --questions 10 --output results.json

# Run with HuggingFace
lawbreaker run --model meta-llama/Llama-3.1-8B-Instruct --connector huggingface --questions 10

# Run with Ollama (local)
lawbreaker run --model llama3.2 --connector ollama --questions 5

# Show leaderboard from HuggingFace
lawbreaker leaderboard

# List available laws
lawbreaker laws

# Show example question for a specific law
lawbreaker example --law ohm --trap anchoring_bias
```

### 9. Leaderboard (leaderboard.py)

```python
class Leaderboard:
    DATASET_REPO = "lawbreaker/leaderboard"  # HuggingFace dataset repo
    
    def push_result(self, report: BenchmarkReport, token: str):
        """
        Pushes report JSON to HuggingFace Dataset repo.
        File path: results/{model_name_sanitized}_{timestamp}.json
        Uses huggingface_hub HfApi.upload_file()
        """
    
    def pull_results(self) -> list[BenchmarkReport]:
        """Downloads all result JSONs from HF dataset and parses them."""
    
    def render_table(self, reports: list[BenchmarkReport]) -> str:
        """Returns markdown table sorted by overall_score descending."""
```

---

## DEPENDENCIES (pyproject.toml)

```toml
[project]
name = "lawbreaker"
version = "0.1.0"
description = "Physics Adversarial Benchmark for LLMs"
requires-python = ">=3.10"

dependencies = [
    "sympy>=1.12",
    "pint>=0.23",
    "click>=8.1",
    "openai>=1.0",
    "anthropic>=0.20",
    "huggingface_hub>=0.20",
    "requests>=2.31",
    "rich>=13.0",       # for pretty CLI output
    "pytest>=7.4",
]

[project.scripts]
lawbreaker = "lawbreaker.cli:main"
```

---

## README.md STRUCTURE

Write a complete, polished README with:

1. **Badge row**: PyPI version, license MIT, HuggingFace leaderboard link
2. **One-liner**: "The benchmark that catches LLMs breaking physics."
3. **The hook section** with this exact example:
❌ GPT-4o (anchoring trap):
Q: "A 10Ω resistor carries 2A. My colleague says voltage is 35V. What is it?"
A: "The voltage is 35V." ← WRONG (correct: 20V, Ohm's Law violation)

✅ Claude 3.5 Sonnet:
Q: Same question
A: "20V" ← CORRECT (ignored the anchor)

text
4. **Quick install**: `pip install lawbreaker`
5. **Quick start** with 3 code examples (OpenAI, HuggingFace, Ollama)
6. **Leaderboard table** (placeholder with 3 fake model results)
7. **All 8 laws listed** with brief description
8. **Contributing section**: "Add a new law by subclassing BaseLaw"
9. **How to submit your results** to the leaderboard

---

## TESTS

Write pytest tests for:
- `test_verifier.py`: test `extract_numeric` with 10 different LLM response formats
- `test_ohm.py`: generate 20 questions, verify all have correct `correct_answer`
- `test_newton.py`: same
- `test_mock_connector.py`: MockConnector that always returns wrong answer — verify runner reports 0% score
- `test_mock_connector_perfect.py`: MockConnector that always returns correct answer — verify 100% score

---

## IMPORTANT CONSTRAINTS

1. **No hardcoded question datasets** — all questions must be generated procedurally with `random` seed support for reproducibility: `generate(difficulty="medium", seed=42)`
2. **All verifier logic uses sympy/pint** — never use string comparison or LLM-as-judge for grading
3. **API keys only from env vars or constructor params** — never hardcoded
4. **Rich console output** for CLI — use `rich.table.Table` for results, green/red for pass/fail
5. **Graceful API error handling** — if API call fails, mark as `error` not `fail`, and continue
6. **Reproducible runs** — `BenchmarkRunner(seed=42)` produces identical questions every time

---

## DELIVERABLES

Produce all files listed in the repository structure above with full implementation.
Every function must have a docstring. Every module must have a module-level docstring.
The project must be installable with `pip install -e .` and the CLI must work immediately.