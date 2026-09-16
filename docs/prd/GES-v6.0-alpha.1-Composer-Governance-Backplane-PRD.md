---
title: "GES 6.0-alpha.1 — Composer Bootstrap PRD"
subtitle: "Composer + Governance Backplane Architecture Baseline"
status: "DRAFT_FOR_IMPLEMENTATION"
product_line: "GES 6"
release: "6.0.0-alpha.1"
change_type: "ARCHITECTURE_RESET"
repository: "smc-delivery-governance"
golden_consumer: "smc-copilot"
---

# GES 6.0-alpha.1 — Composer Bootstrap PRD

## 0. 文档目的

本 PRD 是 GES 6.0 架构断代后的第一份工程实施基线，承担两个职责：

1. 完整冻结 GES 6.0 的产品定义、系统边界、总体架构和长期演进方向，避免后续 Alpha/Beta 再把 GES 演化为 PRD Engine、Plan Engine、Context Engine、Execution Engine 或 Agent Runtime。
2. 定义 GES 6.0-alpha.1 的可实施范围：优先完成面向业务仓库的 Composer Bootstrap，让 `smc-copilot` 在删除 GES v5 治理工程包后，可以通过新的 `ges` CLI 分析仓库、解析需要的能力、引入 Matt Pocock Skills / Spec Kit / Superpowers 的最小能力集合，并以可重入、可升级、可撤销的方式管理这些投影。

`6.0-alpha.1` 的目标是先建立：

```text
Repo Analyze
→ Capability Resolve
→ Source Resolve
→ Harness Projection
→ Reconcile / Check
```

为后续：

```text
Policy
Risk
Ownership
Evidence
Approval
Delivery
Release
Audit
```

提供稳定、低耦合、可追溯的业务项目接入基础。

# Part I — GES 6.0 产品定义与完整架构基线

## 1. GES 6.0 产品定位

GES 6.0 的产品定位冻结为：

> **Composer + Governance Backplane for AI-assisted software delivery**

中文定义：

> **GES 6 是面向人与 AI Agent 协同研发的软件工程能力组合器与治理底座。GES 负责根据业务仓库实际情况组合 AI Engineering 能力，并基于 Artifact / Evidence / Policy / Approval / Release Truth 对交付结果进行治理；GES 不接管需求分析、Spec 生产、实现计划、代码生成、TDD、Debug、Review 推理和模型运行时。**

GES 6 从：

```text
Process-centric Governance
```

迁移为：

```text
Outcome-centric Governance
```

GES 不再试图证明：

```text
Agent 是如何思考的
Agent 是否读取了“正确”的上下文
Agent 是否按照 GES 自己规定的步骤推理
```

GES 只需要证明：

```text
变更是什么
对应哪个 Intent / Spec / Ticket
风险是什么
谁负责
需要哪些 Evidence
Evidence 是否真实存在
谁已经批准
目标 Commit / PR / Build / Release 是什么
是否具备交付条件
```

## 2. GES 6 不再拥有的能力

以下能力明确不属于 GES 6 Core：

```text
PRD Author
PRD Grounding
PRD Converge
Implementation Plan Author
Implementation Plan Review
TDD Runtime
Debug Runtime
Code Review Reasoning
LLM Context Engine
LLM Model Dispatch
LLM Token Budget Runtime
LLM Usage Accounting
Agent Worker Runtime
Repository-wide semantic execution context
AI Coding Methodology
```

GES 可以引用这些系统产生的 Artifact / Event / Evidence，但不得重新实现这些能力、复制正文或成为这些能力的执行 Owner。

## 3. AI Engineering Stack Owner 冻结

```text
Matt Pocock Skills
= Engineering Disciplines

Spec Kit
= Intent SOT

Superpowers
= Execution Methodology

GES
= Composer + Governance Backplane
```

### 3.1 Matt Pocock Skills

负责：

```text
需求深挖
领域语言
Domain Modeling
Codebase Design
Tracer Bullet decomposition
Engineering writing discipline
```

典型能力：

```text
grill-with-docs
grilling
domain-modeling
codebase-design
to-tickets
```

### 3.2 Spec Kit

负责：

```text
WHAT / WHY
Feature Intent
Specification
Clarification
Technical direction
```

在 GES 6 推荐组合中，默认 Owner：

```text
constitution
specify
clarify
plan
```

### 3.3 Superpowers

负责：

```text
Implementation planning
Worktree
Fresh subagent execution
TDD
Systematic debugging
Code review
Verification
Branch finishing
```

### 3.4 GES

负责：

```text
能力组合
版本锁定
投影管理
Policy
Risk
Ownership
Evidence
Approval
Traceability
Delivery
Release
Audit
```

## 4. 单一 Owner 原则

同一个工程阶段只允许一个 Owner。

禁止：

```text
Matt to-spec + Spec Kit specify
Spec Kit implement + Superpowers execution
Matt tdd + Superpowers TDD + GES TDD runtime
```

因此 GES 6 Composer 必须把：

```text
capability dependency
capability ownership
capability conflict
```

作为一等公民进行解析。

## 5. GES 6 完整生命周期架构

```text
                    Human / Product
                          │
                          ▼
                 Matt Pocock Skills
          grill / domain-modeling / codebase-design
                          │
                          ▼
                       Spec Kit
                 specify / clarify / plan
                          │
                          ▼
              ┌──────────────────────┐
              │ Large Feature only   │
              │ Matt: to-tickets     │
              │ Tracer Bullets       │
              └──────────┬───────────┘
                         │
                         ▼
                    Superpowers
                 per-ticket plan
                         │
                         ▼
               fresh task/subagent
                         │
                TDD / debug / review
                         │
                         ▼
                      Git / CI
                         │
            ┌────────────┴─────────────┐
            │                          │
            ▼                          ▼
         Evidence                   Metadata
     test/review/build       spec/ticket/commit/PR
            │                          │
            └────────────┬─────────────┘
                         ▼
                    GES Backplane
       Policy / Risk / Ownership / Approval
          Evidence / Audit / Release Truth
                         │
                         ▼
                   DELIVERY_READY
```

GES 不站在 Agent 推理链中间，而位于 Development Plane 旁侧和交付边界。

## 6. GES 6 两大产品面

GES 6 由两个正交子系统组成：

```text
GES Composer
+
GES Governance Backplane
```

### 6.1 GES Composer

职责：

```text
分析业务仓库
识别 Harness / Agent
识别已有工具与配置
解析需要的 Engineering Capability
锁定上游版本
投影所需 Skill / Runtime / Adapter
管理升级
管理撤销
```

### 6.2 Governance Backplane

职责：

```text
Work Registry
Artifact Registry
Policy
Risk
Ownership
Evidence
Approval
Delivery
Release
Audit
```

Composer 解决“业务项目应该具备哪些 AI Engineering 能力，以及如何可靠安装”；Backplane 解决“业务项目产生的交付物是否具备企业级交付资格”。

## 7. GES 6 Core Domain Model

```text
Work
Artifact
Evidence
Policy
Risk
Ownership
Approval
Release
```

关系：

```text
Work
 │
 ├── references → Artifact
 ├── classified-by → Risk
 ├── governed-by → Policy
 ├── owned-by → Ownership
 ├── requires → Evidence
 ├── requires → Approval
 └── produces → Release
```

Artifact 采用：

```text
pointer
identity
digest
status
timestamp
```

而不是正文复制。

## 8. Governance Backplane 完整目标模块

```text
01 Registry
02 Policy
03 Risk
04 Ownership
05 Evidence
06 Approval
07 Traceability
08 Delivery
09 Release
10 Audit
```

Alpha.1 不要求实现上述全部运行能力，但所有 Alpha 设计必须兼容该长期模型。

## 9. GES 6 推荐 Gate 模型

完整 GES 6 最终只强调三个治理边界：

```text
Gate A — Work Intake
Gate B — Merge Readiness
Gate C — Release Readiness
```

GES 不在每一个 Agent Turn 上设 Gate。

## 10. GES 6 仓库新代码结构

```text
smc-delivery-governance/
│
├── ges/
│   ├── cli/
│   │   ├── init
│   │   ├── analyze
│   │   ├── diff
│   │   ├── apply
│   │   ├── check
│   │   ├── remove
│   │   └── legacy
│   ├── analyzer/
│   ├── resolver/
│   ├── catalog/
│   │   ├── capabilities.yaml
│   │   ├── sources.yaml
│   │   ├── conflicts.yaml
│   │   └── profiles/
│   ├── source_adapters/
│   │   ├── matt.*
│   │   ├── speckit.*
│   │   └── superpowers.*
│   ├── harness_adapters/
│   │   ├── cursor.*
│   │   ├── codex.*
│   │   └── hermes.*
│   ├── reconciler/
│   ├── schemas/
│   └── governance/
│       ├── registry/
│       ├── policy/
│       ├── risk/
│       ├── ownership/
│       ├── evidence/
│       ├── approval/
│       ├── delivery/
│       └── release/
├── legacy/
│   └── v5/
└── tests/
```

# Part II — GES 6.0-alpha.1 产品范围

## 11. Alpha.1 产品目标

> **让一个已有 Brownfield 业务仓库，在不复制 GES Runtime、不污染业务源码、不覆盖用户配置的前提下，通过 GES Composer 获取经过解析的 Matt / Spec Kit / Superpowers 最小能力集合，并支持版本锁定、幂等更新和完全撤销。**

Golden Consumer：

```text
loudon84/smc-copilot
```

目标命令：

```bash
ges init smc-copilot
```

或：

```bash
cd smc-copilot
ges init .
```

## 12. Alpha.1 负责的五件事

```text
A. Repo Analyze
B. Capability Resolve
C. Source Resolve
D. Harness Projection
E. Reconcile / Check
```


## 13. A — Repo Analyze

### 13.1 目标

对目标仓库做 deterministic inspection，建立 `Repo Profile`，不调用 LLM。

安装分析阶段要求：

```text
LLM token usage = 0
```

### 13.2 必须识别

```text
Brownfield / Greenfield
single repo / monorepo
languages
package managers
primary frameworks
existing AGENTS.md / CLAUDE.md
existing .agents
existing .cursor
existing .codex
existing .specify
existing .smc
Git repository
Git remote
GitHub Actions
test/build/lint scripts
CONTEXT.md / CONTEXT-MAP.md
docs/adr
legacy GES v5 markers / receipts / known paths
```

### 13.3 `smc-copilot` 必须识别

```text
Repository type:
  Brownfield monorepo

Detected agents:
  Cursor
  Codex

Detected:
  AGENTS.md
  .agents/
  .cursor/
  .codex/
  .specify/
  .smc/
```

### 13.4 输出 Schema

```json
{
  "schema": "ges.repo-profile.v1",
  "repository_kind": "brownfield-monorepo",
  "agents": ["cursor", "codex"],
  "languages": ["typescript"],
  "spec_kit": true,
  "legacy_ges": true,
  "ci": ["github-actions"]
}
```

## 14. B — Capability Resolve

Repo Profile + Product Profile + User Selection：

```text
→ Resolved Capability Graph
```

GES 不安装“三个完整产品”，只安装：

```text
resolved capability closure
```

### 14.1 Capability Catalog

Alpha.1 必须引入：

```text
ges/catalog/capabilities.yaml
```

每个 capability 至少声明：

```yaml
id:
source:
source_path:
owner_domain:
requires:
conflicts:
supported_harnesses:
projection_type:
default_profiles:
```

### 14.2 Ownership Conflict

至少检测：

```text
matt.to-spec vs speckit.specify
matt.implement vs superpowers.execution
speckit.implement vs superpowers.execution
superpowers.brainstorming vs matt.grill-with-docs
```

冲突时输出：

```text
CAPABILITY_OWNERSHIP_CONFLICT
```

并 BLOCK Apply。

### 14.3 Dependency Closure

选择：

```text
matt.grill-with-docs
```

必须自动补齐：

```text
matt.grilling
matt.domain-modeling
```

## 15. Alpha.1 默认能力组合

Profile：

```text
brownfield-product-app
```

### Matt

```text
matt.setup
matt.grill-with-docs
matt.grilling
matt.domain-modeling
matt.codebase-design
matt.to-tickets
```

默认不引入：

```text
matt.to-spec
matt.implement
matt.tdd
matt.diagnosing-bugs
matt.code-review
```

### Spec Kit

```text
speckit.constitution
speckit.specify
speckit.clarify
speckit.plan
```

默认不启用：

```text
speckit.tasks
speckit.implement
speckit.converge
```

### Superpowers

```text
superpowers.using-git-worktrees
superpowers.writing-plans
superpowers.subagent-driven-development
superpowers.test-driven-development
superpowers.systematic-debugging
superpowers.requesting-code-review
superpowers.receiving-code-review
superpowers.verification-before-completion
superpowers.finishing-a-development-branch
```

可选：

```text
superpowers.executing-plans
```

默认不引入：

```text
superpowers.brainstorming
superpowers.using-superpowers
```

## 16. 用户可取消 capability

`ges init` 必须在 Apply 前展示 Recommended Capability Set。

用户可以取消 optional capability，但取消后必须重新进行：

```text
dependency validation
ownership validation
```

## 17. C — Source Resolve

对选中的能力解析：

```text
upstream source
version
commit SHA
source path
content identity
```

Alpha.1 上游 Source：

```text
mattpocock/skills
github/spec-kit
obra/superpowers
```

必须锁定 immutable commit SHA。

### 17.1 本地 Source Cache

```text
~/.cache/ges/sources/
├── mattpocock-skills/<sha>/
├── spec-kit/<sha>/
└── superpowers/<sha>/
```

业务仓库不保存完整上游源码。

### 17.2 Lock File

业务仓库保存：

```text
.ges/lock.json
```

记录：

```text
GES version
source repo
source commit SHA
resolved capabilities
content identity
```

## 18. Spec Kit 特殊规则

Spec Kit 需区分：

```text
Spec Kit shared project runtime
vs
Spec Kit exposed capabilities
```

原则：

```text
安装 Spec Kit 必需 runtime
只暴露 selected Intent capabilities
```

对于已有 `.specify/` 的 Brownfield 项目，不得无条件覆盖。

推荐：

```text
Pinned Spec Kit SHA
→ 临时目录 materialize
→ 形成 desired projection
→ 与 Consumer 当前文件 diff
→ 只写 managed path / managed section
```

`smc-copilot` 已存在 `.specify/`，因此必须采用：

```text
adopt / reconcile
```

而不是：

```text
reinitialize / overwrite
```

## 19. D — Harness Projection

Alpha.1 至少支持：

```text
Cursor
Codex
```

Hermes 保留 Adapter interface，实施可延后。

### 19.1 两类 Adapter

```text
Source Adapter:
  MattAdapter
  SpecKitAdapter
  SuperpowersAdapter

Harness Adapter:
  CursorAdapter
  CodexAdapter
  HermesAdapter
```

禁止写成 N×M 硬编码 installer。

## 20. Cursor Projection

必须识别并保护：

```text
.cursor/
AGENTS.md
.agents/
```

优先共享：

```text
.agents/skills/<skill>/
```

Cursor-specific 内容只能写：

```text
GES-managed file
或
GES-managed marker section
```

## 21. Codex Projection

必须识别：

```text
.codex/
AGENTS.md
.agents/
```

可共享的 Skill 优先放：

```text
.agents/skills/
```

只有 Codex-specific integration 才写 `.codex/*`。

## 22. AGENTS.md 管理规则

必须满足：

```text
不覆盖现有 AGENTS.md
```

采用 marker：

```markdown
<!-- ges:v6:engineering-stack:begin -->

## AI Engineering Stack

Requirement clarification and domain modeling:
use Matt Pocock engineering skills.

Feature specification and technical intent:
use Spec Kit.

Implementation planning, TDD, debugging and code review:
use the installed Superpowers execution skills.

GES manages composition and governance metadata.
GES does not generate Specs, implementation plans or code.

<!-- ges:v6:engineering-stack:end -->
```

规则：

```text
不存在 marker:
  append block

存在 marker 且未被用户修改:
  safe replace

存在 marker 且被用户修改:
  report conflict / require confirmation

marker 外内容:
  永不修改
```

## 23. 业务源码保护

Alpha.1 必须满足：

```text
业务源码 0 bytes modified
```

Composer 默认只允许写：

```text
.ges/**
.agents/skills/**
.specify/**        # managed/reconciled paths only
.cursor/**         # managed paths/sections only
.codex/**          # managed paths/sections only
AGENTS.md          # marker section only
.gitignore         # managed entry only when necessary
```

默认禁止修改：

```text
apps/**
services/**
src/**
packages/**
contracts/**
```

错误：

```text
BUSINESS_SOURCE_MODIFICATION_FORBIDDEN
```

## 24. E — Reconcile / Check

GES 安装采用：

```text
Desired State
vs
Current State
```

支持：

```text
Diff
Apply
Check
Remove
```

## 25. Project Desired State

业务仓库保存：

```text
.ges/project.yaml
```

示例：

```yaml
schema: ges.project.v1

profile: brownfield-product-app

agents:
  - cursor
  - codex

engineering_stack:
  disciplines:
    provider: matt
  intent:
    provider: spec-kit
  execution:
    provider: superpowers

resolution:
  mode: auto
```

## 26. Install Receipt

保存：

```text
.ges/install-receipt.json
```

至少记录：

```text
installed_at
ges_version
repo_identity
managed_files
managed_sections
content_hashes
source_commits
capability_set
```

## 27. 幂等要求

连续执行：

```bash
ges apply
ges apply
```

第二次必须：

```text
NOOP
0 content change
0 duplicate marker
0 duplicate skill
```

输出：

```text
GES_RECONCILE_NOOP
```

## 28. 更新规则

`ges diff` 输出：

```text
ADD
UPDATE
REMOVE
PRESERVE
CONFLICT
```

更新只允许修改 GES-managed content。

## 29. Managed Content Hash

保存：

```text
generated content hash
last-applied hash
upstream source SHA
```

更新规则：

```text
current == last-applied
→ safe update

current != last-applied
→ MANAGED_CONTENT_MODIFIED
```

## 30. ges remove

必须支持：

```bash
ges remove .
```

目标：

```text
完全撤销 GES-owned projection
```

删除：

```text
GES 添加的 Skill
GES marker section
GES-only integration file
GES lock / receipt
```

保留：

```text
用户原有 .specify
用户原有 AGENTS.md 内容
用户原有 .cursor 内容
用户原有 .codex 内容
业务源码
第三方但非 GES-owned 的 Skill
```

## 31. Legacy GES v5 Detection

Alpha.1 必须识别并报告 legacy GES v5，不默认删除。

建议命令：

```text
ges legacy inspect .
ges legacy remove . --dry-run
ges legacy remove . --apply
```

无法证明 ownership：

```text
PRESERVE + REPORT
```

## 32. Alpha.1 CLI

```text
ges init [repo]
ges analyze [repo]
ges diff [repo]
ges apply [repo]
ges check [repo]
ges remove [repo]
ges legacy inspect [repo]
ges legacy remove [repo] --dry-run/--apply
```


## 33. `ges init` 推荐交互

```text
$ ges init .

Repository analysis
-------------------

Repository:
  Brownfield monorepo

Detected agents:
  Cursor
  Codex

Existing:
  AGENTS.md        YES
  .agents/         YES
  .cursor/         YES
  .codex/          YES
  .specify/        YES
  Legacy GES v5    YES

Recommended engineering composition
------------------------------------

Matt:
  + grill-with-docs
  + grilling
  + domain-modeling
  + codebase-design
  + to-tickets

Spec Kit:
  + constitution
  + specify
  + clarify
  + plan

Superpowers:
  + using-git-worktrees
  + writing-plans
  + subagent-driven-development
  + test-driven-development
  + systematic-debugging
  + requesting-code-review
  + receiving-code-review
  + verification-before-completion
  + finishing-a-development-branch

Excluded due to ownership overlap:
  - matt.to-spec
  - matt.implement
  - matt.tdd
  - superpowers.brainstorming
  - superpowers.using-superpowers
  - speckit.tasks
  - speckit.implement
  - speckit.converge

Legacy GES v5 detected.
No legacy files will be removed automatically.

Apply this composition? [Y/n]
```

## 34. Preview-first 原则

任何写入前必须形成 Install Plan，至少包含：

```text
files to create
files to update
managed sections to add
skills to add
skills to remove
source SHAs
legacy report
business source guard result
```

内部流程：

```text
analyze
→ resolve
→ source resolve
→ project plan
→ user confirm
→ apply
→ check
```

## 35. Alpha.1 错误码

至少：

```text
REPO_NOT_SUPPORTED
REPO_PROFILE_INVALID
HARNESS_NOT_SUPPORTED
CAPABILITY_NOT_FOUND
CAPABILITY_DEPENDENCY_MISSING
CAPABILITY_OWNERSHIP_CONFLICT
UPSTREAM_SOURCE_UNRESOLVED
UPSTREAM_SHA_NOT_PINNED
SPEC_KIT_RECONCILE_CONFLICT
MANAGED_CONTENT_MODIFIED
BUSINESS_SOURCE_MODIFICATION_FORBIDDEN
LEGACY_OWNERSHIP_UNKNOWN
GES_RECONCILE_NOOP
GES_CHECK_FAILED
```

# Part III — 实施顺序

## 36. Phase 0 — v5 Freeze & Legacy Inventory

实现：

```text
v5 capability inventory
legacy ownership markers
legacy detect rules
legacy dry-run report
```

DoD：

```text
能在 smc-copilot 中报告 v5
不删除任何 uncertain ownership 文件
```

## 37. Phase 1 — CLI + Project State

实现：

```text
ges CLI shell
.ges/project.yaml
.ges/repo-profile.json
.ges/lock.json
.ges/install-receipt.json
schema validation
```

## 38. Phase 2 — Deterministic Repo Analyzer

实现：

```text
Brownfield detection
monorepo detection
Cursor detection
Codex detection
Spec Kit detection
legacy GES detection
source-root detection
business-source protection map
```

DoD：

```text
smc-copilot profile generated
LLM token usage = 0
```

## 39. Phase 3 — Capability Catalog & Resolver

实现：

```text
capability registry
requires graph
conflict graph
owner domain
profiles
user exclude
dependency closure
conflict validation
```

## 40. Phase 4 — Matt Source Adapter

实现 selective source resolve + projection。

DoD：

```text
only selected Matt skills materialized
```

## 41. Phase 5 — Spec Kit Source Adapter

实现：

```text
existing .specify adoption
staging materialization
selected capability exposure
managed path reconciliation
```

## 42. Phase 6 — Superpowers Source Adapter

实现：

```text
pinned source
execution-only skill projection
exclude whole-process bootstrap
```

## 43. Phase 7 — Cursor + Codex Harness Adapter

实现：

```text
shared .agents/skills
Cursor projection
Codex projection
AGENTS marker block
deduplication
```

## 44. Phase 8 — Reconciler

实现：

```text
desired/current diff
managed hashes
safe apply
NOOP detection
update
remove
rollback-on-failure
```

## 45. Phase 9 — Golden Consumer Acceptance

目标：

```text
smc-copilot
```

完整执行：

```text
legacy detect
init
apply
check
second apply
upgrade simulation
remove
restore validation
```

# Part IV — 验收需求

## 46. Golden Acceptance Chain

```text
ges init smc-copilot
→ 能识别 Brownfield repo
→ 能识别 Cursor/Codex
→ 不覆盖现有 AGENTS.md
→ 不破坏现有 .specify
→ 能识别并报告 legacy GES v5
→ 生成能力推荐
→ 用户可取消任意 capability
→ 自动补齐 dependency
→ 自动发现 ownership conflict
→ 只安装 resolved skills
→ 上游 SHA 被锁定
→ 第二次 ges apply = NOOP
→ 更新时只改 managed content
→ ges remove 可完全撤销 GES-owned projection
→ 业务源码 0 bytes modified
```

## 47. Acceptance IDs

### A01 — Brownfield Detection

`smc-copilot`：

```text
repository_kind = brownfield
```

### A02 — Harness Detection

```text
Cursor = detected
Codex = detected
```

### A03 — Existing AGENTS Preservation

执行前后：

```text
marker 外内容 byte-identical
```

### A04 — Existing Spec Kit Preservation

已有 `.specify/` 内容不被无条件重初始化覆盖。

### A05 — Legacy Detection

```text
legacy_ges_v5 = true
```

正常 init：

```text
0 legacy deletion
```

### A06 — Capability Recommendation

推荐结果来自：

```text
Repo Profile + Product Profile + Catalog
```

### A07 — Capability Exclusion

用户移除 optional capability 后 resolution 仍合法，并写回 desired state。

### A08 — Dependency Closure

选择 `matt.grill-with-docs` 自动包含：

```text
matt.grilling
matt.domain-modeling
```

### A09 — Ownership Conflict

两个 Feature Spec Owner 同时存在：

```text
CAPABILITY_OWNERSHIP_CONFLICT
```

Apply BLOCK。

### A10 — Selective Install

目标项目中不存在未 resolved 的 Matt / Spec Kit / Superpowers skills。

### A11 — Upstream Lock

三类 upstream source 均锁定 immutable commit SHA。

### A12 — Idempotent Apply

第一次：

```text
changes > 0
```

第二次：

```text
changes = 0
GES_RECONCILE_NOOP
```

### A13 — Managed Update

模拟上游 Skill 升级，仅 GES-managed content 改变。

### A14 — User Modification Conflict

用户手工修改 GES-managed section，升级时：

```text
MANAGED_CONTENT_MODIFIED
```

不得静默覆盖。

### A15 — Remove

`ges remove .` 后所有 GES-owned projection 删除，用户内容保留。

### A16 — Business Source Guard

比较：

```text
apps/**
services/**
src/**
packages/**
contracts/**
```

Expect：

```text
0 files changed
0 bytes changed
```

## 48. Reconcile Verification

Acceptance 建立：

```text
before tree snapshot
after init snapshot
after second apply snapshot
after remove snapshot
```

验证：

```text
after second apply == after first apply
```

在无用户中间变更的 fixture 中：

```text
after remove == before install
```

针对所有非 GES-owned 内容成立。

## 49. Business Source Zero-Byte Test

记录 source-root：

```text
relative path
size
sha256
```

`ges init/apply/remove` 后比较。

任何变化：

```text
BUSINESS_SOURCE_MODIFICATION_FORBIDDEN
```

## 50. Failure Atomicity

Alpha.1 必须：

```text
plan
→ stage
→ verify
→ commit projection
```

失败时 rollback，禁止半安装状态。

## 51. Non-Goals

Alpha.1 不实现：

```text
Policy Engine GA
Risk Engine GA
Evidence ingestion GA
Approval workflow GA
Delivery evaluator GA
Release orchestration
GitHub merge gate
CI gate enforcement
LLM runtime
Token accounting
Spec generation
Plan generation
TDD orchestration
Review orchestration
```

## 52. 安全与供应链

必须满足：

```text
immutable upstream SHA
HTTPS source
source identity verification
path traversal rejection
projection root containment
no writes outside repo
no arbitrary post-install execution by default
business-source denylist
```

上游能力至少记录：

```text
source repo
commit SHA
selected paths
content hash
```

## 53. 可观测性

结构化操作日志阶段：

```text
ANALYZE
RESOLVE
FETCH
PROJECT
RECONCILE
CHECK
REMOVE
```

不引入 LLM telemetry。

## 54. `ges check`

必须验证：

```text
project.yaml valid
repo-profile valid
lock valid
all locked source SHAs present/resolvable
all resolved capabilities projected
no ownership conflict
managed hashes match
AGENTS marker exactly one
business-source guard clean
```

成功：

```text
GES_CHECK_PASS
```

## 55. Definition of Done

```text
[ ] GES 6 architecture baseline frozen in docs
[ ] Composer / Backplane boundary documented
[ ] v5 execution-centric capability no longer part of v6 core
[ ] ges CLI created
[ ] deterministic repo analyzer completed
[ ] Brownfield smc-copilot detected correctly
[ ] Cursor detected
[ ] Codex detected
[ ] existing AGENTS.md preserved
[ ] existing .specify preserved
[ ] legacy GES v5 detected and reported
[ ] capability catalog implemented
[ ] dependency closure implemented
[ ] ownership conflict detection implemented
[ ] user capability exclusion implemented
[ ] Matt selective adapter implemented
[ ] Spec Kit adoption/reconcile adapter implemented
[ ] Superpowers execution-only adapter implemented
[ ] upstream SHA locking implemented
[ ] Cursor projection implemented
[ ] Codex projection implemented
[ ] managed marker/hash implemented
[ ] second apply is NOOP
[ ] update touches managed content only
[ ] remove completely removes GES-owned projection
[ ] uncertain ownership content preserved
[ ] business source 0 bytes modified
[ ] failure rollback verified
[ ] ges check passes on Golden Consumer
[ ] acceptance A01-A16 all PASS
```

## 56. Alpha.1 完成后的业务项目状态

```text
smc-copilot/
│
├── .ges/
│   ├── project.yaml
│   ├── repo-profile.json
│   ├── lock.json
│   └── install-receipt.json
├── .agents/
│   └── skills/
│       ├── selected Matt skills
│       ├── selected Spec Kit integration skills
│       └── selected Superpowers execution skills
├── .specify/
│   └── existing/adopted Spec Kit runtime
├── .cursor/
│   └── only required GES-managed integration material
├── .codex/
│   └── only required GES-managed integration material
├── AGENTS.md
│   └── one short GES-managed engineering-stack pointer block
├── apps/
├── services/
├── contracts/
└── ...
```

GES Core 不复制到业务仓库。

## 57. GES 6 长期演进顺序

```text
6.0-alpha.1
Composer Bootstrap

6.0-alpha.2
Work / Artifact Registry

6.0-alpha.3
Evidence / Ownership / Approval primitives

6.0-beta.1
Policy + Risk

6.0-beta.2
Delivery Evaluator

6.0-rc
Merge / Release integration

6.0 GA
Composer + Governance Backplane
```

## 58. 最终架构原则

```text
1. Business project stores desired state, lock and receipts — not GES Core.
2. Engineering capabilities are composed, not bundled wholesale.
3. Every engineering domain has a single Owner.
4. Capability dependencies are explicit.
5. Capability ownership conflicts fail before apply.
6. Upstream sources are immutable by SHA.
7. Installation is desired-state reconciliation, not file copying.
8. Shared files are marker-managed, never wholesale overwritten.
9. User-managed content always wins unless explicitly approved otherwise.
10. Business source code is outside Composer write scope.
11. GES consumes artifacts/evidence; it does not reproduce engineering reasoning.
12. Governance happens at outcome boundaries, not every Agent turn.
```

## 59. Release Verdict Standard

只有当：

```text
ges init smc-copilot
```

完整实现：

```text
Brownfield detected
→ Cursor/Codex detected
→ AGENTS preserved
→ .specify preserved
→ legacy v5 reported
→ capability recommendation generated
→ user selection honored
→ dependencies closed
→ ownership conflicts blocked
→ only resolved capabilities projected
→ source SHA locked
→ second apply NOOP
→ update touches managed content only
→ remove reverses GES projection
→ business source remains byte-identical
```

才能将 `GES 6.0-alpha.1` 标记为：

```text
COMPOSER_BOOTSTRAP_COMPLETE
```

它只代表：

> **GES 6 已经拥有一个可安全进入真实 Brownfield 业务项目的最小接入面。**

并不代表 Governance Backplane 已全部完成。
