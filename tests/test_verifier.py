"""
Tests for PhysicsVerifier — exercise extract_numeric with 10+ LLM response formats.
"""

import pytest

from lawbreaker.core.verifier import PhysicsVerifier


@pytest.fixture
def verifier():
    """Return a fresh PhysicsVerifier instance."""
    return PhysicsVerifier()


class TestExtractNumeric:
    """Tests for extract_numeric covering diverse LLM output formats."""

    def test_plain_number(self, verifier):
        """Bare number string."""
        assert verifier.extract_numeric("10.5") == 10.5

    def test_with_unit_suffix(self, verifier):
        """Number followed by unit abbreviation."""
        assert verifier.extract_numeric("10.5 V") == 10.5

    def test_equals_format(self, verifier):
        """Variable = value pattern."""
        assert verifier.extract_numeric("V = 20 volts") == 20.0

    def test_sentence_format(self, verifier):
        """Full sentence with number inside."""
        assert verifier.extract_numeric("The voltage is 10V") == 10.0

    def test_approximately(self, verifier):
        """Approximation symbol."""
        assert verifier.extract_numeric("≈10") == 10.0

    def test_negative(self, verifier):
        """Negative number."""
        assert verifier.extract_numeric("-273.15 K") == -273.15

    def test_scientific_e(self, verifier):
        """E-notation."""
        assert verifier.extract_numeric("3.2e3 Pa") == 3200.0

    def test_scientific_times(self, verifier):
        """× notation scientific."""
        assert verifier.extract_numeric("8.99×10^9") == 8.99e9

    def test_answer_prefix(self, verifier):
        """Answer: prefix common in LLMs."""
        assert verifier.extract_numeric("Answer: 42 J") == 42.0

    def test_wordy_response(self, verifier):
        """LLM gives explanation then number."""
        result = verifier.extract_numeric(
            "Using Ohm's law, V = IR = 10 × 2 = 20V. The answer is 20 V."
        )
        assert result is not None
        # Should extract a number (the first one it finds)
        assert isinstance(result, float)

    def test_empty_string(self, verifier):
        """Empty input returns None."""
        assert verifier.extract_numeric("") is None

    def test_no_number(self, verifier):
        """Text with no numbers returns None."""
        assert verifier.extract_numeric("I don't know") is None

    def test_integer(self, verifier):
        """Plain integer."""
        assert verifier.extract_numeric("42") == 42.0

    def test_tilde_approx(self, verifier):
        """Tilde approximation."""
        assert verifier.extract_numeric("~9.81 N") == 9.81


class TestVerifyNumeric:
    """Tests for verify_numeric tolerance checking."""

    def test_exact_match(self, verifier):
        """Exact match is within tolerance."""
        assert verifier.verify_numeric(20.0, 20.0) is True

    def test_within_tolerance(self, verifier):
        """Value within 1% tolerance."""
        assert verifier.verify_numeric(20.1, 20.0, tolerance=0.01) is True

    def test_outside_tolerance(self, verifier):
        """Value outside 1% tolerance."""
        assert verifier.verify_numeric(25.0, 20.0, tolerance=0.01) is False

    def test_zero_correct(self, verifier):
        """Correct answer is zero — absolute tolerance check."""
        assert verifier.verify_numeric(0.005, 0.0, tolerance=0.01) is True
        assert verifier.verify_numeric(0.05, 0.0, tolerance=0.01) is False

    def test_negative_values(self, verifier):
        """Negative correct answer."""
        assert verifier.verify_numeric(-9.8, -9.81, tolerance=0.01) is True


class TestCheckUnits:
    """Tests for pint-based dimensional analysis."""

    def test_compatible_units(self, verifier):
        """V and volt are the same dimension."""
        assert verifier.check_units(10, "V", "V") is True

    def test_incompatible_units(self, verifier):
        """V and N are different dimensions."""
        assert verifier.check_units(10, "V", "N") is False

    def test_prefix_compatibility(self, verifier):
        """mA and A are same dimension."""
        assert verifier.check_units(10, "mA", "A") is True
