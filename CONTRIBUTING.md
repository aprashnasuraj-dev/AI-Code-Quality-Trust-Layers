# Contributing

## Setup

```bash
git clone https://github.com/aprashnasuraj-dev/AI-Code-Quality-Trust-Layers.git
cd AI-Code-Quality-Trust-Layers
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
ruff check .
mypy src/repoverity
python -m build
python -m twine check dist/*
```

## Rule contribution contract

Every new rule PR must include:

1. a concrete failure mechanism, not a style preference;
2. deterministic evidence and an explicit evidence level;
3. severity independent of confidence;
4. positive fixture;
5. explicit clean negative fixture;
6. legitimate exception/edge fixture when counterexamples exist;
7. canonical metadata with limitation and suppression guidance;
8. docs regeneration: `PYTHONPATH=src python scripts/generate_rule_docs.py`;
9. tests showing the intended false-positive boundary.

Prefer AST/token/package metadata over regex. Rules may suggest simplification but must not assume every wrapper/interface/hook is accidental.

## Quality expectations

Keep CLI thin, reporters free of analysis logic, discovery centralized, paths deterministic, and default audit non-mutating/offline. Avoid new runtime dependencies unless stdlib is materially insufficient and the API/dependency has been verified.
