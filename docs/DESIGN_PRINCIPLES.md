# Design Principles

1. Evidence before summary: every finding exposes observation, mechanism, confidence, counterexample and action.
2. Static and local by default: no telemetry, source upload, target-code import, or target-code execution.
3. Severity is not confidence: a heuristic clue cannot become a critical claim merely because it sounds concerning.
4. Candidate rules, not automatic architecture rewrites: unusual abstractions may encode real framework or compatibility contracts.
5. Determinism: sorted discovery, stable fingerprints and stable report ordering are product requirements.
6. Complement existing tools: Ruff, type checkers and security scanners remain better at their core domains.
7. False positives are product defects when a general legitimate pattern can be recognized safely.
