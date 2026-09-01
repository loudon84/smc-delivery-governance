# Migration v1.0 → v1.1

## Central Repository

1. Merge v1.1 code.
2. Run `python tools/validate_registry.py`.
3. Run `python tools/validate_feature.py` for every Feature.
4. Enable `.github/workflows/governance-ci.yml`.
5. Configure `SMC_GOVERNANCE_GITHUB_TOKEN` if managed repositories are private.
6. Enable `sync-project-status.yml` after project repositories have installed governance receipts.

## Existing Repositories

For each registered project:

```bash
python tools/governance_sync.py \
  --repo <local-clone> \
  --project <PROJECT-ID> \
  --feature <FEATURE-ID> \
  --with-ci \
  --apply
```

Commit generated `.agents/governance/` and `.github` governance files in the project repository.

Then create/update Receipt after local PRD/Plan/Verification.

## Important

Do not auto-mark old Work Packages DONE during migration. First synchronize receipts, Acceptance Evidence and source revision pins; let central reconciler advance only validated states.
