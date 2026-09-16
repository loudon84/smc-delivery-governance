---
title: "GES 6.0-alpha.1 Bootstrap — smc-copilot 首装闭环 PRD"
subtitle: "Clean Brownfield Bootstrap for Matt Skills + Spec Kit + Superpowers"
prd_id: "PRD-GES6-BOOTSTRAP-ALPHA1"
version: "1.0"
status: "APPROVED_FOR_PLAN"
product: "GES 6"
repository: "loudon84/smc-delivery-governance"
branch: "feat/ges-v6.0"
owner: "SMC Engineering Governance"
reviewers:
  - "Product / Architecture Owner"
  - "Independent Engineering Reviewer"
created_at: "2026-09-16"
updated_at: "2026-09-16"
target_release: "GES 6.0-alpha.1 Bootstrap"
change_type:
  - "BROWNFIELD_CHANGE"
  - "INTEGRATION"
  - "GOVERNANCE"
golden_consumer:
  repository: "loudon84/smc-copilot"
  branch: "work/prd-v5.1"
related_docs:
  - "需求PRD工程模板.md"
  - "GES-v6.0-alpha.1-spec-hardened-PRD.md"
supersedes:
  - "GES 6.0-alpha.1 Bootstrap 中与 v5 Legacy 自动兼容、自动迁移、自动清理有关的实施要求"
---

# GES 6.0-alpha.1 Bootstrap — smc-copilot 首装闭环 PRD

> 本 PRD 按《需求PRD工程模板.md》输出。
>
> 本版本目标不是完成 GES 6 全生命周期能力，而是建立一个可在真实 Brownfield 业务项目中稳定使用的最小首装闭环：
>
> **人工清理 GES v5 残留 → 安装 GES 6 → `ges init` 安装 Matt + Spec Kit + Superpowers → 完成 Matt 项目 bootstrap → `ges doctor` READY → 第二次 `ges init` NOOP。**

---

# 0. PRD 使用原则

## 0.1 本 PRD 的工程职责

本 PRD 必须同时冻结：

```text
WHY
  为什么要有 GES 6 Bootstrap

WHAT
  首次安装到底要安装什么

BOUNDARY
  GES 负责什么 / 不负责什么

STATE
  哪些状态是 Desired / Observed / Applied / Readiness

INPUT
  smc-copilot 当前 Brownfield 项目状态

OUTPUT
  项目最终获得哪些文件、Skills、Runtime 与状态

SIDE EFFECT
  GES init 允许改哪些路径、禁止改哪些路径

FAILURE
  冲突、Runtime 缺失、事务失败时必须发生什么

ACCEPTANCE
  如何证明不是“文件装上了”，而是真的可用

EVIDENCE
  如何证明真实 smc-copilot 已通过首装闭环
```

## 0.2 Normative Keywords

```text
MUST
MUST NOT
SHOULD
SHOULD NOT
MAY
```

所有 `MUST / MUST NOT` 必须映射到 Acceptance。

## 0.3 No-Inference Rule

Plan Agent / Coding Agent 对以下事项不得自行补义：

```text
Spec Kit Runtime 如何产生
已有用户文件是否可覆盖
Matt setup 是否自动执行
Cursor Skill 如何被发现
什么状态代表 INSTALLED
什么状态代表 READY
首装后是否允许 capability reconfiguration
ges check 与 ges doctor 的职责边界
Golden Consumer 什么结果才算通过
```

无法唯一确定时：

```text
SPEC_SEMANTIC_GAP
→ BLOCK PLAN
```

---

# 1. 文档元数据

见文档头部 YAML。

实施基线：

```text
GES repository:
  loudon84/smc-delivery-governance
  branch: feat/ges-v6.0

Golden Consumer:
  loudon84/smc-copilot
  branch: work/prd-v5.1
```

当前 `smc-copilot` 已存在：

```text
.agents/
.cursor/
.codex/
.specify/
AGENTS.md
业务源码
项目自定义 Skills
```

因此本需求属于：

```text
CLEANED-BUT-NOT-EMPTY BROWNFIELD BOOTSTRAP
```

不是 Greenfield Init。

---

# 2. 一句话目标

让 `smc-copilot` 在人工删除 GES v5 残留、保留现有业务资产的前提下，通过一次 `ges init` 安全安装并激活首版 `Matt Skills + selected Spec Kit Intent Runtime + selected Superpowers Execution Skills`，完成项目级 readiness 验证，并保证业务源码、自定义 Skills、既有 AGENTS 内容和用户-owned Spec Kit 内容不被错误覆盖。

---

# 3. 背景与问题定义

## 3.1 Current State

当前 GES 6 已具备：

```text
Repo Analyze
Capability Resolve
Pinned Source Resolve
Matt Adapter
Spec Kit Adapter
Superpowers Adapter
Cursor / Codex Harness Adapter
Install Plan
Transactional Apply
Receipt / Lock
ges check
```

当前 `smc-copilot` 已存在：

```text
.agents/skills/**
.cursor/**
.codex/**
.specify/constitution.md
.specify/scripts/.gitkeep
.specify/templates/.gitkeep
AGENTS.md
apps/**
services/**
packages/**
contracts/**
```

现有 `.specify/` 目录的存在不能证明完整 Spec Kit Runtime 已安装。

## 3.2 Problem

当前实现尚未形成“真实可用首装”闭环，主要问题：

```text
P1. Spec Kit Adapter 在检测到 .specify 已存在时跳过 Runtime materialization，
    可能形成“Skill 已出现，但 Runtime 不完整”。

P2. 当前 Spec Kit wrapper 直接引用 pinned raw command template，
    但 raw template 仍可能依赖 resolver、runtime script、template、placeholder token。

P3. 首次安装遇到目标路径已存在但没有 GES Receipt ownership 时，
    不能明确区分“可安全 adopt”与“未知冲突”。

P4. Matt setup skill 被安装后仍需项目级交互 bootstrap，
    但当前没有 INSTALLED / BOOTSTRAP_PENDING / READY 的 readiness 状态。

P5. AGENTS routing 只描述三类方法论，
    但未把具体工作阶段映射到具体 selected Skill。

P6. ges check 主要验证 materialized state，
    但不能证明 Spec Kit / Matt / Cursor 真实可用。

P7. 尚未完成真实 smc-copilot 的 Golden Bootstrap：
    init → check → Matt setup → doctor → Cursor discovery → second init NOOP。
```

## 3.3 Impact

```text
业务影响：
  GES 文件看起来安装成功，但工程 Agent 可能实际无法调用完整 Spec Kit 工作流。

工程影响：
  首装后需要人工排查 runtime、skill、routing，不能作为团队标准入口。

安全影响：
  Brownfield 目标路径若无 ownership 保护，可能覆盖已有自定义 Skill。

AI Coding 影响：
  模型看到多个 Skill/Runtime，但缺乏唯一 routing 与 readiness 语义，
  容易重新产生方法论混用和隐式猜测。

验证影响：
  ges check PASS 不能等价于“工程栈 READY”。
```

---

# 4. Scope

## 4.1 In Scope

```text
SCOPE-001  Clean Brownfield 首次安装
SCOPE-002  smc-copilot 作为 Golden Consumer
SCOPE-003  Cursor 作为 Alpha.1 REQUIRED Harness
SCOPE-004  Matt selected Skills selective install
SCOPE-005  Spec Kit selected Intent capabilities + 所需 Runtime
SCOPE-006  Superpowers selected Execution Skills selective install
SCOPE-007  AGENTS.md managed routing section
SCOPE-008  unmanaged collision protection
SCOPE-009  transactional init/apply
SCOPE-010  ges check materialized-state verification
SCOPE-011  ges doctor runtime/readiness verification
SCOPE-012  Matt post-init interactive bootstrap
SCOPE-013  second init idempotent NOOP
SCOPE-014  Golden Consumer end-to-end Evidence
```

## 4.2 Out of Scope

Alpha.1 Bootstrap MUST NOT implement：

```text
NON-GOAL-001  GES v5 自动检测作为 Release Gate
NON-GOAL-002  GES v5 自动迁移
NON-GOAL-003  GES v5 自动删除
NON-GOAL-004  首装后的 capability reconfiguration
NON-GOAL-005  managed REMOVE 生命周期
NON-GOAL-006  GES version upgrade
NON-GOAL-007  cross-version migration
NON-GOAL-008  自动执行 Matt setup 的交互流程
NON-GOAL-009  自动执行 Spec Kit feature workflow
NON-GOAL-010  自动执行 Superpowers coding workflow
NON-GOAL-011  Hermes Harness 支持
NON-GOAL-012  Codex 作为 Alpha.1 Release Gate
NON-GOAL-013  Governance Backplane GA
NON-GOAL-014  Policy / Risk / Approval / Delivery runtime
```

`ges legacy` MAY 暂时保留代码，但：

```text
MUST NOT 是 Alpha.1 Bootstrap Release Gate 的组成部分。
```

## 4.3 Architecture Boundary

| Domain | Owner | Input | Output | 不负责 |
|---|---|---|---|---|
| Repo Analysis | GES | Consumer Repo | Repo Profile | 业务需求解释 |
| Capability Composition | GES | Profile + Catalog | Resolved Capability Graph | 编码 |
| Engineering Disciplines | Matt | selected skills | discovery/design/decompose skills | Spec author / execution |
| Intent / Spec | Spec Kit | selected intent capabilities | constitution/specify/clarify/plan runtime | implementation |
| Execution Methodology | Superpowers | selected execution skills | plan/TDD/debug/review/finish skills | Spec ownership |
| Harness Integration | GES Cursor Adapter | Shared projection | Cursor-readable Skill/Routing | Cursor Runtime 本体 |
| Project Bootstrap | Human + Matt Setup Skill | Installed Matt setup | docs/agents + project config | 自动替用户决策 |
| Materialized Check | GES Check | Project/Lock/Receipt/Files | PASS/FAIL | Runtime readiness |
| Readiness Check | GES Doctor | Installed stack + project environment | READY/BLOCKED/PENDING | 修改项目 |

---

# 5. Terminology / Domain Model

```text
Clean Brownfield
  人工移除 GES v5 残留，但保留业务项目本身的 AGENTS、Skills、Spec Kit 用户内容与源码。

Installed
  GES 已 materialize 所选能力，Receipt/Lock 与文件状态一致。

Bootstrap Pending
  Engineering capability 已安装，但仍存在必须由用户/Agent 完成的一次性项目配置。

Ready
  GES core、Spec Kit runtime、Matt project bootstrap、Cursor Skill discovery 全部通过 doctor。

User-owned Content
  首装前已存在、且没有 GES 6 Receipt ownership 的内容。

GES-owned Content
  由 GES 6 首装创建，并记录在 install-receipt 中的内容。

Adoptable Identical Content
  首装前已存在，内容与 GES desired bytes 完全一致，但没有 Receipt ownership。
  Alpha.1 默认 PRESERVE + RECORD AS ADOPTED，仅在明确满足本 PRD的 adopt 条件时允许。

Unmanaged Collision
  目标路径存在、无 GES ownership，且内容或 ownership semantics 与 desired 不一致。

Spec Kit Runtime
  selected Spec Kit capability 真正执行所依赖的 command、template、resolver/script、project-local runtime。

Spec Kit Intent Capability
  Alpha.1 只暴露：
  constitution / specify / clarify / plan。

Readiness
  不等价于“文件存在”；必须通过 ges doctor 的运行时检查。

Golden Bootstrap
  在真实 smc-copilot 上完成的首装、check、post-bootstrap、doctor、Cursor discovery、NOOP 验收。
```

---

# 6. System Context

## 6.1 Context Diagram

```text
Human
  │
  │ manually clean GES v5 leftovers
  ▼
smc-copilot Brownfield Repo
  │
  │ ges doctor --preflight
  ▼
GES 6 CLI
  │
  ├── Repo Analyzer
  ├── Capability Resolver
  ├── Source Resolver
  ├── Matt Adapter
  ├── Spec Kit Adapter
  ├── Superpowers Adapter
  ├── Cursor Adapter
  └── Transactional Reconciler
  │
  ▼
smc-copilot materialized engineering stack
  │
  ├── .agents/skills/**
  ├── .specify/.ges/**
  ├── AGENTS.md managed section
  ├── .cursor/ges/**
  └── .ges/**
  │
  ├── run Matt setup skill
  ▼
Project engineering bootstrap state
  │
  └── ges doctor
      ▼
READY
```

## 6.2 System Boundary

```text
Inside boundary:
  GES CLI
  Catalog
  Source Pins
  Adapter projection
  Consumer repo managed projection
  GES state
  check / doctor
  Golden Bootstrap verification

Outside boundary:
  GES v5 cleanup
  Feature development
  Product PRD generation
  Coding execution
  Release deployment

External dependency:
  mattpocock/skills
  github/spec-kit
  obra/superpowers
  git
  Python runtime
  Cursor

Trusted input:
  GES catalog shipped with current GES release
  pinned source SHA
  validated GES state files

Untrusted input:
  existing Brownfield repo files
  local source cache
  user modified managed files
  unexpected pre-existing skill/runtime paths
```

---

# 7. Authoritative State / Source of Truth

| State | Role | Authoritative? | Writer | Reader | 可自动覆盖 |
|---|---|---:|---|---|---:|
| `.ges/project.yaml` | DESIRED_STATE | YES | GES init | compose/check | NO，首装后 Alpha.1 冻结 |
| `.ges/repo-profile.json` | OBSERVED_STATE | NO | analyzer/apply | compose/check/doctor | YES |
| `.ges/lock.json` | RESOLVED_STATE | YES for installed source closure | GES apply | check/doctor | 仅事务内 |
| `.ges/install-receipt.json` | LAST_APPLIED_STATE | YES | GES apply | plan/check | 仅事务内 |
| `.ges/readiness.json` | RUNTIME_STATE | YES for last doctor observation | ges doctor | user/CI | YES |
| `audit/ges6/bootstrap/*.json` | EVIDENCE_STATE | YES for acceptance execution | acceptance runner | release gate | append-only |
| `AGENTS.md` GES marker section | ROUTING_STATE | YES for GES routing only | GES | Cursor/Agent | marker 内可更新 |
| `.agents/skills/**` GES-owned paths | MATERIALIZED CAPABILITY | Receipt-defined | GES | Cursor | 首装后 Alpha.1 不重配置 |
| `.specify/.ges/**` | SPEC KIT MANAGED RUNTIME | Receipt-defined | GES | Spec Kit Skill | 首装后 Alpha.1 不重配置 |
| `.specify/memory/**` / `.specify/specs/**` | USER/RUNTIME DATA | USER | Spec Kit/User | Spec Kit | GES MUST NOT overwrite |

Alpha.1 Bootstrap 强制：

```text
project.yaml 在首次 install 完成后视为冻结 Desired State。
```

如用户需要改 capability：

```text
MUST report RECONFIGURE_NOT_SUPPORTED
MUST NOT 尝试 REMOVE / partial recompose
```

---

# 8. State Machine

```text
PRE_CLEAN
  │ 人工删除 v5 残留
  ▼
CLEAN_BROWNFIELD
  │ ges doctor --preflight
  ▼
PREFLIGHT_PASS
  │ ges init preview
  ▼
PLANNED
  │ confirm
  ▼
INSTALLING
  │ transaction commit
  ▼
INSTALLED
  │ ges check
  ▼
MATERIALIZED_VERIFIED
  │ Matt setup still pending
  ▼
BOOTSTRAP_PENDING
  │ run setup-matt-pocock-skills
  ▼
BOOTSTRAPPED
  │ ges doctor
  ▼
READY
  │ second ges init
  ▼
READY_NOOP
```

非法转移：

```text
UNMANAGED_COLLISION
  → BLOCKED

SPEC_KIT_RUNTIME_INVALID
  → BLOCKED

CAPABILITY_RECONFIG_REQUEST
  → BLOCKED

APPLY_FAILURE
  → rollback to T0

DOCTOR_REQUIRED_CHECK_FAIL
  → BLOCKED / PENDING
```

持久状态：

```text
INSTALLED / MATERIALIZED_VERIFIED
  → .ges project/lock/receipt

BOOTSTRAP_PENDING / READY
  → .ges/readiness.json
```

---

# 9. Data / Schema Contract

## 9.1 Schema Set

Alpha.1 Bootstrap 必须冻结：

```text
ges.project.v2
ges.repo-profile.v2
ges.lock.v1 or successor frozen for Alpha.1
ges.install-receipt.v2
ges.readiness.v1
ges.bootstrap-evidence.v1
```

新 schema：

### `ges.readiness.v1`

```json
{
  "schema": "ges.readiness.v1",
  "ges_version": "6.0.0-alpha.1",
  "repo_head": "<git-sha>",
  "checked_at": "<iso8601>",
  "overall": "READY | BOOTSTRAP_PENDING | BLOCKED",
  "checks": {
    "ges_core": "PASS | FAIL",
    "cursor_harness": "PASS | FAIL",
    "spec_kit_runtime": "PASS | FAIL",
    "matt_skills_installed": "PASS | FAIL",
    "matt_project_bootstrap": "PASS | PENDING | FAIL",
    "superpowers_skills": "PASS | FAIL"
  }
}
```

### `ges.bootstrap-evidence.v1`

```json
{
  "schema": "ges.bootstrap-evidence.v1",
  "ges_version": "6.0.0-alpha.1",
  "ges_commit": "<sha>",
  "consumer_repo": "loudon84/smc-copilot",
  "consumer_commit": "<sha>",
  "branch": "work/prd-v5.1",
  "started_at": "...",
  "finished_at": "...",
  "acceptances": []
}
```

## 9.2 Schema Rule

所有 Alpha.1 Bootstrap 新 schema：

```text
MUST set additionalProperties=false
除非特定 extension field 被本 PRD 明确定义。
```

---

# 10. Requirement Units

## REQ-BOOT-001 — Clean Brownfield Preflight

### Goal

保证 GES 6 首装只处理当前 Brownfield 业务状态，不承担 GES v5 自动迁移责任。

### Normative Requirement

```text
MUST accept an existing Brownfield repo.
MUST NOT require automatic GES v5 migration.
MUST NOT delete unknown pre-existing files.
MUST provide preflight result before first consumer mutation.
```

### Inputs

```text
smc-copilot working tree
current git HEAD
existing AGENTS/.agents/.cursor/.codex/.specify
```

### Preconditions

```text
PRE-BOOT-001:
  用户已人工删除明确的 GES v5 残留。

PRE-BOOT-002:
  业务源码和需要保留的自定义工程资产仍存在。
```

### State Transition

```text
CLEAN_BROWNFIELD
→ PREFLIGHT_PASS | BLOCKED
```

### Allowed Side Effects

```text
ges doctor --preflight:
  consumer repo mutation = 0
```

### Forbidden Side Effects

```text
MUST NOT 删除 .smc / .agents / .cursor / .specify 中未知内容。
MUST NOT 自动清理 legacy。
```

### Failure Semantics

```text
unresolved collision
→ UNMANAGED_PATH_CONFLICT

runtime prerequisite missing
→ BOOTSTRAP_PREREQUISITE_FAILED
```

### Acceptance

```text
A-BOOT-001
A-COLLISION-001
```

---

## REQ-CAP-001 — Fixed Alpha.1 Capability Set

### Goal

首次安装只安装已确认的最小能力集，不安装三套上游 repo 的全部能力。

### Normative Requirement

Matt：

```text
MUST install:
  matt.setup
  matt.grill-with-docs
  matt.grilling
  matt.domain-modeling
  matt.codebase-design
  matt.to-tickets

MUST NOT install:
  matt.to-spec
  matt.implement
  matt.tdd
  matt.diagnosing-bugs
  matt.code-review
  matt.triage unless explicitly introduced by later release
```

Spec Kit：

```text
MUST expose:
  speckit.constitution
  speckit.specify
  speckit.clarify
  speckit.plan

MUST NOT expose:
  speckit.tasks
  speckit.implement
  speckit.converge
```

Superpowers：

```text
MUST install:
  superpowers.using-git-worktrees
  superpowers.writing-plans
  superpowers.subagent-driven-development
  superpowers.test-driven-development
  superpowers.systematic-debugging
  superpowers.requesting-code-review
  superpowers.receiving-code-review
  superpowers.verification-before-completion
  superpowers.finishing-a-development-branch

MUST NOT install by default:
  superpowers.brainstorming
  superpowers.using-superpowers
  superpowers.executing-plans
```

### Invariant

```text
INV-CAP-001:
  Resolver installs dependency closure, not repo wholesale.

INV-CAP-002:
  One engineering domain has one active owner.
```

### Acceptance

```text
A-CAP-001
A-CAP-002
```

---

## REQ-SPECKIT-001 — Spec Kit Runtime Must Be Executable

### Goal

阻止“Spec Kit Skill 已安装，但 command/runtime 不可执行”的假完成状态。

### Normative Requirement

GES MUST 从 pinned Spec Kit source/version 生成 selected Intent capabilities 所需的完整 runtime。

禁止：

```text
MUST NOT simply copy raw templates/commands/*.md and treat them as ready-to-run skills
when unresolved runtime placeholders or dependencies remain.
```

GES Spec Kit Adapter 必须：

```text
1. resolve pinned Spec Kit source
2. stage/render selected integration outside consumer repo
3. obtain deterministic runtime artifacts
4. expose only selected capabilities
5. project required runtime under GES-managed namespace
6. preserve user-owned Spec Kit project data
7. verify runtime dependency closure before commit
```

### Frozen Projection

```text
.specify/
├── memory/**                   USER/Spec Kit runtime data
├── specs/**                    USER/Spec Kit runtime data
└── .ges/
    ├── commands/
    │   ├── constitution.md
    │   ├── specify.md
    │   ├── clarify.md
    │   └── plan.md
    └── runtime/
        └── <required resolver/scripts/templates only>

.agents/skills/
├── speckit-constitution/
├── speckit-specify/
├── speckit-clarify/
└── speckit-plan/
```

### Runtime Render Rule

允许实现方式：

```text
Pinned Spec Kit official CLI in staging
OR
deterministic renderer that produces byte-equivalent selected runtime semantics.
```

Alpha.1 采用单一实现，Plan MUST 选定一种，不得同时存在两套路径。

推荐实现：

```text
staging directory
→ pinned Spec Kit integration generation
→ GES filters selected runtime/capabilities
→ projection
```

### Required Validation

最终 projected Spec Kit command/skill 中：

```text
MUST NOT contain unresolved required placeholders such as:
  {SCRIPT}
  __SPECKIT_COMMAND_*
  unresolved template path tokens
```

除非该 token 明确属于 runtime contract 且 doctor 能证明 resolver 可处理。

### Existing `.specify`

存在 `.specify`：

```text
MUST NOT imply runtime already installed.
```

存在：

```text
.specify/constitution.md
```

不自动迁移。

GES MUST：

```text
PRESERVE
REPORT LEGACY_OR_USER_SPEC_STATE
```

并在 preflight/doctor 中提示用户：

```text
current Spec Kit expects .specify/memory/constitution.md
manual review may be required
```

### Failure

```text
SPEC_KIT_RUNTIME_INCOMPLETE
SPEC_KIT_RENDER_FAILED
SPEC_KIT_UNRESOLVED_TOKEN
SPEC_KIT_MANAGED_CONFLICT
```

### Acceptance

```text
A-SPECKIT-001
A-SPECKIT-002
A-SPECKIT-003
A-SPECKIT-004
```

---

## REQ-COLLISION-001 — Unmanaged Collision Protection

### Goal

保护 smc-copilot 已有自定义 Skills 与配置。

### Normative Requirement

对于每一个 desired path：

```text
Case 1:
  path absent
  → ADD

Case 2:
  path exists
  AND exact bytes == desired bytes
  AND ownership semantics compatible
  → ADOPT_IDENTICAL / PRESERVE
  → record ownership explicitly

Case 3:
  path exists
  AND receipt proves current GES ownership
  → managed reconcile

Case 4:
  path exists
  AND no GES ownership
  AND content differs
  → UNMANAGED_PATH_CONFLICT
  → 0 consumer mutations

Case 5:
  same bytes
  BUT incompatible ownership semantics
  → UNMANAGED_PATH_CONFLICT
```

### Forbidden Side Effects

```text
MUST NOT first-install UPDATE an unknown pre-existing file.
```

### Acceptance

```text
A-COLLISION-001
A-COLLISION-002
A-COLLISION-003
```

---

## REQ-MATT-001 — Matt Installed vs Bootstrapped

### Goal

明确安装 Matt Skill 不等于项目已完成 Matt 一次性 setup。

### Normative Requirement

`ges init`：

```text
MUST install setup-matt-pocock-skills
MUST NOT auto-execute its interactive project decisions
```

init 完成后 readiness：

```text
matt_skills_installed = PASS
matt_project_bootstrap = PENDING
overall = BOOTSTRAP_PENDING
```

当以下项目级输出存在且通过 doctor contract：

```text
docs/agents/issue-tracker.md
docs/agents/domain.md
AGENTS.md / existing routing contains Matt project setup outcome
```

则：

```text
matt_project_bootstrap = PASS
```

`triage-labels.md` 仅当实际安装 triage 时 required。

### Acceptance

```text
A-MATT-001
A-MATT-002
```

---

## REQ-ROUTE-001 — Deterministic Owner → Skill Routing

### Goal

让 Cursor / Agent 不需要自行猜“Matt / Spec Kit / Superpowers 到底用哪个 Skill”。

### Normative Requirement

GES-managed AGENTS section MUST 至少表达：

```text
Discovery / requirement grilling:
  grill-with-docs
  grilling
  domain-modeling

Architecture / codebase design:
  codebase-design

Work decomposition:
  to-tickets

Project principles / constitution:
  speckit-constitution

Feature specification:
  speckit-specify

Requirement clarification:
  speckit-clarify

Technical intent planning:
  speckit-plan

Implementation plan methodology:
  writing-plans

Execution:
  subagent-driven-development

TDD:
  test-driven-development

Debug:
  systematic-debugging

Review:
  requesting-code-review
  receiving-code-review

Completion:
  verification-before-completion
  finishing-a-development-branch
```

### Ownership

```text
AGENTS.md:
  GES owns SECTION only
  outside marker = USER
```

### Acceptance

```text
A-ROUTE-001
A-ROUTE-002
```

---

## REQ-CURSOR-001 — Cursor Skill Discovery

### Goal

证明 GES materialized Skills 能被 Cursor 项目级 Skill 机制消费。

### Normative Requirement

Alpha.1 REQUIRED harness：

```text
cursor
```

Skill root：

```text
.agents/skills/**
```

GES MAY 保留：

```text
.cursor/ges/engineering-stack.md
```

作为 pointer/audit material，但：

```text
MUST NOT 把该 pointer 当作 Skill activation 本身。
```

### Acceptance

Golden Consumer 必须执行至少一个 Cursor Skill discovery smoke：

```text
selected Matt skill discoverable
selected Spec Kit wrapper discoverable
selected Superpowers skill discoverable
```

无需在 Alpha.1 自动执行真实 coding task。

### Acceptance

```text
A-CURSOR-001
```

---

## REQ-CHECK-001 — Materialized-State Check

### Goal

验证安装状态完整一致。

### Normative Requirement

`ges check` MUST be read-only，并验证：

```text
project schema
repo profile schema
lock schema
receipt schema

project requested capability closure
==
lock resolved capability closure

lock source SHA
==
current GES catalog pin

available source cache provenance valid

all managed FILE identities match
all managed SECTION identities match
all managed ENTRY identities match

AGENTS marker grammar valid
all selected capability projections exist

selected Spec Kit commands/runtime artifacts exist

business source unchanged

recompose from frozen Desired State
→ NOOP
```

任何 required item fail：

```text
GES_CHECK_FAILED
process exit != 0
```

### Acceptance

```text
A-CHECK-001 ... A-CHECK-010
```

---

## REQ-DOCTOR-001 — Runtime Readiness Check

### Goal

区分“GES 状态一致”和“工程栈真实可用”。

### Normative Requirement

新增：

```text
ges doctor [repo]
ges doctor [repo] --preflight
```

`doctor --preflight`：

```text
MUST NOT require GES state to exist.
MUST NOT mutate consumer repo.
```

正式 `doctor`：

```text
MUST NOT mutate consumer repo.
```

Required checks：

```text
GES Core               PASS/FAIL
Python/runtime prereq  PASS/FAIL
git                    PASS/FAIL
Cursor project harness PASS/FAIL
Spec Kit runtime       PASS/FAIL
Matt skills installed  PASS/FAIL
Matt project bootstrap PASS/PENDING/FAIL
Superpowers skills     PASS/FAIL
```

Overall：

```text
all required PASS
→ READY

only Matt bootstrap PENDING
→ BOOTSTRAP_PENDING

any other required FAIL
→ BLOCKED
```

`ges doctor` MUST 写入 `.ges/readiness.json` 吗？

为保证 read-only 语义，冻结为：

```text
NO.
```

`ges doctor` stdout/JSON 是 observation。

如需要 persist readiness：

```text
ges init/apply transaction MAY write last known readiness,
but doctor itself MUST remain read-only.
```

Alpha.1 简化：

```text
readiness.json 不作为 REQUIRED persisted state。
```

因此 Part 7 中 `.ges/readiness.json` 调整为：

```text
MAY, not required for Alpha.1.
```

### Acceptance

```text
A-DOCTOR-001
A-DOCTOR-002
A-DOCTOR-003
```

---

## REQ-TXN-001 — Bootstrap Transaction

### Goal

首装失败时保证 consumer repo 回到 T0。

### Transaction Boundary

包括：

```text
.ges/**
.agents/skills/** GES desired paths
.specify/.ges/**
.cursor/ges/**
AGENTS.md managed section
```

不包括：

```text
apps/**
services/**
packages/**
contracts/**
.specify/specs/**
.specify/memory/** user data
existing user-owned Skills
```

### Commit Order

```text
analyze in memory
→ resolve
→ fetch/render in external cache/stage
→ build desired
→ detect collision
→ build install plan
→ preview
→ confirm
→ stage complete install
→ validate stage
→ snapshot T0
→ commit
→ post-commit ges check
→ receipt complete
```

### Failure Atomicity

任何 caught failure：

```text
managed_scope(after rollback)
==
managed_scope(T0)
```

### Rollback Failure

```text
TRANSACTION_ROLLBACK_FAILED
backup MUST be retained
error MUST include recovery location
process exit != 0
```

### Acceptance

```text
A-TXN-001
A-TXN-002
A-TXN-003
A-TXN-004
```

---

## REQ-IDEMP-001 — Second Init NOOP

### Goal

证明首装结果稳定。

### Normative Requirement

在：

```text
same GES version
same catalog
same project Desired State
no managed drift
```

条件下第二次：

```bash
ges init .
```

必须：

```text
no consumer content mutation
GES_RECONCILE_NOOP
exit 0
```

不得重复：

```text
duplicate AGENTS marker
duplicate skill
duplicate Spec Kit runtime
duplicate pointer
```

### Acceptance

```text
A-IDEMP-001
```

---

## REQ-STATE-001 — Alpha.1 No Reconfiguration

### Goal

避免首装 Alpha 被 capability REMOVE / reconfigure 生命周期拖入复杂状态机。

### Normative Requirement

首次成功安装后：

```text
project.yaml = FROZEN bootstrap desired state
```

如果用户执行：

```text
ges init --exclude ...
ges init --enable ...
ges apply with a changed requested set
```

导致 direct requested set 与 installed bootstrap set 不一致：

```text
RECONFIGURE_NOT_SUPPORTED
0 consumer mutation
```

### Acceptance

```text
A-STATE-001
```

---

## REQ-PKG-001 — GES Version Identity

### Goal

保证安装包、CLI 和 Receipt 版本一致。

### Normative Requirement

以下必须一致：

```text
Python package version
ges --version
receipt.ges_version
evidence.ges_version
```

如果 repository release numbering 与 Python package 存在更大产品版本体系，必须引入显式双版本字段：

```text
distribution_version
ges_product_version
```

不得继续让：

```text
package = 1.2.1
ges = 6.0.0-alpha.1
```

在无说明情况下共存。

### Acceptance

```text
A-PKG-001
```

---

# 11. Side-Effect Contract

| Operation | Consumer File Write | Network | Cache Write | GES State | Business Source |
|---|---:|---:|---:|---:|---:|
| `ges doctor --preflight` | NO | NO | NO | NO | NO |
| `ges analyze` | NO | NO | NO | NO | NO |
| `ges diff` | NO | MAY | MAY | NO | NO |
| `ges init` before confirm | NO | MAY | MAY | NO | NO |
| `ges init` after confirm | YES | MAY | MAY | YES | NO |
| `ges check` | NO | MAY only for verified source availability if current design requires | MAY cache verification only | NO | NO |
| `ges doctor` | NO | SHOULD NOT | NO | NO | NO |
| Matt setup skill | YES, user-confirmed project config only | MAY | N/A | NO | NO |

Alpha.1 禁止：

```text
ges init 修改 apps/services/packages/contracts
ges init 删除未知 user-owned file
doctor/check 通过“修文件”让自己 PASS
```

---

# 12. Ownership Contract

## 12.1 Ownership Types

```text
FILE
SECTION
USER_OWNED
ADOPTED_IDENTICAL
```

Alpha.1 Bootstrap 不依赖 ENTRY ownership 完成首装主路径。

## 12.2 Ownership Rule

```text
GES-created FILE
→ GES FILE ownership

AGENTS marker
→ GES SECTION ownership

pre-existing identical selected Skill
→ ADOPTED_IDENTICAL only if exact bytes + compatible semantics

pre-existing different content
→ USER_OWNED conflict
→ BLOCK
```

## 12.3 Drift

首装后：

```text
current == last_applied
→ check PASS

current != last_applied
→ MANAGED_CONTENT_MODIFIED
→ check FAIL
```

Alpha.1 不自动 merge drift。

---

# 13. Hash / Identity Contract

FILE：

```text
sha256(file_bytes)
```

SECTION：

```text
sha256(exact managed marker section bytes)
```

Source Cache：

```text
source_repo
pinned_commit_sha
selected_source_paths
content_digest
```

Spec Kit staged runtime：

```text
runtime_identity MUST be derived from final projected runtime bytes,
separate from upstream source identity.
```

必须分开：

```text
source_content_digest
projection_content_digest
```

---

# 14. Transaction Contract

详见 `REQ-TXN-001`。

额外要求：

```text
collision detection MUST complete before first consumer mutation.

Spec Kit runtime verification MUST complete in stage before first consumer mutation.

post-commit ges check failure MUST trigger rollback.
```

---

# 15. Conflict Contract

| Conflict | Detection | Behavior | Error | Mutation |
|---|---|---|---|---:|
| unknown existing desired path differs | preflight diff | BLOCK | UNMANAGED_PATH_CONFLICT | 0 |
| same bytes, incompatible ownership | ownership compare | BLOCK | UNMANAGED_PATH_CONFLICT | 0 |
| GES managed drift | hash compare | BLOCK | MANAGED_CONTENT_MODIFIED | 0 |
| duplicate owner domain | resolver | BLOCK | CAPABILITY_OWNERSHIP_CONFLICT | 0 |
| Spec Kit unresolved runtime token | staged validation | BLOCK | SPEC_KIT_UNRESOLVED_TOKEN | 0 |
| Spec Kit runtime incomplete | runtime dependency validation | BLOCK | SPEC_KIT_RUNTIME_INCOMPLETE | 0 |
| post-install reconfiguration | requested set compare | BLOCK | RECONFIGURE_NOT_SUPPORTED | 0 |

---

# 16. Compatibility / Migration

## 16.1 GES v5

冻结：

```text
GES v5 migration = OUT OF SCOPE
```

用户负责：

```text
人工识别
人工删除
人工保留业务资产
```

GES 6：

```text
MUST NOT infer legacy ownership.
MUST NOT auto-delete legacy-looking paths.
```

## 16.2 Existing Spec Kit User State

当前可能存在：

```text
.specify/constitution.md
.specify/specs/**
```

GES：

```text
PRESERVE
REPORT
MUST NOT auto-migrate to .specify/memory/constitution.md
```

人工决定：

```text
迁移旧 constitution
OR
重新运行 speckit-constitution
```

---

# 17. External Dependency Contract

## Matt

```text
repo:
  https://github.com/mattpocock/skills.git
commit:
  959a8e9f1edc3adbe2f7e3054bb6fbefa6696260
usage:
  selected source paths only
```

## Spec Kit

```text
repo:
  https://github.com/github/spec-kit.git
commit:
  1d5106f59e1b148ee23ab136638932dd790ff1b6
expected CLI source version:
  1.0.8.dev0 at pinned source
usage:
  selected intent capabilities + required runtime only
```

## Superpowers

```text
repo:
  https://github.com/obra/superpowers.git
commit:
  b36e0829c6d0140e93cfef2ca599b1b07d4a7797
usage:
  selected execution skills only
```

## Cursor

```text
required Alpha.1 harness
project skill root:
  .agents/skills/**
```

所有 Git Source：

```text
MUST use immutable 40-char SHA.
```

---

# 18. Security Contract

| Threat | Control | Acceptance |
|---|---|---|
| Path traversal | contain repo-root | A-SEC-001 |
| Symlink source injection | reject unsafe selected source | A-SEC-002 |
| Unknown Brownfield overwrite | unmanaged collision BLOCK | A-COLLISION-001 |
| Business source modification | deny source roots | A-SEC-003 |
| Source cache tamper | content provenance | A-SEC-004 |
| Arbitrary post-install execution | GES MUST NOT run unknown hooks | A-SEC-005 |
| Spec Kit staging side effect leakage | staging outside consumer repo | A-SPECKIT-003 |
| Credential leakage | logs/evidence MUST NOT include secrets | A-SEC-006 |

---

# 19. Observability

Required stages：

```text
PREFLIGHT
ANALYZE
RESOLVE
FETCH
RENDER
PROJECT
COLLISION_CHECK
PLAN
APPLY
CHECK
DOCTOR
```

每次至少输出：

```text
operation_id
stage
status
timestamp
repo
ges_version
result
error_code
```

`ges init` completion report MUST 输出：

```text
GES install: PASS
ges check: PASS
Spec Kit runtime: PASS
Matt skills: INSTALLED
Matt project bootstrap: PENDING
Overall readiness: BOOTSTRAP_PENDING

Next required action:
  run setup-matt-pocock-skills
  then run ges doctor
```

---

# 20. Acceptance Design Standard

以下 Acceptance 均为 Alpha.1 REQUIRED，除非特别标记。

## A-BOOT-001 — Preflight Is Read-only

### Requirement Refs

```text
REQ-BOOT-001
REQ-DOCTOR-001
```

### Given

Clean Brownfield fixture。

### When

```bash
ges doctor . --preflight
```

### Oracle

```text
consumer_tree_before == consumer_tree_after
exit = 0 when prerequisites pass
```

### Evidence

```text
TEST-A-BOOT-001
pre_tree_digest
post_tree_digest
```

---

## A-CAP-001 — Exact Capability Exposure

### Given

Default Alpha.1 profile。

### When

resolve。

### Oracle

```text
selected set exactly matches this PRD
forbidden/non-selected capabilities absent
```

---

## A-CAP-002 — Dependency Closure

### Oracle

```text
grill-with-docs implies grilling + domain-modeling
Superpowers execution dependencies close successfully
0 duplicate owner conflict
```

---

## A-SPECKIT-001 — Existing `.specify` Does Not Skip Runtime

### Given

```text
.specify exists
scripts/templates may be empty
```

### When

`ges init` builds desired stage。

### Oracle

```text
required selected Spec Kit runtime exists in stage
```

---

## A-SPECKIT-002 — No Unresolved Runtime Tokens

### Oracle

Selected final Spec Kit executable artifacts：

```text
0 unresolved required {SCRIPT}
0 unresolved __SPECKIT_COMMAND_* tokens
0 unresolved required template resolver path
```

---

## A-SPECKIT-003 — Existing User Spec Data Preserved

### Given

existing：

```text
.specify/constitution.md
.specify/specs/**
```

### Oracle

```text
byte-identical after init
```

---

## A-SPECKIT-004 — Runtime Smoke

### Oracle

至少验证：

```text
speckit-constitution runtime dependency resolution PASS
speckit-specify runtime dependency resolution PASS
speckit-plan runtime dependency resolution PASS
```

不要求创建真实 feature。

---

## A-COLLISION-001 — Unknown Existing Different File Blocks

### Given

目标 skill path 已存在，内容不同，无 receipt。

### Then

```text
UNMANAGED_PATH_CONFLICT
0 mutation
```

---

## A-COLLISION-002 — Existing Identical Content Is Safe

### Given

目标文件已存在且 bytes 与 desired 完全一致。

### Then

```text
PRESERVE or ADOPT_IDENTICAL
no rewrite required
receipt ownership semantics explicit
```

---

## A-COLLISION-003 — Same Bytes / Different Ownership Blocks

### Oracle

```text
UNMANAGED_PATH_CONFLICT
```

---

## A-MATT-001 — Matt Setup Installed, Not Auto-run

### Oracle

```text
setup-matt-pocock-skills exists
docs/agents is not fabricated automatically
status = BOOTSTRAP_PENDING
```

---

## A-MATT-002 — Matt Bootstrap Becomes Ready

### Given

用户完成 setup skill。

### When

```bash
ges doctor .
```

### Oracle

```text
matt_project_bootstrap = PASS
```

---

## A-ROUTE-001 — AGENTS Routing Exact

### Oracle

GES marker 内存在本 PRD冻结的 Owner → Skill routing。

---

## A-ROUTE-002 — Outside AGENTS Bytes Preserved

测试矩阵必须覆盖：

```text
existing file with trailing newline
existing file without trailing newline
existing marker absent
```

Oracle：

```text
outside-marker semantic/user bytes preserved
```

如为了 marker boundary 必须插入分隔换行，则：

```text
必须通过 section ownership 设计使该分隔符属于 managed section，
不得偷偷改变 user-owned outside bytes。
```

---

## A-CURSOR-001 — Cursor Skill Discovery Smoke

真实 `smc-copilot`：

```text
Matt selected skill discoverable
Spec Kit selected wrapper discoverable
Superpowers selected skill discoverable
```

状态：

```text
PASS
```

---

## A-CHECK-001 — Project/Schema

```text
all state schemas valid
```

## A-CHECK-002 — Desired Closure Equals Lock

```text
recomputed closure == lock closure
```

## A-CHECK-003 — Source SHA

```text
lock source SHA == current catalog pin
```

## A-CHECK-004 — Source Provenance

```text
available cache provenance valid
```

## A-CHECK-005 — Managed File Identity

```text
all FILE exact
```

## A-CHECK-006 — Managed Section Identity

```text
AGENTS marker exact
```

## A-CHECK-007 — Selected Projection Exists

```text
all selected skills/runtime exist
```

## A-CHECK-008 — Spec Kit Runtime Exists

```text
all required runtime artifacts present
```

## A-CHECK-009 — Business Source Guard

```text
0 business source bytes changed
```

## A-CHECK-010 — Recompose NOOP

```text
compose current frozen desired state
→ plan.noop == true
```

---

## A-DOCTOR-001 — Preflight

```text
Python/runtime/git/Cursor prerequisites observable
0 mutation
```

## A-DOCTOR-002 — Bootstrap Pending

Matt setup 未完成：

```text
overall = BOOTSTRAP_PENDING
exit = 0
```

`BOOTSTRAP_PENDING` 是已知可恢复状态，不等价于 Release Ready。

## A-DOCTOR-003 — Ready

完成 Matt setup 后：

```text
all required doctor checks PASS
overall = READY
```

---

## A-TXN-001 — Failure Before Commit

```text
consumer tree unchanged
```

## A-TXN-002 — Failure After First/Nth Write

```text
rollback tree == T0
```

## A-TXN-003 — Post-check Failure

```text
rollback tree == T0
```

## A-TXN-004 — Rollback Failure

```text
TRANSACTION_ROLLBACK_FAILED
backup path exists after process returns
manual recovery data usable
exit != 0
```

---

## A-IDEMP-001 — Second Init NOOP

真实 Golden Consumer：

```text
second ges init
→ GES_RECONCILE_NOOP
→ 0 file content changes
→ 0 duplicate markers
```

---

## A-STATE-001 — Reconfiguration Blocked

改变 requested set：

```text
RECONFIGURE_NOT_SUPPORTED
0 mutation
```

---

## A-PKG-001 — Version Identity

```text
installed distribution identity
ges --version
receipt.ges_version
evidence.ges_version
```

符合冻结的版本策略。

---

# 21. Acceptance Input Matrix

| Case | Existing AGENTS | Existing `.agents/skills` | Existing `.specify` | GES Receipt | Expected |
|---|---|---|---|---|---|
| B1 | YES | YES custom | YES incomplete runtime | NO | safe bootstrap |
| B2 | YES no trailing newline | YES custom | YES | NO | preserve user bytes |
| B3 | YES | selected target absent | YES | NO | ADD |
| B4 | YES | selected target identical | YES | NO | ADOPT/PRESERVE |
| B5 | YES | selected target different | YES | NO | BLOCK |
| B6 | YES | GES-owned exact | YES | YES | NOOP |
| B7 | YES | GES-owned drift | YES | YES | check FAIL |
| B8 | YES | normal | `.specify` absent | NO | install selected Spec Kit runtime |
| B9 | YES | normal | `.specify` exists but runtime empty | NO | still install required runtime |
| B10 | YES | normal | user `.specify/specs` present | NO | preserve byte-identical |
| B11 | YES | normal | user `.specify/constitution.md` present | NO | preserve + report |
| B12 | YES | normal | normal | installed | requested set changed | RECONFIGURE_NOT_SUPPORTED |

---

# 22. Negative Acceptance

必须至少包括：

```text
NEG-001 unknown skill collision
→ UNMANAGED_PATH_CONFLICT

NEG-002 source cache tamper
→ SOURCE_CACHE_INTEGRITY_FAILED

NEG-003 unresolved Spec Kit token
→ SPEC_KIT_UNRESOLVED_TOKEN

NEG-004 missing Spec Kit runtime dependency
→ SPEC_KIT_RUNTIME_INCOMPLETE

NEG-005 business source write attempt
→ BUSINESS_SOURCE_MODIFICATION_FORBIDDEN

NEG-006 changed bootstrap capability set
→ RECONFIGURE_NOT_SUPPORTED

NEG-007 managed drift
→ GES_CHECK_FAILED / MANAGED_CONTENT_MODIFIED
```

---

# 23. Failure Injection

事务测试至少：

```text
FI-001 before_commit
FI-002 after_first_write
FI-003 after_nth_write
FI-004 before_receipt
FI-005 post_check
FI-006 rollback_write_failure
```

每一个 failure point 必须有明确 postcondition。

---

# 24. Evidence Contract

## 24.1 Evidence Artifact

真实 Golden Bootstrap：

```text
audit/ges6/bootstrap/<timestamp>.json
```

至少：

```json
{
  "schema": "ges.bootstrap-evidence.v1",
  "ges_version": "6.0.0-alpha.1",
  "ges_commit": "<sha>",
  "consumer_repo": "loudon84/smc-copilot",
  "consumer_commit": "<sha>",
  "branch": "work/prd-v5.1",
  "results": [
    {
      "acceptance_id": "A-SPECKIT-004",
      "requirement_ids": ["REQ-SPECKIT-001"],
      "test_ids": ["TEST-A-SPECKIT-004"],
      "status": "PASS",
      "command": "...",
      "exit_code": 0,
      "oracle": {
        "expected": "runtime smoke pass",
        "actual": "runtime smoke pass"
      },
      "evidence_files": []
    }
  ]
}
```

## 24.2 Evidence Integrity

必须绑定：

```text
GES commit
Consumer commit
branch
command
exit code
timestamp
test id
oracle
```

禁止：

```json
{"A01": "PASS"}
```

作为唯一证据。

---

# 25. Release Gate

状态：

```text
PASS
FAIL
SKIPPED
BLOCKED
```

Alpha.1 Bootstrap REQUIRED Acceptance 任一：

```text
!= PASS
```

则：

```text
BOOTSTRAP_RELEASE_GATE = FAIL
acceptance runner process exit != 0
```

唯一例外：

`A-DOCTOR-002 BOOTSTRAP_PENDING` 是 install 后正常中间状态，不代表 Release Gate PASS。

最终 Golden Consumer Gate 必须达到：

```text
ges check PASS
Matt setup completed
ges doctor READY
Cursor discovery PASS
second init NOOP
business source unchanged
all required acceptance PASS
```

---

# 26. Golden Consumer / Real-world Acceptance

## 26.1 Golden Consumer

```text
repo:
  loudon84/smc-copilot

branch:
  work/prd-v5.1
```

## 26.2 Manual Baseline Preconditions

人工完成：

```text
1. 删除已确认的 GES v5 残留
2. 保留业务源码
3. 保留业务 AGENTS
4. 保留仍需使用的自定义 Skills
5. 保留/人工评估现有 .specify 内容
6. 工作树进入可记录 baseline
```

## 26.3 Golden Bootstrap Flow

```text
git record HEAD
↓
snapshot business/user-owned content
↓
ges doctor --preflight
↓
ges init preview
↓
confirm
↓
transactional install
↓
ges check
↓
assert BOOTSTRAP_PENDING
↓
run setup-matt-pocock-skills
↓
ges doctor
↓
assert READY
↓
Cursor skill discovery smoke
↓
second ges init
↓
assert GES_RECONCILE_NOOP
↓
compare business/user-owned snapshot
↓
write bootstrap evidence
```

## 26.4 Required Oracle

```text
business source digest unchanged
user-owned custom skills unchanged
outside AGENTS managed section preserved
existing .specify user data preserved
selected Matt skills present
selected Spec Kit runtime usable
selected Superpowers skills present
doctor READY
second init NOOP
```

---

# 27. Requirement Traceability Matrix

| Requirement | Invariant | Acceptance | Release Gate |
|---|---|---|---|
| REQ-BOOT-001 | Clean Brownfield only | A-BOOT-001 | REQUIRED |
| REQ-CAP-001 | fixed selected stack | A-CAP-001, A-CAP-002 | REQUIRED |
| REQ-SPECKIT-001 | executable runtime | A-SPECKIT-001..004 | REQUIRED |
| REQ-COLLISION-001 | no unknown overwrite | A-COLLISION-001..003 | REQUIRED |
| REQ-MATT-001 | installed != bootstrapped | A-MATT-001..002 | REQUIRED |
| REQ-ROUTE-001 | deterministic routing | A-ROUTE-001..002 | REQUIRED |
| REQ-CURSOR-001 | real discovery | A-CURSOR-001 | REQUIRED |
| REQ-CHECK-001 | materialized correctness | A-CHECK-001..010 | REQUIRED |
| REQ-DOCTOR-001 | runtime readiness | A-DOCTOR-001..003 | REQUIRED |
| REQ-TXN-001 | rollback to T0 | A-TXN-001..004 | REQUIRED |
| REQ-IDEMP-001 | second init NOOP | A-IDEMP-001 | REQUIRED |
| REQ-STATE-001 | no reconfigure | A-STATE-001 | REQUIRED |
| REQ-PKG-001 | version identity | A-PKG-001 | REQUIRED |

Plan MUST 为每个 Acceptance 创建 Test ID 与 Evidence target。

---

# 28. Plan Generation Contract

只有本 PRD：

```text
status = APPROVED_FOR_PLAN
```

且以下全部满足时才允许创建 `.plan.md`：

```text
[ ] Spec Kit Runtime 实现路径唯一
[ ] no GES v5 migration
[ ] no capability reconfigure
[ ] Cursor 是唯一 Alpha.1 REQUIRED harness
[ ] unmanaged collision 规则冻结
[ ] Matt setup 不自动执行
[ ] check / doctor 职责冻结
[ ] Golden Bootstrap 流程冻结
```

Plan MUST NOT 重新讨论：

```text
是否把 tasks/implement/converge 装回来
是否自动迁移 v5
是否自动运行 Matt setup
是否默认支持 remove/reconfigure
```

这些均已超出 Alpha.1 Scope。

---

# 29. `.plan.md` 输出标准

每个 Todo：

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

建议 Plan 至少拆成：

```text
P0 Bootstrap Scope Cleanup
P1 Spec Kit Runtime Renderer
P2 Unmanaged Collision
P3 Deterministic Routing
P4 Check Hardening
P5 Doctor
P6 Transaction Failure Closure
P7 Version Identity
P8 Synthetic Acceptance
P9 Golden Consumer Bootstrap
```

---

# 30. Code Review Contract

Review 顺序：

```text
1. 是否仍混入 GES v5 migration
2. Spec Kit 是否真实可执行，而非只有文件
3. 是否会覆盖 unknown user-owned path
4. 是否区分 Installed / Bootstrap Pending / Ready
5. AGENTS routing 是否确定
6. check 是否验证 SOT/Lock/Projection
7. doctor 是否验证 Runtime
8. transaction failure 是否回 T0
9. Golden Bootstrap 是否真实执行
10. Evidence 是否逐 Acceptance
11. 最后才是普通代码质量
```

---

# 31. PRD Quality Gate

## Architecture

```text
[x] Goal 唯一明确
[x] Scope / Non-goal 完整
[x] Owner 不重叠
[x] System Boundary 明确
```

## State

```text
[x] Desired / Observed / Applied / Readiness 分离
[x] project.yaml SOT 明确
[x] Bootstrap 状态机明确
```

## Semantics

```text
[x] capability set 明确
[x] Spec Kit runtime 明确
[x] Matt installed/ready 明确
[x] unmanaged collision 明确
[x] routing 明确
```

## Side Effects

```text
[x] preflight/check/doctor read-only
[x] init write scope 明确
[x] business source 禁写
```

## Failure

```text
[x] collision error 明确
[x] runtime error 明确
[x] rollback postcondition 明确
[x] rollback failure backup retention 明确
```

## Acceptance

```text
[x] 每个 MUST 有 AC
[x] Negative AC 已定义
[x] Failure Injection 已定义
[x] Input Matrix 已定义
[x] Oracle 可机器判断
```

## Evidence

```text
[x] Golden evidence schema 定义
[x] bind commit / test / oracle
[x] BLOCKED/SKIPPED 不算 PASS
[x] Release Gate 非 PASS → non-zero
```

## Plan Readiness

```text
[x] 无已知 SPEC_SEMANTIC_GAP
[x] Traceability 完整
[x] status = APPROVED_FOR_PLAN
```

---

# 32. PRD 禁止写法

本项目后续 Plan/Code Review 禁止使用：

```text
Spec Kit 已安装
```

如果只证明 Skill 文件存在。

必须改成：

```text
Spec Kit runtime dependency closure verified.
```

禁止：

```text
Matt Ready
```

如果只安装 setup skill。

禁止：

```text
safe update
```

而不说明 collision/ownership。

禁止：

```text
check passed
```

而不说明 A-CHECK 哪些 Oracle PASS。

禁止：

```text
Golden Consumer tested
```

如果没有真实 smc-copilot commit-bound Evidence。

---

# 33. ID 体系

```text
REQ-BOOT-xxx
REQ-CAP-xxx
REQ-SPECKIT-xxx
REQ-COLLISION-xxx
REQ-MATT-xxx
REQ-ROUTE-xxx
REQ-CURSOR-xxx
REQ-CHECK-xxx
REQ-DOCTOR-xxx
REQ-TXN-xxx
REQ-IDEMP-xxx
REQ-STATE-xxx
REQ-PKG-xxx

A-BOOT-xxx
A-CAP-xxx
A-SPECKIT-xxx
A-COLLISION-xxx
A-MATT-xxx
A-ROUTE-xxx
A-CURSOR-xxx
A-CHECK-xxx
A-DOCTOR-xxx
A-TXN-xxx
A-IDEMP-xxx
A-STATE-xxx
A-PKG-xxx
```

---

# 34. PRD 最小交付结构检查

本 PRD 已覆盖：

```text
Goal
Background
Scope
Architecture Boundary
Terminology
State / SOT
State Machine
Schema
Requirements
Side Effects
Ownership
Identity / Hash
Transaction
Failure
Conflict
Migration
Security
Observability
Acceptance
Edge-case Matrix
Negative Acceptance
Failure Injection
Evidence
Traceability
Release Gate
Plan Generation Gate
DoD
```

---

# 35. Definition of Done

GES 6.0-alpha.1 Bootstrap 只有满足以下条件才可标记：

```text
BOOTSTRAP_ALPHA_READY
```

必须：

```text
[ ] 已移除 v5 migration/cleanup 对 Alpha.1 Gate 的依赖
[ ] Spec Kit selected runtime 能在 existing .specify 场景安装
[ ] Spec Kit final runtime 无未解析 required token
[ ] Spec Kit user data 保持
[ ] Matt selected skills 正确安装
[ ] Matt setup 不自动执行
[ ] Matt bootstrap 后 doctor 能转 READY
[ ] Superpowers selected skills 正确安装
[ ] AGENTS Owner → Skill routing 确定
[ ] unknown existing path 冲突会 BLOCK
[ ] no unknown user-owned overwrite
[ ] check A-CHECK-001..010 PASS
[ ] doctor readiness PASS
[ ] transaction failure rollback to T0
[ ] rollback failure backup retained
[ ] GES version identity 一致
[ ] smc-copilot Golden Bootstrap PASS
[ ] Cursor discovery smoke PASS
[ ] second ges init = GES_RECONCILE_NOOP
[ ] business source 0 bytes changed
[ ] user-owned content preserved
[ ] Evidence 绑定 GES commit + smc-copilot commit
```

---

# 36. 最终原则

```text
1. Alpha.1 首先解决“真实能装、真实能用”，不解决完整生命周期。
2. GES v5 清理由人完成，不再污染 GES 6 Bootstrap 范围。
3. Brownfield 首装安全与 Legacy migration 是两件不同的事。
4. 已存在目录不能被当成 Runtime 已完整安装的证据。
5. Spec Kit 必须安装 selected Intent Runtime，而不是只复制 raw command 文件。
6. Matt Skill installed 不等于 Matt project bootstrap complete。
7. Superpowers 只安装 selected execution methodology skills。
8. Cursor 通过 .agents/skills 消费共享 Skills；pointer 不是 activation。
9. AGENTS 必须把工程阶段映射到具体 Skill，不能只写 provider 名称。
10. 首装不能覆盖无 Receipt ownership 的未知文件。
11. ges check 证明 materialized state；ges doctor 证明 runtime readiness。
12. BOOTSTRAP_PENDING 是合法中间状态，不等于 READY。
13. Alpha.1 安装后 capability set 冻结；reconfiguration 延后。
14. second init NOOP 是首装稳定性的硬门禁。
15. Golden Consumer 必须是真实 smc-copilot，不得由 synthetic fixture 替代。
16. Evidence 必须证明 Acceptance，而不是只声明 PASS。
17. 只有 Golden Bootstrap 全链闭合，GES 6.0-alpha.1 Bootstrap 才算完成。
