# CHANGES — GES v5.0.6 Adaptive Governance + Frontend Context System

## Summary

Adds Adaptive Governance (Risk Facts v2, Work Router v3, Engineering Method v3, classification correction, LEAN compact plan, token budget/cache, Telemetry v2, Commit Guard v3) and the Frontend Context System (App Registry, Stack Adapters, Per-App UX Baseline, Surface Reuse Gate, Shared UI, Incremental Refresh, Work Scope). Consumer Bootstrap gains `frontend_audit.py` with OBSERVE/GUIDED/ENFORCED adoption. Acceptance corpus extends to G01–G42 plus UC-PROFILE-GOV golden regression.

Pilot / Benchmark remain `NOT_EXECUTED`. `BASELINE.md` unchanged. Bundle stays `5.0.0` pending Release Review.

## Change map (C01–C20)

| ID | Area | Notes |
|---|---|---|
| C01 | Context Optimization Engine | `context-engine/work_scope.py` + token budget / cache |
| C02 | Risk Facts v2 | Sensitive touch vs hard boundary separation |
| C03 | Work Router v3 | BOUNDED/LEAN allowed with sensitive touch |
| C04 | (reserved / folded) | Adaptive routing + method cohesion |
| C05 | Frontend Application Registry | `.agents/ges/frontend/apps-registry.json` |
| C06 | Stack Classifier + Adapters | `frontend-adapters/*/adapter.json` |
| C07 | Per-App UX Baseline | Static scan under `apps/<app-id>/` |
| C08 | Surface Registry | UX Role / owner / actions |
| C09 | UX Surface Reuse Gate | REUSE/EXTEND/… + `UX_SURFACE_REUSE_REQUIRED` |
| C10 | Visual Intent Binder | `smc.ges.visual-intent.v1` |
| C11 | Shared UI Registry | Component reuse; no cross-app surfaces |
| C12 | Incremental Refresh | Path → affected app only |
| C13 | Engineering Method v3 | `BOUNDED_BEHAVIOR` / `SENSITIVE_BOUNDED` / `TDD_FOCUSED_REQUIRED` |
| C14 | Classification Correction | `classification_state.py` PROVISIONAL→FROZEN |
| C15 | LEAN Compact Plan | Seed helpers omit FULL-only sections |
| C16 | Token Budget + Context Cache | LEAN targeted / cache-first |
| C17 | Telemetry v2 | `cost_bucket` aggregation |
| C18 | Commit Guard v3 | CHECKPOINT / CANDIDATE / FINAL |
| C19 | Consumer Bootstrap | `frontend_audit.py` + validate/remediate integration |
| C20 | Acceptance | G31–G42 + UC-PROFILE-GOV |

## Entrypoints

```text
python consumer-bootstrap/frontend_audit.py <repo> [--mode OBSERVE|GUIDED|ENFORCED] [--apply] [--json]
python acceptance/run_acceptance.py   # G01-G42
```

## Compatibility

- Work Facts v1 still accepted; v1 `security_boundary=true` without v2 evidence remains hard risk (fail-safe).
- `BEHAVIOR_CHANGE` remains a deprecated alias of `BOUNDED_BEHAVIOR`.
- Plan contract stays `smc.plan.v3.7`; LEAN/FULL via frontmatter.
- Existing monorepos default to OBSERVE until baselines stabilize.
