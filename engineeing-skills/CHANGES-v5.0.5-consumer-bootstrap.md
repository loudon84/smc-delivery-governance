# CHANGES — GES v5.0.5 Consumer Bootstrap Platform Integration

## Summary

Added `consumer-bootstrap/` platform integration: read-only audit, gap analysis, remediation plan generation, transactional apply (missing-only templates), and consumer validation. Spec Kit scaffold and method shims use GES-owned templates (`ADAPTER_READY` / `GES_NATIVE`); Bridge contracts land under `.agents/ges/*.json`.

Pilot / Benchmark remain `NOT_EXECUTED`. `BASELINE.md` unchanged. Bundle stays `5.0.0` pending Release Review.

## Claim vocabulary (unchanged)

| Term | Meaning |
|---|---|
| INSPIRED | Method borrow; no upstream identity or call evidence |
| ADAPTER_READY | Interfaces + deterministic conformance; no real external call |
| UPSTREAM_PINNED | Upstream skill bytes pinned + conformance |
| EXTERNAL_VERIFIED | Real external provider call with receipt |
| GES_NATIVE | Native GES path / shim without upstream bytes |
| NATIVE_ONLY | External CLI absent; native fallback honest |

## Contract narrowing vs v5.0.3

| Topic | v5.0.3 | v5.0.5 |
|---|---|---|
| `.specify/spec.md` | Forbidden as second requirements SOT | Still forbidden |
| `.specify/` scaffold (`constitution.md`, `templates/`, `scripts/`, `specs/README.md`) | Probe/import must not write | Bootstrap `--apply` may create **missing** scaffold only |
| Spec Kit probe/import | Never `init`, never write Consumer-root `.specify/` SOT | Unchanged |
| Method skills without provenance | Not auto-installed | Optional `GES_NATIVE` routing shims; never claim `UPSTREAM_PINNED` |
| Config root | `.agents/ges/*.json` | Same; no `.ges/*.yaml`, no PyYAML |

## Entrypoints

```text
python consumer-bootstrap/audit_consumer.py <project>
python consumer-bootstrap/analyze_gap.py <project>
python consumer-bootstrap/generate_remediation.py <project>
python consumer-bootstrap/apply_remediation.py <project>            # dry-run
python consumer-bootstrap/apply_remediation.py <project> --apply
python consumer-bootstrap/validate_consumer.py <project>
```

## OPEN

- smc-copilot-desktop `--apply` pending explicit consumer confirmation.
- ChatBox Artifact Preview end-to-end product validation (PRD §10) deferred.
- Spec Kit / Superpowers `EXTERNAL_VERIFIED` still requires real CLI/provider receipts.
