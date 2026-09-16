---
name: smc-plan-review
description: GES 5 adaptive semantic Plan gate. External NOT_REQUIRED/REQUIRED contract is stable; internal NONE/DELTA/FULL depth is profile- and risk-aware.
version: 2.0.0
---

# SMC Plan Review v2.0

External router remains:

```text
NOT_REQUIRED | REQUIRED
```

Actual review verdict remains:

```text
PASS | REVISE | RETURN_PRD
```

Internal cost depth:

```text
NONE   deterministic clearance for safe unchanged/low-risk semantics
DELTA  review only semantic changes against last accepted snapshot
FULL   full semantic review
```

`governance_profile: LEAN` biases toward NONE/DELTA but never overrides deterministic risk.
`FULL`, Acceptance Contract risk, new/changed boundary, LIVE/FAULT/EXTERNAL proof, lifecycle,
security, schema/protocol, cross-domain ownership or stale upstream semantics force FULL.

## v5.0.9 Review cost closure

- First semantic review defaults to `FULL`; after `REVISE` the next round defaults to `DELTA`.
- `FULL` re-entry requires PRD/scope/route/profile/owner/boundary/public-contract/feature-scope change.
- Loop cap defaults: `FULL ≤ 1`, `DELTA ≤ 2`; beyond cap → `REVIEW_LOOP_EXCEEDED` and
  `PLAN_REVISE_REQUIRED` instead of unbounded automatic review.
- Model review calls go through the managed dispatch runtime with `phase=REVIEW` and a
  review-scoped context envelope (findings + changed sections + affected capsules).

Review snapshots bind normalized semantic Plan hash. Cursor runtime status/display projection is
excluded from semantic change; Change Matrix, ownership, AC, Verification, Domain/Test Asset and
behavior changes are semantic.

A reviewer consumes a normalized review packet/diff and source anchors, not the entire historical
conversation. `NOT_REQUIRED` still writes a content-bound clearance record.
