# GES v4.3.1 Candidate — Test Asset Lifecycle

This candidate adds durable test-asset reuse to the v4.3 Domain Pack architecture without changing canonical Plan, Delivery, Commit, or Roadmap ownership.

## Changed contracts

- New `smc.plan.v3.6` extends v3.5 with Test Asset Ledger.
- New `smc.test-asset.v1` manifests bind test asset IDs to content digests.
- New Plans write v3.6; v3.3–v3.5 remain readable through the shared contract resolver.

## Changed skills

- `smc-plan-from-approved-prd-ponytail` 3.6.0 -> 3.7.0
- `smc-plan-validator` 1.5.0 -> 1.6.0
- `smc-plan-delivery` 1.2.0 -> 1.3.0
- `using-superpowers` 4.3.0 -> 4.3.1

## Consumer impact

Consumer Profiles must declare the Test Asset root and preserve the existing verification skill plus legacy validator required by the v3.3 compatibility layer. New v3.6 Plans that create or extend an asset must include the asset file and its manifest in Change Matrix ownership.
