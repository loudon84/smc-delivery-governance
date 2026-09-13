# Master Ruleset activation (manual — after CI is green)

Do **not** enable required checks while CI is red.

## Prerequisites

1. `validate` job PASS on a PR and on `master` push
2. `GES Package Gate / validate-package` PASS on the same runs
3. Status names exactly:
   - `validate`
   - `GES Package Gate / validate-package`

## Create Ruleset

Name: `GES Master Governance`  
Target: `refs/heads/master`  
Enforcement: `ACTIVE`

Require:

- pull request before merge
- status checks: `validate`, `GES Package Gate / validate-package`
- block force push
- block branch deletion
- restrict direct updates

Default approvals: 1 (or Governance Owner written exception for 0 + mandatory PR/status).

## Verify

```bash
# Export ruleset JSON to evidence file, then:
python engineeing-skills/acceptance/verify_repository_protection.py --evidence audit/ges/acceptance/<candidate>/ruleset.json --json

# Or with token in env (never commit token):
# SMC_GOVERNANCE_GITHUB_TOKEN=... python ... --api OWNER REPO --json
```

Negative checks (expect reject):

- direct push to master
- force push to master
