# GES v4.4.0 Candidate — Runtime Cost Optimization

## Scope

v4.4.0 Candidate is a compatibility-first runtime optimization release. It does not introduce a new Plan/PRD/Roadmap contract and does not replace the v4.3 Domain Pack framework.

## Changed Skills

| Skill | Before | Candidate | Change |
|---|---:|---:|---|
| `using-superpowers` | 4.3.1 | 4.4.0 | adaptive complexity routing |
| `smc-plan-review` | 1.1.0 | 1.2.0 | NONE/DELTA/FULL internal review depth + packets |
| `smc-plan-delivery` | 1.2.0 | 1.3.0 | execution-context artifact API (brief/report/review package) |
| `subagent-driven-development` | 4.2.0 | 4.3.0 | file handoff, batching, model tiers, bounded fix loop |

## Not Changed

- `smc.plan.v3.6` and its Test Asset Ledger
- Consumer Profile v2
- Domain Pack v1
- Domain Activation v1
- `post_review`
- Completion Audit / Implementation Review / Verification / Evidence Freshness / Roadmap state ordering

## Upgrade Behavior

The public installation command is unchanged:

```bash
python engineeing-skills/install.py <project> --apply
```

`install.py` prefers `install_v440.py`. The v4.4 installer reuses v4.3.1 transactional copy/profile/domain/mirror/rollback behavior and inserts two additional core self-tests.

## Deferred

A governed `plan_profile: bounded` / Lean Plan path is intentionally deferred because it requires an explicit Plan Contract + Validator + Delivery compatibility change. v4.4A must not simulate that feature by bypassing existing governed artifacts.
