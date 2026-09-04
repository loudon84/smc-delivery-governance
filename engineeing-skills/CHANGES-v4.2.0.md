# GES v4.2.0 — Plan Projection + Scoped Execution Context

Status: **release candidate for central `engineeing-skills/` acceptance**.

## Epic A — `smc.plan.v3.4` Cursor Projection Contract

`smc.plan.v3.4` keeps one canonical `.plan.md` and makes Cursor todo interoperability explicit:

```yaml
todos:
  - id: t1-public-contract
    content: "T1 — Public contract [C01, C02]"
    status: pending
```

Ownership is frozen:

- `id` — Plan identity, owned by Plan author;
- `content` — deterministic UI projection of Markdown Todo heading + `Owns Changes`, owned by Plan author;
- `status` — runtime state, owned only by delivery controller.

The Markdown Todo remains the specification SOT. `content` is a validated projection and is excluded from semantic Plan hash. Runtime `status` is normalized from that hash. v3.3 remains legacy-readable; missing content is a compatibility warning. New Plans are v3.4.

New/changed implementation:

- Plan author `3.5.0`;
- Plan validator `1.4.0`;
- `validate_plan_v34.py`;
- v3.2/v3.3 -> v3.4 migration preserving status + unknown Cursor fields;
- deterministic `sync-content` support;
- seed generator emits quoted Cursor `content`;
- project validation wrapper routes v3.4/v3.3/legacy.

## Epic B — Plan-Scoped Delivery Workspace + Persistent Execution Context

`smc-plan-delivery 1.1.0` changes delivery ownership from repository-wide dirtiness to explicit Plan scope.

### Workspace contract

At the boundary after Static + Semantic Plan clearance and before implementation:

- freeze `base_commit`;
- derive `PLAN_OWNED` paths from Change Matrix;
- snapshot unrelated pre-existing dirty as `AMBIENT_PREEXISTING`;
- reject dirty Plan targets with `DELIVERY_TARGET_CONFLICT`;
- reject unrelated dirty governance tooling with `DELIVERY_TOOLING_BLOCKED`.

During implementation:

- Plan scope has a content-first `scope_fingerprint`;
- ambient state has a separate `ambient_fingerprint`;
- ambient must remain byte/state stable;
- new unrelated mutation -> `DELIVERY_SCOPE_DRIFT`;
- tooling mutation -> `DELIVERY_TOOLING_MUTATION`;
- Plan semantic change -> `DELIVERY_PLAN_SEMANTIC_DRIFT`;
- unexpected HEAD change -> `DELIVERY_HEAD_DRIFT`.

Completion Audit, implementation review, Verification evidence, durable manifest and commit guard bind to these scoped fingerprints. The implementation commit is path-whitelisted; pre-existing ambient dirty may remain after commit if unchanged.

### Persistent execution context

Local runtime state lives under:

```text
.smc/runs/<plan-id>/
  workspace-baseline.json
  resume.json
  ledger-<agent>.jsonl
  errors.jsonl
  continuation-gate.json
```

Workers append their own ledgers. The controller alone owns canonical Plan todo `status`. Resume capsule provides current Todo/content, next step, completed/blocked state, last event/error and workspace fingerprints after context loss/compaction.

The bounded continuation gate detects progress/stall and only decides whether an Agent should continue. It is **not** the SMC Completion Gate and cannot produce `IMPLEMENTED_AND_PROVEN`.

## Delivery proof remains unchanged in principle

```text
Static Gate
-> Semantic Gate
-> Scoped Execution
-> Completion Audit
-> Implementation Review
-> Blocking Verification
-> Evidence Freshness + Durable Manifest
-> post_review Implementation Commit
-> Roadmap DONE
```

The four state classes remain separate: specification, Todo runtime, proof, Roadmap/delivery.

## Compatibility

- Current accepted central baseline remains v4.1.2 until this candidate is reviewed/merged/accepted.
- v3.3 Plan: supported as legacy input; migrate before new v4.2 delivery.
- v3.2 Plan: legacy migration path retained.
- Existing raw `.smc` evidence remains local; no mass rewrite.
- Cursor mirror is a consumer declaration. Core install no longer manufactures `.cursor`; when a consumer already declares `.cursor/skills` or `.cursor/references`, the v4.1.2 full-tree mirror repair semantics are preserved.

## Verification target

- 32 `smc-plan-delivery` tests;
- 4 Roadmap/evidence tests;
- declared Cursor mirror installer smoke;
- non-Cursor consumer installer smoke;
- transactional rollback smoke;
- Python 3.12 compatibility and Windows path-identity regressions retained.
