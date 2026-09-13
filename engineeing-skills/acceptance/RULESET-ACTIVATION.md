# Master Ruleset activation (manual — after CI is green)

Do **not** enable required checks while CI is red.

Tracked desired-state: `governance/github/master-ruleset.json` (`smc.repo.ruleset.v1`).

C03-AC02 (actual master Ruleset ACTIVE) remains **OPEN** until a GitHub Admin enables it after CI is continuously green.

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

Require (must match `governance/github/master-ruleset.json`):

- pull request before merge
- status checks: `validate`, `GES Package Gate / validate-package`
- block force push
- block branch deletion
- restrict direct updates

Default approvals: 1 (or Governance Owner written exception for 0 + mandatory PR/status). Not hard-coded by GES Core.

## Verify

```bash
# Desired-state drift checker (read-only, no write privileges):
python tools/check_repo_governance.py --evidence audit/ges/acceptance/<candidate>/ruleset.json --json

# Or with token in env (never commit token):
# SMC_GOVERNANCE_GITHUB_TOKEN=... python tools/check_repo_governance.py --api OWNER REPO --json

# Legacy acceptance verifier:
python engineeing-skills/acceptance/verify_repository_protection.py --evidence audit/ges/acceptance/<candidate>/ruleset.json --json
```

Expected codes: `REPO_GOVERNANCE_PASS` | `REPO_GOVERNANCE_DRIFT` | `REPO_GOVERNANCE_UNAVAILABLE`.

Negative checks (expect reject):

- direct push to master
- force push to master
