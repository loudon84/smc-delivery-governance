# v5.0.9 Runtime Cost Closure

Closes Budget, Cache, and Telemetry into real GES-managed model paths without adding a second Router, Plan, or Delivery authority.

## Telemetry Usage Semantics

[[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/runtime_metrics.py#summarize]] distinguishes `AVAILABLE`, `UNAVAILABLE`, and `MIXED`; unavailable usage must not summarize as zero tokens.

## Model Dispatch Runtime

[[engineeing-skills/context-engine/model_dispatch.py#prepare_dispatch]] and [[engineeing-skills/context-engine/model_dispatch.py#run_managed_call]] enforce trim → cache → budget → envelope → permit → dispatch/result. Harness modes live in [[engineeing-skills/context-engine/harness_contract.py#classify_mode]].

## Context Envelope

[[engineeing-skills/context-engine/context_envelope.py#build_envelope]] builds phase-scoped minimum context for PLAN / IMPLEMENT / REVIEW and rejects full-repo / full-history dump kinds.

## Stage Cost Closure

[[engineeing-skills/context-engine/stage_cost_closure.py#evaluate_stage]] gates PLANNING / IMPLEMENTATION / REVIEW on paired telemetry, envelope digest, and managed calls.

## Plan Author Cost Closure

[[engineeing-skills/.agents/skills/smc-plan-from-approved-prd-ponytail/scripts/plan_author_cost.py#apply_structured_patches]] keeps deterministic seed authority and records structured patches only.

## Delivery Worker Cost Closure

[[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/execution_context.py#create_worker_context_envelope]] makes Task Brief + Todo envelope mandatory worker input.

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
