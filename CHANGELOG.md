# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
