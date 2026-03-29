"""
Symbolic physics verifier — extracts numeric answers from LLM text and
validates them against the correct value using sympy and pint.

No string comparison or LLM-as-judge is ever used for grading.
"""

from __future__ import annotations

import re
from typing import Optional

from pint import UnitRegistry

ureg = UnitRegistry()


class PhysicsVerifier:
    """Verifies LLM answers against correct physics results.

    Uses regex-based extraction for numeric values and pint for
    dimensional analysis.
    """

    # Regex patterns ordered from most specific to most general
    _NUMERIC_PATTERNS = [
        # Scientific notation: 1.23e4, 1.23E-4, 1.23×10^4
        r"[≈≅~]?\s*([+-]?\d+\.?\d*)\s*[×x]\s*10\^?\s*([+-]?\d+)",
        r"[≈≅~]?\s*([+-]?\d+\.?\d*)\s*[eE]\s*([+-]?\d+)",
        # Standard decimal: 10.5, -3.14, +42.0
        r"[≈≅~]?\s*([+-]?\d+\.\d+)",
        # Integer: 10, -5, +42
        r"[≈≅~]?\s*([+-]?\d+)",
    ]

    def verify_numeric(
        self,
        llm_answer: float,
        correct_answer: float,
        tolerance: float = 0.01,
    ) -> bool:
        """Check if the LLM answer is within tolerance of the correct answer.

        Args:
            llm_answer: The numeric value extracted from the LLM response.
            correct_answer: The known correct value.
            tolerance: Maximum allowed relative error (default 1%).

        Returns:
            True if the relative error is within tolerance.
        """
        if correct_answer == 0:
            return abs(llm_answer) < tolerance
        relative_error = abs(llm_answer - correct_answer) / abs(correct_answer)
        return relative_error <= tolerance

    def extract_numeric(self, llm_response: str) -> Optional[float]:
        """Parse the final numeric answer from a free-text LLM response.

        LLMs often show working before the answer, so we prefer:
        1. A number on the last non-empty line (the final answer)
        2. The last scientific-notation number in the full text
        3. The last decimal/integer in the full text

        Handles formats such as:
            "The voltage is 10V"
            "V = 10 volts"
            "10.0"
            "≈10"
            "approximately 9.81 N"
            "3.2e3 Pa"
            "-273.15"
            "Answer: 42 J"
            "KE = ½ × 8.75 × (8.83)² = 341.114 J\\n\\n341.114 J"

        Args:
            llm_response: Raw text string from the LLM.

        Returns:
            The extracted float, or None if no number was found.
        """
        if not llm_response or not llm_response.strip():
            return None

        text = llm_response.strip()

        # --- Strategy: extract the LAST number, since LLMs put the answer last ---

        # Helper: find all scientific notation matches (×10^N style)
        sci_matches = list(re.finditer(
            r"[≈≅~]?\s*([+-]?\d+\.?\d*)\s*[×x]\s*10\s*\^?\s*([+-]?\d+)", text
        ))
        if sci_matches:
            m = sci_matches[-1]
            mantissa = float(m.group(1))
            exponent = int(m.group(2))
            try:
                return mantissa * (10.0 ** exponent)
            except OverflowError:
                return float("inf") if mantissa >= 0 else float("-inf")

        # Helper: find all e-notation matches
        e_matches = list(re.finditer(
            r"[≈≅~]?\s*([+-]?\d+\.?\d*)[eE]([+-]?\d+)", text
        ))
        if e_matches:
            m = e_matches[-1]
            try:
                return float(m.group(1) + "e" + m.group(2))
            except (OverflowError, ValueError):
                return float("inf")

        # Strip commas from numbers (e.g. "345,085.3" → "345085.3")
        cleaned = re.sub(r"(\d),(\d)", r"\1\2", text)

        # Find last decimal number
        dec_matches = list(re.finditer(r"[≈≅~]?\s*([+-]?\d+\.\d+)", cleaned))
        if dec_matches:
            return float(dec_matches[-1].group(1))

        # Find last integer followed by a unit or end of string
        int_matches = list(re.finditer(
            r"[≈≅~]?\s*([+-]?\d+)\s*(?:[a-zA-Zμ°Ω]|$)", cleaned
        ))
        if int_matches:
            return float(int_matches[-1].group(1))

        # Last resort: last standalone number
        num_matches = list(re.finditer(r"([+-]?\d+\.?\d*)", cleaned))
        if num_matches:
            return float(num_matches[-1].group(1))

        return None

    def check_units(
        self, value: float, unit_str: str, expected_unit: str
    ) -> bool:
        """Check if two unit strings are dimensionally compatible using pint.

        Args:
            value: Numeric value (unused in check, but available for conversion).
            unit_str: Unit string extracted from the LLM response.
            expected_unit: The expected unit.

        Returns:
            True if both units have the same dimensionality.
        """
        try:
            given = ureg.parse_expression(f"1 {unit_str}")
            expected = ureg.parse_expression(f"1 {expected_unit}")
            return given.dimensionality == expected.dimensionality
        except Exception:
            return False
