# CHANGES — GES v6.0.0 Context Optimization Engine

## Summary

Adds Context Optimization Engine (Registry, Dependency Graph, Budget Manager, Context Compiler), Plan contract `smc.plan.v4.0` with required `context_binding`, Consumer Bootstrap Registry templates, and fail-closed rejection of in-flight v3.6/v3.7 Plans.

Pilot / Benchmark remain `NOT_EXECUTED`. `BASELINE.md` unchanged. Bundle candidate is `6.0.0`.

## Contracts

| Axis | Value |
|---|---|
| Bundle | 6.0.0 candidate |
| Plan contract | `smc.plan.v4.0` |
| Context schemas | `smc.context.registry.v1` / `impact.v1` / `package.v1` / `request.v1` |
| Consumer Registry path | `.agents/ges/context/` |
| Runtime overlay | `.agents/ges/context-engine/` |

## Compatibility

- No dual-contract execution. Delivery rejects non-v4.0 with `CONTEXT_LEGACY_PLAN_UNSUPPORTED`.
- Validators v3.3–v3.7 reject declared required `context_binding`.
- Historical completed Plans remain read-only evidence.

## Entrypoints

```text
python context-engine/run_selftest.py
python .agents/skills/smc-plan-validator/scripts/validate_plan_v40.py <plan>
python consumer-bootstrap/audit_consumer.py <project>
```

## OPEN

- Real Pilot / Token Benchmark still banned until separately approved.
- Host read enforcement remains ADVISORY until a verified file gateway exists.
- First-language adapter is Python import AST only.
