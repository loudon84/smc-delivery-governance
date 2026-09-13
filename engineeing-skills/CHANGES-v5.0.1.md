# CHANGES — GES Acceptance Hardening (PRD v5.0.1)

Candidate slice over Bundle 5.0.0. PRD version is independent of Bundle SemVer; Release Review decides `5.0.1` vs `5.1.0`.

## Implemented

- **C02 Work Router Research Trust**: `research_only` is hint-only; `effective_research_only` requires authority facts; fail-closed reasons.
- **C03 Structured Risk Runtime**: `domain-runtime/risk_signals.py` shared by PRD / Plan / Review; negation-aware hints; LEAN first-review clearance; Plan seed Risk Facts Snapshot.
- **C04 Domain Semantic Validation**: `domain_table` enum/conditional primitives; FE/BE/Ops preplan + review validators.
- **C05 install-lock.v2**: release identity + owned_files; safe stale reconciliation; v1 skip destructive cleanup.
- **C06 Runtime Telemetry**: `runtime_metrics.py` + source_context cache hit/miss hooks (not Final Evidence).
- **C01 Package Gate**: `ges-package-gate` job in `.github/workflows/governance-ci.yml` (set required after stable PASS).
- **Acceptance tooling**: `engineeing-skills/acceptance/` golden runner + benchmark stub.

## Not claimed yet

- Full G01–G30 corpus expansion and Consumer Pilot / cost benchmark evidence
- GitHub `master` required status activation (manual ruleset after gate stability)
- `BASELINE.md` promotion
