# Migration v1.2 → v1.2.1

v1.2.1 is a closure patch. It does not add a new governance domain. It closes trust gaps in the v1.2 Trusted Delivery Control Loop.

## Breaking enforcement changes

- `receipt_version: "2"` source-controlled ArtifactRefs require full strong identity.
- Feature `source_prd` requires Source PRD ArtifactRef fields.
- Production governance sync requires a canonical Governance Kit release; source-tree install requires explicit `--allow-source-tree`.
- Consumer Work Package `VERIFIED` is based on centrally verified acceptance evidence, not a remote receipt claiming `PASS`.
- Integration PASS requires a real IntegrationRun attempt and runner evidence.
- Tests may not mutate the repository SOT.

## Required migration

1. Apply this patch.
2. Run `cleanup_sample_sot.py`.
3. Run `upgrade_source_prd_artifact.py` for every Feature.
4. Run tests and `verify_state_invariants.py`.
5. Tag `governance-kit-v1.2.1`.
6. Bootstrap actual project repositories from the canonical Kit.
7. Commit actual project receipts.
8. Verify remote bootstrap.
9. Configure acceptance workflow dispatch.
10. Configure a real runner for every Integration Scenario before trying to close Feature DONE.
