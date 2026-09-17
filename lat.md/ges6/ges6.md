# GES 6 Composer Bootstrap

GES 6 is a Composer plus Governance Backplane. Alpha.1 only ships the Composer bootstrap that composes Matt, Spec Kit and Superpowers into a business repo.

Alpha.1 Functionally Complete: official Spec Kit staging, Cursor runtime, and Golden Consumer are PASS. Tag remains PENDING RELEASE HARDENING until an immutable candidate SHA has external evidence.

Alpha.2 synthetic backplane acceptances exist. Live Golden merge observation was skipped by operator and is not a READY claim. See [[governance-backplane]].

v5 execution-centric runtime in `engineeing-skills/` is frozen and is not part of v6 core. See [[ADR-012-ges6-composer-backplane-boundary]], [[composer]], [[governance-backplane]] and [[ges]].

Operator CLI install and consumer `ges init` examples for 6.0.0-alpha.2 live in the repo-root `GUIDE.md`.

- [[composer]] — analyze, resolve, project, reconcile
- [[capability-catalog]] — capability graph, owners, conflicts
- [[source-resolve]] — pinned upstream SHAs and cache
- [[harness-projection]] — Cursor, Codex and AGENTS.md markers
- [[reconcile]] — desired-state apply, check, remove
- [[large-repo-snapshot]] — Git-index Business Source Guard v2 and analyzer GitFileIndex
- [[large-repo-tests]] — large-repo snapshot, overlay, ledger, and fallback oracles
- [[doctor]] — read-only runtime readiness; Installed vs BOOTSTRAP_PENDING vs READY
- [[legacy-v5-detection]] — report v5 without deleting uncertain files
- [[governance-backplane]] — Alpha.2 Work/Policy/Evidence/Trace and Gate A/B runtime
- [[governance-tests]] — synthetic Work, artifact, policy, evidence, and gate oracles
- [[release-hardening]] — immutable candidate SHA, external evidence, strict smoke, native Cursor V2
- [[ges6-tests]] — A01–A26 synthetic acceptances; A27 is the Golden Consumer detached-HEAD contract
- [[bootstrap-tests]] — Alpha.1 first-install loop oracles
- [[closure-tests]] — official Spec Kit staging, Cursor structure, detached Golden HEAD, and closure evidence; `BOOTSTRAP_ALPHA_READY` only after all required Golden ACs PASS
- [[release-hardening-tests]] — external evidence, observer-zero-write, native probe, and doc/tag oracles
