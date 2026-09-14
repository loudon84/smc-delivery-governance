# GES v6 Context Optimization Upgrade

v6 adds a Context Registry, dependency impact analysis and budgeted Context Packages on top of local GES; Bundle 6.0.0 is a candidate, not an accepted baseline.

Formal requirements: [PRD-GES-v6.0.0-Context-Optimization-Upgrade.md](../../docs/prd/PRD-GES-v6.0.0-Context-Optimization-Upgrade.md). Phase 0 defaults: [PRD-GES-v6.0.0-Phase0-Contract-Freeze.md](../../docs/prd/PRD-GES-v6.0.0-Phase0-Contract-Freeze.md). Status remains candidate until Release Review.

## Current Baseline

Accepted Bundle remains 4.1.2. The working tree is Bundle **6.0.0 candidate** with Plan `smc.plan.v4.0`, Context Engine runtime and no in-flight v3.6/v3.7 execution path.

Reusable anchors: [[ges]], [[identity]], [[consumer-bootstrap]], [[runtime-cost#Task Context Artifacts]], [[acceptance-hardening#Runtime Telemetry]]. Runtime tests exist under `engineeing-skills/context-engine/tests/`; Pilot/Benchmark stay NOT_EXECUTED.

## Ownership Boundary

COE owns only derived context and impact manifests. Central Interface / local Implementation, unique Plan and Delivery owners stay unchanged.

[[ADR-001-central-local-boundary]], [[invariants]] and [[skills#Artifact Ownership]] remain authoritative. Module is the business unit; [[domain-packs]] stay professional-method packs.

## Context Contract

Registry and Packages bind source, Work Facts, Plan, modules, dependencies and policy digests. Scope and risk stay orthogonal; budget pressure cannot drop mandatory obligations.

Planning binds request/PRD; execution binds canonical Plan/Todo. Read sets never grant writes. ENFORCED read isolation requires a verified host gateway. Package states READY/INCOMPLETE/BLOCKED/STALE feed Delivery without replacing [[invariants#Four State Classes]].

## Upgrade Changes

C01–C08 are implemented as `engineeing-skills/context-engine/` plus extensions of Work Router, Delivery, validators, bootstrap and telemetry.

- Plan contract `smc.plan.v4.0` requires `context_binding`.
- Validators v3.3–v3.7 reject required `context_binding`; Delivery rejects non-v4.0 with `CONTEXT_LEGACY_PLAN_UNSUPPORTED`.
- Consumer Registry lives in `.agents/ges/context/`; runtime overlay is `.agents/ges/context-engine/`.
- Shared helpers live in `coe_common.py` so imports do not collide with Delivery `common.py` when validators share `sys.path`.
- Canonical `tools/agent-skills/validate_plan.py` routes `smc.plan.v4.0` to `validate_plan_v40.py`.

## Acceptance Mapping

PRD AC-01–24 map to `context-engine/tests/test_ac_suite.py` plus bootstrap AC-17. Document checks and package selftests are not Pilot/Benchmark evidence and do not promote `BASELINE.md`.

Disabled → Shadow → Advisory → Enforced applies only to v6 contracts. Rollback must not resume legacy in-flight Plans.

## Platform Adapters

External adapters report capability only; they never own Delivery or Roadmap truth.

Field requirements live in [ADAPTER-CONTRACT.md](../../engineeing-skills/context-engine/ADAPTER-CONTRACT.md). Dispatch/epoch helpers reject stale receipts; external DONE never writes Roadmap DONE.
