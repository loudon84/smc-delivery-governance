# GES 6 Governance Backplane

This package holds the Alpha.1 domain model only. Runtime engines for
Registry, Policy, Risk, Ownership, Evidence, Approval, Delivery, Release
and Audit start in 6.0-alpha.2 and later.

Composer Bootstrap (alpha.1) must stay compatible with this model:
Work references Artifact, Risk, Policy, Ownership, Evidence, Approval
and produces Release. Artifacts are pointers, not copied bodies.
