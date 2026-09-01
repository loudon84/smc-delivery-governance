# v1.1.0 Changes

## Added

- Project onboarding registry automation and repository governance adoption states.
- Project bootstrap report and scheduled central project-status sync.
- Immutable Source PRD / `source_revision` linkage for cross-repo Features.
- Work Package `sync_state` and Delivery Receipt contract.
- Delivery Ledger and traceability graph.
- GitHub Issue/Bug/PR label templates and automatic label workflow.
- PRD Acceptance Manifest / Report schemas and local runner.
- Central Acceptance Gate.
- Central lifecycle transition engine and evidence-aware state reconciliation.
- Central GitHub Actions CI and hourly repository synchronization.
- Project Governance CI template.
- New universal skills: `smc-project-binding`, `smc-delivery-receipt`, `smc-prd-acceptance`.
- New cross-repo skills: `smc-project-onboarding`, `smc-delivery-trace`.

## Changed

- `governance_sync.py` now syncs Binding, Work Packages, Contracts, schemas, validation tool and optional GitHub workflows/templates.
- Governance lock uses synchronized content hashes rather than unrelated central HEAD changes.
- Remote repository reports only observed facts; central status is advanced only by central state machine/reconciler.
- `validate_feature.py` validates Source Revision and traceability.
- Registry validation now covers Projects, Repositories and Contracts with referential integrity.

## Migration Note

After deploying v1.1, existing repositories initially become `MISSING_RECEIPT` / `OUT_OF_SYNC` until the v1.1 Governance Kit is synchronized and their Delivery Receipts are committed. This is an intentional fail-closed migration state, not a product regression.
