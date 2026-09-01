# CHANGES v1.2.1

## Engineering Delivery Control Plane — Closed Loop v1

- Tests run against isolated `SMC_GOVERNANCE_ROOT`; central SOT mutation during tests is rejected.
- Sample-derived `delivery-ledger`, traceability and sync state can be quarantined with `cleanup_sample_sot.py`.
- Real remote bootstrap verifier for governed repositories.
- Governance Kit installs only from a verified canonical release Bundle by default.
- Governance Kit `SHA256SUMS` includes `manifest.json`.
- ArtifactRef v2 now requires commit/blob SHA/content SHA-256 for source-controlled delivery artifacts.
- Feature Source PRD becomes a strong ArtifactRef.
- Acceptance PASS uses a separate GitHub Actions attestation artifact verified by central governance.
- Sync workflows correctly distinguish exit `0`, expected-non-ready `2`, and system-error `1`.
- Contract Release state is reconciled from Provider Release / Consumer Pin / Conformance evidence.
- Integration runs are immutable attempts with a reviewed scenario runner and workflow evidence.
- State writes and audit events use a transactional helper with rollback.
- State invariant checker verifies audit chains, materialized state and sample contamination.
