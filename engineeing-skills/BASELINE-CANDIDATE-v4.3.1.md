# GES v4.3.1 Candidate Baseline

This document is a candidate. Accepted `BASELINE.md` remains authoritative until v4.3.1 is reviewed and accepted.

```text
Bundle Candidate          : 4.3.1
Pipeline Contract         : v4.3
Plan Contract             : smc.plan.v3.6
Test Asset Contract       : smc.test-asset.v1
Domain Pack Contract      : smc.ges.domain-pack.v1
Domain Activation         : smc.ges.domain-activation.v1
Consumer Profile          : smc.ges.consumer-profile.v2
Commit Policy             : post_review
```

Candidate changes over v4.3.0:

- Test Asset Catalog with stable asset manifests under the Consumer Profile root.
- v3.6 Test Asset Ledger with deterministic `REUSE | EXTEND | NEW` rules.
- Delivery synchronization that records final asset digests in Evidence Manifests.
- One contract resolver for v3.3–v3.6 static validation, readiness, and completion.
- Consumer preflight checks for required verification and legacy validator dependencies.

Acceptance requires a real multi-Roadmap delivery that reuses an unchanged live asset, extends it under a new Plan, and proves the old evidence becomes stale when the asset changes.
