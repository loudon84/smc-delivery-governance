---
title: "GES v5.0.7 Frontend Context 指定 Scope 安装工程方案 PRD"
prd_version: "v5.0.7"
status: "DRAFT"
baseline: "GES v5.0.6"
scope: "Frontend Context Scoped Install + Application Boundary + Frontend Runtime Delivery"
language: "简体中文"
supersedes: "patchs/GES-v5.0.7-Frontend-Context-System-PRD.md"
---

# GES v5.0.7 Frontend Context 指定 Scope 安装工程方案 PRD

## 1. 文档定位

本 PRD 是对草案 `patchs/GES-v5.0.7-Frontend-Context-System-PRD.md` 的修订版，收窄范围并驳回其中的破坏性变更。

GES 总体分层保持不变，本版本不新增第二套治理体系：

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

v5.0.6 已交付 Frontend Context System 的主体能力。本版本只解决在真实 monorepo 消费者上暴露的一个核心问题：

> **Frontend Context 只能全仓一次性初始化，无法按指定 scope（单个前端应用）安装。**

在 `smc-copilot` 这类多应用仓库中，全量初始化会强制为所有应用生成 Baseline，带来无关扫描成本、无关 Surface 噪声，并使单应用接入无法独立灰度。


## 2. 对草案的评审结论

草案约 70% 的内容在重述 v5.0.6 已交付能力，真实新增诉求仅集中在「指定 scope 安装」，且夹带了一次收益为零的破坏性路径重命名。

### 2.1 驳回项

| 草案章节 | 草案要求 | 驳回理由 |
|---|---|---|
| §3.1 | `apps-registry.json` 改名 `repository-registry.json` | 纯改名、零技术收益；破坏 `core/manifest.json` 的 `frontend_context_root` 契约与已装消费者数据 |
| §3.2 / §8 | `apps/<app-id>/` 改名 `applications/<app>/` | 同上；`smc-copilot-desktop` 已落两个真实应用 Baseline，草案 §11 未定义迁移与双读兼容 |
| §3.2 | `ui-baseline.json` 改名 `ux-baseline.json` | 同上；连带 11 个模板、4 项 Consumer Validation 检查、G34–G39 全套 Golden 需返工 |
| §3.2 | 新增独立 `stack-profile.json` | 技术栈字段已在 `app-profile.json` 内，拆分会产生双真值来源 |
| §3.1 | Registry 示例仅保留 `repository` + `applications[]` | 会丢弃现有 `shared_ui[]`、`root`、`runtime`、`framework`、`stack_adapter`，导致 Schema 退化 |
| §7 | 把 repository registry / discover / init 并入 install 主流程 | 与既有决策冲突：Frontend Context 数据由 `consumer-bootstrap/frontend_audit.py` 拥有，installer 不得覆盖，否则破坏 forbidden-writes 边界与回滚语义 |

### 2.2 需补强项

| 草案章节 | 问题 | 本 PRD 处理 |
|---|---|---|
| §7 | `ges frontend init --app apps/work` 无语义定义 | 见第 6 章，定义为 `frontend_audit.py --app`，含幂等、兄弟应用保留、dry-run 语义 |
| §7 | `--app` 传路径，现有接口用 `app_id` | 见 C23，统一做 path 与 app_id 归一 |
| §10 | 四条验收标准均为「支持 xxx」，不可测 | 见第 12 章，固化为 G43–G50 确定性回归 |
| §11 | 迁移计划未覆盖 v5.0.6 存量数据 | 见第 13 章，明确 v1 兼容读与零迁移原则 |


## 3. 核心目标

> **让 Frontend Context 能按前端应用边界独立安装、独立刷新、独立验证，并把应用边界从隐式扫描规则升级为可声明、可审计的契约。**

目标执行路径：

```text
monorepo 消费者
→ 指定 scope 初始化（单应用）
→ 声明式 Application Boundary
→ 边界内 Surface / Component 扫描
→ Feature Scope 解析管线
→ 局部 Context + Token Budget
```


## 4. 非目标（v5.0.6 已交付，本版本不重复实现）

以下能力已在 v5.0.6 落地并有 Golden 回归覆盖，本版本仅复用，不重写、不改 Schema 名称。

| 能力 | v5.0.6 实现位置 | 既有回归 |
|---|---|---|
| Monorepo 多应用发现与隔离 | `context-engine/frontend_app_registry.py` | G36 |
| 跨应用 Surface 隔离恒为禁止 | `cross_app_surface_allowed` | G36 |
| 技术栈分类与 Adapter | `context-engine/stack_classifier.py` + `frontend-adapters/` | G37 |
| 每应用 UX Baseline | `context-engine/ux_context_resolver.py` | G35 |
| Surface Registry 与 UX Role | `resolve_surface` | G34 / G35 |
| UX Surface 复用门禁 | `reuse_gate` | G34 / G35 |
| Shared UI 组件复用 | `shared_ui_reuse_decision` | G38 |
| Baseline 增量刷新 | `incremental_refresh` | G39 |
| Token Budget 与 Context Cache | `token_budget.py` / `context_cache.py` | G42 |
| Work Scope 统一入口 | `context-engine/work_scope.py` | 单元测试覆盖 |

草案 §2.1–§2.5、§3.3、§4、§6 所述能力全部落入本表，不构成 v5.0.7 变更项。


## 5. 路径与命名冻结决策

本版本**不改动**任何既有 Consumer 数据路径，冻结如下：

```text
.agents/ges/frontend/
    apps-registry.json                       仓库级应用注册表
    adoption-mode.json                       OBSERVE / GUIDED / ENFORCED
    apps/<app-id>/
        app-profile.json                     应用画像（含技术栈与边界）
        ui-baseline.json
        surface-registry.json
        layout-map.json
        navigation-map.json
        component-registry.json
        state-owner-map.json
        design-system.json
        baseline.lock.json
    shared/
        shared-ui-registry.json
```

新增运行时目录（installer 拥有，与上述数据目录严格分离）：

```text
.agents/ges/frontend-runtime/                Frontend Context Runtime 代码
.agents/ges/frontend-adapters/               技术栈 Adapter 定义
```

所有格式仍为 JSON，不引入 YAML，与 v5.0.5 冻结决策一致。


## 6. 指定 Scope 安装语义

这是本版本的核心新增能力。

### 6.1 入口

```bash
# 全量（v5.0.6 既有行为，保持不变）
python consumer-bootstrap/frontend_audit.py <project> --apply

# 指定 scope：只初始化单个应用
python consumer-bootstrap/frontend_audit.py <project> --app work --apply

# 指定 scope：可重复，可用路径
python consumer-bootstrap/frontend_audit.py <project> --app apps/work --app apps/admin --apply
```

### 6.2 语义契约

| 规则 | 定义 |
|---|---|
| 默认 dry-run | 不带 `--apply` 时只报告将写入的路径，不落盘 |
| Registry 仍为仓库级真值 | `apps-registry.json` 始终记录**全部**发现的应用，不因 scope 而裁剪 |
| Baseline 按 scope 写入 | 只为选中应用生成 `apps/<app-id>/` 文件集 |
| 兄弟应用保留 | 未选中应用的既有 Baseline 不删除、不改写、不标记失效 |
| 幂等 | 同一 scope 重复执行，内容稳定；仅 `baseline.lock.json` 的时间戳与摘要按输入变化更新 |
| 标识归一 | `--app work`、`--app apps/work`、`--app apps/work/` 三者等价 |
| 未知标识 fail-closed | scope 无法解析到已发现应用时返回 `FRONTEND_SCOPE_APP_UNKNOWN`，退出码非 0，且不写入任何文件 |
| Shared UI 始终刷新 | `shared/shared-ui-registry.json` 为仓库级共享资产，任一 scope 安装均刷新 |

### 6.3 Baseline 状态可见性

`apps-registry.json` 每个应用条目增加 `baseline_status`：

```json
{
  "app_id": "work",
  "root": "apps/work",
  "runtime": "electron",
  "framework": "react",
  "stack_adapter": "react-electron",
  "baseline_status": "INITIALIZED"
}
```

枚举：`INITIALIZED`、`NOT_INITIALIZED`、`STALE`。

未初始化的应用必须在报告中显式列出，禁止静默跳过——避免使用者误以为全仓已治理。


## 7. Application Boundary 声明化

v5.0.6 的边界是隐式的（只扫描 `app_root`）。本版本升级为可声明、可审计契约。

### 7.1 位置

写入 `apps/<app-id>/app-profile.json`，Schema 升级为 `smc.ges.app-profile.v2`，保留 v1 兼容读。

```json
{
  "schema": "smc.ges.app-profile.v2",
  "app_id": "work",
  "root": "apps/work",
  "runtime": "electron",
  "framework": "react",
  "stack_adapter": "react-electron",
  "boundary": {
    "allowed_roots": ["apps/work", "packages/ui", "packages/shared/ui"],
    "forbidden_roots": ["apps/admin", "apps/mobile"]
  }
}
```

### 7.2 默认推导规则

| 集合 | 默认内容 |
|---|---|
| `allowed_roots` | 本应用 `root` + 全部已发现 shared UI package root |
| `forbidden_roots` | 其他应用的 `root` |

推导为纯静态规则，不调用模型。使用者可手工收窄 `allowed_roots`，但**不得**加入其他应用的 `root`——冲突时以 `forbidden_roots` 优先，并在审计报告中标记 `BOUNDARY_CONFLICT`。

### 7.3 扫描约束

Baseline 扫描、Surface 解析、Component 索引一律限定在 `allowed_roots` 内。`backend`、`scripts`、`.smc`、`.agents` 及未列入 `allowed_roots` 的任何目录禁止自动扫描。


## 8. 嵌套 Shared UI 发现

v5.0.6 只遍历 `packages/` 的直接子目录且名称须为 `ui` 或 `*-ui`，导致草案 §5 明确要求支持的 `packages/shared/ui` 无法识别。

本版本扩展发现规则：

| 规则 | 定义 |
|---|---|
| 搜索深度 | `packages/` 下最多 3 层 |
| 名称匹配 | 目录名为 `ui` 或以 `-ui` 结尾 |
| 排除 | `node_modules`、以 `.` 开头的目录 |
| 去重 | 同一 root 只登记一次；父子同时命中时取最深路径 |
| 应用排除 | 命中 shared UI 的 package 不得同时被登记为前端应用 |

`shared-ui-registry.json` 的 Schema 名称与结构不变。


## 9. Frontend Context Runtime 交付到消费者

### 9.1 问题

`context-engine/` 与 `frontend-adapters/` 目前仅存在于包内，从未安装到消费者。Install Lock 的 `owned_files` 只包含 `.agents/ges/domain-runtime/`。后果：

- 消费者无法在本地执行 Application Resolver / Surface Resolver；
- `validate_consumer.py` 的「Stack Adapter availability」会回退接受包内路径，验证结论虚高。

### 9.2 方案

由 installer 将运行时安装到消费者，纳入 `owned_files`，具备事务回滚能力：

| 来源 | 目标 |
|---|---|
| `context-engine/` | `.agents/ges/frontend-runtime/` |
| `frontend-adapters/` | `.agents/ges/frontend-adapters/` |

### 9.3 边界原则（关键）

**运行时代码由 installer 拥有；Frontend Context 数据由 consumer-bootstrap 拥有。** 两者路径分离，职责不交叉。

installer 仍**禁止**写入 `.agents/ges/frontend/`（数据目录）与 `.agents/ges/profile.json`。这条边界不因本版本变更而放宽，草案 §7 将 discover / init 并入 install 主流程的方案予以驳回。


## 10. Feature Scope 解析管线

把草案 §4 的四段流程从「分散函数」固化为「单一可断言入口」。

```text
Requirement
    ↓
Application Resolve      定位目标应用
    ↓
Surface Resolve          定位已有 Surface 候选
    ↓
Layout Owner Resolve     定位布局归属
    ↓
Component Reuse Check    共享组件复用决策
    ↓
Plan
```

新增 `resolve_feature_scope()`，输出 Schema `smc.ges.feature-scope.v1`，四段结果均须存在，任一段缺失即为失败。

默认策略与 v5.0.6 保持一致，不改判定语义：

| 情形 | 决策 |
|---|---|
| 同应用、同 UX Role 或同 Action Cluster | `EXTEND` |
| 同应用、`ADD_NEW` 且无 `NEW_SURFACE_JUSTIFICATION` | `UX_SURFACE_REUSE_REQUIRED` |
| 跨应用 | 不复用 Surface，视为新建 |
| 同技术栈或经共享 package | 允许自动 Component Reuse |
| 跨技术栈 | 允许 UX Pattern Reuse，不允许自动 Component Reuse |


## 11. Change Matrix

| Change ID | Component | 变更 |
|---|---|---|
| C21 | Frontend App Registry | Schema v2：新增 `repository` 与 `baseline_status`，v1 兼容读 |
| C22 | Shared UI Discovery | 支持 `packages/` 下最多 3 层嵌套发现 |
| C23 | Scoped Install | `frontend_audit.py --app`，含归一、幂等、兄弟保留、fail-closed |
| C24 | Application Boundary | `app-profile.json` v2 增加 `boundary`，扫描受 `allowed_roots` 约束 |
| C25 | Frontend Runtime Delivery | installer 安装 `frontend-runtime/` 与 `frontend-adapters/` 并纳入 `owned_files` |
| C26 | Feature Scope Pipeline | 新增 `resolve_feature_scope()`，Schema `smc.ges.feature-scope.v1` |
| C27 | Consumer Validation | 新增 Scoped Baseline、Boundary、Runtime 三项检查，取消包路径回退 |
| C28 | Acceptance | 新增 G43–G50 确定性回归 |


## 12. Acceptance Corpus

新增确定性回归，编号接续 v5.0.6 的 G42。

### G43 — Scoped Init Single App

双应用 monorepo（`apps/work`、`apps/admin`），仅执行 `--app work --apply`：

```text
apps/work    baseline 已生成
apps/admin   无 baseline 目录
registry     仍包含 work 与 admin 两条记录
admin.baseline_status = NOT_INITIALIZED
```

### G44 — Scoped Init Idempotent

对同一 scope 连续执行两次 `--app work --apply`：

```text
surface-registry.json 内容逐字节一致
```

### G45 — Scoped Init Preserves Siblings

先 `--app work --apply`，再 `--app admin --apply`：

```text
work baseline 保持存在且内容未被改写
admin baseline 新增生成
```

### G46 — Scope Identifier Normalization

`--app work`、`--app apps/work`、`--app apps/work/` 三种写法：

```text
解析到同一 app_id
产出同一 baseline 目录
```

未知标识：

```text
FRONTEND_SCOPE_APP_UNKNOWN
退出码非 0
无任何文件写入
```

### G47 — Nested Shared UI Discovery

存在 `packages/shared/ui/Button.tsx`：

```text
shared-ui-registry 登记 packages/shared/ui
kind = shared-ui-library
该 package 未被登记为前端应用
```

### G48 — Application Boundary Deny

`apps/work` 与 `apps/admin` 均含 `UserCenter.tsx`，初始化 `work`：

```text
work.boundary.allowed_roots 含 apps/work
work.boundary.forbidden_roots 含 apps/admin
work surface-registry 不含任何 apps/admin 路径
```

### G49 — Frontend Runtime Installed

安装后消费者侧：

```text
.agents/ges/frontend-runtime/ 存在且可导入
.agents/ges/frontend-adapters/<stack>/adapter.json 存在
install lock owned_files 覆盖上述路径
Stack Adapter 检查不回退包内路径
```

### G50 — Feature Scope Pipeline

对已有 identity surface 提出「修改用户中心头像」：

```text
application / surface / layout_owner / component_reuse 四段均存在
surface 决策 = EXTEND
```


## 13. 迁移与兼容

### 13.1 零迁移原则

本版本对 v5.0.6 存量 Consumer 数据实行零迁移：

| 存量 | 处理 |
|---|---|
| `apps-registry.json`（v1） | 兼容读；下次 `--apply` 时补写 `repository` 与 `baseline_status` 升级为 v2 |
| `apps/<app-id>/app-profile.json`（v1） | 兼容读；下次 `--apply` 时补写 `boundary` 升级为 v2 |
| 其余 Baseline 文件 | 路径与 Schema 不变，无需迁移 |
| `_template/` | 保留 |

禁止删除、禁止重命名、禁止要求使用者手工搬迁目录。

### 13.2 交付阶段

| 阶段 | 内容 |
|---|---|
| Phase 1 | C21 / C22 / C24：Registry 与 Boundary Schema 升级，嵌套 Shared UI 发现 |
| Phase 2 | C23 / C26：Scoped Install 与 Feature Scope 管线 |
| Phase 3 | C25：Frontend Runtime 交付进安装事务 |
| Phase 4 | C27 / C28：Consumer Validation 升级与 G43–G50 接入 |
| Phase 5 | 在 `smc-copilot-desktop` 与 `smc-copilot` 双消费者执行 Consumer Validation |


## 14. 禁止写入边界

本版本不放宽任何既有 forbidden writes：

```text
.agents/ges/profile.json                installer 拥有，bootstrap 禁写
.agents/ges/domain-packs/registry.json  installer 拥有，bootstrap 禁写
.specify/spec.md                         使用者拥有，GES 禁写
.agents/ges/frontend/                    bootstrap 拥有，installer 禁写
.agents/ges/frontend-runtime/            installer 拥有，bootstrap 禁写
.agents/ges/frontend-adapters/           installer 拥有，bootstrap 禁写
```


## 15. 交付验收清单

```text
[ ] C21–C28 全部落地
[ ] G43–G50 全部 PASS
[ ] G01–G42 无回归
[ ] 单元测试 无回归
[ ] validate_package 门禁 PASS（含安装与回滚 fixture）
[ ] Install Lock owned_files 覆盖 frontend-runtime 与 frontend-adapters
[ ] 回滚 fixture 可清理 frontend-runtime 与 frontend-adapters
[ ] lat.md 文档更新且 lat check PASS
[ ] smc-copilot-desktop Consumer Validation PASS
[ ] 指定 scope 安装在真实 monorepo 上验证 PASS
```


## 16. 版本定位

GES v5.0.7 形成的治理链：

```text
Repository（apps-registry.json）
    ↓
Application（apps/<app-id>/ + boundary）
    ↓
Feature Surface（surface-registry.json）
    ↓
Component Ownership（component-registry.json / shared-ui-registry.json）
    ↓
Safe AI Coding Delivery
```

与草案的最终差异：治理链的**层级语义完全采纳**，文件命名与目录结构**保持 v5.0.6 冻结状态**，新增能力聚焦于指定 scope 安装、声明式应用边界与运行时交付。
