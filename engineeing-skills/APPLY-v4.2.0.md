# Apply GES v4.2.0 central upgrade

From repository root:

```powershell
git checkout master
git pull

git apply --check <path>\smc-delivery-governance-engineeing-skills-v4.2.0.patch
git apply <path>\smc-delivery-governance-engineeing-skills-v4.2.0.patch

python engineeing-skills\validate_package.py
```

Expected terminal summary:

```text
PACKAGE VALIDATION PASS — 13 pipeline skills, 32 delivery tests, 4 Roadmap tests, declared-mirror + no-Cursor installer smoke, rollback smoke PASS
```

Review `git diff` before commit. The patch performs no Git commit and does not update the accepted `BASELINE.md`; accept/update that baseline only after v4.2 is reviewed and merged.
