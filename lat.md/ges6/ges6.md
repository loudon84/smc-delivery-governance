# GES 6 Composer Bootstrap

GES 6 is a Composer plus Governance Backplane. Alpha.1 only ships the Composer bootstrap that composes Matt, Spec Kit and Superpowers into a business repo.

Alpha.1 Functionally Complete: official Spec Kit staging, Cursor runtime, and Golden Consumer are PASS. Tag remains PENDING RELEASE HARDENING until an immutable candidate SHA has external evidence.

v5 execution-centric runtime in `engineeing-skills/` is frozen and is not part of v6 core. See [[ADR-012-ges6-composer-backplane-boundary]], [[composer]], [[governance-backplane]] and [[ges]].

- [[composer]] — analyze, resolve, project, reconcile
- [[capability-catalog]] — capability graph, owners, conflicts
- [[source-resolve]] — pinned upstream SHAs and cache
- [[harness-projection]] — Cursor, Codex and AGENTS.md markers
- [[reconcile]] — desired-state apply, check, remove
- [[doctor]] — read-only runtime readiness; Installed vs BOOTSTRAP_PENDING vs READY
- [[legacy-v5-detection]] — report v5 without deleting uncertain files
- [[governance-backplane]] — Work/Artifact domain model reserved for alpha.2+
- [[release-hardening]] — immutable candidate SHA, external evidence, strict smoke, native Cursor V2
- [[ges6-tests]] — A01–A26 synthetic acceptances; A27 is the Golden Consumer detached-HEAD contract
- [[bootstrap-tests]] — Alpha.1 first-install loop oracles
- [[closure-tests]] — official Spec Kit staging, Cursor structure, detached Golden HEAD, and closure evidence; `BOOTSTRAP_ALPHA_READY` only after all required Golden ACs PASS
- [[release-hardening-tests]] — external evidence, observer-zero-write, native probe, and doc/tag oracles
