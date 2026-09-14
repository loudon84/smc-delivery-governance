---
title: GES v6.0.0 Phase 0 Contract Freeze
version: v6.0.0
document_revision: 1.0
status: PROPOSED
document_type: PHASE0_DECISION_RECORD
date: 2026-09-14
source_prd: docs/prd/PRD-GES-v6.0.0-Context-Optimization-Upgrade.md
---

# GES v6.0.0 Phase 0 Contract Freeze

本记录冻结 v6 实施默认值。所有条目均为 `PROPOSED`，不替代 Architecture Review、PRD Review 或 Converge，也不更新 accepted baseline。

## D01 — Owners

角色沿用 Upgrade PRD §5.3。实际任命待项目方指定；实施按角色而非人名绑定。

| Role | Canonical owner | Appointment |
|---|---|---|
| Product | 待指定 | PROPOSED |
| Architecture | `smc-architecture-decision` | PROPOSED |
| Registry | Consumer architecture/module maintainer | PROPOSED |
| Context Package | Context Optimization Engine | PROPOSED |
| Delivery / Review / Release | existing canonical owners | unchanged |
| Installer | existing installer | unchanged |

## D02 — ADR-001

Retain central-to-Interface / local-to-Implementation. v6 does not migrate central ownership.

## D03 — Registry layout, schema, Plan capability

- Consumer canonical config: `.agents/ges/context/`
- Runtime overlay: `.agents/ges/context-engine/` (installer-owned, like domain-runtime)
- Schemas: `smc.context.registry.v1`, `smc.context.impact.v1`, `smc.context.package.v1`, `smc.context.request.v1`
- Plan contract: `smc.plan.v4.0` = `smc.plan.v3.7` + required `context_binding: required`
- Old validators (v3.3–v3.7) reject declared required `context_binding`
- v6 runtime rejects in-flight non-v4.0 Plans with `CONTEXT_LEGACY_PLAN_UNSUPPORTED`
- No dual-contract execution; completed historical Plans remain read-only evidence

## D04 — First-ship Consumer, language, host

| Item | Default | Status |
|---|---|---|
| First Consumer | generic fixture / current repo | PROPOSED |
| Language adapter | Python static `import` AST | PROPOSED |
| Host | Cursor local tools | PROPOSED |
| Read enforcement | `ADVISORY` until a verified file-read gateway exists | PROPOSED |
| Token metering | host-reported tokens; missing stays missing | PROPOSED |

## D05 — Budget, corpus, thresholds

Use Upgrade PRD §9.2 unpublished targets. COMPONENT/MODULE cost −30% vs v5 candidate is a certification goal, not a current measurement. Hardware/corpus remain unset until an approved evaluation stage.

## D06 — Pilot / Benchmark

Real Pilot and Token Benchmark stay `NOT_EXECUTED`. This freeze does not lift those bans or grant baseline promotion.

## Frozen identifiers

- Context Registry path: `.agents/ges/context/`
- Package output: `.smc/runs/<plan_id>/context/<todo_id>/<epoch>/`
- Planning requests: `.smc/context/requests/<request_id>/`
- Parser identity: `ges.context.parser.v1`
- Current Plan contract: `smc.plan.v4.0`
