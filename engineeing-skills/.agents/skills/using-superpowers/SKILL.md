---
name: using-superpowers
description: GES 5 work router with explicit risk facts and monotonic NONE/LEAN/FULL governance.
version: 5.0.0
---
# GES Work Router

Read references/work-routing-contract.md. Route one request with scripts/work_router.py using explicit facts; unknown risk selects FULL. Research-only work uses SPIKE/NONE. Existing bounded work may use BOUNDED/LEAN even when governed by a Roadmap.

## Canonical ownership

Architecture and Roadmap keep their existing owners. smc-prd-grounding owns discover/clarify/verify/revision; smc-prd-review and smc-prd-converge review and approve the same PRD. Only smc-plan-from-approved-prd-ponytail creates the canonical Plan. smc-plan-delivery owns all post-creation sequencing through audit, review, verification, freshness, post_review commit and separate Roadmap DONE.

## Continuation

Read the existing artifact's governance_profile before routing and supply it as --previous-profile. FULL cannot become LEAN; LEAN cannot become NONE. Never create a second spec/Plan or infer that a lightweight label clears a blocking finding. Existing v3.6 Plans remain supported; new Plans use v3.7.
