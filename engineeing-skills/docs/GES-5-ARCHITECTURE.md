# GES 5 architecture

GES keeps one artifact owner per stage and one Delivery state machine. Adaptive routing controls which context is read; it does not remove acceptance, ownership or evidence invariants.

## Canonical flow

Work facts route to SPIKE (research only), BOUNDED or ARCHITECTURAL work. Governed work selects LEAN/FULL monotonically. Domain preplan providers contribute intent to the same Stage PRD, which is grounded and reviewed before a v3.7 Plan seed is emitted. Seeds remain non-executable until all required values and gates pass.

## Execution and review

Engineering method v2 derives a policy and unique epoch per semantic Plan/policy configuration. Commands record output digests and receipts; TDD tracks a matching-command RED/GREEN sequence with fresh content scope. Debugging requires evidenced reproduction, root cause before fix and final successful verification. Plan state and completion both enforce these checks. Final verification, implementation review and commit remain separate authorities.

Semantic review clearance is content-bound. Unresolved prior verdicts cannot be bypassed by changing Plan text. DELTA requires a snapshot bound to the exact prior PASS record and bytes; missing or inconsistent snapshots require FULL.

## Cost and compatibility

The source capsule and review packet are discardable derived context. Test Asset Catalog owns reusable drivers across RM items. Freshness is recomputed, not claimed. Old contracts dispatch to their retained validators and v1 engineering runtime; installed v2 profile policies stay stable until an explicit migration.
