---
lat:
  require-code-mention: true
---
# GES 6 Acceptance Tests

A01–A16 prove Composer Bootstrap on a synthetic brownfield fixture that mirrors smc-copilot, using an offline source cache.

## A01 — Brownfield Detection

The analyzer must classify the Golden-shaped fixture as a brownfield monorepo without calling an LLM.

## A02 — Harness Detection

Cursor and Codex must be detected from `.cursor/` and `.codex/` so both harness adapters can project.

## A03 — Existing AGENTS Preservation

Bytes outside the GES marker must stay identical across apply so user routing text is never overwritten.

## A04 — Existing Spec Kit Preservation

An existing `.specify/` tree must be adopted. Constitution and user templates are not reinitialized.

## A05 — Legacy Detection

v5 lock presence must set `legacy_ges` and classify owned, absent and unknown files without deleting them on init.

## A06 — Capability Recommendation

The recommended set must come from the repo profile plus the brownfield-product-app catalog profile.

## A07 — Capability Exclusion

Removing an optional capability must keep resolution legal and persist the exclusion in desired state.

## A08 — Dependency Closure

Selecting `matt.grill-with-docs` must automatically include `matt.grilling` and `matt.domain-modeling`.

## A09 — Ownership Conflict

Two Feature Spec owners at once must raise `CAPABILITY_OWNERSHIP_CONFLICT` and block apply.

## A10 — Selective Install

Unresolved Matt, Spec Kit and Superpowers skills must not be materialized by Composer.

## A11 — Upstream Lock

Matt, Spec Kit and Superpowers must each lock a 40-character immutable commit SHA.

## A12 — Idempotent Apply

The first apply writes changes; the second apply is `GES_RECONCILE_NOOP` with zero content change.

## A13 — Managed Update

A pinned skill upgrade may change only GES-managed content. Business source and user AGENTS text stay intact.

## A14 — User Modification Conflict

A user edit to the GES marker section must raise `MANAGED_CONTENT_MODIFIED` and must not be overwritten.

## A15 — Remove

`ges remove` deletes GES-owned projection and keeps user `.specify`, AGENTS body, third-party skills and governance kit.

## A16 — Business Source Guard

`apps/`, `services/`, `src/`, `packages/` and `contracts/` must stay byte-identical across apply, second apply and remove.
