# GES v4.4.0 Candidate Baseline

This document is a candidate. Accepted `BASELINE.md` remains authoritative until v4.4.0 is reviewed and accepted.

```text
Bundle Candidate          : 4.4.0
Base Source                : master@eea9fa8 (GES v4.3.1)
Pipeline Contract         : v4.3.1 compatible
Plan Contract             : smc.plan.v3.6 (unchanged)
Domain Pack Contract      : smc.ges.domain-pack.v1 (unchanged)
Consumer Profile          : smc.ges.consumer-profile.v2 (unchanged)
Commit Policy             : post_review (unchanged)
Adaptive Routing          : smc.ges.complexity-routing.v1
Semantic Review Packet    : smc.plan.semantic-review-packet.v1
```

## Candidate Goal

Reduce token/context cost and subagent seats without weakening delivery truth or changing project installation references.

## Candidate Changes

- SPIKE / BOUNDED / ARCHITECTURAL front-door classification with monotonic upgrade.
- Compatibility boundary: existing governed artifacts still use the full canonical pipeline; no Lean Plan Contract in this candidate.
- Plan Review retains `NOT_REQUIRED/REQUIRED` public routing and adds internal `NONE/DELTA/FULL` depth.
- DELTA review uses a normalized semantic snapshot/diff and escalates to FULL when no safe snapshot exists.
- Execution context generates per-Todo briefs, report paths and write-scoped review packages in `.smc/runs/<plan-id>/`.
- SDD adds conservative same-shape batching, model tiers and bounded fix-loop escalation.
- `install.py` remains the stable entrypoint and dispatches to `install_v440.py`, which reuses v4.3.1 transactional Consumer Profile/Domain Pack installation semantics.

## Frozen Invariants Preserved

- one canonical Plan for governed delivery;
- one production write owner per `path#symbol`;
- Static PASS != implementation complete;
- Todo completed != implemented-and-proven;
- content change invalidates stale proof;
- blocking failure cannot be downgraded to observation;
- `post_review` implementation commit boundary;
- implementation commit and Roadmap DONE remain separate states;
- `smc-plan-delivery` remains the only governed delivery orchestrator.

## Acceptance Requirements

1. `install.py` dry-run and apply paths dispatch v4.4 without changing the consumer command.
2. Existing v4.3.1 delivery self-tests continue to pass.
3. `smc-plan-review/scripts/selftest.py` passes.
4. `smc-plan-delivery/scripts/test_context_artifacts.py` passes.
5. At least one existing consumer profile completes transactional install + project validator.
6. Replay benchmark records tokens/turns/subagent seats for v4.3 vs v4.4 on representative mechanical, integration and high-risk tasks.
