---
title: "GES 6.0.0-alpha.5 — Alpha.4 Closure + Work Execution Contract & Capability Binding PRD"
subtitle: "Capability Governance Closure → Work Execution Readiness"
prd_id: "PRD-GES6-A4-CLOSURE-A5-WORK-EXECUTION"
version: "1.1"
status: "BINDING_GRILLME"
product: "GES 6"
repository: "loudon84/smc-delivery-governance"
branch: "feat/ges-v6.1"
owner: "GES"
reviewers: ["Product Owner", "Engineering Governance Owner"]
created_at: "2026-09-19"
updated_at: "2026-09-19"
target_release: "GES 6.0.0-alpha.5"
change_type: ["BROWNFIELD_CHANGE", "GOVERNANCE", "ARCHITECTURE_CHANGE", "INTEGRATION"]
golden_consumer: "E:\\git\\smc-copilot-desktop"
baseline:
  branch_head: "6ff5a0ac126794814bb843a1592ad7c63d9102a5"
  current_product_version: "6.0.0-alpha.4"
  distribution_version: "1.2.1"
related_docs:
  - "docs/prd/GES-v6.2-Capability-Governance-Foundation-PRD-v1.0.md"
  - "PRD-GES6-Capability-Resolver-RTK-Provider-v1.0.md"
  - "PRD-GES-Large-Repo-Snapshot-Optimization-v1.0.md"
  - "需求PRD工程模板.md"
supersedes: null
binding_source: "grill-me Q1–Q31"
---

# GES 6.0.0-alpha.5 — Alpha.4 Closure + Work Execution Contract & Capability Binding PRD

> 本文档按照《需求PRD工程模板.md》的 Engineering Contract 规范编写。
>
> 本 PRD 包含两个严格有序的交付阶段：
>
> 1. **Alpha.4 Closure**：把 Capability Governance Foundation 从“代码存在 / Golden observed”关闭为真实 Golden Evidence 支撑的 PASS。
> 2. **Alpha.5**：将 Parallel Capability 正式绑定到 Work Execution Contract，并新增独立 `EXECUTION_READY` Gate。
>
> 本 PRD **不实现最终 Release Readiness / Gate C**；CI/Review Evidence Truth Hardening 继续留给 Alpha.6/Alpha.7。

Binding source: grill-me **Q1–Q31**. Where a later section conflicts with §0 Binding table, the Binding table wins.

---

# 0. Binding Grill-me Decisions

These rows are the implementation contract. A later section that conflicts with this table is stale.

| ID | Decision |
|---|---|
| Q1 | Alpha.4 Closure 产品号保持 `6.0.0-alpha.4`。只有 Alpha.5 Release Gate PASS 后才 bump 到 `6.0.0-alpha.5`。Closure 成功标记仅为 `ALPHA4_CAPABILITY_GOVERNANCE_READY`。 |
| Q2 | Alpha.5 代码 MAY 与 Closure 同分支先合入；合成测试 MAY 绿。`ALPHA5_RELEASE_GATE` / `ALPHA5_WORK_EXECUTION_READY` MUST NOT PASS unless `ALPHA4_CLOSURE_GATE == PASS`。 |
| Q9 | `__product_version__` 在 Alpha.5 Release Gate 前 MUST 保持 `6.0.0-alpha.4`（即使 Alpha.5 代码已合入）。Distribution 仍 `1.2.1`。 |
| Q3 | RTK Alpha.4 provider `health_checks` MUST 仅为 `binary` + `version`。MUST 同步改 `providers.yaml`、probe、既有测试。MUST NOT 因 version PASS 自动把 `integration` 置 PASS。 |
| Q22 | Closure MUST 删除假 integration 路径；旧“三格 integration PASS”断言改为 NEG/FAIL 测试。 |
| Q23 | `ges.capability-status.v1` MUST NOT 枚举 health check name；权威名字集合以 `providers.yaml.health_checks` 为准，由测试断言 probe↔catalog exact match。 |
| Q27 | `ges doctor` / `ges capability doctor` 继续 stdout status v1（仅 binary+version）。RTK missing/NOT_READY MUST NOT 使 doctor overall BLOCKED。BOUND MUST NOT 进入 doctor overall。 |
| Q7 / Q17 | `REQUIRED_ALPHA4_ACCEPTANCES` 字面冻结为恰好下列 11 个 id（不多不少）：`A-A4-STATUS-001`, `A-A4-STATUS-002`, `A-A4-GOLD-001`, `A-A4-GOLD-002`, `A-A4-GOLD-003`, `A-A4-GOLD-004`, `A-A4-EVID-001`, `A-A4-EVID-002`, `A-A4-EVID-003`, `A-A4-READY-001`, `A-A4-READY-002`。bootstrap/governance/large-repo/capability-resolver/capability-governance 回归 PASS 是 Closure Gate 另条要求，MUST NOT 混入该 AC id 集合。 |
| Q20 / Q29 | Golden 默认 `E:\git\smc-copilot-desktop`。Alpha.4 Closure env：`GES_ALPHA4_GOLDEN_REPO`。Alpha.5 env：`GES_ALPHA5_GOLDEN_REPO`。缺省皆 desktop；覆盖仅用于本机/CI，不改变契约默认。 |
| Q21 | Golden G2 因真实 RTK/host 未 BOUND 而 BLOCKED 时，Alpha.5 Release MUST NOT PASS。Synthetic PASS MUST NOT 冒充 G2 READY（NEG-013）。 |
| Q4 / Q18 | `ges work create` MUST 要求 `--host cursor\|codex\|hermes`。新 Work MUST 为 `ges.work.v2`，`execution.profile=ges-native`，`capabilities.required=[]` 默认。create MUST NOT 接受 capability 列表，MUST NOT 拷贝 `policy.required`。 |
| Q19 | `ges work migrate --id … --host …` 只改 Work YAML（schema/capabilities/execution/updated_at）；已有 SPEC/PLAN 指针与 digest 原样保留；MUST NOT 自动推断 host；MUST NOT 自动跑 Gate A。 |
| Q5 / Q13 | `effective_required=[]` 且 Gate A PASS 且 v2 契约合法时，Execution Gate MAY PASS。仍校验 profile/host enum；MUST NOT 跑 provider/binding。 |
| Q11 | 无 `.ges/capabilities/policy.yaml` 时 project buckets 视为全空；MUST NOT 因此 FAIL/BLOCK。 |
| Q12 | 每个 `effective_required` id MUST 在 `installed.yaml` 中，否则 `WORK_CAPABILITY_REQUIRED_MISSING`（BLOCKED）。Work-local required MUST NOT 绕过 overlay selection。 |
| Q10 | FAIL(exit 2)：`prohibited` / `conflict` / unknown / Composer id / invalid schema / policy 多桶同 id。BLOCKED(exit 3)：not installed / provider missing\|NOT_READY / UNBOUND\|UNPROVEN / binding race / Gate A 非 PASS / Work v1 缺 execution contract。§7.4「Effective required valid」仅指策略/冲突合法性。 |
| Q8 | Execution Gate MUST 直接调用现有 Gate A 实现并复用其 verdict；MUST NOT 改 Gate A/B 语义。 |
| Q26 | `ges gate explain --gate execution` 复用 explain；零写盘；reasons 与 readiness JSON 同源。 |
| Q24 | Execution Gate / binding probe：stdout 或 `--json` only；MUST NOT 写消费仓；MUST NOT 写入 `ges.evidence-snapshot.v1`。外部 evidence 仅 acceptance runner 在候选树外写。 |
| Q6 | Cursor BOUND：读 `~/.cursor/hooks.json`（或 Cursor 文档钉死的等价路径）→ 存在指向可解析 `rtk`/`rtk.exe` 的 PreToolUse/rewrite 注册 → observation 含 normalized path + SHA256(exact bytes)。仅文件存在 → UNBOUND/UNPROVEN，MUST NOT BOUND。 |
| Q14 | Codex BOUND：项目 `.codex/hooks.json`，否则 `$CODEX_HOME/hooks.json`；须含可解析 RTK PreToolUse/rewrite。若探测到 RTK.md/AGENTS.md 联动模式，两处都 MUST 有效，否则 UNPROVEN。 |
| Q15 / Q25 | Hermes BOUND：插件根查找顺序 (1) `$HERMES_HOME/plugins`（若设）(2) `%LOCALAPPDATA%` 下文档钉死的 Hermes plugins 相对约定路径。找到 RTK rewrite 插件且主配置显式 enable → BOUND。路径缺失/多候选冲突/仅目录存在 → UNPROVEN。MUST NOT 硬编码盘符。MUST NOT 跑 `rtk init`。 |
| Q16 | 配置可读且结构明确但无 RTK 注册 → `UNBOUND`；缺失/多义/无法解析/模式冲突 → `UNPROVEN`。二者 Gate 皆 BLOCKED（不同 reason），MUST NOT PASS。 |
| Q28 | 错误码以本 PRD §14 + 本 Binding 表为权威。实现若需新码 → `SPEC_SEMANTIC_GAP`，先改本 PRD。 |
| Q30 | Grill-me 决策只回写本 PRD；MUST NOT 为对本切片而改写 Foundation PRD，除非发现硬冲突。 |
| Q31 | 本文件为 BINDING_GRILLME 后的 plan 输入；codegen 前以本表为准。 |

Implied：Composer 继续冻结；Gate A=`WORK_READY`；Gate B=`MERGE_READY`；Execution Gate 独立；RTK install/init 外部；runtime observation 非持久 SOT；无 Gate C / RELEASE_READY。

---

# 0A. PRD 使用原则

## 0.1 Normative Keywords

```text
MUST
MUST NOT
SHOULD
SHOULD NOT
MAY
```

所有 `MUST / MUST NOT` 必须映射到 Acceptance、Test 与 Evidence。

## 0.2 No-Inference Rule

Plan / Coding Agent 不得自行决定：

```text
Alpha.4 是否已经 READY
RTK Provider READY 是否等价于 Host 已绑定
Work v1 是否自动推断 execution host
Work v1 是否自动升级
Project Policy 与 Work capability requirement 的优先级
required capability 缺失时 Gate 是 PASS / WARN / BLOCK
unknown capability 是否允许写入 Work
Composer capability 是否允许作为 Parallel Work capability
execution host 配置从哪里读取
Golden Consumer dirty 时是否继续执行
BLOCKED / SKIPPED 是否可计为 PASS
Alpha.5 是否修改 Gate A / Gate B
```

无法唯一确定时：

```text
SPEC_SEMANTIC_GAP
→ BLOCK PLAN
→ MUST NOT 自行补全
```

## 0.3 两阶段发布约束

```text
Alpha.4 Closure Gate
        ↓ PASS only
Alpha.5 Implementation
        ↓
Alpha.5 Release Gate
```

Alpha.5 代码 MAY 与 Alpha.4 Closure 在同一开发分支实现，但：

```text
ALPHA5_RELEASE_GATE MUST NOT PASS
unless ALPHA4_CLOSURE_GATE == PASS
```

产品号（Binding Q1/Q9）：

```text
Closure 期间 __product_version__ == 6.0.0-alpha.4
ALPHA5_WORK_EXECUTION_READY 之前 MUST NOT bump 到 6.0.0-alpha.5
```

---

# 1. 一句话目标

让 GES 在当前 `6.0.0-alpha.4` Capability Governance Foundation 已实现的前提下，先通过真实 Golden Consumer、完整 Required Acceptance Evidence 与 truthful RTK readiness 关闭 Alpha.4，再在 `6.0.0-alpha.5` 中通过 **Work v2 + Explicit Execution Contract + Parallel Capability Binding + Host Binding Observation + EXECUTION_READY Gate** 实现：

```text
Capability
    ↓
Work
    ↓
Execution Readiness
```

同时保证：

```text
Composer 继续冻结
Gate A / Gate B 语义不改变
Business Source 0 mutation
Provider runtime observation 不伪装成持久事实
不提前实现 Alpha.6 / Alpha.7 的最终 Evidence/Release Truth
```

---

# 2. 背景与问题定义

## 2.1 Current State

当前 `feat/ges-v6.1` 基线：

```text
HEAD: 6ff5a0ac126794814bb843a1592ad7c63d9102a5
Product: 6.0.0-alpha.4
Distribution: 1.2.1
```

已实现：

```text
Alpha.1
  Composer bootstrap / Spec Kit / Superpowers / Matt / Cursor discovery

Alpha.2
  Work / Policy / Artifact / Evidence / Trace / Gate A+B

Large Repo
  Git-index Business Source Guard

Alpha.3
  Capability Resolver
  command-output.rtk verify-only provider discovery

Alpha.4
  .ges/capabilities/installed.yaml
  .ges/capabilities/policy.yaml
  ges capability list|add|remove|doctor
  RTK-only parallel catalog
  compatibility framework
  Golden runner skeleton
```

当前 Work 仍是：

```text
ges.work.v1
kind = FEATURE
status = OPEN | CLOSED
artifacts = SPEC | PLAN
```

当前 Work 没有：

```text
required_capabilities
execution profile
execution host
host capability binding
```

当前 Gate：

```text
Gate A / INTAKE
→ Work + Policy + SPEC + PLAN
→ WORK_READY

Gate B / MERGE
→ GitHub PR + CI + Review + Local Git
→ MERGE_READY
```

当前 Capability Governance 与 Work/Gate 仍隔离：

```text
Capability Resolver / Overlay / RTK Probe
              │
              X
              │
           Work v1
              ↓
           Gate A/B
```

## 2.2 Alpha.4 Closure 问题

### P0 — Golden 仅 OBSERVED

当前 Golden runner 仅：

```text
run list
compare tree
→ GOLDEN_CAPABILITY_GOVERNANCE_OBSERVED
```

没有证明：

```text
add
remove
policy preservation
lock.requested preservation
real overlay lifecycle
required Alpha.4 AC completeness
```

因此：

```text
runner exists != Alpha.4 READY
```

### P0 — RTK integration health 语义不真实

当前 RTK probe 在：

```text
binary PASS
version PASS
```

之后直接把 `integration PASS` 置为 PASS，但 Alpha.4 本身并没有证明 Host hook/plugin 已接入。

Alpha.4 `READY` 必须收敛为：

```text
Provider Binary Ready
```

Host Binding 由 Alpha.5 独立建模。

### P0 — Capability 尚未进入 Work

Project capability policy 可以写 `required`，但 Work 不能显式声明本次交付要求哪些 parallel capabilities。

### P0 — 缺少 Execution Readiness Gate

Gate A 证明 Work artifacts ready，Gate B 证明 PR merge ready；中间缺少：

```text
当前 Work 是否具备执行所需 Capability + Host Binding
```

## 2.3 Impact

```text
业务影响：AI Coding 开始执行前，无法机器证明执行环境符合 Work 能力要求。
工程影响：Capability Governance 停留在 Project-level，未进入 Delivery-level contract。
安全影响：binary detected 可能被误判成 hook/plugin 已激活，产生 false READY。
运维影响：安装、可运行、已绑定三个状态未分离。
AI Coding 影响：Agent 可在 Work 未声明、Provider 未绑定、Host 未准备时直接开始实现。
```

---

# 3. Scope / Non-goal

## 3.1 In Scope

```text
SCOPE-A4-001 修正 RTK provider status 语义，Provider READY 与 Host BOUND 分离。
SCOPE-A4-002 增强 Alpha.4 Golden：list/add/doctor/remove 真实 Consumer 生命周期验证。
SCOPE-A4-003 建立 Alpha.4 Closure Evidence，Required AC 完整且唯一。
SCOPE-A4-004 建立 ALPHA4_CAPABILITY_GOVERNANCE_READY closure marker。
SCOPE-A4-005 既有 bootstrap/governance/large-repo/capability-resolver/capability-governance 回归 PASS。

SCOPE-A5-001 新增 ges.work.v2。
SCOPE-A5-002 Work v2 增加 parallel required capabilities。
SCOPE-A5-003 Work v2 增加 execution profile / host。
SCOPE-A5-004 显式 v1→v2 migration，不自动猜 host。
SCOPE-A5-005 新增 Work capability add/remove contract。
SCOPE-A5-006 新增 Runtime Host Binding Observation。
SCOPE-A5-007 RTK binding observation 支持 Cursor / Codex / Hermes。
SCOPE-A5-008 新增 ges gate execution → EXECUTION_READY。
SCOPE-A5-009 Project policy.required 与 Work local required 合并。
SCOPE-A5-010 Project policy.prohibited 具有最高拒绝优先级。
SCOPE-A5-011 Execution Gate 全程 read-only。
SCOPE-A5-012 Golden Consumer 验证 Work v2 + required RTK + Execution Gate。
SCOPE-A5-013 外部 release evidence 绑定 candidate commit SHA。
```

## 3.2 Out of Scope

```text
NON-GOAL-001 Alpha.5 MUST NOT 实现 Gate C / RELEASE_READY。
NON-GOAL-002 Alpha.5 MUST NOT修复 CI Evidence subject semantics；进入 Alpha.6。
NON-GOAL-003 Alpha.5 MUST NOT实现 Review-current-HEAD binding；进入 Alpha.6。
NON-GOAL-004 Alpha.5 MUST NOT改变 ges.evidence-snapshot.v1。
NON-GOAL-005 Alpha.5 MUST NOT改变 Gate B MERGE_READY 计算语义。
NON-GOAL-006 Alpha.5 MUST NOT自动安装 RTK binary。
NON-GOAL-007 Alpha.5 MUST NOT自动执行 rtk init 修改 Host 配置。
NON-GOAL-008 Alpha.5 MUST NOT注册 CodeGraph/Ponytail/Caveman/Comet。
NON-GOAL-009 Alpha.5 MUST NOT thaw Composer / lock.requested。
NON-GOAL-010 Alpha.5 MUST NOT扩展 Work kind；仍仅 FEATURE。
NON-GOAL-011 Alpha.5 MUST NOT引入 allowed_paths/denied_paths enforcement。
NON-GOAL-012 Alpha.5 MUST NOT持久化 Host runtime binding status 为 SOT。
NON-GOAL-013 Alpha.5 MUST NOT把 Runtime READY/BOUND 写入 lock/project/receipt。
```

## 3.3 Architecture Boundary

| Domain | Owner | Input | Output | 不负责 |
|---|---|---|---|---|
| Composer Desired State | Existing Composer | project profile | frozen resolved capabilities | Parallel Provider |
| Parallel Provider Catalog | GES package | providers.yaml | Provider identity | Work state |
| Capability Selection | installed.yaml | capability CLI | selected ids | Host binding |
| Capability Policy | policy.yaml | user policy | required/recommended/optional/prohibited | Work mutation |
| Work Contract | governance works | human/CLI | Work v1/v2 | Runtime observation |
| Provider Probe | Provider Adapter | local runtime | READY/NOT_READY/missing | Persistent truth |
| Host Binding Probe | Binding Adapter | host config | BOUND/UNBOUND/UNPROVEN | 自动安装 |
| Execution Gate | GES | Work+Policy+Probe | EXECUTION_READY/BLOCKED | GitHub Merge |
| Gate A | Existing GES | Work+SPEC+PLAN | WORK_READY | Runtime host |
| Gate B | Existing GES | PR/CI/Review/Git | MERGE_READY | Release Gate C |
| Closure Evidence | Acceptance Runner | tests+Golden | external JSON | Product source mutation |

---

# 4. Terminology / Domain Model

**Capability Provider**：Package catalog 中的 parallel provider。Alpha.5 仍只有 `command-output.rtk`。

**Installed Capability**：存在于 `.ges/capabilities/installed.yaml` 的 parallel capability id。

```text
INSTALLED != READY != BOUND
```

**Provider READY**：Provider binary/runtime 自身可执行。RTK 在 Alpha.4 Closure 后定义为 **binary + version** 可证明（Binding Q3）；不代表 Host 已绑定。health_checks MUST NOT 含未证明的 `integration`。

**Host BOUND**：Provider 与当前 Work 声明的 `execution.host` 形成可机器证明的 hook/plugin 接线。

**Work-local Required Capability**：`ges.work.v2.capabilities.required[]` 中的能力，只对该 Work 生效。

**Project Required Capability**：`.ges/capabilities/policy.yaml.required[]`，对所有 Alpha.5 Execution Gate 生效。

**Effective Required Capability**：

```text
effective_required = project_policy.required UNION work.capabilities.required
```

去重、排序。

**Execution Contract**：Work v2 中 `execution.profile` + `execution.host`。

**WORK_READY**：既有 Gate A verdict，语义不变。

**EXECUTION_READY**：Alpha.5 新 verdict：

```text
WORK_READY
+ valid execution contract
+ all effective required selected
+ Provider READY
+ Host BOUND
+ no prohibited/conflict
```

**MERGE_READY**：既有 Gate B verdict，Alpha.5 不修改。

---

# 5. System Context

## 5.1 Context Diagram

```text
Capability Policy
      │
Capability Catalog → Capability Overlay
      │
      ▼
   Work v2
      │
      ▼
Gate A / WORK_READY
      │
      ▼
Host Binding Observation
      │
      ▼
Gate Execution / EXECUTION_READY
      │
      ▼
AI Coding Agent
      │
      ▼
PR / CI / Review
      │
      ▼
Gate B / MERGE_READY
```

## 5.2 System Boundary

```text
Inside boundary:
- Work v2 schema
- Work capability binding
- capability policy evaluation
- provider readiness observation
- Cursor/Codex/Hermes RTK binding observation
- Execution Gate
- Alpha.4/Alpha.5 acceptance evidence

Outside boundary:
- RTK binary installation
- RTK hook installation mutation
- host product internals
- code generation
- CI execution
- PR review
- deployment

Trusted input:
- GES package schemas
- validated provider catalog
- validated Work YAML
- validated capability policy YAML

Untrusted input:
- user-edited host config
- environment variables
- RTK CLI human text
- unvalidated policy/work files
```

---

# 6. Authoritative State / SOT

| State | Class | Authoritative? | Writer | Reader | 自动覆盖 |
|---|---|---:|---|---|---:|
| `ges/catalog/providers.yaml` | DESIRED_STATE | YES provider identity | GES package | Resolver/CLI/Gate | NO |
| `.ges/capabilities/installed.yaml` | LAST_APPLIED_STATE | YES selection | capability add/remove | Gate/CLI | ENTRY only |
| `.ges/capabilities/policy.yaml` | DESIRED_STATE | YES project policy | user; GES seed only | Gate/CLI | NO after create |
| `ges.work.v1` | DESIRED_STATE | YES legacy Work | GES CLI | Gate/Trace | NO auto migrate |
| `ges.work.v2` | DESIRED_STATE | YES Alpha.5 Work | GES CLI | Gate/Trace | Work CLI only |
| RTK binary/version | OBSERVED_STATE | NO persist | external runtime | Provider Probe | N/A |
| Host binding | OBSERVED_STATE | NO persist | external host | Binding Probe | N/A |
| binding status v1 | RUNTIME_STATE | DERIVED | Binding Probe | Execution Gate | NO persist |
| execution readiness v1 | EVIDENCE_STATE | DERIVED | Execution Gate | user/runner | NO persist |
| closure evidence | EVIDENCE_STATE | YES for slice release | acceptance runner | release gate | external only |

Invariants：

```text
Runtime observation MUST NOT become Desired State.
Installed MUST NOT imply READY.
READY MUST NOT imply BOUND.
BOUND MUST be evaluated against Work.execution.host.
```

---

# 7. State Machines

## 7.1 Alpha State

```text
ALPHA4_IMPLEMENTED
  ↓ closure evidence
ALPHA4_CLOSURE_PENDING
  ↓ all required AC PASS
ALPHA4_CLOSED
  ↓ Alpha.5 implementation
ALPHA5_IMPLEMENTED
  ↓ synthetic + golden
ALPHA5_VERIFIED
```

Illegal：

```text
ALPHA4_CLOSURE_PENDING → ALPHA5_VERIFIED
ALPHA4_BLOCKED → ALPHA5_VERIFIED
```

## 7.2 Parallel Capability

Persistent selection：

```text
AVAILABLE → INSTALLED → AVAILABLE
```

Provider observation：

```text
missing | NOT_READY | READY
```

Host binding observation：

```text
UNSUPPORTED | UNPROVEN | UNBOUND | BOUND
```

These axes MUST NOT collapse.

## 7.3 Work Schema

```text
WORK_V1
  ├─ show/update/close → remains V1
  └─ explicit migrate --host <host>
        ↓
      WORK_V2
        ↓
      capability add/remove
        ↓
      WORK_V2
```

## 7.4 Execution Gate

```text
WORK_READY? ──NO──> BLOCKED
   │YES
   ▼
Execution Contract valid? ──NO──> BLOCKED
   │YES
   ▼
Policy/conflict legality for effective_required? ──NO──> FAIL
   │YES
   ▼
For each effective_required: installed + READY + BOUND? ──NO──> BLOCKED
   │YES (or effective_required empty)
   ▼
EXECUTION_READY
```

Binding Q10/Q13：空 `effective_required` 在 Gate A PASS 且契约合法时直接到 EXECUTION_READY，不跑 provider/binding。

---

# 8. Data / Schema Contract

## 8.1 `ges.work.v2`

```json
{
  "schema": "ges.work.v2",
  "id": "WI-EXAMPLE-001",
  "kind": "FEATURE",
  "title": "Example",
  "status": "OPEN",
  "owner": "team",
  "risk": "MEDIUM",
  "policy": "default-v1",
  "artifacts": [],
  "capabilities": {"required": ["command-output.rtk"]},
  "execution": {"profile": "ges-native", "host": "cursor"},
  "created_at": "...",
  "updated_at": "..."
}
```

Rules：

```text
additionalProperties=false
kind const FEATURE
capabilities.required uniqueItems=true
execution.profile const ges-native
execution.host enum cursor|codex|hermes
```

Composer IDs `matt.* / speckit.* / superpowers.*` MUST NOT be accepted in `capabilities.required`。

## 8.2 `ges.capability-binding-status.v1`

```json
{
  "schema": "ges.capability-binding-status.v1",
  "capability_id": "command-output.rtk",
  "provider": "rtk",
  "host": "cursor",
  "status": "BOUND",
  "provider_status": "READY",
  "observations": [
    {"name": "host_registration", "status": "PASS", "source": "~/.cursor/hooks.json", "digest": "sha256:..."}
  ],
  "evaluated_at": "..."
}
```

Status enum：

```text
BOUND | UNBOUND | UNPROVEN | UNSUPPORTED
```

MUST NOT persist automatically.

## 8.3 `ges.execution-readiness.v1`

```json
{
  "schema": "ges.execution-readiness.v1",
  "work_id": "WI-EXAMPLE-001",
  "status": "PASS",
  "verdict": "EXECUTION_READY",
  "execution_profile": "ges-native",
  "host": "cursor",
  "effective_required": ["command-output.rtk"],
  "capabilities": [],
  "reasons": [],
  "evaluated_at": "...",
  "tool_version": "6.0.0-alpha.5"
}
```

## 8.4 Alpha.4 Closure Evidence

`ges.alpha4-capability-closure-evidence.v1` MUST contain：

```text
candidate_sha
product_version
distribution_version
golden.source_path
golden.origin
golden.head_sha
golden.source_clean
required_acceptance_ids
acceptances
regression
release_gate
generated_at
tool_version
```

`required_acceptance_ids` MUST equal Binding Q17 字面集合（排序后 exact match）：

```text
A-A4-STATUS-001
A-A4-STATUS-002
A-A4-GOLD-001
A-A4-GOLD-002
A-A4-GOLD-003
A-A4-GOLD-004
A-A4-EVID-001
A-A4-EVID-002
A-A4-EVID-003
A-A4-READY-001
A-A4-READY-002
```

Artifact MUST be outside candidate source tree.

---

# 9. Requirement Units

## REQ-A4-CLOSE-001 — Truthful RTK Provider Readiness

### Goal
消除未经 Host integration 证明的 false-ready。

### Normative Requirement

```text
RTK Alpha.4 provider READY MUST mean:
- binary found
- rtk --version exit 0
- non-empty version

RTK Alpha.4 provider READY MUST NOT mean Host BOUND.
integration MUST NOT auto-PASS solely because version PASS.
Alpha.4 provider health_checks MUST contain only Alpha.4 真正能证明的 checks。
```

冻结实现语义（Binding Q3/Q22/Q23）：

```text
providers.yaml health_checks: [binary, version]
probe health_checks MUST exact-match catalog
MUST NOT emit integration check
ges.capability-status.v1 MUST NOT enum health check names
Host Binding → Alpha.5 ges.capability-binding-status.v1
```

### Inputs
`PATH`、RTK executable、`rtk --version`。

### Preconditions
`providers.yaml` only contains `command-output.rtk` as parallel provider.

### Authoritative State

```text
SOT: package provider contract
Observed: binary path + version
Derived: READY / NOT_READY / missing
```

### Allowed Side Effects
仅 spawn `rtk --version` + stdout。

### Forbidden Side Effects

```text
rtk init
hook install
PATH rewrite
.cursor/.codex/.hermes write
overlay write during doctor
```

### Ownership Scope
`NONE` for external runtime; `PACKAGE FILE` for provider catalog.

### Idempotency
Unchanged runtime → semantically identical status.

### Failure Semantics

```text
binary absent → status=missing → retryable
version nonzero/empty → status=NOT_READY → retryable
```

### Invariants

```text
INV-A4-STATUS-001 INSTALLED != READY
INV-A4-STATUS-002 READY != BOUND
```

### Acceptance
`A-A4-STATUS-001..002`

### Evidence
`TEST-A-A4-STATUS-*` + status payload + catalog snapshot.

---

## REQ-A4-CLOSE-002 — Real Golden Capability Governance Lifecycle

### Goal
将 Alpha.4 Golden 从 list-only observation 升级为真实 lifecycle proof。

### Normative Requirement

Golden MUST use `E:\git\smc-copilot-desktop` or `GES_ALPHA4_GOLDEN_REPO` override，source MUST clean，MUST create detached worktree at exact HEAD，并执行：

```text
1 capability list --json
2 capability add command-output.rtk
3 capability doctor command-output.rtk
4 capability add command-output.rtk again
5 capability remove command-output.rtk
6 capability list --json
```

MUST prove：

```text
list writes 0
first add creates overlay
repeat add is idempotent
remove leaves installed=[] and policy preserved
lock.requested unchanged
project.yaml unchanged
install-receipt unchanged
business source unchanged
source Golden repo unchanged
```

RTK MAY be missing；Alpha.4 Golden MUST NOT require Host RTK。

### Allowed Side Effects
Detached worktree `.ges/capabilities/**` + external evidence dir.

### Forbidden Side Effects
Source Golden repo、business source、Composer desired/lock/receipt mutation.

### Failure Semantics

```text
Golden missing/dirty/detached failure → BLOCKED
source/composer/business mutation → FAIL
overlay semantics mismatch → FAIL
```

### Invariants

```text
INV-A4-GOLD-001 SourceGoldenAfter == SourceGoldenBefore
INV-A4-GOLD-002 ComposerStateAfter == ComposerStateBefore
INV-A4-GOLD-003 BusinessSourceAfter == BusinessSourceBefore
```

### Error Codes

```text
GOLDEN_CAPABILITY_GOVERNANCE_BLOCKED
GOLDEN_SOURCE_MUTATED
GOLDEN_COMPOSER_STATE_MUTATED
GOLDEN_BUSINESS_SOURCE_MUTATED
GOLDEN_OVERLAY_CONTRACT_FAILED
```

### Acceptance
`A-A4-GOLD-001..004`

---

## REQ-A4-CLOSE-003 — Required Acceptance Completeness

### Goal
禁止 partial PASS 伪装成 release PASS。

### Normative Requirement
Alpha.4 Closure runner MUST define canonical `REQUIRED_ALPHA4_ACCEPTANCES` 为 Binding Q17 字面列表（恰好 11 个 id，见 §0）；每个 required id MUST exactly once，unknown=0，duplicate=0，all status=PASS。

Regression suites（bootstrap/governance/large-repo/capability-resolver/capability-governance）MUST PASS 作为 Closure Gate 另条，MUST NOT 混入该 AC id 集合。

### Failure Semantics

```text
missing → ALPHA4_REQUIRED_ACCEPTANCE_MISSING → BLOCKED
duplicate → ALPHA4_ACCEPTANCE_DUPLICATE → FAIL
unknown → ALPHA4_ACCEPTANCE_UNKNOWN → FAIL
```

### Invariant
`release PASS iff exact required set complete and all PASS`。

### Acceptance
`A-A4-EVID-001..003`

---

## REQ-A4-CLOSE-004 — Alpha.4 Closure Gate

### Normative Requirement
`ALPHA4_CLOSURE_GATE=PASS` requires：

```text
truthful RTK status tests PASS
capability-governance synthetic PASS
bootstrap PASS
governance PASS
large-repo PASS
capability-resolver PASS
Golden lifecycle PASS
Required AC completeness PASS
```

Success output exactly：

```text
ALPHA4_CAPABILITY_GOVERNANCE_READY
```

MUST NOT emit READY on BLOCKED/FAIL/SKIPPED。
MUST NOT bump `__product_version__`（保持 `6.0.0-alpha.4`）。

### Acceptance
`A-A4-READY-001..002`

---

## REQ-A5-WORK-001 — Work v2 Schema

### Goal
让 Work 成为 capability requirement + execution contract SOT。

### Normative Requirement
Alpha.5 新 Work MUST use `ges.work.v2`，包含 `capabilities.required` + `execution.profile/host`。Unknown parallel id MUST BLOCK before write；Composer IDs MUST BLOCK before write。

`ges work create` MUST 要求 `--host`；默认 `capabilities.required=[]`；MUST NOT 在 create 时接受 capability 列表或拷贝 project policy.required（Binding Q4/Q18）。

### Inputs
Work create args + provider catalog.

### Preconditions
Governance initialized.

### State Transition
`none → WORK_V2`。

### Allowed Side Effects
One Work file.

### Forbidden Side Effects
Business source、overlay、lock/project mutation.

### Idempotency
Duplicate create → `WORK_ALREADY_EXISTS`, 0 mutation.

### Failure Semantics

```text
unknown capability → WORK_CAPABILITY_NOT_FOUND
Composer capability → WORK_CAPABILITY_UNSUPPORTED
invalid host → WORK_EXECUTION_HOST_UNSUPPORTED
invalid schema → WORK_SCHEMA_INVALID
```

### Invariant
`INV-A5-WORK-001 Work v2 is authority for local work capability requirement`。

### Acceptance
`A-A5-WORK-001..003`

---

## REQ-A5-MIGRATE-001 — Explicit Work v1 → v2 Migration

### Goal
Brownfield Work 不通过推断自动获得 execution host。

### Normative Requirement
新增：

```text
ges work migrate --id <WORK_ID> --host cursor|codex|hermes
```

Migration MUST preserve existing fields（含 artifacts 指针与 digest），set：

```text
schema=ges.work.v2
capabilities.required=[]
execution.profile=ges-native
execution.host=<explicit host>
updated_at=now
```

Read/show/update/close v1 MUST NOT auto-migrate。
MUST NOT 自动跑 Gate A（Binding Q19）。

### Transaction
Validate in memory → atomic replace one Work file → reread/validate.

### Failure Atomicity
`AfterFailure(work bytes)==T0`。

### Error Codes

```text
WORK_ALREADY_V2
WORK_MIGRATION_INVALID
WORK_EXECUTION_HOST_UNSUPPORTED
```

### Acceptance
`A-A5-MIGRATE-001..003`

---

## REQ-A5-WORK-002 — Work Capability Binding CLI

### Normative Requirement
新增：

```text
ges work capability add --id <WORK_ID> <CAPABILITY_ID>
ges work capability remove --id <WORK_ID> <CAPABILITY_ID>
```

Rules：

```text
Work MUST be v2
add known provider → sorted unique atomic write
repeat add → idempotent exit 0
remove present → remove local binding only
remove missing → WORK_CAPABILITY_NOT_BOUND + 0 mutation
```

Project policy.required MUST NOT be edited by Work CLI。

If capability is project prohibited：`WORK_CAPABILITY_PROHIBITED` before write。

### Acceptance
`A-A5-WORKCAP-001..004`

---

## REQ-A5-EXEC-001 — Explicit Execution Contract

Work v2 MUST contain：

```yaml
execution:
  profile: ges-native
  host: cursor | codex | hermes
```

Alpha.5 profile MUST equal `ges-native`。MUST NOT infer host from installed IDE/current process/env/git config/last used agent。

### Acceptance
`A-A5-EXEC-001..002`

---

## REQ-A5-BIND-001 — RTK Host Binding Observation

### Goal
把 Provider READY 与实际 Host BOUND 分离。

### Normative Requirement
Implement read-only：

```text
probe_binding(command-output.rtk, host)
```

Supported hosts：`cursor|codex|hermes`。

Common：Provider READY first；MUST NOT run `rtk init`；MUST NOT patch host config；MUST return `ges.capability-binding-status.v1`。

### Cursor（Binding Q6）
BOUND requires：

```text
read ~/.cursor/hooks.json (or Cursor-documented equivalent path)
→ active PreToolUse/rewrite registration referencing resolvable rtk/rtk.exe
→ observation: normalized display path + SHA256(exact bytes)
```

File exists without valid registration → `UNBOUND` or `UNPROVEN`，MUST NOT `BOUND`。

Remediation（external；GES MUST NOT run）：

```text
rtk init -g --agent cursor
```

### Codex（Binding Q14）
BOUND requires project `.codex/hooks.json` or `$CODEX_HOME/hooks.json` contains resolvable RTK PreToolUse/rewrite registration。If detected mode uses RTK.md/AGENTS.md linkage，both MUST be valid，else `UNPROVEN`。

Remediation（external）：

```text
rtk init -g --codex
```

### Hermes（Binding Q15/Q25）
Plugin root search order：

```text
1. $HERMES_HOME/plugins (if set)
2. %LOCALAPPDATA% under the Hermes plugins relative path frozen in implementation tests / lat (MUST NOT hardcode drive letters)
```

BOUND requires RTK rewrite plugin present under the resolved root **and** main config explicitly enables it。Missing path / multiple conflicting candidates / directory-only → `UNPROVEN`。

Remediation（external）：

```text
rtk init --agent hermes
```

### Unknown/Ambiguous（Binding Q16）
Readable config, clear structure, no RTK registration → `UNBOUND`。
Missing / ambiguous / unparseable / mode conflict → `UNPROVEN`。
MUST NOT return BOUND from file existence alone。Both statuses BLOCK Execution Gate（different reason codes）。

### Identity
Observed host config represented by normalized display path + SHA256 exact bytes；raw content MUST NOT appear in normal status output。

### Race
Execution Gate captures T0 binding identity and rechecks before PASS。Change → `CAPABILITY_BINDING_CHANGED_DURING_EVALUATION` → BLOCKED。

### Acceptance
`A-A5-BIND-001..005`

---

## REQ-A5-POLICY-001 — Effective Required Capability Precedence

### Normative Requirement

```text
effective_required = sorted_unique(project_policy.required UNION work.capabilities.required)
```

Missing `policy.yaml` → all project buckets empty（Binding Q11）。

Precedence：

```text
project prohibited > effective required > project recommended > project optional
```

Same id in multiple project policy buckets → `POLICY_SCHEMA_INVALID`。

Required + prohibited → `WORK_CAPABILITY_PROHIBITED` → FAIL。

Each effective required id MUST appear in `installed.yaml`（Binding Q12），else BLOCKED `WORK_CAPABILITY_REQUIRED_MISSING`。

Recommended/optional missing MUST NOT block unless also effective required。

Empty `effective_required` → Execution Gate MAY PASS when Gate A PASS and Work v2 contract valid；MUST NOT require provider READY or host BOUND（Binding Q5/Q13）。

### Acceptance
`A-A5-POLICY-001..003`

---

## REQ-A5-GATE-001 — EXECUTION_READY Gate

### Normative Requirement
新增：

```text
ges gate execution <work_id> [--json]
ges gate explain <work_id> --gate execution
```

Algorithm：

```text
1 Load Work
2 Require Work v2
3 Call existing Gate A implementation (Binding Q8); reuse verdict
4 Gate A != PASS → BLOCKED
5 Resolve effective_required (empty policy → empty buckets)
6 Validate prohibited/conflict/unknown → FAIL if illegal
7 For each required: installed? provider READY? host BOUND?
8 Recheck binding identity
9 PASS only when all checks PASS (or effective_required empty after steps 1–6)
```

Gate A implementation/verdict MUST NOT change。Gate B implementation/verdict MUST NOT change。

Side effects：0 repo writes；0 overlay writes；0 host writes；0 business source writes（Binding Q24）。

### Status Semantics

```text
PASS → EXECUTION_READY

BLOCKED:
WORK_EXECUTION_CONTRACT_MISSING
WORK_NOT_READY
WORK_CAPABILITY_REQUIRED_MISSING
WORK_CAPABILITY_PROVIDER_NOT_READY
WORK_CAPABILITY_BINDING_UNBOUND
WORK_CAPABILITY_BINDING_UNPROVEN
CAPABILITY_BINDING_CHANGED_DURING_EVALUATION

FAIL:
WORK_CAPABILITY_PROHIBITED
WORK_CAPABILITY_CONFLICT
invalid Work v2 schema
```

### Exit Code

```text
PASS=0
FAIL=2
BLOCKED=3
```

### Acceptance
`A-A5-GATE-001..008`

---

## REQ-A5-COMPAT-001 — Work Capability Compatibility

For `effective_required`，if any pair conflicts via package incompatible → `WORK_CAPABILITY_CONFLICT` → FAIL。Alpha.5 catalog may remain empty incompatible matrix。MUST NOT fabricate OpenSpec/Comet conflicts。

### Acceptance
`A-A5-COMPAT-001..002`

---

## REQ-A5-EVID-001 — Execution Readiness Evidence

`ges gate execution --json` MUST emit `ges.execution-readiness.v1`，including work/profile/host/effective_required/per-capability provider+binding/reasons/tool_version/evaluated_at。

MUST NOT include raw host config/secrets/full env/source bytes。MUST NOT write into `ges.evidence-snapshot.v1`。

### Acceptance
`A-A5-EVID-001..003`

---

## REQ-A5-GOLDEN-001 — Alpha.5 Real Golden Consumer

Golden runner MUST use `E:\git\smc-copilot-desktop` or `GES_ALPHA5_GOLDEN_REPO`，and：

```text
verify source clean
resolve HEAD+origin
create detached worktree
create/migrate temporary Work v2 with explicit --host
link valid SPEC+PLAN
Gate A PASS
bind work-local RTK requirement when testing G2
Execution Gate evaluate
```

Required scenarios：

```text
G1 effective_required=[] → EXECUTION_READY PASS
G2 RTK required + provider READY + declared host BOUND → EXECUTION_READY PASS
```

If real host lacks RTK/binding，G2 → `GOLDEN_ALPHA5_EXECUTION_BLOCKED`；synthetic PASS MUST NOT convert to READY（Binding Q21）。

Source consumer MUST remain unchanged。

### Acceptance
`A-A5-GOLDEN-001..003`

---

# 10. Side-Effect Contract

| Operation | Repo Write | User Home Write | Network | Business Source | External Evidence |
|---|---:|---:|---:|---:|---:|
| capability list/doctor | NO | NO | NO | NO | NO |
| Alpha.4 Golden list | detached/read-only | NO | NO | NO | MAY |
| Alpha.4 Golden add/remove | detached `.ges/capabilities/**` | NO | NO | NO | MAY |
| work create | one Work file | NO | NO | NO | NO |
| work migrate | one Work file | NO | NO | NO | NO |
| work capability add/remove | one Work file | NO | NO | NO | NO |
| RTK provider probe | NO | NO | NO | NO | NO |
| RTK binding probe | NO | NO | NO | NO | NO |
| gate execution | NO | NO | NO | NO | NO |
| Alpha.5 Golden | detached governance state | NO | NO | NO | YES |
| closure evidence writer | NO candidate write | NO | NO | NO | YES |

MUST NOT log raw host config or secrets。

---

# 11. Ownership Contract

| Resource | Ownership | Rule |
|---|---|---|
| `providers.yaml` | PACKAGE/GES | distribution-owned |
| installed.yaml | GES ENTRY-managed | add/remove owns entries |
| policy.yaml | SHARED | GES seeds once; user owns bucket edits |
| Work YAML | GES WHOLE_RESOURCE | Work CLI only |
| SPEC/PLAN target | USER_OWNED | pointer+digest only |
| Cursor/Codex/Hermes configs | EXTERNAL USER_OWNED | read-only |
| RTK binary/hooks/plugins | EXTERNAL | GES does not install |
| closure/golden evidence | GENERATED_ONLY | acceptance runner |

Drift：invalid Work/policy → BLOCK；binding config changes during gate → BLOCK；Golden source dirty → BLOCK。

---

# 12. Hash / Identity Contract

```text
Work/Policy/Host config digest = SHA256(exact bytes)
Candidate identity = git rev-parse HEAD, exact 40 lowercase hex
Golden identity = origin + HEAD + clean/dirty
Host config output = digest only, no raw content
Required Acceptance identity = sorted UTF-8 IDs + duplicate detection
```

No newline normalization。

---

# 13. Transaction Contract

## 13.1 Work Mutation

```text
read T0
→ validate inputs
→ build payload in memory
→ validate schema
→ atomic write
→ reread/validate
```

Failure：`AfterFailure(work bytes)==T0`。

## 13.2 Alpha.4 Golden

```text
source precheck
→ detached worktree
→ snapshot protected state
→ capability lifecycle
→ verify
→ external evidence
→ remove worktree
```

Source repo MUST remain unchanged。

## 13.3 Evidence Commit Order

```text
tests
→ golden
→ required AC completeness
→ bind candidate SHA
→ atomic external evidence write
→ READY marker last
```

## 13.4 Rollback Failure

Temporary worktree cleanup failure → BLOCKED + retained path；diagnostic evidence MUST NOT be deleted。

---

# 14. Failure Contract

| Failure | Status | Code | Mutation | Retryable |
|---|---|---|---:|---:|
| RTK binary absent | observed | missing | 0 | YES |
| RTK version fails | observed | NOT_READY | 0 | YES |
| Golden missing/dirty | BLOCKED | GOLDEN_CAPABILITY_GOVERNANCE_BLOCKED | 0 source | YES |
| Required Alpha4 AC missing | BLOCKED | ALPHA4_REQUIRED_ACCEPTANCE_MISSING | evidence only | YES |
| Duplicate Alpha4 AC | FAIL | ALPHA4_ACCEPTANCE_DUPLICATE | evidence only | NO until fix |
| Work v1 execution gate | BLOCKED | WORK_EXECUTION_CONTRACT_MISSING | 0 | YES after migrate |
| Unknown Work capability | FAIL | WORK_CAPABILITY_NOT_FOUND | 0 | NO until input fix |
| Composer id bound locally | FAIL | WORK_CAPABILITY_UNSUPPORTED | 0 | NO until input fix |
| Prohibited required cap | FAIL | WORK_CAPABILITY_PROHIBITED | 0 | YES after policy fix |
| Required cap not installed | BLOCKED | WORK_CAPABILITY_REQUIRED_MISSING | 0 | YES |
| Provider not ready | BLOCKED | WORK_CAPABILITY_PROVIDER_NOT_READY | 0 | YES |
| Host unbound | BLOCKED | WORK_CAPABILITY_BINDING_UNBOUND | 0 | YES |
| Binding unproven | BLOCKED | WORK_CAPABILITY_BINDING_UNPROVEN | 0 | YES |
| Binding race | BLOCKED | CAPABILITY_BINDING_CHANGED_DURING_EVALUATION | 0 | YES |
| incompatible providers | FAIL | WORK_CAPABILITY_CONFLICT | 0 | YES after contract fix |
| invalid Work v2 | FAIL | WORK_SCHEMA_INVALID | 0 | YES |

---

# 15. Conflict Contract

| Conflict | Detection | Default | Error | Mutation |
|---|---|---|---|---:|
| Work+project both require same id | set union | dedupe | none | 0 |
| required + prohibited | policy evaluator | FAIL | WORK_CAPABILITY_PROHIBITED | 0 |
| incompatible pair | provider catalog | FAIL | WORK_CAPABILITY_CONFLICT | 0 |
| unknown provider | catalog | FAIL | WORK_CAPABILITY_NOT_FOUND | 0 |
| Composer id in local parallel list | ownership | FAIL | WORK_CAPABILITY_UNSUPPORTED | 0 |
| Work v1 execution | schema | BLOCK | WORK_EXECUTION_CONTRACT_MISSING | 0 |
| ambiguous host binding | adapter | BLOCK | WORK_CAPABILITY_BINDING_UNPROVEN | 0 |
| host config changes mid-gate | digest recheck | BLOCK | CAPABILITY_BINDING_CHANGED_DURING_EVALUATION | 0 |

Forbidden：last-writer-wins、auto host inference、auto mass migration、auto RTK install、auto prohibited override。

---

# 16. Compatibility / Migration

Existing：`ges.work.v1`、Alpha.4 overlay v1、Gate A/B v1、evidence-snapshot v1。

Rules：

```text
Gate A MUST read v1/v2
Gate B MUST read v1/v2 with no capability behavior change
work show/update/close MUST support v1/v2
Execution Gate MUST require v2
```

Migration only via `ges work migrate --id ... --host ...`。Unknown schema ownership → PRESERVE + REPORT + MUST NOT DELETE。

---

# 17. External Dependency Contract

## RTK

```text
name: RTK / Rust Token Killer
repo: rtk-ai/rtk
reviewed upstream source identity: 0924356b4caba4989607227b7c8824d3d8098719
runtime: external; GES does not install
provider probe: executable + rtk --version
Cursor remediation: rtk init -g --agent cursor
Codex remediation: rtk init -g --codex
Hermes remediation: rtk init --agent hermes
offline behavior: all GES probes local
```

Cursor upstream hook requires RTK >=0.23.0；Cursor binding with lower version → BLOCKED。GES MUST NOT invent minimum versions for other hosts without pinned provider contract/tests。

---

# 18. Security Contract

| Threat | Control | Acceptance |
|---|---|---|
| fake BOUND from binary existence | separate binding probe | A-A5-BIND-* |
| host secret leakage | digest only | A-A5-EVID-003 |
| host config mutation | read-only probe | A-A5-BIND-005 |
| unknown provider injection | catalog validation | A-A5-WORK-002 |
| Composer owner bypass | owner boundary | A-A5-WORK-003 |
| prohibited bypass | precedence | A-A5-POLICY-002 |
| Golden modifies real consumer | detached + before/after | A-A4-GOLD-003 |
| partial AC false PASS | canonical required set | A-A4-EVID-* |
| runtime config race | digest recheck | A-A5-BIND-005 |

---

# 19. Observability

Stages：

```text
ALPHA4_CLOSE_PRECHECK
ALPHA4_CLOSE_SYNTHETIC
ALPHA4_CLOSE_GOLDEN
ALPHA4_CLOSE_EVIDENCE
WORK_MIGRATE
WORK_CAPABILITY_BIND
CAPABILITY_PROVIDER_PROBE
CAPABILITY_HOST_BINDING_PROBE
GATE_EXECUTION_INTAKE
GATE_EXECUTION_CAPABILITY
GATE_EXECUTION_BINDING
GATE_EXECUTION_RECHECK
```

记录：operation id、stage、status、timestamp、repo identity、work id/capability/host（适用时）、error code。MUST NOT记录 raw host config / secret。

---

# 20. Acceptance

## Alpha.4 Closure

### A-A4-STATUS-001
RTK binary+version PASS 时，health checks 与 provider catalog 一致，且不存在未经 binding probe 证明的 integration PASS。

**Oracle**：health check names exact match catalog；no fake integration PASS。

### A-A4-STATUS-002
RTK absent → `status=missing`；tree digest unchanged。

### A-A4-GOLD-001
Golden list read-only：before tree == after tree。

### A-A4-GOLD-002
Golden add/remove：first add installed=[rtk]；repeat row count=1；remove installed=[]；policy persists。

### A-A4-GOLD-003
Golden preservation：lock.requested/project/receipt/business source/source HEAD+status before==after。

### A-A4-GOLD-004
Golden identity：clean=true；HEAD 40 hex；origin non-empty。

### A-A4-EVID-001
actual acceptance id set == canonical required set。

### A-A4-EVID-002
duplicate id → ALPHA4_ACCEPTANCE_DUPLICATE；release != PASS。

### A-A4-EVID-003
any required status != PASS → release != PASS。

### A-A4-READY-001
all required PASS → exactly one `ALPHA4_CAPABILITY_GOVERNANCE_READY` + exit 0。

### A-A4-READY-002
BLOCKED/FAIL → READY marker absent + exit !=0。

## Alpha.5

### A-A5-WORK-001
New Work create emits v2，profile=ges-native，explicit host，required=[] default。

### A-A5-WORK-002
Unknown capability → WORK_CAPABILITY_NOT_FOUND + 0 bytes changed。

### A-A5-WORK-003
matt./speckit./superpowers. → WORK_CAPABILITY_UNSUPPORTED + 0 bytes changed。

### A-A5-MIGRATE-001
Explicit v1 migration preserves semantic fields，adds v2 contract exactly。

### A-A5-MIGRATE-002
Read/show does not migrate；v1 digest unchanged。

### A-A5-MIGRATE-003
Injected migration failure → post bytes == pre bytes。

### A-A5-WORKCAP-001
Add RTK occurs exactly once。

### A-A5-WORKCAP-002
Repeat add idempotent exit 0；semantic digest unchanged。

### A-A5-WORKCAP-003
Remove missing → WORK_CAPABILITY_NOT_BOUND + 0 mutation。

### A-A5-WORKCAP-004
Work capability mutation leaves project policy digest unchanged。

### A-A5-EXEC-001
Create/migrate without host → CLI validation failure。

### A-A5-EXEC-002
profile != ges-native → reject。

### A-A5-BIND-001
Valid Cursor RTK registration + resolvable hook → BOUND。

### A-A5-BIND-002
Valid Codex RTK hook registration → BOUND。

### A-A5-BIND-003
Hermes RTK plugin present+enabled → BOUND。

### A-A5-BIND-004
Hook file exists but no valid registration → UNBOUND/UNPROVEN，not BOUND。

### A-A5-BIND-005
Binding probe writes 0；mid-evaluation config digest change → CAPABILITY_BINDING_CHANGED_DURING_EVALUATION。

### A-A5-POLICY-001
policy.required=[rtk], work.required=[] → effective_required=[rtk]。

### A-A5-POLICY-002
prohibited+work required RTK → FAIL WORK_CAPABILITY_PROHIBITED。

### A-A5-POLICY-003
only recommended RTK missing → does not block Execution Gate。

### A-A5-GATE-001
Work v1 → BLOCKED WORK_EXECUTION_CONTRACT_MISSING exit3。

### A-A5-GATE-002
Gate A != PASS → Execution Gate != PASS。

### A-A5-GATE-003
Required RTK not installed → BLOCKED WORK_CAPABILITY_REQUIRED_MISSING。

### A-A5-GATE-004
Installed but provider missing/not-ready → BLOCKED WORK_CAPABILITY_PROVIDER_NOT_READY。

### A-A5-GATE-005
Provider READY but binding !=BOUND → BLOCKED。

### A-A5-GATE-006
Gate A PASS + installed + READY + BOUND + no conflict/prohibited → PASS EXECUTION_READY exit0。

### A-A5-GATE-007
Execution Gate repo+host config digests before==after。

### A-A5-GATE-008
Existing Gate A/B fixtures preserve verdicts。

### A-A5-COMPAT-001
Synthetic incompatible pair → WORK_CAPABILITY_CONFLICT。

### A-A5-COMPAT-002
Empty incompatible → no fabricated conflict。

### A-A5-EVID-001
Execution JSON validates against ges.execution-readiness.v1。

### A-A5-EVID-002
ges.evidence-snapshot.v1 unchanged/no capabilities field。

### A-A5-EVID-003
Output does not contain secret fixture value from host config。

### A-A5-GOLDEN-001
Real Consumer Work v2 + valid SPEC/PLAN + no required parallel → EXECUTION_READY PASS。

### A-A5-GOLDEN-002
Real RTK READY + real declared Host BOUND + RTK required → EXECUTION_READY PASS。

### A-A5-GOLDEN-003
Golden source HEAD/status/digests unchanged。

---

# 21. Edge-case Matrix

| Case | Work | Policy | Work Required | Provider | Binding | Expected |
|---|---|---|---|---|---|---|
| 1 | v2 | optional | [] | missing | UNBOUND | PASS if Gate A PASS |
| 2 | v2 | recommended RTK | [] | missing | UNBOUND | PASS if Gate A PASS |
| 3 | v2 | required RTK | [] | missing | UNBOUND | BLOCKED |
| 4 | v2 | optional | RTK | missing | UNBOUND | BLOCKED |
| 5 | v2 | optional | RTK | READY | UNBOUND | BLOCKED |
| 6 | v2 | optional | RTK | READY | BOUND | PASS |
| 7 | v2 | prohibited RTK | RTK | READY | BOUND | FAIL |
| 8 | v1 | any | N/A | READY | BOUND | BLOCKED contract missing |
| 9 | v2 | required RTK | RTK | READY | BOUND | PASS dedup |
| 10 | v2 | duplicate policy buckets | RTK | READY | BOUND | FAIL policy invalid |
| 11 | v2 | optional | unknown id | N/A | N/A | write BLOCK |
| 12 | v2 | optional | Composer id | N/A | N/A | write BLOCK |
| 13 | v2 | optional | RTK | READY | changes mid-gate | BLOCKED |
| 14 | v2 | optional | RTK | READY | ambiguous | BLOCKED |
| 15 | v2 | optional | RTK | READY | BOUND | Gate A FAIL→BLOCKED |

---

# 22. Negative Acceptance

```text
NEG-001 RTK version PASS auto-sets integration PASS → FAIL test
NEG-002 Golden only list then READY → FAIL closure
NEG-003 missing Required Alpha4 AC gives PASS → FAIL
NEG-004 v1 silently infers cursor → FAIL
NEG-005 Work add accepts unknown provider → FAIL
NEG-006 Work add accepts Composer id → FAIL
NEG-007 prohibited overridden by Work required → FAIL
NEG-008 Provider READY treated as Host BOUND → FAIL
NEG-009 Execution Gate writes host config → FAIL
NEG-010 Execution Gate writes overlay → FAIL
NEG-011 Execution Gate changes Gate A/B semantics → FAIL
NEG-012 Alpha.5 adds capabilities to evidence-snapshot.v1 → FAIL
NEG-013 Synthetic PASS substitutes blocked Golden → FAIL
NEG-014 BLOCKED/SKIPPED counted PASS → FAIL
```

---

# 23. Failure Injection

| Injection | Postcondition |
|---|---|
| before Alpha4 worktree create | source 0 mutation |
| after Alpha4 add | source 0 mutation; detached diagnostics retained on cleanup failure |
| after remove before evidence | no READY marker |
| before closure evidence write | candidate repo unchanged |
| during evidence write | no partial artifact visible |
| before Work migration replace | Work bytes=T0 |
| after temp Work write before replace | Work bytes=T0 |
| host binding read failure | gate non-PASS, 0 writes |
| host config changes after T0 | binding changed reason |
| provider binary disappears mid-gate | gate non-PASS |
| Golden Alpha5 dirty | BLOCKED, no source mutation |

---

# 24. Evidence Contract

Every Required AC evidence record MUST include：

```json
{
  "acceptance_id": "A-A5-GATE-006",
  "status": "PASS",
  "requirement_ids": ["REQ-A5-GATE-001"],
  "test_ids": ["TEST-A-A5-GATE-006"],
  "command": "pytest ...",
  "exit_code": 0,
  "oracle": {"type": "field_equals", "expected": "EXECUTION_READY", "actual": "EXECUTION_READY"},
  "evidence_files": []
}
```

Evidence MUST bind：repo、candidate SHA、branch、product/distribution version、test command、timestamp、tool version、Golden origin/HEAD。

Evidence MUST be external to candidate tree before SHA binding。

---

# 25. Requirement Traceability Matrix

| Requirement | Acceptance | Test | Evidence | Gate |
|---|---|---|---|---|
| REQ-A4-CLOSE-001 | A-A4-STATUS-001..002 | TEST-A4-STATUS | EVID-A4-STATUS | A4 REQUIRED |
| REQ-A4-CLOSE-002 | A-A4-GOLD-001..004 | TEST-A4-GOLDEN | EVID-A4-GOLDEN | A4 REQUIRED |
| REQ-A4-CLOSE-003 | A-A4-EVID-001..003 | TEST-A4-EVID | EVID-A4-CLOSURE | A4 REQUIRED |
| REQ-A4-CLOSE-004 | A-A4-READY-001..002 | TEST-A4-READY | EVID-A4-CLOSURE | A4 REQUIRED |
| REQ-A5-WORK-001 | A-A5-WORK-001..003 | TEST-A5-WORK | EVID-A5-WORK | A5 REQUIRED |
| REQ-A5-MIGRATE-001 | A-A5-MIGRATE-001..003 | TEST-A5-MIGRATE | EVID-A5-MIGRATE | A5 REQUIRED |
| REQ-A5-WORK-002 | A-A5-WORKCAP-001..004 | TEST-A5-WORKCAP | EVID-A5-WORKCAP | A5 REQUIRED |
| REQ-A5-EXEC-001 | A-A5-EXEC-001..002 | TEST-A5-EXEC | EVID-A5-EXEC | A5 REQUIRED |
| REQ-A5-BIND-001 | A-A5-BIND-001..005 | TEST-A5-BIND | EVID-A5-BIND | A5 REQUIRED |
| REQ-A5-POLICY-001 | A-A5-POLICY-001..003 | TEST-A5-POLICY | EVID-A5-POLICY | A5 REQUIRED |
| REQ-A5-GATE-001 | A-A5-GATE-001..008 | TEST-A5-GATE | EVID-A5-GATE | A5 REQUIRED |
| REQ-A5-COMPAT-001 | A-A5-COMPAT-001..002 | TEST-A5-COMPAT | EVID-A5-COMPAT | A5 REQUIRED |
| REQ-A5-EVID-001 | A-A5-EVID-001..003 | TEST-A5-EVID | EVID-A5-EXEC | A5 REQUIRED |
| REQ-A5-GOLDEN-001 | A-A5-GOLDEN-001..003 | TEST-A5-GOLDEN | EVID-A5-GOLDEN | A5 REQUIRED |

Any MUST without AC / AC without Test / Test without Oracle / Required AC without Evidence → BLOCK。

---

# 26. Release Gate

## 26.1 Alpha.4 Closure Gate

```text
PASS iff:
- exact REQUIRED_ALPHA4_ACCEPTANCES all PASS
- required regression suites PASS
- real Golden PASS
- candidate SHA bound
```

Success：`ALPHA4_CAPABILITY_GOVERNANCE_READY` + exit0。

FAIL → exit2；BLOCKED → exit3；READY marker absent。

## 26.2 Alpha.5 Release Gate

`ALPHA5_RELEASE_GATE=PASS` requires：

```text
ALPHA4_CLOSURE_GATE == PASS
all Alpha.5 Required AC == PASS
Golden G1 == PASS
Golden G2 == PASS with real RTK Provider READY + real Host BOUND
then bump __product_version__ to 6.0.0-alpha.5
```

Success marker：

```text
ALPHA5_WORK_EXECUTION_READY
```

它只代表 Alpha.5 slice verified，MUST NOT解释为应用发布/生产部署/Gate C RELEASE_READY。
在 bump 之前源码产品号 MUST 保持 `6.0.0-alpha.4`（Binding Q1/Q9）。

---

# 27. Golden Consumer

Golden：`E:\git\smc-copilot-desktop`。

Runner MUST record：source path、origin、HEAD、clean、candidate GES SHA、Work id/schema、host、effective required、provider/binding、Gate A、Execution Gate、source before/after identity。

Synthetic Fixture MUST NOT substitute Golden。

Golden missing/dirty/RTK unready/unbound（G2）→ BLOCKED；只有 contract/source mutation violation 才 FAIL。

---

# 28. Plan Generation Contract

Only `status=BINDING_GRILLME` or `APPROVED_FOR_PLAN` may generate `.plan.md`。Plan MUST treat §0 Binding Grill-me Decisions as superseding any conflicting later prose。

Mandatory phases：

```text
PLAN-P0 Alpha.4 Closure Baseline
PLAN-P1 Truthful RTK Provider Status
PLAN-P2 Alpha.4 Golden Lifecycle
PLAN-P3 Alpha.4 Closure Evidence + Gate
PLAN-P4 Work v2 Schema + Storage Compatibility
PLAN-P5 Explicit Work Migration
PLAN-P6 Work Capability CLI
PLAN-P7 Host Binding Observation
PLAN-P8 Execution Readiness Gate
PLAN-P9 Synthetic Acceptance
PLAN-P10 Alpha.5 Golden
PLAN-P11 Release Evidence
```

Suggested files：

```text
ges/catalog/providers.yaml
ges/providers/rtk.py
ges/acceptance/run_golden_capability_governance.py
ges/schemas/ges.work.v2.json
ges/schemas/ges.capability-binding-status.v1.json
ges/schemas/ges.execution-readiness.v1.json
ges/governance/storage.py
ges/governance/registry.py
ges/governance/<execution_gate>.py
ges/providers/<binding>.py
ges/providers/<rtk_binding>.py
ges/cli/work.py
ges/cli/gate.py
ges/cli/main.py
tests/ges6/test_work_execution.py
tests/ges6/test_capability_binding.py
tests/ges6/test_execution_gate.py
ges/acceptance/run_golden_work_execution.py
lat.md/ges6/work-execution.md
lat.md/ges6/work-execution-tests.md
```

Plan Todo schema：

```yaml
id:
requirement_refs:
acceptance_refs:
files_or_symbols:
implementation_goal:
preconditions:
state_transition:
side_effect_scope:
failure_cases:
verification:
status:
evidence:
```

`implemented != verified`。

---

# 29. Code Review Contract

```text
1 Alpha.4 Closure 是否真的依赖 Golden PASS
2 RTK READY 是否仍伪造 integration PASS
3 READY 与 BOUND 是否彻底分离
4 Work v1 是否隐式推断/自动迁移
5 Work v2 是否仅允许 known parallel provider
6 prohibited 是否最高优先级
7 Work mutation 是否只写一个 Work resource
8 Binding Probe 是否 read-only
9 Execution Gate 是否保持 Gate A/B 原语义
10 Execution Gate 是否 fail-closed
11 Host config race 是否检测
12 evidence-snapshot.v1 是否未污染
13 Golden Consumer 是否 source 0 mutation
14 Required AC completeness 是否机器判断
15 最后审 code quality
```

---

# 30. PRD Quality Gate

```text
[x] Goal 唯一明确
[x] Scope / Non-goal 完整
[x] Owner 不重叠
[x] System Boundary 明确
[x] 所有持久状态有 SOT
[x] Desired / Observed / Runtime / Evidence 分离
[x] State transition 明确
[x] default/required/prohibited/conflict 语义明确
[x] ownership 明确
[x] hash scope 明确
[x] mutation contract 明确
[x] read-only 可证明
[x] failure/error/rollback 明确
[x] MUST/MUST NOT 均映射 AC
[x] 高风险路径有矩阵
[x] failure injection 明确
[x] Oracle 可机器判断
[x] Required AC 有 Evidence
[x] Evidence 绑定 commit SHA
[x] BLOCKED/SKIPPED 不算 PASS
[x] Synthetic 不替代 Golden
[x] 无 TBD
[x] 无 SPEC_SEMANTIC_GAP（grill-me Q1–Q31 已冻结；冲突以 §0 Binding 表为准）
[x] status=BINDING_GRILLME
```

---

# 31. Definition of Done

## Alpha.4 Closure

```text
[ ] RTK provider READY 不再自动宣称 integration PASS
[ ] catalog/probe health checks 一致
[ ] Golden 覆盖 list/add/doctor/add/remove/list
[ ] Golden lock.requested 不变
[ ] Golden project/receipt 不变
[ ] Golden business source 不变
[ ] Golden source repo 0 mutation
[ ] Required Alpha4 AC canonical set 完整
[ ] duplicate/unknown/missing AC fail-closed
[ ] regression suites PASS
[ ] external evidence 绑定 candidate SHA
[ ] ALPHA4_CAPABILITY_GOVERNANCE_READY only on PASS
```

## Alpha.5

```text
[ ] ges.work.v2
[ ] new Work create emits v2
[ ] v1 remains readable
[ ] explicit work migrate --host
[ ] no automatic host inference
[ ] work capability add/remove
[ ] only parallel provider ids accepted
[ ] project required ∪ work required implemented
[ ] prohibited precedence implemented
[ ] Cursor binding observation
[ ] Codex binding observation
[ ] Hermes binding observation
[ ] binding probe 0 mutation
[ ] binding race detection
[ ] ges.execution-readiness.v1
[ ] ges gate execution
[ ] gate explain execution
[ ] Gate A regression unchanged
[ ] Gate B regression unchanged
[ ] ges.evidence-snapshot.v1 unchanged
[ ] synthetic AC all PASS
[ ] Golden G1 PASS
[ ] Golden G2 real RTK+host BOUND PASS
[ ] Golden source 0 mutation
[ ] Alpha.5 evidence binds candidate SHA
[ ] ALPHA5_WORK_EXECUTION_READY only on full PASS
```

---

# 32. Product Evolution After This PRD

完成后主链：

```text
Architecture
  ↓
PRD
  ↓
Capability Governance
  ↓
Work Contract
  ↓
SPEC + PLAN
  ↓
WORK_READY
  ↓
Execution Contract
  ↓
Provider READY + Host BOUND
  ↓
EXECUTION_READY
  ↓
Agent Coding
  ↓
PR / CI / Review
  ↓
MERGE_READY
```

仍未完成：

```text
Alpha.6
  CI Evidence exact subject provenance
  Review current-HEAD binding
  Evidence Truth hardening
  delivery Required Acceptance completeness

Alpha.7
  RELEASE_READY / Gate C
  Release Evidence
```

---

# 33. Final Engineering Contract

```text
Alpha.4 Closure
================
Capability Catalog
 + Consumer Overlay
 + Truthful Provider Probe
 + Synthetic Acceptance
 + Real Golden Lifecycle
 + Complete Required AC Evidence
 ↓
ALPHA4_CAPABILITY_GOVERNANCE_READY

Alpha.5
=======
Project Capability Policy
 + Work v2 Local Requirement
 ↓
Effective Required Capabilities
 + Execution Host
 ↓
Provider READY
 + Host BOUND
 + WORK_READY
 ↓
EXECUTION_READY
 ↓
Agent may start governed execution
```

必须保持：

```text
Composer remains frozen.
Gate A remains WORK_READY.
Gate B remains MERGE_READY.
Execution Gate is a new independent gate.
RTK install/init is external in Alpha.5.
Runtime observation is not persistent truth.
No business source mutation.
No final RELEASE_READY claim.
```
