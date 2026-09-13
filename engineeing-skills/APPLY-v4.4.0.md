# Apply GES v4.4.0 Candidate Patch

## Patch Base

```text
repository: loudon84/smc-delivery-governance
branch: master
base: c3d10d42221052dfc9036a5d09596e299fd4d43c
```

## Apply Source Patch

From the repository root:

```bash
git status --short
git rev-parse HEAD
git apply --check smc-ges-v4.4.0-candidate.patch
git apply smc-ges-v4.4.0-candidate.patch
```

Inspect before committing:

```bash
git diff --check
git diff --stat
python -m py_compile \
  engineeing-skills/install_v440.py \
  engineeing-skills/.agents/skills/smc-plan-review/scripts/assess_plan_review.py \
  engineeing-skills/.agents/skills/smc-plan-review/scripts/build_review_packet.py \
  engineeing-skills/.agents/skills/smc-plan-delivery/scripts/execution_context.py
```

## Upgrade A Consumer Project

The consumer command remains unchanged:

```bash
python engineeing-skills/install.py /path/to/consumer
python engineeing-skills/install.py /path/to/consumer --apply
```

The first command is dry-run. `--apply` remains transactional and runs core self-tests plus the consumer validator configured by the existing Consumer Profile.

## Important Boundary

This candidate does not add a governed BOUNDED Lean Plan contract. Existing Architecture/Roadmap/Stage PRD/Plan work continues through the existing canonical pipeline.
