# GES v5.0.8 — Adaptive Governance & Context Budget

Closes the v5.0.7 Router / Plan / Context / Delivery boundary with a derived feature-complexity receipt, versioned stage budgets, and work-item context capsules. Bundle identity remains `5.0.0`. No parallel `complexity-router/`, `context-budget/` product roots, or second Plan/Delivery owner.

**Numbering note:** v5.0.7 CHANGES still owns C30 (Baseline Scan Hygiene). This slice documents **v5.0.8 C30–C35**; cross-refs must include the version prefix.

## Change Matrix

| ID | Area | Summary |
| --- | --- | --- |
| C30 | Package Identity | Rebuild `PACKAGE-MANIFEST.json` / `SHA256SUMS`; `--check` prints `PACKAGE_MANIFEST_VALID` beside integrity PASS |
| C31 | Work Router | Derive `smc.ges.feature-complexity.v1` from `work-route.v3`; Scope fail-closed; `CLASSIFICATION_DOWNGRADE_DENIED` |
| C32 | Plan Docs | BOUNDED uses existing `smc.plan.v3.7` + `governance_profile: LEAN`; remove lean-plan migration myth |
| C33 | Context Budget | `policies/context-budget.v1.json` + `budget_controller.decide_budget`; LEAN→FULL then `CONTEXT_BUDGET_INSUFFICIENT` |
| C34 | Context Cache | Capsule keys + `.smc/runs/<id>/context/` persistence; legacy `app_id\|path\|sha` API retained |
| C35 | Acceptance / Telemetry | G51–G60; golden `G01-G60`; redacted budget/cache fields in telemetry summarize |

## Hard Constraints Honored

- No Pilot / Benchmark / real Consumer install in this slice.
- `smc-plan-delivery` post-plan gates unchanged for LEAN and FULL.
- Installer continues to copy `context-engine/` into `.agents/ges/frontend-runtime/`; `.smc/runs/*/context/` is never a managed install artifact.
- `token_budget.budget_for("LEAN").independent_review=False` retained for legacy G cases; review/final_verification independent review is expressed in the new phase policy.

## Verification

```bash
python engineeing-skills/build_package_manifest.py --check   # PACKAGE_MANIFEST_VALID
python engineeing-skills/tests/test_context_engine.py -v
python engineeing-skills/.agents/skills/smc-work-router/scripts/test_work_router.py -v
python engineeing-skills/acceptance/run_acceptance.py        # golden G01-G60
lat check
```
