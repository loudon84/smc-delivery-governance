# Upgrade Manifest — SMC Governed Engineering Skills v4.1.2

## Package Type

- Type: overlay upgrade
- Target: existing `loudon84/nodeskclaw` SMC governed skills baseline
- Deletes: none
- Production runtime changes: none
- Git commits performed by installer: none
- Upgrade transaction: per-file backup + installed SHA256 + automatic rollback on failed validation
- Package integrity: `SHA256SUMS` checked before target writes

## New Skill

| Skill | Version | Purpose |
|---|---:|---|
| `smc-plan-delivery` | 1.0.1 | Plan -> implementation -> audit -> review -> verification -> post_review commit -> Roadmap orchestration |

## Upgraded Skills

| Skill | Version | Change |
|---|---:|---|
| `smc-plan-from-approved-prd-ponytail` | 3.4.0 | Plan v3.3, canonical Plan, Cursor todos, evidence policy, diagnose mode |
| `smc-plan-validator` | 1.3.0 | v3.3 canonical/todo/policy/duplicate validation + legacy gate reuse |
| `smc-plan-review` | 1.1.0 | Router vs actual review separation + content-bound clearance |
| `executing-plans` | 4.1.0 | implementation engine only |
| `subagent-driven-development` | 4.1.0 | implementation engine only; controller owns status |
| `smc-roadmap` | 1.1.0 | durable evidence Manifest resolution from implementation commit + stronger DONE gate |
| `using-superpowers` | 4.1.0 | route canonical Plan -> smc-plan-delivery |

## Included Unchanged Pipeline Entry Skills

These SKILL.md files are included to keep the package's end-to-end route explicit; their existing references/scripts remain authoritative in the target repository:

- `smc-architecture-decision` 1.0.0
- `smc-architecture-review` 1.0.0
- `smc-prd-grounding` 4.0.0
- `smc-prd-review` 4.0.0
- `smc-prd-converge` 3.0.0

## Required Existing Baseline Components

The installer fails closed if key compatibility dependencies are missing:

- `.agents/skills/smc-plan-validator/scripts/validate_plan.py`
- `.agents/skills/smc-plan-review/scripts/assess_plan_review.py`
- `.agents/skills/smc-plan-from-approved-prd-ponytail/scripts/validate_generation_integrity.py`
- `.agents/skills/smc-plan-from-approved-prd-ponytail/references/ponytail-minimality.md`
- `.agents/skills/smc-plan-from-approved-prd-ponytail/references/ownership-aware-slicing.md`
- `.agents/skills/smc-plan-from-approved-prd-ponytail/references/generation-integrity-gates.md`
- `.agents/skills/smc-plan-from-approved-prd-ponytail/references/source-basis.md`
- `.agents/skills/code-review-and-quality/SKILL.md`
- `.agents/skills/verification-before-completion/SKILL.md`
- `.agents/references/prd-contract.md`
- `.agents/references/evidence-contract.md`
- `.agents/references/architecture-convergence.md`

## Compatibility Policy

- New Plan: MUST use `smc.plan.v3.3`.
- Existing v3.2 Plan: LEGACY; do not mass rewrite.
- Existing v3.2 in-flight work may finish under its old frozen flow.
- v3.2 Plan entering REVISE/new delivery SHOULD migrate to v3.3 first.
- Existing tracked `artifacts/*` are retained as legacy evidence; no mass deletion.
- New delivery raw evidence lives under gitignored `.smc/evidence/`; compact durable evidence lives under tracked `docs_agent/evidence/`.
