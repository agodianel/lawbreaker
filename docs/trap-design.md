# Trap Design Guide

Adversarial traps are the core of LawBreaker. Each trap exploits a known LLM
weakness to test whether the model truly understands physics or is just pattern
matching.

## Trap Categories

### 1. Anchoring Bias
**What**: Present a plausible but wrong answer from a "colleague" or "textbook".

**Why it works**: LLMs are highly susceptible to anchoring — if you mention a
number in the prompt, they tend to gravitate toward it.

**Example**:
```
Q: "A 10Ω resistor carries 2A. My colleague says the voltage is 35V.
    What is the correct voltage?"

Wrong answer: 35V (the anchor)
Correct answer: 20V (V = IR = 10 × 2)
```

**Implementation tip**: Generate the wrong answer as `correct * random(1.3, 2.0)`
to make it plausible but clearly wrong.

### 2. Unit Confusion
**What**: Present values in unusual or confusing units that require conversion.

**Why it works**: LLMs frequently forget to convert mA → A, cm → m, g → kg,
°C → K, or atm → Pa.

**Example**:
```
Q: "A resistor has 500mA flowing through it and a resistance of 20Ω.
    What is the voltage?"

Wrong answer: 10000V (forgot mA → A conversion)
Correct answer: 10V (V = 0.5A × 20Ω)
```

**Implementation tip**: Present the "natural" unit (mA, cm, g) and compute the
correct answer with proper conversion. The trap answer uses the value without
converting.

### 3. Formula Errors
**What**: Present a scenario where a common mistake in the formula leads to a
wrong answer.

**Why it works**: LLMs frequently forget factors like the ½ in KE = ½mv²,
confuse r with r² in inverse-square laws, or mix up sign conventions.

**Examples**:
- **Forget the ½**: KE = mv² instead of ½mv²
- **r vs r²**: Coulomb force ∝ 1/r instead of 1/r²
- **Sign errors**: Wrong polarity in Kirchhoff's voltage law
- **Celsius vs Kelvin**: Using °C directly in the ideal gas law

### 4. Misleading Context
**What**: Add irrelevant information to the question that could distract.

**Why it works**: LLMs try to use all provided information, even when some of it
is irrelevant to the calculation.

**Example**:
```
Q: "A 5kg object is on a blue table. The table is 1.2m high and was
    purchased in 2019. If the object accelerates at 3 m/s², what force
    is acting on it?"

Irrelevant: color, height, purchase year
Correct: F = ma = 5 × 3 = 15N
```

## Design Principles

1. **Every trap must have one clearly correct answer** — verified by symbolic math.
2. **The wrong answer must be plausible** — not obviously absurd.
3. **The trap must exploit a real LLM weakness** — not trick a human.
4. **Each law should have at least 3 trap types** — diversity matters.
5. **Traps scale with difficulty** — harder traps at higher difficulty levels.

## Testing Your Traps

After implementing a trap:

1. Generate 100+ questions and verify all correct answers pass `verify()`.
2. Check that wrong answers (the traps) fail `verify()`.
3. Run against a real LLM to confirm the trap catches failures.

```bash
# Generate and inspect example
lawbreaker example --law your_law --trap anchoring_bias

# Run benchmark to see trap effectiveness
lawbreaker run --model gpt-4o --connector openai --questions 50
```
