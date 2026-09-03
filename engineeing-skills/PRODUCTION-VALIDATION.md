# Production Validation — SMC Governed Engineering Skills v4.1.0

Release date: 2026-09-03

## Release gates

The production ZIP is considered releasable only when all of the following pass from the unpacked package root:

```bash
python validate_package.py
```

The validator covers:

- 13 governed pipeline Skill frontmatter/version checks;
- Python syntax compilation for every shipped `.py` file;
- `smc.plan.v3.3` contract tokens and durable Evidence Manifest contract;
- 11 `smc-plan-delivery` unit/integration-style tests;
- 3 `smc-roadmap v1.1` durable evidence/implementation-commit tests;
- transactional installer smoke test;
- manual rollback smoke test;
- release `SHA256SUMS` verification.

## Delivery tests

The delivery test suite verifies at minimum:

1. Cursor Todo ↔ Markdown Todo deterministic mapping;
2. Todo runtime status update in the single canonical Plan;
3. Plan semantic review remains fresh when only runtime Todo status changes;
4. implementation review becomes stale when implementation content changes;
5. verification evidence becomes stale when implementation content changes;
6. exact verification command mismatch is rejected;
7. completion audit rejects unplanned/untracked scope drift;
8. completion audit becomes stale when implementation content changes;
9. legacy `smc.plan.v3.2` migration to v3.3;
10. `docs_agent/evidence/` does not mutate implementation fingerprint;
11. durable Evidence Manifest becomes stale when implementation content changes.

## Roadmap tests

The Roadmap test suite verifies:

- a `smc-evidence:<plan_id>@sha256:<fingerprint>` reference is accepted only when the referenced implementation commit contains a valid `docs_agent/evidence/<plan_id>-evidence.json`;
- fingerprint mismatch is rejected;
- Roadmap v1.1 rejects repository raw artifact paths as the new evidence-reference contract.

## Transactional upgrade safety

`install.py` is dry-run by default. With `--apply` it:

1. verifies package SHA256 payload integrity;
2. checks required current baseline files;
3. creates `.smc/skill-upgrade-backups/<timestamp>/upgrade-manifest.json`;
4. records original/installed SHA256 for every touched file;
5. updates `.agents/skills` and mirrors the same files to `.cursor/skills`;
6. runs delivery and Roadmap self-tests;
7. runs the repository Skill validator when present;
8. automatically restores the original files if a post-install gate fails.

`rollback.py` supports a later operator-initiated rollback and refuses to overwrite files that have drifted since installation unless `--force` is explicitly supplied.

## Runtime boundary

This release changes development-governance Skills and local developer evidence state only. It does not add a second NodeSkClaw/Hermes production runtime owner and does not alter production Agent artifact storage.
