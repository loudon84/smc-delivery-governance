# GES v4.3.0 — Domain Pack Framework + Frontend Domain

## Architecture

GES now has three orthogonal planes:

```text
Core Governance
+ Domain Packs
+ Consumer Profiles
```

Domain Packs are professional capability providers, not workflow owners.

## Contracts

- `smc.plan.v3.5`
- `smc.ges.domain-pack.v1`
- `smc.ges.domain-activation.v1`
- `smc.ges.consumer-profile.v2`
- `smc.frontend.quality.v1`

## New Skills

- `smc-frontend-engineering` 1.0.0
- `smc-frontend-review` 1.0.0
- `smc-frontend-visual-verification` 1.0.0

## Changed Skills

- `smc-plan-from-approved-prd-ponytail` 3.6.0
- `smc-plan-validator` 1.5.0
- `smc-plan-delivery` 1.2.0
- `using-superpowers` 4.3.0

## Extensibility Proof

Package validation creates a temporary `fixture` Domain Pack with its own extension and engineering provider. The unmodified generic resolver must activate it solely from registry/profile/pack data. This is the release gate proving later backend/electron/mobile/data packs do not require Core routing changes.
