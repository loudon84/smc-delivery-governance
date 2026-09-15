# GES v5.0.9 — Runtime Cost Closure

**Baseline:** GES v5.0.8  
**Bundle identity:** remains `5.0.0`  
**Change type:** RUNTIME_COST_CLOSURE_ONLY

## Summary

Forces Budget / Cache / Telemetry into Plan Author → Model Dispatch → Delivery Worker → Review. No second Router, Plan contract, or Delivery pipeline.

## Changes

| ID | Area | Notes |
|---|---|---|
| C01 | Model Dispatch | `context-engine/model_dispatch.py` + permit |
| C02 | Harness Contract | `harness_contract.py` ENFORCED/OBSERVABLE/UNMANAGED |
| C03 | Context Envelope | `context_envelope.py` phase-scoped minimum context |
| C04–C05 | Budget/Cache | Reuse `budget_controller` + `CapsuleStore` on dispatch path |
| C06 | Telemetry | `usage_status`; unavailable ≠ 0; pair-rate counters |
| C07 | Plan Author | `plan_author_cost.py` structured patches + grounding dir |
| C08 | Delivery Worker | Mandatory task brief + `worker-context-envelope.json` |
| C09 | Review | REVISE→DELTA default; FULL re-entry; loop cap |
| C10 | Stage Closure | `stage_cost_closure.py` PASS / PASS_USAGE_UNAVAILABLE / BLOCKED |
| Probe | Install identity | Infers `5.0.8` / `5.0.9` feature slices |
| Acceptance | G61–G80 | Golden `G01-G80` |

## Hard constraints honored

- No `complexity-router/` or `context-budget/` product roots
- No `lean-plan.v1`; `smc.plan.v3.7` unchanged as authoring contract
- `.agents/ges/frontend-runtime` name retained
- No required real Consumer Pilot install in this slice (G80 simulated)

## Verification

```text
python engineeing-skills/acceptance/run_acceptance.py
python engineeing-skills/validate_package_v500.py
lat check
```
