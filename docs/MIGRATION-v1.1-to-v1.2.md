# Migration v1.1 → v1.2

## Summary

v1.2 upgrades the control plane from Git-based governance automation to a **Trusted Delivery Control Loop**:

- Immutable governance kit releases with tag/commit/manifest pin
- ArtifactRef v2 with semantic verification
- Multi-version contract registry with consumer pins
- Append-only transition audit events
- Full reconciler for Contract / WP / Roadmap / Feature / IntegrationRun
- GitHub Actions provenance for acceptance reports
- Event-driven sync via `repository_dispatch`
- IntegrationRun model for proven cross-repo PASS

## Central Repository

1. Merge v1.2 code and tag `governance-kit-v1.2.0`.
2. Run `python tools/release_governance_kit.py --version 1.2.0 --apply`.
3. Enable `.github/workflows/governance-sync-dispatch.yml`.
4. Replace hourly-only sync with event-driven + hourly repair model.
5. Verify `audit/transitions/` is committed with bot sync commits.

## Project Repositories

Re-sync governance kit:

```bash
python tools/governance_sync.py \
  --repo <local-clone> \
  --project <PROJECT-ID> \
  --feature <FEATURE-ID> \
  --with-ci \
  --apply
```

Upgrade receipts to `receipt_version: "2"` with full 40-char commit SHAs and ArtifactRef fields.

Upgrade acceptance reports to `report_version: "2"` with GitHub Actions provenance.

Configure `SMC_GOVERNANCE_DISPATCH_TOKEN` in project repos to notify central on receipt/acceptance updates.

## Contract Registry

Contracts now require:

```yaml
releases:
  - version: 1.2.1
    state: CONFORMANCE_PASS
consumers:
  REPO-SMC-COPILOT:
    pinned_version: 1.2.1
current_release:
  version: 1.2.1
```

Gates resolve `(contract_id, required_version, consumer_repository)` instead of only `current_release.state`.

## Breaking Changes

- Delivery receipt commits must be full 40-char SHAs.
- Acceptance report v2 requires provenance for central PASS validation.
- Feature DONE requires IntegrationRun PASS (not manual scenario YAML edit).
- Sync workflow fails on system errors instead of swallowing them.
