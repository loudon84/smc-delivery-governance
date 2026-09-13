# Apply GES v4.4.1 Candidate Patch

## Patch Base

```text
repository: loudon84/smc-delivery-governance
branch: master
base: d28bc3a83b1bc4952199a1dba7935eda65bf9d9f
```

This patch is a context-only unified diff. It intentionally omits Git blob `index` lines and executable-mode changes so `git apply` does not depend on historical base blobs or Windows executable-bit behavior.

## Apply

From repository root:

```bash
git status --short
git rev-parse HEAD
git apply --check smc-ges-v4.4.1-candidate.patch
git apply smc-ges-v4.4.1-candidate.patch
```

Then validate:

```bash
git diff --check
python engineeing-skills/.agents/skills/smc-plan-delivery/scripts/test_engineering_method.py -q
python engineeing-skills/validate_package.py
```

## Upgrade Consumer

Consumer commands remain unchanged:

```bash
python engineeing-skills/install.py /path/to/consumer
python engineeing-skills/install.py /path/to/consumer --apply
```

The first is dry-run; `--apply` remains transactional.
