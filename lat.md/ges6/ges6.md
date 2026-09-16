# GES 6 Composer Bootstrap

GES 6 is a Composer plus Governance Backplane. Alpha.1 only ships the Composer bootstrap that composes Matt, Spec Kit and Superpowers into a business repo.

v5 execution-centric runtime in `engineeing-skills/` is frozen and is not part of v6 core. See [[ADR-012-ges6-composer-backplane-boundary]], [[composer]], [[governance-backplane]] and [[ges]].

- [[composer]] — analyze, resolve, project, reconcile
- [[capability-catalog]] — capability graph, owners, conflicts
- [[source-resolve]] — pinned upstream SHAs and cache
- [[harness-projection]] — Cursor, Codex and AGENTS.md markers
- [[reconcile]] — desired-state apply, check, remove
- [[legacy-v5-detection]] — report v5 without deleting uncertain files
- [[governance-backplane]] — Work/Artifact domain model reserved for alpha.2+
- [[ges6-tests]] — A01–A16 acceptance specs
