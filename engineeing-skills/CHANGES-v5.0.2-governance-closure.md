# CHANGES — GES v5.0.2 Governance Architecture Closure

Architecture-only closure for C01–C07 per `docs/prd/PRD-GES-v5.0.2-Governance-Architecture-Closure.md`.
Does **not** promote `BASELINE.md`. Pilot / Benchmark remain `NOT_EXECUTED`.

## Naming migration (legacy → canonical)

| Legacy | Canonical |
|---|---|
| `smc.ges.work-authority.v1` | `smc.ges.work-facts.v1` |
| pack `intent_binding.fields` @ 2.1.0 | `intent_bindings` @ 2.2.0 |
| `DOMAIN_INTENT_BINDING_*` | `PLAN_SOURCE_PRD_*` / `PLAN_DOMAIN_INTENT_STALE` |
| `PLAN_REVIEW_HARD_RISK_FULL_REQUIRED` | `PLAN_REVIEW_CURRENT_RISK_FULL_REQUIRED` (+ `DELTA_INELIGIBLE`) |
| `TELEMETRY_ORPHAN_DISPATCH` | `TELEMETRY_DISPATCH_UNPAIRED` (+ duplicate / model / token codes) |
| `thresholds.v1` (+stability) | `thresholds.v2` (PRD §22 keys) |
| `BENCHMARK_PASS|COST_GAP|REJECT|…` | `BENCHMARK_READY|THRESHOLD_MET|THRESHOLD_NOT_MET|UNPAIRED_CASES|…` |
| `verify_pilot_evidence.py` | `acceptance/pilot/run_pilot.py` |

Read-only compat shims retained for one release where noted in `lat.md/ges/governance-architecture-closure.md`.

## Delivered

- C01: `package_version` from `core/manifest.json` bundle; validate job `git diff --check`
- C02: 9-step plan-review precedence + `delta_eligible`
- C03: `governance/github/master-ruleset.json` + `tools/check_repo_governance.py`
- C04: `work_facts.py` + `route_bound` / `--unsafe-raw-facts`
- C05: FE token canonical+alias; child preplan error propagation; intent_bindings 2.2.0; seed writes `source_prd`
- C06: receipt → lock → PASS; receipts under `.smc/ges-install-receipts/`
- C07: telemetry completeness codes + `ingest --event-json`; paired benchmark engine + synthetic selftest; pilot matrix (12 slots, NOT_EXECUTED)

## OPEN

- **C03-AC02**: master branch Ruleset must be enabled manually by GitHub Admin after CI is continuously green (`gh` not authenticated in this slice).
- Real Consumer Pilot execution — out of scope
- Real 4.4.1 vs 5.x Benchmark — out of scope
- Bundle SemVer / Release Review — deferred
