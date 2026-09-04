# GES v4.2.0 Candidate Baseline

This document is a candidate. `BASELINE.md` remains the accepted v4.1.2 authority until v4.2.0 is reviewed and accepted.

```text
Bundle Candidate     : 4.2.0
Pipeline Contract    : v4.2
Plan Contract        : smc.plan.v3.4
Delivery Workspace   : smc.delivery.workspace.v1
Execution Context    : smc.execution.context.v1
Evidence Manifest    : smc.evidence.manifest.v2
Commit Policy        : post_review
```

Candidate Skill versions:

| Skill | Version |
|---|---:|
| smc-plan-delivery | 1.1.0 |
| smc-plan-from-approved-prd-ponytail | 3.5.0 |
| smc-plan-validator | 1.4.0 |
| smc-roadmap | 1.2.0 |
| executing-plans | 4.2.0 |
| subagent-driven-development | 4.2.0 |
| using-superpowers | 4.2.0 |

Unchanged governed entry skills retain their accepted versions.

Acceptance requires `python engineeing-skills/validate_package.py` to pass after the patch is applied, plus at least one real consumer integration run.
