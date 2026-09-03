# Changelog

## v4.1.0 — 2026-09-03

- Added `smc-plan-delivery v1.0.0` as the unique post-Plan delivery orchestrator.
- Upgraded SMC Plan contract to `smc.plan.v3.3`.
- Unified Cursor UI Todo state and SMC Plan Todo identity in one canonical Plan.
- Added deterministic working-tree content fingerprint.
- Added content-bound plan and implementation review ledger.
- Added local verification evidence ledger with FRESH/STALE/MISSING semantics.
- Added Plan Completion Audit and commit guard.
- Reworked execution skills as implementation engines under delivery orchestration.
- Changed new Plan Verification Ledger from physical `Evidence Output` paths to `Evidence Policy`.
- Updated Roadmap DONE proof to accept logical evidence references while retaining real implementation commit validation.
- Added read-only `DIAGNOSE_PLAN` mode.
- Preserved post_review, single-writer, lifecycle closure, AC/DoD traceability, Ponytail minimality and separate Roadmap commit invariants.
- Production hardening: added durable `docs_agent/evidence/<plan_id>-evidence.json` Manifest committed with implementation while keeping raw logs out of Git.
- Production hardening: `smc-roadmap v1.1` now resolves `smc-evidence:` against the Manifest stored in the referenced implementation commit and validates Plan ID/fingerprint/digest/audit/review/blocking verification proof.
- Production hardening: transactional installer with automatic rollback on post-install validation failure plus standalone `rollback.py` with post-install drift protection.
- Production hardening: package SHA256 integrity verification before installation.
