# GES 6.0.0 candidate

Context Optimization Engine on top of GES 5 repaired candidate. New Plans use
`smc.plan.v4.0` with required context binding. In-flight v3.6/v3.7 Plans are rejected
by the v6 runtime. See CHANGES-v6.0.0.md.

# Changelog

## v6.0.0 Candidate — 2026-09-14

### Added

- Context Registry, path identity, discovery proposals and registry snapshots.
- Context Compiler, Budget Manager, freshness gates and ADVISORY/ENFORCED handshake.
- Dependency graph (declared + Python imports), impact manifests and review triggers.
- Plan contract `smc.plan.v4.0` and validator; legacy capability rejection on v3.3–v3.7.
- Consumer bootstrap templates/audit for `.agents/ges/context/`.
- Dispatch/epoch ledger helpers and external adapter capability reports.

### Compatibility

- No dual-contract execution. Completed historical Plans remain read-only evidence.
- Consumer Registry under `.agents/ges/context/` is not overlay-owned.

## v5.0.0 repaired candidate

Adaptive profiles, Domain v2 preplan, Plan v3.7 compatibility, command-bound method freshness and closed review gates. Existing v3.6 consumers preserve policy bindings. See CHANGES-v5.0.0.md.
