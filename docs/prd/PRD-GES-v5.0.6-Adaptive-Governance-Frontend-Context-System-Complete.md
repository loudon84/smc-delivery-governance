---
title: "GES v5.0.6 自适应治理与 Frontend Context System 完整工程方案 PRD"
prd_version: "v5.0.6"
status: "DRAFT"
baseline: "GES v5.0.5"
scope: "Adaptive Governance + Frontend UX Context + Monorepo Isolation"
language: "简体中文"
---

# GES v5.0.6 自适应治理与 Frontend Context System 完整工程方案 PRD

## 1. 文档定位

本 PRD 基于 GES v5.0.5 已完成的平台化 Consumer 接入能力继续演进。

GES 总体分层保持不变：

```text
Spec Kit
负责前半程 Requirement / Spec / UX Intent

        ↓

Superpowers
负责中段 Planning / Implementation / TDD / Debug / Review

        ↓

GES
负责后半程 Governance / Evidence / Delivery Truth / Release
```

v5.0.6 不新增第二套治理体系，而是解决 v5.0.5 在真实 Consumer `smc-copilot-desktop` 首次 Feature 落地后暴露的两个核心问题：

1. **治理过重**：小型增量改动因为触碰 `auth / profile / session` 等敏感关键词，被升级为 FULL / HIGH_RISK，造成 PRD、Plan、TDD、独立 Review、REASONING 模型成本叠加。
2. **UX 意图复用不足**：代码能力复用正确，但前端没有优先复用已有 UI/UX Surface，导致新增独立 UserCenter 入口，破坏原有身份入口一致性。

同时，面向已有 React / Vue / Electron / H5 monorepo，必须解决：

- 不同前端应用之间的 UX Baseline 隔离；
- 不同技术栈识别与适配；
- Shared UI package 与业务 Surface 的区分；
- 每个 Feature 避免全仓库扫描；
- 增量更新 Baseline，降低长期 Token 成本。


## 2. 核心目标

GES v5.0.6 的核心目标：

> **让治理强度与真实“变化风险”匹配，而不是与关键词匹配；让前端治理以“已有应用、已有 Surface、已有 Layout Owner”为基础，而不是每个 Feature 从零理解整个仓库。**

目标执行路径：

```text
小改动
→ 精准 Grounding
→ BOUNDED / LEAN
→ Compact Plan
→ Targeted Context
→ Minimal Code Change
→ Focused Verification
→ Unified Review
→ Delivery Truth
```

真实边界变化：

```text
Architecture / Security / Schema / Protocol / Ownership Change
→ ARCHITECTURAL / FULL
→ Full Contract
→ TDD
→ REASONING
→ Independent Review
→ Strong Evidence
```

前端 Feature：

```text
Target App Resolution
→ Per-App UX Baseline
→ Surface Resolution
→ Shared Component Resolution
→ UX Reuse Gate
→ PRD / Plan
```


## 3. 真实问题来源：UC-PROFILE-GOV Golden Case

真实 Consumer：

```text
smc-copilot-desktop
```

真实 Feature：

1. Work 登录后显示用户状态、邮件、退出；
2. Local Desktop 隐藏 Profile Switch。

本次实际暴露：

```text
Backend/Auth capability reuse:
  PASS

Token/Auth/Logout contract reuse:
  PASS

Frontend UX Surface reuse:
  FAIL

User intent compliance:
  FAIL

Governance profile:
  OVER-CLASSIFIED FULL

TDD scope:
  OVER-APPLIED

Token efficiency:
  POOR
```

核心根因：

- “触碰已有安全能力”与“改变安全边界”没有分离；
- Engineering Method 使用关键词直接放大风险；
- Frontend Grounding 只判断代码有没有，没有判断已有 Surface / Layout Owner；
- LEAN 与 FULL 的 Artifact 成本差异不足；
- TDD 粒度过大；
- Feature Commit 与最终 Delivery Truth 边界不够明确。


## 4. 设计原则

### P1 — Change Semantics First

风险判断基于：

```text
发生了什么变化
```

而不是：

```text
出现了什么关键词
```

### P2 — Existing Owner First

已有 Production Owner、API Contract、State Owner、UX Surface、Runtime Capability 时，默认：

```text
REUSE / EXTEND
```

而不是：

```text
ADD PARALLEL OWNER
```

### P3 — Boundary Change 才触发 FULL

FULL 只由真实控制面变化触发，包括：

- 新 owner；
- public contract change；
- auth/security boundary change；
- schema migration；
- protocol change；
- ownership transfer；
- external dependency change；
- lifecycle contract change；
- external live acceptance。

仅“使用已有安全能力”不能自动 FULL。

### P4 — Frontend Application 是 UX Governance Boundary

```text
Repository
≠ UX Governance Boundary

Frontend Application
= UX Governance Boundary
```

### P5 — UX Role 优先于 Component Name

不能只问：

```text
有没有 UserCenter.tsx？
```

必须先问：

```text
这个需求承担什么 UX Role？
```

### P6 — Governance Monotonicity

正式执行开始后：

```text
LEAN → FULL
允许

FULL → LEAN
禁止
```

首次 production write 前允许 `CLASSIFICATION_CORRECTION`。

### P7 — Evidence Cost Proportionality

Artifact、TDD、Review 深度必须与真实风险成比例。


## 5. 总体架构

```text
Consumer Repository
        │
        ▼
GES Context Optimization Engine
        │
        ├─ Work Scope Resolver
        ├─ Frontend Application Registry
        ├─ Stack Classifier
        ├─ UX Context Resolver
        └─ Token Budget Controller
        │
        ▼
Spec Kit / PRD Grounding
        │
        ├─ Risk Facts v2
        ├─ Existing Capability Scan
        ├─ Existing UX Surface Scan
        └─ Visual Intent Binding
        │
        ▼
Work Router v3
        │
        ├─ SPIKE / NONE
        ├─ BOUNDED / LEAN
        └─ ARCHITECTURAL / FULL
        │
        ▼
Canonical Plan
        │
        ├─ LEAN Compact Plan
        └─ FULL Plan
        │
        ▼
Superpowers Engineering Method v3
        │
        ├─ MECHANICAL
        ├─ BOUNDED_BEHAVIOR
        ├─ SENSITIVE_BOUNDED
        ├─ BUG_FIX
        └─ HIGH_RISK
        │
        ▼
GES Delivery Truth
        │
        ├─ Completion Audit
        ├─ Review
        ├─ Verification
        ├─ Evidence
        └─ Commit Guard
```


## 6. GES Context Optimization Engine

新增核心组件：

```text
engineeing-skills/context-engine/
├── work_scope.py
├── frontend_app_registry.py
├── stack_classifier.py
├── ux_context_resolver.py
├── context_cache.py
├── token_budget.py
└── schemas/
```

职责：

1. 判断任务范围；
2. 选择治理层级；
3. 选择目标前端应用；
4. 加载局部 Context；
5. 控制 Token Budget；
6. 避免重复读取；
7. 防止过度分析。


## 7. Risk Facts v2

新增：

```text
smc.ges.risk-facts.v2
```

### 7.1 Sensitive Touch Signals

以下信号允许 LEAN：

```text
security_sensitive_touch
existing_lifecycle_wiring
cross_layer_existing_contract
local_ui_acceptance
existing_public_contract_use
existing_external_dependency_use
```

含义：

```text
使用 / 读取 / 展示已有能力
但不改变 owner、contract、trust boundary
```

### 7.2 Hard Boundary Change Signals

以下必须 FULL：

```text
new_owner
public_contract_change
security_boundary_change
schema_migration
protocol_change
external_dependency_change
lifecycle_contract_change
ownership_transfer
cross_domain_contract_change
external_live_acceptance
```

### 7.3 BOUNDED 必需事实

```text
existing_owner = true
existing_capability = true
bounded_writes = true
deterministic_verification = true
```

并且所有 Hard Boundary Change 均为 `false`。


## 8. Work Router v3

输出：

```text
smc.ges.work-route.v3
```

规则：

```text
IF research-only
AND no production write
AND authority verified
  → SPIKE / NONE

ELSE IF bounded facts all true
AND hard boundary changes all false
  → BOUNDED / LEAN

ELSE
  → ARCHITECTURAL / FULL
```

Sensitive Touch 不参与 FULL 强制升级。

### 示例 A：读取已有 Portal User

```json
{
  "existing_owner": true,
  "existing_capability": true,
  "bounded_writes": true,
  "deterministic_verification": true,
  "security_sensitive_touch": true,
  "security_boundary_change": false
}
```

结果：

```text
BOUNDED / LEAN
```

### 示例 B：修改 Token Ownership

```json
{
  "security_boundary_change": true
}
```

结果：

```text
ARCHITECTURAL / FULL
```


## 9. Classification Correction Window

状态：

```text
PROVISIONAL
FROZEN
ESCALATED
```

### PROVISIONAL

在 PRD Grounding、Plan Generation、第一次 production write 前，允许：

```text
FULL → LEAN
```

但必须记录：

```text
reason = CLASSIFICATION_CORRECTION
risk facts updated
evidence updated
```

### FROZEN

第一次 production write 后：

```text
LEAN → FULL
允许

FULL → LEAN
禁止
```


## 10. GES Frontend Context System

v5.0.6 不只增加 `UX Surface Reuse Gate`，而是建立完整：

```text
GES Frontend Context System
```

三级结构：

```text
1. Frontend Application Registry
   ├─ App discovery
   ├─ Stack classification
   └─ Shared package mapping

2. Per-App UX Context Engine
   ├─ UI Baseline
   ├─ Surface Registry
   ├─ Layout Map
   ├─ Navigation Map
   ├─ State Owner Map
   └─ Design System Index

3. Feature UX Resolution
   ├─ App Resolver
   ├─ Surface Resolver
   ├─ Shared Component Resolver
   └─ UX Surface Reuse Gate
```


## 11. Frontend Application Registry

目录：

```text
.ges/frontend/
├── apps-registry.json
├── apps/
└── shared/
```

示例：

```json
{
  "schema": "smc.ges.frontend-app-registry.v1",
  "apps": [
    {
      "app_id": "desktop",
      "root": "apps/desktop",
      "runtime": "electron-renderer",
      "framework": "react",
      "stack_adapter": "react-electron"
    },
    {
      "app_id": "web",
      "root": "apps/web",
      "runtime": "browser",
      "framework": "vue3",
      "stack_adapter": "vue3-web"
    }
  ]
}
```

Feature Grounding 必须先 Resolve `target_app`，再查询对应 UX Baseline。

跨 App Feature 仍保持：

```text
One PRD
One Canonical Plan
```

但产生多个 App-scoped Frontend Intent。


## 12. 技术栈分类与 Stack Adapter

禁止只按 React/Vue 分类。

Stack Key 由：

```text
Runtime
+
Framework
+
Router
+
State
+
UI System
+
Build/Test Stack
```

组成。

支持：

```text
react-web
react-electron
vue3-web
nextjs
nuxt
react-native
generic
```

目录：

```text
engineeing-skills/frontend-adapters/
├── react-web/
├── react-electron/
├── vue3-web/
├── nextjs/
└── generic/
```

React Electron Adapter 必须额外理解：

```text
main
preload
IPC
renderer
window bridge
```


## 13. Per-App UX Baseline

每个 App 独立：

```text
.ges/frontend/apps/<app-id>/
├── app-profile.json
├── ui-baseline.json
├── surface-registry.json
├── layout-map.json
├── navigation-map.json
├── component-registry.json
├── state-owner-map.json
├── design-system.json
└── baseline.lock
```

不同 App 之间禁止共享 Surface Registry。


## 14. Surface Registry 与 UX Role

示例：

```yaml
surface_id: desktop:sidebar.footer.identity

app_id: desktop

ux_role:
  identity_control

business_entities:
  - portal_user
  - agent_profile

owner:
  apps/desktop/src/renderer/screens/Layout/ProfileSwitcher.tsx

layout_owner:
  apps/desktop/src/renderer/screens/Layout/Layout.tsx

visual_position:
  sidebar.footer

actions:
  - show_identity
  - switch_profile

reuse_priority:
  HIGH
```

必须区分：

```text
Business Entity
UX Role
Visual Surface
```

例如 Portal User 与 Agent Profile 是不同实体，但可以共享 `identity_control` UX Role。


## 15. UX Surface Resolution Gate

Feature 进入 Grounding：

```text
Target App
→ UX Role
→ Candidate Surface
→ Reuse Decision
```

决策：

```text
REUSE
EXTEND
MODIFY
HIDE
REPLACE
ADD_NEW
```

如果：

```text
SAME_UX_ROLE
或
SAME_ACTION_CLUSTER
```

默认：

```text
EXTEND_EXISTING
```

若 Plan 选择 `ADD_NEW`，必须有：

```text
NEW_SURFACE_JUSTIFICATION
```

否则：

```text
UX_SURFACE_REUSE_REQUIRED
```


## 16. Visual Intent Binder

用户提供截图、原型、明确位置或“复用现有入口”要求时，生成：

```text
Visual Intent Contract
```

示例：

```yaml
visual_intent:
  app_id: desktop
  target_surface: desktop:sidebar.footer.identity

  keep:
    - existing_position

  modify:
    - display_username
    - display_email
    - click_behavior

  hide:
    - profile_switch

  must_not_add:
    - second_identity_row
```

Visual Intent 必须绑定：

```text
PRD
→ Plan
→ Frontend Verification
```


## 17. Layout Ownership Map 与 Design System Index

Layout Ownership：

```yaml
layout:
  app-shell:
    owner: Layout.tsx

    regions:
      sidebar.footer:
        owner: ProfileSwitcher
```

Feature 命中 `sidebar.footer` 后，只加载：

```text
Layout Owner
Surface Owner
State Owner
相关 Tests
```

Design System Index 记录：

```text
Button
IconButton
Avatar
ProfileAvatar
Dialog
Popover
Menu
DataGrid
layout tokens
typography tokens
```

新 UI 必须先做：

```text
Surface Reuse
→ Shared Component Reuse
```


## 18. Shared UI Package 与跨 App 复用

`packages/ui` 等归类为：

```text
shared-ui-library
```

它记录共享组件，不记录业务 Surface。

规则：

| 场景 | 允许复用 |
|---|---|
| 同 App | Surface Reuse |
| 同 Stack / Shared Package | Component Reuse |
| 不同 App | 不自动 Surface Reuse |
| 不同技术栈 | UX Pattern Reuse only |

Resolution 顺序：

```text
App Surface Resolver
→ Shared Component Resolver
```


## 19. Frontend Adoption 与 Baseline 建立

首次接入已有项目：

```bash
python consumer-bootstrap/frontend_audit.py <repo>
```

### 第一层：静态扫描

不调用 LLM，识别：

- app roots；
- framework；
- router；
- layouts；
- component graph；
- state owners；
- shared UI package；
- test stack。

### 第二层：有限语义分类

只发送摘要进行 UX Role 分类。

### 第三层：人工/视觉校准

只确认：

```text
Sidebar
Header
Workspace
Settings
Account
Navigation
```

等核心区域。

支持三种 Adoption Mode：

```text
OBSERVE
GUIDED
ENFORCED
```

旧项目首次接入默认 OBSERVE，稳定后再进入 GUIDED / ENFORCED。


## 20. Incremental Baseline Refresh

Delivery 完成后：

```text
git diff
→ path → app registry
→ affected app
→ affected surface
→ incremental refresh
```

例如：

```text
apps/desktop/**
→ refresh desktop only
```

如果修改：

```text
packages/ui/ProfileAvatar.tsx
```

则：

```text
refresh shared-ui
→ mark dependent surfaces DEPENDENCY_STALE
```

禁止全量重扫所有 App。


## 21. Engineering Method Runtime v3

方法类型：

```text
MECHANICAL
BOUNDED_BEHAVIOR
SENSITIVE_BOUNDED
BUG_FIX
HIGH_RISK
```

| Method | TDD | Debug | Model | Review |
|---|---|---|---|---|
| MECHANICAL | NOT_APPLICABLE / PREFERRED | ON_FAILURE | FAST | UNIFIED |
| BOUNDED_BEHAVIOR | PREFERRED | ON_FAILURE | FAST / STANDARD | UNIFIED |
| SENSITIVE_BOUNDED | FOCUSED_REQUIRED | ON_FAILURE | STANDARD | UNIFIED |
| BUG_FIX | REQUIRED | REQUIRED | STANDARD | UNIFIED |
| HIGH_RISK | REQUIRED | REQUIRED/ON_FAILURE | REASONING | INDEPENDENT |

禁止 Keyword-only HIGH_RISK。

`auth / security / session / profile / protocol` 只作为 candidate signal，不能单独升级 HIGH_RISK。

优先级：

```text
Structured Signal
>
Domain Binding
>
Risk Facts
>
Keyword Hint
```


## 22. Focused TDD

新增：

```text
TDD_FOCUSED_REQUIRED
```

用于 `SENSITIVE_BOUNDED`。

例如 Logout：

```text
RED: token/session 未清理时失败
GREEN: existing logout wiring 清理成功
```

不要求同一个 Todo 的布局、文案、图标、一般展示逻辑全部做完整 TDD。

`BOUNDED_BEHAVIOR` 默认：

```text
TDD_PREFERRED
```

已有测试则优先扩展已有测试。


## 23. LEAN Compact Plan

LEAN 仅保留：

```text
Approved PRD
Scope
Existing Capability Decision
UX Surface Decision
Change Matrix
Todo
Verification
DoD
```

默认不要求：

```text
Full Lifecycle Matrix
Full Contract/Data Flow Matrix
Full Acceptance Claim Ledger
Live Environment Matrix
Independent Review Ledger
```

除非对应风险实际触发。

FULL Contract 保持完整。


## 24. Token Budget Controller 与 Context Dedup

建议配置：

```yaml
token_budget:
  lean:
    model_max_tier: STANDARD
    independent_review: false
    max_review_rounds: 1
    context_mode: targeted
    repeated_context_read: cache_first

  full:
    model_max_tier: REASONING
    independent_review: true
    context_mode: expanded
```

Context Cache Key：

```text
app_id
+
path
+
content_sha256
```

同一版本文件重复读取：

```text
cache-hit
```

LEAN Stop Condition：

```text
Plan verified
Todo implementation complete
Focused verification PASS
Unified review PASS
```

满足后立即停止，禁止继续“进一步优化”式扩展。


## 25. Telemetry v2

新增：

```text
smc.execution.telemetry.v2
```

除现有模型/Token/Cache/Retry/Latency 外，新增：

```text
cost_bucket
context_files_read
unique_context_files
repeated_context_reads
target_app_ids
surface_candidates
selected_surface
governance_profile
engineering_method
review_mode
tdd_mode
```

Cost Bucket：

```text
ROUTING
BASELINE_LOOKUP
GROUNDING
PRD
PLAN
IMPLEMENT
TDD
DEBUG
REVIEW
DELIVERY
```

目标：准确区分“写代码成本”与“治理成本”。


## 26. Commit / Delivery Guard

Commit Kind：

```text
CHECKPOINT
CANDIDATE
FINAL
```

CHECKPOINT：

```text
允许 pending Todo
delivery_complete=false
```

FINAL：

```text
all blocking todos completed
verification fresh PASS
review PASS
delivery audit PASS
```

否则：

```text
FINAL_COMMIT_BLOCKED_PENDING_TODO
```


## 27. Consumer Bootstrap 升级

`validate_consumer.py` 增加检查：

```text
Frontend Application Registry
Stack Adapter availability
Per-App baseline health
Surface registry health
Plan validator bridge
Engineering method runtime
TDD runtime
Telemetry runtime
```

禁止真实 Feature 执行阶段才发现运行时依赖缺失。


## 28. Change Matrix

| Change ID | Component | 变更 |
|---|---|---|
| C01 | Context Optimization Engine | 新增统一上下文优化入口 |
| C02 | Risk Facts | v2：Sensitive Touch / Boundary Change 分离 |
| C03 | Work Router | v3 Adaptive Routing |
| C04 | PRD Grounding | Structured Change Semantics |
| C05 | Frontend Application Registry | Monorepo App 隔离 |
| C06 | Stack Adapter | React/Vue/Electron 技术栈分类 |
| C07 | Per-App UX Baseline | 存量 UI 数字地图 |
| C08 | Surface Registry | UX Role / Surface Registry |
| C09 | Visual Intent | Screenshot / Prototype binding |
| C10 | UX Surface Gate | EXTEND existing 优先 |
| C11 | Shared UI Registry | 共享组件索引 |
| C12 | Incremental Refresh | Baseline 增量刷新 |
| C13 | Engineering Method | v3 |
| C14 | Focused TDD | Sensitive bounded focused cycle |
| C15 | LEAN Plan | Compact Contract |
| C16 | Token Controller | Budget + Context Dedup |
| C17 | Telemetry | v2 |
| C18 | Commit Guard | CHECKPOINT/CANDIDATE/FINAL |
| C19 | Consumer Bootstrap | Frontend Context completeness |
| C20 | Acceptance | Golden regression corpus |


## 29. Acceptance Corpus

新增确定性回归：

### G31 — Existing Auth Read

读取已有 `DesktopAuthState` 并显示 email：

```text
BOUNDED / LEAN
SENSITIVE_BOUNDED
STANDARD
UNIFIED
```

### G32 — Existing Logout Wiring

调用已有 logout，不修改 auth contract：

```text
BOUNDED / LEAN
TDD_FOCUSED_REQUIRED
```

### G33 — Security Boundary Change

修改 token owner / auth protocol：

```text
ARCHITECTURAL / FULL
HIGH_RISK
REASONING
INDEPENDENT
```

### G34 — Existing Surface Candidate

已有 `desktop:sidebar.footer.identity`，Plan 却新增 UserCenter：

```text
UX_SURFACE_REUSE_REQUIRED
```

### G35 — Extend Surface

扩展已有 identity surface：

```text
PASS
```

### G36 — Different App Isolation

desktop Feature 不得自动复用 web Surface。

### G37 — Different Stack Isolation

React Electron 与 Vue Web：

```text
UX Pattern Reuse allowed
Component Reuse not automatic
```

### G38 — Shared UI Reuse

已有 `packages/ui/ProfileAvatar`：

```text
REUSE
```

### G39 — Incremental Refresh

只修改 desktop：

```text
desktop baseline stale/refresh
web baseline fresh
```

### G40 — Sensitive Bounded TDD

Logout side effect：

```text
Focused RED/GREEN
```

### G41 — Final Commit Pending Todo

```text
FINAL → BLOCK
```

### G42 — Telemetry Cost Buckets

必须输出：

```text
routing
baseline lookup
grounding
plan
implementation
tdd
review
delivery
```


## 30. UC-PROFILE-GOV Golden Regression

本次真实 Feature 固化为 v5.0.6 Golden Case。

正确结果：

```text
Work Class:
  BOUNDED

Governance:
  LEAN

Target App:
  smc-copilot-desktop

Target Surface:
  desktop:sidebar.footer.identity

Decision:
  EXTEND_EXISTING
```

最终 UI 应：

```text
复用原 sidebar footer identity 入口
显示 avatar / username / email / logout
Local 模式隐藏 profile switch
保留 profile runtime capability
```

Engineering Method：

```text
用户信息展示:
  BOUNDED_BEHAVIOR
  TDD_PREFERRED
  FAST / STANDARD
  UNIFIED

Logout:
  SENSITIVE_BOUNDED
  TDD_FOCUSED_REQUIRED
  STANDARD
  UNIFIED

Hide Profile Switch:
  BOUNDED_BEHAVIOR
  TDD_PREFERRED
  FAST
  UNIFIED
```


## 31. 兼容策略

### v5.0.5 Risk Facts

旧字段：

```text
security_boundary=true
```

如果没有 v2 细分证据，继续按 Hard Risk 处理，保持 fail-safe。

只有 v2 producer 才允许表达：

```text
security_sensitive_touch=true
security_boundary_change=false
```

### Existing FULL Work

已进入 FROZEN 的 FULL Work 不自动降级。

### Existing Monorepo

首次启用 Frontend Context System：

```text
OBSERVE
```

Baseline 稳定后再切：

```text
GUIDED
→ ENFORCED
```


## 32. Non-Goals

v5.0.6 不负责：

- 删除 FULL Governance；
- 删除 TDD；
- 删除 Independent Review；
- 降低真正安全边界变化的治理要求；
- 强制旧项目重构 UI；
- 让不同技术栈自动复用组件；
- 用 Token 节省覆盖 correctness；
- Promote Accepted Baseline。


## 33. 实施顺序

必须按以下顺序：

```text
1. Risk Facts v2
2. Work Router v3
3. Engineering Method v3
4. Frontend Application Registry
5. Stack Adapters
6. Per-App UX Baseline
7. Surface Registry
8. UX Surface Resolution Gate
9. Visual Intent Binder
10. Shared UI Registry
11. Incremental Refresh
12. LEAN Compact Plan
13. Focused TDD
14. Token Budget Controller
15. Telemetry v2
16. Commit Guard
17. Consumer Bootstrap validation
18. G31-G42 acceptance
```


## 34. Definition of Done

```text
[ ] Risk Facts v2 完成
[ ] Sensitive Touch 与 Boundary Change 分离
[ ] Work Router v3 deterministic
[ ] auth/profile/session 关键词无法独立 HIGH_RISK
[ ] Frontend Application Registry 支持 monorepo
[ ] 不同 App Baseline 隔离
[ ] React/Vue/Electron Stack Adapter 可识别
[ ] Per-App Surface Registry 可生成
[ ] UX Role 可解析
[ ] UX Surface Reuse Gate 可阻止重复入口
[ ] Visual Intent 可绑定截图/原型约束
[ ] Shared UI Package 可独立索引
[ ] Cross-App 不自动 Surface Reuse
[ ] Cross-Stack 仅允许 UX Pattern Reuse
[ ] Baseline 支持增量刷新
[ ] LEAN Compact Plan 可生成
[ ] SENSITIVE_BOUNDED 支持 Focused TDD
[ ] Token Budget Controller 生效
[ ] Telemetry v2 可拆分治理成本
[ ] FINAL Commit pending Todo fail closed
[ ] Consumer Bootstrap 能提前发现 Frontend Context 缺失
[ ] UC-PROFILE-GOV Golden Regression PASS
[ ] G31-G42 PASS
[ ] Package Validation PASS
```


## 35. 最终目标状态

GES v5.0.6 最终形成：

```text
Spec Kit
让需求与 UX Intent 更准确

        ↓

GES Frontend Context System
让 Agent 理解：
“这是哪个 App、哪个 Surface、哪个 Layout Owner、哪些现有组件”

        ↓

Superpowers
用合适的 Engineering Method 执行

        ↓

GES Delivery Truth
保证最终状态可信
```

对存量 monorepo：

```text
一次性建立 Frontend Application Registry
        ↓
每个 App 独立 UX Baseline
        ↓
每个 Feature 只查询目标 App
        ↓
只读取局部相关文件
        ↓
优先 EXTEND existing surface
        ↓
最小化代码和 Token
```

GES 的定位从：

```text
强治理 Skill 集合
```

进一步升级为：

```text
具有项目上下文、风险分层、UX 资产复用与交付真值能力的 AI 软件工程治理平台
```

最终实现：

> **简单任务轻治理，大任务重治理；已有 UI 优先复用，不同应用严格隔离；不重复读代码，不重复造 Surface，不因为敏感关键词浪费大量 Token。**
