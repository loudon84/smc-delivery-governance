# CHANGES v1.2.0

## Trusted Delivery Control Loop

- Governance kit immutable releases (`dist/governance-kit-v1.2.0/`) with tag/commit/manifest pin
- ArtifactRef v2 in receipts and traceability with semantic verification tools
- Multi-version contract registry with consumer pins and `resolve_contract()`
- Append-only audit transition ledger under `audit/transitions/`
- Full reconciler for Work Package, Roadmap Item, and Feature with role-aware provider gates
- GitHub Actions provenance on acceptance reports (report v2)
- Event-driven sync via `repository_dispatch` plus fail-fast scheduled reconcile
- IntegrationRun model and `tools/integration_run.py`
- Sample receipts and local sync path for v1.1 closure testing

## Migration

See [docs/MIGRATION-v1.1-to-v1.2.md](docs/MIGRATION-v1.1-to-v1.2.md).
