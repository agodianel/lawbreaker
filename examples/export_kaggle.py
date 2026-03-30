"""Export benchmark results to Kaggle-ready CSV files.

Reads all JSON result files from examples/results/ and produces:
  - kaggle/leaderboard.csv  (one row per model)
  - kaggle/results.csv      (one row per question per model)

Usage:
    python examples/export_kaggle.py
"""

import csv
import json
import glob
import os
import re
import unicodedata

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(_SCRIPT_DIR, "results")
OUT_DIR = os.path.join(_SCRIPT_DIR, "kaggle")

# Map result subdirectory to provider name
_PROVIDER_MAP = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "gemini": "Google",
    "huggingface": "HuggingFace",
    "ollama": "Ollama",
}

# Unicode → ASCII replacements for physics symbols
_UNICODE_MAP = {
    "Ω": "ohm",
    "Ω": "ohm",
    "μ": "u",
    "°": "deg",
    "×": "x",
    "÷": "/",
    "√": "sqrt",
    "≈": "~",
    "≅": "~",
    "π": "pi",
    "²": "^2",
    "³": "^3",
    "⁴": "^4",
    "¹": "^1",
    "⁰": "^0",
    "⁵": "^5",
    "⁶": "^6",
    "⁷": "^7",
    "⁸": "^8",
    "⁹": "^9",
    "⁻": "-",
    "₀": "0",
    "₁": "1",
    "₂": "2",
    "₃": "3",
    "₄": "4",
    "₅": "5",
    "₆": "6",
    "₇": "7",
    "₈": "8",
    "₉": "9",
    "−": "-",
    "·": "*",
    "'": "'",
    "'": "'",
    """: '"',
    """: '"',
    "→": "->",
    "½": "1/2",
    "θ": "theta",
    "λ": "lambda",
    "ρ": "rho",
    "σ": "sigma",
    "α": "alpha",
    "ε": "epsilon",
    "\u2009": " ",  # thin space
    "\u00a0": " ",  # non-breaking space
}


def _to_ascii(text: str) -> str:
    """Replace Unicode physics symbols with ASCII equivalents."""
    if not text:
        return text
    for uc, asc in _UNICODE_MAP.items():
        text = text.replace(uc, asc)
    # Drop any remaining non-ASCII
    text = text.encode("ascii", errors="ignore").decode("ascii")
    return text


def _detect_provider(filepath: str) -> str:
    """Detect provider from the result file path."""
    parts = filepath.replace("\\", "/").split("/")
    for part in parts:
        if part in _PROVIDER_MAP:
            return _PROVIDER_MAP[part]
    return "Unknown"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    all_files = sorted(glob.glob(os.path.join(RESULTS_DIR, "**", "*.json"), recursive=True))
    all_files = [f for f in all_files if "_leaderboard" not in f]

    if not all_files:
        print("No result files found in", RESULTS_DIR)
        return

    print(f"Found {len(all_files)} result files.\n")

    leaderboard_rows = []
    question_rows = []

    for fpath in all_files:
        data = json.load(open(fpath))
        provider = _detect_provider(fpath)
        model = data["model_name"]
        timestamp = data.get("timestamp", "")

        leaderboard_rows.append({
            "model": model,
            "provider": provider,
            "score": round(data["overall_score"], 4),
            "passed": data["total_passed"],
            "total": data["total_questions"],
            "worst_law": data["worst_law"],
            "worst_trap": data["worst_trap"],
            "timestamp": timestamp,
        })

        for q in data["questions"]:
            qi = q["question"]
            question_rows.append({
                "model": model,
                "provider": provider,
                "law": _to_ascii(qi["law"]),
                "trap_type": qi["trap_type"],
                "difficulty": qi.get("difficulty", ""),
                "question_text": _to_ascii(qi["question_text"]),
                "correct_answer": qi["correct_answer"],
                "correct_unit": _to_ascii(qi.get("correct_unit", "")),
                "llm_response": _to_ascii(q["llm_response"] or ""),
                "extracted_answer": q["extracted_answer"],
                "passed": q["passed"],
                "status": q.get("status", ""),
                "error": q.get("error") or "",
            })

    # Sort leaderboard by score descending
    leaderboard_rows.sort(key=lambda r: r["score"], reverse=True)

    # Write leaderboard.csv (Unix line endings, UTF-8 BOM-free)
    lb_path = os.path.join(OUT_DIR, "leaderboard.csv")
    lb_fields = ["model", "provider", "score", "passed", "total",
                 "worst_law", "worst_trap", "timestamp"]
    with open(lb_path, "w", newline="\n", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=lb_fields)
        writer.writeheader()
        writer.writerows(leaderboard_rows)
    print(f"  leaderboard.csv  ({len(leaderboard_rows)} models) -> {lb_path}")

    # Write results.csv (Unix line endings, UTF-8 BOM-free)
    res_path = os.path.join(OUT_DIR, "results.csv")
    res_fields = ["model", "provider", "law", "trap_type", "difficulty",
                  "question_text", "correct_answer", "correct_unit",
                  "llm_response", "extracted_answer", "passed", "status", "error"]
    with open(res_path, "w", newline="\n", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=res_fields)
        writer.writeheader()
        writer.writerows(question_rows)
    print(f"  results.csv      ({len(question_rows)} questions) -> {res_path}")

    print("\nDone. Upload the kaggle/ folder to Kaggle Datasets.")


if __name__ == "__main__":
    main()
