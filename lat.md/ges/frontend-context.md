# GES Frontend Context System

Frontend Context System 为每个前端应用建立可复用的 UX Baseline，使 Feature 先 Resolve target app 与 Surface，再决定 REUSE/EXTEND，而不是全仓扫描。

权威需求见 `docs/prd/PRD-GES-v5.0.6-Adaptive-Governance-Frontend-Context-System-Complete.md`。Consumer 数据根目录固定为 `.agents/ges/frontend/`（仅 JSON）。实现位于 [[engineeing-skills/context-engine/work_scope.py]] 与 `frontend-adapters/`。

## Frontend Application Registry

Registry 发现 `apps/*`、`packages/*`、`src/renderer` 与单包 Electron，产出 `smc.ges.frontend-app-registry.v1`，并强制跨 App Surface 隔离。

写入 `.agents/ges/frontend/apps-registry.json`。`cross_app_surface_allowed` 对 Surface 恒为 false。见 [[engineeing-skills/context-engine/frontend_app_registry.py#discover]]。

## Stack Classifier

Classifier 仅用 package.json / vite / electron / next / nuxt / vue 静态信号映射到 stack_adapter。

支持键：`react-web`、`react-electron`、`vue3-web`、`nextjs`、`nuxt`、`react-native`、`generic`。见 [[engineeing-skills/context-engine/stack_classifier.py#classify]]。

## Per-App UX Baseline

每个 App 在 `.agents/ges/frontend/apps/<app-id>/` 下生成独立 baseline 文件集，禁止共享 Surface Registry。

产物含 app-profile、ui-baseline、surface-registry、layout-map、navigation-map、component-registry、state-owner-map、design-system、baseline.lock。扫描为静态规则，不调用 LLM。见 [[engineeing-skills/context-engine/ux_context_resolver.py#generate_baseline]]。

## Surface Registry

Surface Registry 记录 surface_id、ux_role、owner、layout_owner、visual_position 与 actions，区分 Business Entity / UX Role / Visual Surface。

`identity_control` 由 Layout*.tsx、*Switcher*、sidebar/footer 等静态模式推断。见 [[engineeing-skills/context-engine/ux_context_resolver.py#resolve_surface]]。

## UX Surface Reuse Gate

Gate 在 SAME_UX_ROLE 或 SAME_ACTION_CLUSTER 时默认 EXTEND；ADD_NEW 无 NEW_SURFACE_JUSTIFICATION 则返回 UX_SURFACE_REUSE_REQUIRED。

决策枚举：REUSE、EXTEND、MODIFY、HIDE、REPLACE、ADD_NEW。见 [[engineeing-skills/context-engine/ux_context_resolver.py#reuse_gate]]。

## Visual Intent

Visual Intent Binder 生成 `smc.ges.visual-intent.v1`，绑定 keep/modify/hide/must_not_add，供 PRD → Plan → Frontend Verification 使用。

见 [[engineeing-skills/context-engine/ux_context_resolver.py#bind_visual_intent]]。

## Shared UI Registry

`packages/ui` 与 `packages/*-ui` 归类为 shared-ui-library，只索引共享组件，不记录业务 Surface。

同 Stack / Shared Package 允许 Component Reuse；跨 App 不自动 Surface Reuse。见 [[engineeing-skills/context-engine/frontend_app_registry.py#resolve_shared_components]]。

## Incremental Refresh

增量刷新按变更路径映射到受影响 App，禁止全量重扫；共享 UI 变更仅标记依赖 App 为 DEPENDENCY_STALE。

见 [[engineeing-skills/context-engine/ux_context_resolver.py#incremental_refresh]]。

## Work Scope Resolver

Work Scope 是统一入口：解析目标 App、治理 tip、局部 Context 与 Token Budget，schema 为 `smc.ges.work-scope.v1`。

CLI：`python work_scope.py <repo> [--json]`。见 [[engineeing-skills/context-engine/work_scope.py#resolve_work_scope]]。

## Token Budget

Token Budget 按 LEAN/FULL 输出模型档位、独立审查与 context_mode（targeted vs expanded）。

LEAN 使用 cache_first 重复读；FULL 允许 expanded context。见 [[engineeing-skills/context-engine/token_budget.py#budget_for]]。

## Context Cache

Context Cache 键为 app_id + path + content_sha256，支持 get/put/invalidate 与 cache-first 去重。

见 [[engineeing-skills/context-engine/context_cache.py#ContextCache]]。

## Risk Facts v2

Risk Facts v2 将 Sensitive Touch 与 Hard Boundary 分离，供 Work Scope 的 LEAN/FULL tip 与自适应治理共用。

实现见 [[engineeing-skills/domain-runtime/risk_signals.py]]；本页仅保留跨模块锚点，避免 frontend-context 与 risk runtime 断链。

## Work Router v3

Work Router v3 允许 Sensitive Touch 保持 BOUNDED/LEAN，Hard Boundary 强制 ARCHITECTURAL/FULL。

见 [[engineeing-skills/.agents/skills/smc-work-router/scripts/work_router.py#route]]。

## Engineering Method v3

Engineering Method v3 增加 `BOUNDED_BEHAVIOR` 与 `SENSITIVE_BOUNDED`；`BEHAVIOR_CHANGE` 为 deprecated alias；敏感触达默认 `TDD_FOCUSED_REQUIRED`。

见 [[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/engineering_method.py#classify]]。

## Telemetry v2

Telemetry v2 以 `cost_bucket` 聚合 routing / baseline / grounding / plan / implement / tdd / review / delivery 成本。

见 [[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/runtime_metrics.py#summarize]]。

## Commit Guard v3

Commit Guard v3 区分 CHECKPOINT / CANDIDATE / FINAL；FINAL 遇 pending Todo 返回 `FINAL_COMMIT_BLOCKED_PENDING_TODO`。

见 [[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/commit_guard.py#capture]]。

## Acceptance G31–G42

Acceptance corpus G31–G42 覆盖敏感读、logout wiring、硬边界、Surface gate、跨 App/Stack 隔离、共享 UI、增量刷新、TDD、FINAL commit 与 telemetry buckets，并含 UC-PROFILE-GOV golden。

实现：[[engineeing-skills/acceptance/run_acceptance.py]]。

### G31 Existing Auth Read

验证 v2 sensitive touch 路由 BOUNDED/LEAN，工程分类为 SENSITIVE_BOUNDED 或 BOUNDED_BEHAVIOR（STANDARD/UNIFIED）。

### G32 Existing Logout Wiring

验证 logout wiring 分类为 SENSITIVE_BOUNDED 且 TDD_FOCUSED_REQUIRED。

### G33 Security Boundary Change

验证 security_boundary_change 强制 ARCHITECTURAL/FULL 与 HIGH_RISK REASONING/INDEPENDENT。

### G34 Existing Surface Candidate

验证 ADD_NEW 无 justification 返回 UX_SURFACE_REUSE_REQUIRED。

### G35 Extend Surface

验证 EXTEND 已有 identity surface 通过。

### G36 Different App Isolation

验证 cross_app_surface_allowed(desktop, web) 为 false。

### G37 Different Stack Isolation

验证不同 stack 时 component_reuse_automatic 不为自动复用。

### G38 Shared UI Reuse

验证 ProfileAvatar 共享组件决策为 REUSE。

### G39 Incremental Refresh

验证仅 desktop 路径变更时 desktop 刷新、web 保持 FRESH/untouched。

### G40 Sensitive Bounded TDD

验证 SENSITIVE_BOUNDED 的 tdd_policy 为 TDD_FOCUSED_REQUIRED。

### G41 Final Commit Pending Todo

验证 FINAL capture 在 pending Todo 时返回码 1。

### G42 Telemetry Cost Buckets

验证 summarize.cost_buckets 含 routing/baseline/grounding/plan/implement/tdd/review/delivery 键。

### UC-PROFILE-GOV Golden

验证 BOUNDED/LEAN 与 identity surface EXTEND 决策。

## Tests

Frontend Context Engine 单元测试覆盖发现、隔离、reuse gate、增量刷新、共享 UI、分类器、预算与缓存。

测试文件：[[engineeing-skills/tests/test_context_engine.py]]。

### Discover single electron app

验证单包 Electron（src/renderer）被发现为 react-electron 应用。

### Monorepo app isolation

验证双 App monorepo 隔离且 cross_app_surface_allowed 恒为 false。

### Reuse gate decisions

验证 SAME_UX_ROLE 默认 EXTEND，以及 ADD_NEW 缺 justification 返回 UX_SURFACE_REUSE_REQUIRED。

### Incremental refresh scoped

验证仅 desktop 路径变更时只刷新 desktop，web 保持 untouched。

### Shared UI reuse

验证 packages/ui 组件命中后 shared UI reuse 决策为 REUSE。

### Stack classifier electron

验证 package.json 含 electron 时 stack_adapter 为 react-electron。

### Token budget lean full

验证 LEAN 与 FULL 预算字段差异。

### Context cache hit

验证相同 content_sha256 时 cache hit。
