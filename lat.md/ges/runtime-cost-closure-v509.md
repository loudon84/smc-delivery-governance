# v5.0.9 Runtime Cost Closure

Closes Budget, Cache, and Telemetry into real GES-managed model paths without adding a second Router, Plan, or Delivery authority.

## Telemetry Usage Semantics

[[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/runtime_metrics.py#summarize]] distinguishes `AVAILABLE`, `UNAVAILABLE`, and `MIXED`; unavailable usage must not summarize as zero tokens.

## Model Dispatch Runtime

[[engineeing-skills/context-engine/model_dispatch.py#prepare_dispatch]] and [[engineeing-skills/context-engine/model_dispatch.py#run_managed_call]] enforce trim → cache → budget → envelope → permit → dispatch/result. Harness modes live in [[engineeing-skills/context-engine/harness_contract.py#classify_mode]].

## Context Envelope

[[engineeing-skills/context-engine/context_envelope.py#build_envelope]] builds phase-scoped minimum context for PLAN / IMPLEMENT / REVIEW and rejects full-repo / full-history dump kinds.

## Stage Cost Closure

[[engineeing-skills/context-engine/stage_cost_closure.py#evaluate_stage]] and [[engineeing-skills/context-engine/stage_cost_closure.py#assert_managed_cost_closure]] gate PLANNING / IMPLEMENTATION / REVIEW; completion and readiness fail closed when managed dispatches exist without PASS.

## Runtime Locator

[[engineeing-skills/context-engine/runtime_locator.py#locate]] is the single deterministic path resolver for Provider and Consumer layouts; scripts must not guess `parents[n]`.

## Harness Adapter Registry

[[engineeing-skills/context-engine/harness_registry.py#resolve_adapter]] never defaults to fake in production; `HARNESS_ADAPTER_REQUIRED` is raised when no real adapter is supplied.

## Runtime Cost Contract

[[engineeing-skills/context-engine/runtime_cost_contract.py#init_contract]] writes `smc.ges.runtime-cost-contract.v1`; required stages with zero dispatch fail closed unless a `PASS_NO_MODEL_WORK` receipt exists.

## Plan Author Cost Closure

[[engineeing-skills/.agents/skills/smc-plan-from-approved-prd-ponytail/scripts/plan_author_cost.py#apply_structured_patches]] keeps deterministic seed authority and records structured patches only.

## Delivery Worker Cost Closure

[[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/execution_context.py#create_worker_context_envelope]] is mandatory worker input; Todo completion requires the worker envelope before TDD/debug gates.

## Review Cost Closure

[[engineeing-skills/.agents/skills/smc-plan-review/scripts/assess_plan_review.py#classify]] defaults prior REVISE to DELTA unless FULL re-entry signals fire; [[engineeing-skills/.agents/skills/smc-plan-review/scripts/assess_plan_review.py#record_review_round]] enforces loop caps.

## Acceptance G61–G80

Regression corpus proving dispatch permits, budget blocks, worker scope, review DELTA, usage unavailable, stage closure, upgrade baseline stability, and simulated golden cost summary.

### G61 Plan Author Dispatch Required

Model Plan Author work without a permit fails closed with `MODEL_DISPATCH_PERMIT_MISSING`.

### G62 Plan Budget Enforced

Over-budget planning candidates produce a BLOCKED permit with `CONTEXT_BUDGET_INSUFFICIENT`.

### G63 Deterministic Seed

Identical PRD/context inputs produce identical envelope content digests.

### G64 Structured Plan Patch

Unresolved decisions render as structured patch tables without replacing the Plan body.

### G65 No Full-Plan Reauthor

Patch application preserves seed frontmatter and Todo sections.

### G66 Worker Task Brief Only

Worker envelopes exclude the full Change Matrix and bind Task Brief only.

### G67 Worker Scope Violation

Reads outside Todo `allowed_roots` raise `WORKER_CONTEXT_SCOPE_VIOLATION`.

### G68 Capsule Hit

Matching capsule keys reuse cache and increment hits on dispatch prepare.

### G69 Capsule Stale

Expired capsules count as stale and require refresh.

### G70 Dispatch Result Pair

Managed calls emit exactly one result per dispatch with pair rate 1.0.

### G71 Usage Unavailable

Provider usage gaps surface as `usage_status=UNAVAILABLE` with null token totals.

### G72 Review First FULL

First semantic review without prior PASS routes FULL.

### G73 Review Revision DELTA

Prior REVISE without re-entry signals routes DELTA.

### G74 Review FULL Re-entry

Explicit FULL re-entry markers after REVISE route FULL again.

### G75 Review Loop Cap

Exceeding configured FULL/DELTA rounds raises `REVIEW_LOOP_EXCEEDED`.

### G76 Stage Cost Closure

Orphan dispatch events make stage closure `BLOCKED`.

### G77 Managed Call Ratio

GES-managed stages report unmanaged call count zero when all calls are dispatched.

### G78 Consumer Upgrade

Copying runtime cost modules does not alter Frontend Baseline bytes.

### G79 Install Rollback

Faulted install finalization restores away runtime files and preserves sibling baseline.

### G80 Golden Consumer

Simulated Plan → Delivery → Review managed path yields complete cost summary and stage PASS.

## Acceptance G81–G96

Hardening corpus proving deterministic runtime location, no production fake adapter, runtime cost contract zero-dispatch closure, and corrected telemetry counters.

### G81 Provider Locator

Provider layout resolves `engineeing-skills/context-engine` via `runtime_locator`.

### G82 Consumer Locator

Consumer `.agents/ges/frontend-runtime` resolves via `runtime_locator`.

### G83 Locator Escape

Repo-external `GES_RUNTIME_ROOT` is blocked with `GES_RUNTIME_PATH_ESCAPE`.

### G84 Consumer Dispatch Imports Telemetry

Consumer-layout `model_dispatch` imports `runtime_metrics` via locator.

### G85 Consumer Closure Imports Telemetry

Consumer-layout `stage_cost_closure` imports `runtime_metrics` via locator.

### G86 No Production Fake

`run_managed_call(adapter=None)` raises `HARNESS_ADAPTER_REQUIRED`.

### G87 Fake Test Only

Explicit `fake_enforced_adapter` remains allowed in acceptance.

### G88 Observable Cannot Enforce

`cursor-observable` adapter raises `RUNTIME_COST_OBSERVABLE_NOT_ENFORCED`.

### G89 Runtime Contract Written

`runtime_cost_contract.init_contract` creates the contract receipt.

### G90 Required Stage Zero Dispatch

New contract plan with zero PLANNING dispatches is `BLOCKED` with `STAGE_MODEL_DISPATCH_MISSING`.

### G91 No Model Work Receipt

Deterministic-only stage with receipt yields `PASS_NO_MODEL_WORK`.

### G92 Legacy Plan Compatibility

Plan without `runtime_cost_contract` returns `enforced=False`.

### G93 Delivery Fail Closed

Contract plan with zero dispatch raises `STAGE_MODEL_DISPATCH_MISSING` from `assert_managed_cost_closure`.

### G94 Managed Count Correct

Dispatch events without `managed=True` are not counted as managed.

### G95 Budget Pass Count Correct

Only `kind=dispatch` with `permit_status=PERMITTED` counts as budget pass.

### G96 Real Consumer Runtime Smoke

Temporary consumer layout runs dispatch → result → closure end-to-end.

