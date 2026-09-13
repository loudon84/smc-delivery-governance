# GES v4.4.1 Candidate Baseline

This document is a candidate. Accepted `BASELINE.md` remains authoritative until v4.4.1 is reviewed and accepted.

```text
Bundle Candidate          : 4.4.1
Base Source                : master@d28bc3a83b1bc4952199a1dba7935eda65bf9d9f (GES v4.4.0)
Pipeline Contract         : v4.3.1 compatible
Plan Contract             : smc.plan.v3.6 (unchanged)
Domain Pack Contract      : smc.ges.domain-pack.v1 (unchanged)
Consumer Profile          : smc.ges.consumer-profile.v2 (unchanged)
Commit Policy             : post_review (unchanged)
Engineering Method        : smc.execution.engineering-method.v1
TDD Runtime Record        : smc.execution.tdd-event.v1
Debug Runtime Record      : smc.execution.debug-event.v1
```

## Candidate Goal

Build on v4.4.0 adaptive/context-cost optimization by importing mature implementation, TDD, and systematic-debugging methods without creating new Core artifact owners or weakening SMC delivery truth.

## Candidate Changes

- Adds deterministic Todo engineering profiles: `MECHANICAL`, `BEHAVIOR_CHANGE`, `BUG_FIX`, `HIGH_RISK`.
- Adds runtime TDD policy: `TDD_REQUIRED`, `TDD_PREFERRED`, `TDD_NOT_APPLICABLE`.
- Adds systematic debugging root-cause gate and three-failed-fix architecture escalation.
- Adds FAST/STANDARD/REASONING and UNIFIED/INDEPENDENT task-review routing to the method artifact.
- Makes unified spec+quality task review the default for normal-risk SDD work, reducing reviewer seats while preserving separate verdict dimensions.
- Stores method/TDD/debug records only under `.smc/runs/<plan-id>/engineering/`; they are not durable final Verification proof.
- Keeps `install.py` as the stable consumer entrypoint via `install_v441.py`.

## Frozen Invariants Preserved

- `smc.plan.v3.6` and all existing Plan/PRD/Roadmap contracts remain unchanged;
- one canonical Plan and Single Writer remain unchanged;
- `smc-plan-delivery` remains the only governed delivery orchestrator;
- TDD RED is not a final Verification FAIL;
- debugging root-cause discovery cannot expand Plan write scope;
- Completion Audit, Implementation Review, final Verification, Evidence Freshness, `post_review`, and Roadmap DONE remain unchanged.

## Acceptance Requirements

1. `test_engineering_method.py` passes all classification/TDD/debugging cases.
2. Existing v4.4 Plan Review and execution-context self-tests continue to pass.
3. Existing delivery/roadmap/domain validation suites continue to pass.
4. `install.py` dispatches to v4.4.1 without changing consumer commands.
5. At least one consumer profile completes a transactional install/rollback smoke.
6. Replay benchmark compares reviewer seats, turns, and token cost for mechanical, behavior-change, bug-fix, and high-risk tasks.
