# Package Validation — v1.1.0

Generated: 2026-09-01

## Validation

```text
REGISTRY VALID
projects=2 repositories=2 teams=2 contracts=2
FEATURE VALID
feature_id=FEAT-SKILL-FIRST-001
participants=2
global_changes=5
work_packages=2
contracts=1
source_revision=SKILL-FIRST-PRD@4.0.1
PROJECT-NODESKCLAW — NoDeskClaw [ACTIVE]
  REPO-NODESKCLAW loudon84/nodeskclaw governance=OUT_OF_SYNC branch=main
    FEAT-SKILL-FIRST-001 WP-SKILL-FIRST-NODESKCLAW status=DONE sync=MISSING_RECEIPT
PROJECT-SMC-COPILOT — SMC Copilot [ACTIVE]
  REPO-SMC-COPILOT loudon84/smc-copilot governance=OUT_OF_SYNC branch=work/prd-v4.0
    FEAT-SKILL-FIRST-001 WP-SKILL-FIRST-SMC-COPILOT status=IMPLEMENTING sync=MISSING_RECEIPT
Program PROGRAM-AGENT-PLATFORM — SMC Agent Application Platform [ACTIVE]

FEAT-SKILL-FIRST-001 [IMPLEMENTING] Skill First Employee Execution
  WP-SKILL-FIRST-NODESKCLAW REPO-NODESKCLAW status=DONE sync=MISSING_RECEIPT
  WP-SKILL-FIRST-SMC-COPILOT REPO-SMC-COPILOT status=IMPLEMENTING sync=MISSING_RECEIPT
  Integration INT-SKILL-FIRST-001 state=WAITING_CONSUMER
.........                                                                [100%]
9 passed in 16.47s
```

## Expected migration state

Existing repositories are intentionally `OUT_OF_SYNC` / Work Packages `MISSING_RECEIPT` until the v1.1 Governance Kit and Delivery Receipts are committed in each project. The scheduled reconciler moves them back to `SYNCED` only after receipt/source/contract validation.
