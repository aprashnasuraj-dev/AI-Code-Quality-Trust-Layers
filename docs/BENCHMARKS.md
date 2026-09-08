# Benchmarks

## v0.1.0 release-candidate measurement

Measured on 2026-09-08 with Python 3.13.5 on Linux 6.18.35 x86_64. The harness generates deterministic assignment-only Python modules, invokes the public `python -m repoverity audit ... --format json` path in a subprocess, and records wall time plus child-process high-water RSS. Each workload uses a new temporary repository.

Command:

```bash
PYTHONPATH=src python scripts/benchmark.py
```

| Requested/analyzed LOC | Wall time | Max RSS |
| ---: | ---: | ---: |
| 1,000 | 1.3204 s | 100.8 MiB |
| 10,000 | 1.5309 s | 110.5 MiB |
| 50,000 | 2.5092 s | 169.3 MiB |

Targets from the design brief were <1 s preferred at 1k LOC, <5 s at 10k, <20 s at 50k, and preferably <300 MiB at 50k. The 1k preferred target was not met in this environment; the 10k, 50k and memory targets were met with substantial headroom.

These are environment-specific measurements, not universal performance claims.
