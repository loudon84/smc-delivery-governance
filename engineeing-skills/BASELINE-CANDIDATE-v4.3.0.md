# GES v4.3.0 Candidate Baseline

This document is a candidate. Accepted `BASELINE.md` remains authoritative until v4.3.0 is reviewed and accepted.

```text
Bundle Candidate          : 4.3.0
Pipeline Contract         : v4.3
Plan Contract             : smc.plan.v3.5
Domain Pack Contract      : smc.ges.domain-pack.v1
Domain Activation         : smc.ges.domain-activation.v1
Consumer Profile          : smc.ges.consumer-profile.v2
Frontend Quality Contract : smc.frontend.quality.v1
Delivery Workspace        : smc.delivery.workspace.v1
Execution Context         : smc.execution.context.v1
Commit Policy             : post_review
```

Candidate changes:

- Generic Domain Pack Framework v1.
- Frontend Domain Pack v1 as reference implementation.
- Profile-selected installation of Domain capability skills.
- Plan Change Matrix based deterministic activation.
- Policy digest binding and `DOMAIN_POLICY_STALE` fail-closed behavior.
- Plan v3.5 Domain Activation Ledger and dynamic pack extension validation.
- Generic delivery phase provider resolution; no domain-specific branch in Core runtime.

Acceptance requires package validation plus a real `smc-copilot/apps/work` frontend delivery and a synthetic future-domain extension proof.
