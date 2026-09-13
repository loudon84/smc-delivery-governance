# BASELINE-CANDIDATE — Acceptance Hardening (PRD v5.0.1)

This document records the Hardening candidate over GES 5.0.0 repaired candidate. It does **not** replace accepted `BASELINE.md`.

## Candidate identity

- PRD: `docs/prd/PRD-GES-v5.0.1-Acceptance-Hardening.md`
- Working tree package: Bundle `5.0.0` bytes with Hardening deltas
- Final Bundle SemVer: deferred to Release Review (`5.0.1` vs `5.1.0` per VERSIONING.md)

## Required gates before ACCEPT

1. `python engineeing-skills/build_package_manifest.py --check`
2. `python engineeing-skills/validate_package.py`
3. `python engineeing-skills/acceptance/run_acceptance.py`
4. Golden / Chaos / Consumer Pilot / Benchmark per PRD §27–§29
5. `GES Package Gate / validate-package` stable, then required on `master`

## Verdict options

`ACCEPT` | `ACCEPT_WITH_COST_GAP` | `REJECT` — cost gap must not auto-promote cost claims in `BASELINE.md`.
