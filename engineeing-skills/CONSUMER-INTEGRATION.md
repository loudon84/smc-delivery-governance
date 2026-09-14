# Consumer integration v3

GES is an overlay. Consumers retain their legacy Plan validator, code-review-and-quality and verification-before-completion skills. Core never owns project production files.

## Profiles and compatibility

Fresh consumers select generic or a named v3 profile. Domain availability is profile data; required activation is computed from Change Scope. Project policy files declared by project_policy_paths must exist and their bytes are included in the policy digest. Policy precedence is core invariants, approved architecture, project policy, pinned domain defaults; a lower layer cannot relax a higher layer.

Omitting --profile in an existing installation preserves its installed profile and domain metadata, including v2/v1 policy bindings. New v3.7 work requires explicit adoption of a v3 profile and reviewed v2 domain intent. For an existing v2 project use the v3.6 seed entrypoint or GES_PLAN_V36_COMPAT=1 until that migration. Do not change profiles beneath an in-flight Plan and assume its evidence remains fresh.

## Installation and validation

Run install.py in dry-run mode, then --apply. Full managed tests and the configured project validator run by default; --skip-project-validator is an explicit diagnostic escape only and is not production acceptance. Consumer-owned files are not stubbed by default. For greenfield repos that lack `code-review-and-quality` / `verification-before-completion`, pass `--seed-consumer-skills` once: the installer copies missing skills from package templates (`consumer-baseline/` or packaged skill trees) and never overwrites existing consumer files. Managed skill paths (for example `smc-plan-validator`) are created by overlay and are not preflight-required. Transactional failure restores touched bytes. Abstract FAST/STANDARD/REASONING are policy hints for the calling agent, not automatic model switching.

## Consumer Bootstrap (v5.0.5)

After GES install, use `consumer-bootstrap/` for platform onboarding:

1. `audit_consumer.py` — read-only capability audit → `.smc/consumer-bootstrap/consumer-audit-report.{json,md}`
2. `analyze_gap.py` — layered PASS/PARTIAL/MISSING + claim vocabulary
3. `generate_remediation.py` — ordered remediation plan
4. `apply_remediation.py` — dry-run default; `--apply` writes **missing** Spec Kit scaffold, GES_NATIVE method shims, and `.agents/ges/*-binding.json` contracts only
5. `validate_consumer.py` — end-to-end consumer validation report

Hard rules: never write `.specify/spec.md` (second requirements SOT); never overwrite `.agents/ges/profile.json` (installer-owned); never claim `UPSTREAM_PINNED` for GES template shims. See `CHANGES-v5.0.5-consumer-bootstrap.md`.

## Test reuse and command evidence

Use Test Asset Ledger REUSE/EXTEND/NEW with stable catalog IDs. Reuse drivers, never treat a stale test result as fresh. v3.7 Todo completion requires engineering method checks in addition to final evidence, semantic/implementation review and completion audit. A local receipt is auditable working memory, not tamper-resistant signed remote attestation.
