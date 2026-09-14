# CHANGES — GES v5.0.3 Safety and Runtime Integration Closure

## Summary

Closed fail-open safety defects (C01–C05), introduced Spec Kit UX adapter (`ADAPTER_READY`) and Superpowers method provider (`UPSTREAM_PINNED`), and renamed the canonical Work Router to `smc-work-router`.

Pilot / Benchmark remain `NOT_EXECUTED`. `BASELINE.md` unchanged. Bundle stays `5.0.0` pending Release Review.

## Claim vocabulary

| Term | Meaning |
|---|---|
| INSPIRED | Method borrow; no upstream identity or call evidence |
| ADAPTER_READY | Interfaces + deterministic conformance; no real external call |
| UPSTREAM_PINNED | Upstream skill bytes pinned + conformance |
| EXTERNAL_VERIFIED | Real external provider call with receipt |

## Migration map

| Old | New |
|---|---|
| `using-superpowers` as Work Router | `smc-work-router` (canonical); `using-superpowers` deprecated shim (one release) |
| New Plan docs → `smc.plan.v3.6` | New Plan → `smc.plan.v3.7` (v3.6 = in-flight compatibility) |
| Incomplete Work Facts → possible NONE | Incomplete/stale/unbound → FULL; raw `route()` not production-receipt eligible |
| Repo evidence positive defaults | Tri-state `parse_evidence`; missing ≠ true |
| Receipt outside transaction | `atomic_write_text` for receipt/pointer/lock |
| v3.7 missing all bindings → skip | Hard `PLAN_DOMAIN_INTENT_BINDING_MISSING` |

## OPEN

- Live master GitHub Ruleset activation remains operational (verifier_implementation vs live_master_protection split).
- Spec Kit `EXTERNAL_VERIFIED` deferred until `specify` is available and a real probe/dispatch receipt is stored.
- Superpowers `EXTERNAL_VERIFIED` deferred; current state is `UPSTREAM_PINNED`.
