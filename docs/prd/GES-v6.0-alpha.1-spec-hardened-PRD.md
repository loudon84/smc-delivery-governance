---
title: "GES 6.0-alpha.1-spec-hardened — Composer Bootstrap Engineering Contract PRD"
subtitle: "Machine-Executable Specification for Composer + Governance Backplane Bootstrap"
status: "SPEC_HARDENED_FOR_PLAN_GENERATION"
product_line: "GES 6"
release: "6.0.0-alpha.1-spec-hardened"
change_type: "SPECIFICATION_HARDENING"
repository: "smc-delivery-governance"
golden_consumer: "smc-copilot"
supersedes_implementation_semantics_of: "GES 6.0-alpha.1 — Composer Bootstrap PRD"
architecture_baseline_unchanged: true
---

# GES 6.0-alpha.1-spec-hardened — Composer Bootstrap Engineering Contract PRD

## 0. 文档目的

本 PRD 是 `GES 6.0-alpha.1 — Composer Bootstrap PRD` 的 **Specification Hardening** 版本。

本版本：

- **不改变** GES 6 的产品定位；
- **不改变** `Composer + Governance Backplane` 总体架构；
- **不改变** Matt Pocock Skills / Spec Kit / Superpowers / GES 的 Owner 边界；
- **不扩大** Alpha.1 到 Governance Backplane GA；
- **不重新定义** AI Coding Runtime。

本版本只解决一个问题：

> **把原 PRD 中“人可以理解、模型可能需要猜测”的自然语言要求，冻结为可验证、可追踪、可由 Coding Agent 无歧义执行的工程合同。**

目标是阻断以下循环：

```text
PRD 自然语言
→ Agent 主观补全语义
→ Plan 把推断写成事实
→ Code 实现推断
→ Happy-path Test PASS
→ Review 发现系统语义不一致
→ Patch
→ 再暴露新边界
```

本 PRD 建立新的强制链路：

```text
REQ
→ Normative Contract
→ Invariant / State Transition
→ Acceptance Oracle
→ Test
→ Evidence
→ Release Gate
```

只有闭合上述链路的需求，才允许进入 `.plan.md`。

---

# Part I — 规范解释规则

## 1. Normative Keywords

本文使用以下规范词：

```text
MUST
MUST NOT
SHOULD
SHOULD NOT
MAY
```

含义：

- `MUST`：实现、测试和 Evidence 均为强制；
- `MUST NOT`：违反即 Release Gate 失败；
- `SHOULD`：允许存在明确记录的偏差；
- `MAY`：实现可选，不影响 Alpha.1 Release Gate。

示例、目录示意、伪代码默认是 **非规范性说明**；只有 REQ / INV / AC 中的内容具有工程合同效力。

## 2. No-Inference Rule

Coding Agent、Plan Agent、Review Agent MUST NOT 对以下内容自行补义：

```text
ownership scope
hash scope
transaction boundary
default selection semantics
state authority
failure behavior
side effects
source identity verification
remove behavior under drift
acceptance pass criteria
```

如果实现所需语义无法由本 PRD 唯一确定：

```text
MUST BLOCK
MUST report SPEC_SEMANTIC_GAP
MUST NOT silently choose one interpretation
```

## 3. Requirement Readiness Gate

任何 `MUST` 要进入实施 Plan，至少必须存在：

```text
REQ-ID
Normative Requirement
Input / Preconditions
Authoritative State
Allowed Side Effects
Forbidden Side Effects
Postcondition / Invariant
Failure Semantics
Acceptance ID
Observable Oracle
Evidence Requirement
```

缺一项时，该需求状态为：

```text
SPEC_NOT_IMPLEMENTABLE
```

不得标记为 plan-ready。

---

# Part II — GES 6 架构基线（保持不变）

## 4. 产品定位

GES 6 产品定位保持：

> **Composer + Governance Backplane for AI-assisted software delivery**

Owner 冻结：

```text
Matt Pocock Skills
= Engineering Disciplines

Spec Kit
= Intent SOT

Superpowers
= Execution Methodology

GES
= Capability Composer + Governance Backplane
```

GES 6 不成为：

```text
PRD Engine
Plan Engine
Context Engine
TDD Runtime
Debug Runtime
Code Review Runtime
Agent Runtime
Model Router
Token Accounting Runtime
```

## 5. Alpha.1 Pipeline

Alpha.1 只实现：

```text
Repo Analyze
→ Capability Resolve
→ Source Resolve
→ Harness Projection
→ Reconcile / Check
```

Governance Backplane 的：

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

只保留 Domain Model / Interface / Future Compatibility，不在 Alpha.1 实现运行时。

## 6. Golden Consumer

Alpha.1 Golden Consumer：

```text
loudon84/smc-copilot
```

Release Gate 必须使用真实 Golden Consumer，不得仅用 synthetic fixture 代替。

---

# Part III — 系统状态与事实源

## 7. State Authority Model

GES Alpha.1 必须明确区分四类状态。

### 7.1 `.ges/project.yaml`

角色：

```text
AUTHORITATIVE DESIRED STATE
```

它是用户已经确认的 Engineering Composition 的唯一事实源。

`ges apply` 在存在 `.ges/project.yaml` 时：

```text
MUST resolve from project.yaml
MUST NOT recompute a new default recommendation and silently replace user intent
```

### 7.2 `.ges/repo-profile.json`

角色：

```text
OBSERVED REPOSITORY FACTS
```

它不是 Desired State。

必须记录：

```text
analyzer version
observed repository facts
observation timestamp
git identity / head when available
```

它 MAY 被重新分析，但重新分析不得改变 `project.yaml`。

### 7.3 `.ges/lock.json`

角色：

```text
RESOLVED IMMUTABLE SOURCE STATE
```

记录：

```text
resolved capability closure
source repo
source pinned commit SHA
selected source paths
source content identities
resolver version
```

### 7.4 `.ges/install-receipt.json`

角色：

```text
LAST-APPLIED OWNERSHIP + EVIDENCE STATE
```

记录：

```text
last-applied projection
managed artifacts
ownership scope
last-applied hash
source identity
apply transaction id
```

---

# Part IV — Project Desired State Contract

## 8. REQ-STATE-001 — project.yaml 是唯一 Desired State

### Goal

避免每次 apply 根据 Product Profile 重新推荐并覆盖用户已经确认的选择。

### Normative Contract

首次 `ges init`：

```text
Repo Profile
+ Product Profile
→ Recommendation
→ User Selection
→ Validation
→ Persist exact Desired State
```

后续：

```text
ges diff
ges apply
ges check
```

MUST 以已存在的 `.ges/project.yaml` 为用户意图输入。

### Project Schema

```yaml
schema: ges.project.v2

profile: brownfield-product-app

agents:
  - cursor
  - codex

capabilities:
  requested:
    - matt.setup
    - matt.grill-with-docs
    - matt.grilling
    - matt.domain-modeling
    - matt.codebase-design
    - matt.to-tickets

    - speckit.constitution
    - speckit.specify
    - speckit.clarify
    - speckit.plan

    - superpowers.using-git-worktrees
    - superpowers.writing-plans
    - superpowers.subagent-driven-development
    - superpowers.test-driven-development
    - superpowers.systematic-debugging
    - superpowers.requesting-code-review
    - superpowers.receiving-code-review
    - superpowers.verification-before-completion
    - superpowers.finishing-a-development-branch

  explicitly_disabled: []

resolution:
  mode: explicit

engineering_stack:
  disciplines:
    provider: matt
  intent:
    provider: spec-kit
  execution:
    provider: superpowers
```

`requested` 是 **直接选择集**。

Dependency closure 不写回 `requested`，而写入 `lock.json.resolved_capabilities`。

### Invariant INV-STATE-001

```text
Given:
  project.yaml exists

Then:
  ResolveInput.capabilities == project.yaml.capabilities.requested

And:
  Product Profile defaults MUST NOT add a capability that is absent from requested.
```

### Failure

非法 Desired State：

```text
DESIRED_STATE_INVALID
```

### Acceptance

```text
A18 — Desired State Authority
```

---

# Part V — Capability Selection Semantics

## 9. REQ-CAP-001 — Capability 必须具有明确 Selection Class

Product Profile 中的 capability 必须属于且仅属于：

```text
required
recommended
optional
forbidden
```

语义冻结如下：

| Class | Default selected | User can disable | User can enable |
|---|---:|---:|---:|
| required | YES | NO | N/A |
| recommended | YES | YES | YES |
| optional | NO | N/A | YES |
| forbidden | NO | NO | NO |

### Product Profile Contract

```yaml
schema: ges.product-profile.v2
id: brownfield-product-app

required:
  - matt.setup

recommended:
  - matt.grill-with-docs
  - matt.grilling
  - matt.domain-modeling
  - matt.codebase-design
  - matt.to-tickets
  - speckit.constitution
  - speckit.specify
  - speckit.clarify
  - speckit.plan
  - superpowers.using-git-worktrees
  - superpowers.writing-plans
  - superpowers.subagent-driven-development
  - superpowers.test-driven-development
  - superpowers.systematic-debugging
  - superpowers.requesting-code-review
  - superpowers.receiving-code-review
  - superpowers.verification-before-completion
  - superpowers.finishing-a-development-branch

optional:
  - superpowers.executing-plans

forbidden:
  - matt.to-spec
  - matt.implement
  - matt.tdd
  - matt.diagnosing-bugs
  - matt.code-review
  - speckit.tasks
  - speckit.implement
  - speckit.converge
  - superpowers.brainstorming
  - superpowers.using-superpowers
```

### Invariant INV-CAP-001

```text
optional capability MUST NOT appear in initial requested set
unless the user explicitly enables it.
```

### Invariant INV-CAP-002

```text
required capability exclusion MUST fail before apply.
```

### Invariant INV-CAP-003

```text
forbidden capability selection MUST fail before apply.
```

### Acceptance

```text
A07 — Recommended Capability Exclusion
A19 — Optional Selection Semantics
```

---

# Part VI — Deterministic Repo Analyzer Contract

## 10. REQ-ANALYZE-001 — Analyzer 零 LLM、零主观推断

必须：

```text
LLM token usage = 0
```

Analyzer 只能使用：

```text
filesystem metadata
file names / paths
deterministic file parsing
git metadata
known config files
```

## 11. Repo Profile Schema

```json
{
  "schema": "ges.repo-profile.v2",
  "repository_lifecycle": "brownfield",
  "repository_layout": "monorepo",
  "repository_kind": "brownfield-monorepo",
  "agents": ["cursor", "codex"],
  "languages": ["typescript"],
  "package_managers": ["pnpm"],
  "frameworks": [],
  "spec_kit": true,
  "legacy_ges": true,
  "ci": ["github-actions"],
  "scripts": {
    "test": [],
    "build": [],
    "lint": []
  },
  "existing": {
    "AGENTS.md": true,
    ".agents": true,
    ".cursor": true,
    ".codex": true,
    ".specify": true,
    ".smc": true
  },
  "source_roots": [
    "apps",
    "services",
    "src",
    "packages",
    "contracts"
  ]
}
```

## 12. REQ-ANALYZE-002 — Monorepo / Language Detection

### TypeScript Detection

TypeScript MUST be detected only if at least one actual evidence item exists：

```text
tsconfig*.json
*.ts
*.tsx
package.json with TypeScript dependency
```

空 generator、目录存在本身、未展开的 iterator 不得作为 evidence。

### Scripts Detection

对于所有已识别 `package.json`：

```text
scripts.test
scripts.build
scripts.lint
```

必须被解析并写入 Repo Profile。

### Acceptance

```text
A01 — Brownfield Detection
A02 — Harness Detection
A25 — Analyzer Schema + Script Detection
```

---

# Part VII — Command Side-Effect Contract

## 13. REQ-CMD-001 — Consumer Repo Command Purity

命令对目标业务仓库的写入权限冻结如下：

| Command | May mutate consumer repo |
|---|---|
| `ges analyze` | NO |
| `ges diff` | NO |
| `ges check` | NO |
| `ges legacy inspect` | NO |
| `ges init` before confirmation | NO |
| `ges init` after confirmation | YES, via one apply transaction |
| `ges apply` | YES |
| `ges remove` | YES |
| `ges legacy remove --dry-run` | NO |
| `ges legacy remove --apply` | YES |

### Source Cache Exception

`ges analyze` 不得访问网络。

`ges diff` MAY materialize immutable upstream source into：

```text
~/.cache/ges/sources/**
```

但：

```text
MUST NOT modify consumer repo
MUST report FETCH stage
```

### Invariant INV-CMD-001

对于所有 read-only 命令：

```text
consumer_tree_after == consumer_tree_before
```

按：

```text
relative path + file type + size + sha256
```

比较。

### Acceptance

```text
A17 — Preview / Read-only Command Purity
```

---

# Part VIII — Capability Resolver Contract

## 14. REQ-RESOLVE-001 — Dependency Closure

输入：

```text
project.yaml.capabilities.requested
```

输出：

```text
resolved_capabilities
```

必须：

```text
递归补齐 requires
检测 missing dependency
检测 declared conflicts
检测 owner_domain conflict
检测 harness support
```

### Example

选择：

```text
matt.grill-with-docs
```

必须自动包含：

```text
matt.grilling
matt.domain-modeling
```

### Errors

```text
CAPABILITY_NOT_FOUND
CAPABILITY_DEPENDENCY_MISSING
CAPABILITY_OWNERSHIP_CONFLICT
HARNESS_NOT_SUPPORTED
```

## 15. REQ-RESOLVE-002 — Single Owner

相同非 virtual `owner_domain`：

```text
MUST have <= 1 active owner source
```

冲突：

```text
BLOCK before projection
```

### Acceptance

```text
A08 — Dependency Closure
A09 — Ownership Conflict
```

---

# Part IX — Source Provenance Contract

## 16. REQ-SOURCE-001 — Immutable Upstream Identity

每个 Source 必须锁定：

```text
HTTPS repository URL
40-char commit SHA
selected source paths
content identity
```

禁止：

```text
branch
tag without peeled commit identity
floating ref
latest
HEAD
```

## 17. REQ-SOURCE-002 — Cache Provenance Verification

Cache path：

```text
~/.cache/ges/sources/<source-id>/<sha>/
```

首次 fetch 必须验证：

```text
git rev-parse HEAD == pinned_sha
```

并生成：

```json
{
  "schema": "ges.source-cache-manifest.v1",
  "source": "matt",
  "repo": "https://...",
  "commit": "<40-char sha>",
  "selected_paths": [],
  "content_digest": "sha256:..."
}
```

`content_digest` 计算规则：

```text
sort(relative_file_paths)
for each regular file:
  hash(relative_path UTF-8 bytes + NUL + file bytes)
aggregate by sha256
```

### Cache Hit

每次 cache hit：

```text
MUST verify manifest.repo
MUST verify manifest.commit
MUST recompute content_digest
```

不一致：

```text
SOURCE_CACHE_INTEGRITY_FAILED
```

Online mode：

```text
MAY discard invalid cache and refetch pinned SHA
```

Offline mode：

```text
MUST fail
MUST NOT trust invalid cache
```

## 18. REQ-SOURCE-003 — Symlink / Path Safety

Alpha.1 对 selected source path：

```text
MUST reject symlink
MUST reject .. traversal
MUST reject absolute path
MUST reject projection escaping repo root
```

### Acceptance

```text
A11 — Upstream Lock
A23 — Source Cache Integrity / Provenance
```

---

# Part X — Projection Model

## 19. Managed Artifact Types

所有 projection 必须显式声明 ownership type：

```text
FILE
SECTION
ENTRY
```

### FILE

GES 拥有整个文件。

### SECTION

GES 只拥有文件中的 marker range。

### ENTRY

GES 只拥有一个可唯一识别的条目，例如 `.gitignore` 中的一行。

## 20. Projection Artifact Schema

```json
{
  "path": "AGENTS.md",
  "ownership_type": "SECTION",
  "selector": {
    "begin": "<!-- ges:v6:engineering-stack:begin -->",
    "end": "<!-- ges:v6:engineering-stack:end -->"
  },
  "producer": "harness.agents_md",
  "capability_ids": [],
  "generated_hash": "sha256:...",
  "source_identity": null
}
```

## 21. REQ-PROJ-001 — Projection Collision

两个 producer 若声明：

```text
same path + overlapping ownership scope
```

则：

```text
same content + same ownership semantics
→ deduplicate

different content or different incompatible ownership
→ PROJECTION_PATH_CONFLICT
→ BLOCK before apply
```

后写覆盖前写：

```text
MUST NOT occur silently
```

### Acceptance

```text
A24 — Projection Collision Detection
```

---

# Part XI — AGENTS.md Contract

## 22. REQ-PROJ-AGENTS-001 — Section-only Ownership

GES 只拥有：

```text
<!-- ges:v6:engineering-stack:begin -->
...
<!-- ges:v6:engineering-stack:end -->
```

marker 外：

```text
ownership = USER
```

## 23. REQ-PROJ-AGENTS-002 — Hash Scope

对 AGENTS.md：

```text
last_applied_hash
generated_hash
current_hash
```

MUST 仅计算 marker section bytes。

严禁使用整个 `AGENTS.md` 文件 hash 判断 GES section drift。

### Invariant INV-AGENTS-001

```text
marker 外任意用户修改
MUST NOT trigger MANAGED_CONTENT_MODIFIED
```

### Invariant INV-AGENTS-002

```text
marker 内用户修改
MUST trigger MANAGED_CONTENT_MODIFIED
```

### Update

```text
section_current == section_last_applied
→ safe replace

section_current != section_last_applied
→ BLOCK
```

### Remove

```text
section_current == section_last_applied
→ remove marker section only

section_current != section_last_applied
→ BLOCK entire remove transaction
```

### Acceptance

```text
A03 — Existing AGENTS Preservation
A14 — User Modification Conflict
A20 — Section-scoped Hashing
```

---

# Part XII — Spec Kit Adoption Contract

## 24. REQ-SPECKIT-001 — Existing `.specify/` 是 User-owned Existing Runtime

Golden Consumer 已存在 `.specify/` 时：

```text
MUST NOT reinitialize
MUST NOT wholesale replace
MUST NOT claim ownership of pre-existing files
```

GES 新增内容优先位于：

```text
.specify/.ges/**
```

## 25. Selected Capability Exposure

对于：

```text
speckit.constitution
speckit.specify
speckit.clarify
speckit.plan
```

GES 必须：

1. 从 pinned Spec Kit source materialize 对应 command/source artifact；
2. 将 pinned command copy 投影到：

```text
.specify/.ges/commands/<capability>.md
```

3. 在：

```text
.agents/skills/speckit-<capability>/SKILL.md
```

创建 GES-owned wrapper；
4. Wrapper MUST 明确引用：

```text
.specify/.ges/commands/<capability>.md
source repo
source commit SHA
source path
```

5. Wrapper MUST NOT 模糊地只说“使用项目现有 Spec Kit command”而不指定 pinned managed artifact。

## 26. Existing Managed Namespace Conflict

如果：

```text
.specify/.ges/**
```

存在，但不存在可证明的 GES Receipt ownership：

```text
SPEC_KIT_RECONCILE_CONFLICT
→ BLOCK
→ PRESERVE existing content
```

### Acceptance

```text
A04 — Existing Spec Kit Preservation
A26 — Spec Kit Pinned Adoption / Capability Exposure
```

---

# Part XIII — Reconcile Contract

## 27. REQ-RECON-001 — Desired vs Current

Install Plan action 必须属于：

```text
ADD
UPDATE
REMOVE
PRESERVE
CONFLICT
```

每个 action 必须携带：

```text
path
ownership scope
reason
producer
capability ids
current identity
desired identity
```

## 28. REQ-RECON-002 — Managed Drift

对于 FILE：

```text
current_file_hash == receipt.last_applied_hash
→ safe update/remove

current_file_hash != receipt.last_applied_hash
→ MANAGED_CONTENT_MODIFIED
```

对于 SECTION：

```text
current_section_hash == receipt.last_applied_hash
→ safe update/remove

current_section_hash != receipt.last_applied_hash
→ MANAGED_CONTENT_MODIFIED
```

对于 ENTRY：

```text
current_entry == receipt.last_applied_entry
→ safe update/remove

otherwise
→ MANAGED_CONTENT_MODIFIED
```

---

# Part XIV — Transaction / Failure Atomicity Contract

## 29. REQ-TXN-001 — Apply Transaction Boundary

一次 `ges apply` 的 transaction scope 包括：

```text
.ges/**
.agents/skills/**
.specify/** managed paths only
.cursor/** managed paths only
.codex/** managed paths only
AGENTS.md managed section only
.gitignore managed entry only
```

必须同时包含：

```text
project.yaml
repo-profile.json
lock.json
install-receipt.json
```

任何一个都不得在主 transaction 之外提前落盘。

## 30. REQ-TXN-002 — Preview Before Commit

流程冻结：

```text
analyze in memory
→ resolve
→ source resolve
→ build desired projection
→ build install plan
→ validate plan
→ user confirmation when required
→ stage outside consumer repo
→ verify staged projection
→ snapshot pre-state
→ commit
→ post-commit verify
→ write/commit receipt as part of same transaction
```

在 `commit` 前：

```text
consumer repo MUST be byte-identical to pre-command state
```

## 31. REQ-TXN-003 — Rollback

令：

```text
T0 = immediately before first consumer-repo mutation
```

如果 apply 在任何 consumer-repo mutation 后返回非成功：

```text
managed_scope(after rollback) == managed_scope(T0)
```

包括：

```text
existing .ges state
existing project.yaml
existing repo-profile.json
existing lock.json
existing install-receipt.json
managed files
managed sections
managed entries
```

### Forbidden Rollback Behavior

```text
rm -rf .ges
```

若 `.ges` 在 T0 已存在：

```text
MUST NOT be used as rollback strategy
```

除非 pre-state 明确证明 `.ges` 在 T0 不存在。

### Rollback Failure

如果 rollback 本身失败：

```text
TRANSACTION_ROLLBACK_FAILED
```

必须输出：

```text
transaction id
failed paths
backup location
manual recovery instructions
```

不得报告普通 apply failure 伪装成已回滚成功。

## 32. Atomicity Boundary Limitation

Alpha.1 只承诺：

```text
caught process/runtime failures
```

不承诺：

```text
OS crash
power loss
filesystem hardware corruption
```

这些属于后续 crash-safe journal 范围。

### Acceptance

```text
A21 — Failure Atomicity / Existing State Restore
```

A21 MUST 至少注入：

```text
failure after 1st write
failure after Nth write
failure before receipt commit
failure during post-commit verification
```

每次都比较 pre/post snapshot。

---

# Part XV — Remove Contract

## 33. REQ-REMOVE-001 — Safe Remove

`ges remove` 必须先完成完整 preflight。

### FILE

```text
current == last_applied
→ eligible for delete

current != last_applied
→ MANAGED_CONTENT_MODIFIED
→ BLOCK entire remove
```

### SECTION

```text
section_current == section_last_applied
→ eligible for section removal

section_current != section_last_applied
→ MANAGED_CONTENT_MODIFIED
→ BLOCK entire remove
```

### ENTRY

同样按 managed entry identity 检查。

## 34. REQ-REMOVE-002 — No Partial Remove on Drift Conflict

只要一个 planned remove artifact 存在 drift：

```text
0 consumer-repo mutations
```

本次 remove 返回：

```text
MANAGED_CONTENT_MODIFIED
```

Alpha.1 不提供 silent force-delete。

### Acceptance

```text
A15 — Remove
A22 — Remove Drift Protection
```

---

# Part XVI — Business Source Guard

## 35. REQ-GUARD-001 — Business Source Zero-byte Modification

禁止修改：

```text
apps/**
services/**
src/**
packages/**
contracts/**
```

比较：

```text
relative path
file type
size
sha256
```

任何变化：

```text
BUSINESS_SOURCE_MODIFICATION_FORBIDDEN
```

### Acceptance

```text
A16 — Business Source Guard
```

---

# Part XVII — Install Receipt Contract

## 36. Receipt Schema

```json
{
  "schema": "ges.install-receipt.v2",
  "installed_at": "...",
  "ges_version": "6.0.0-alpha.1-spec-hardened",
  "repo_identity": {},
  "transaction_id": "...",
  "capability_set": [],
  "source_commits": {},
  "managed_artifacts": [
    {
      "path": "AGENTS.md",
      "ownership_type": "SECTION",
      "selector": {},
      "last_applied_hash": "sha256:...",
      "producer": "harness.agents_md",
      "capability_ids": []
    }
  ]
}
```

Receipt MUST NOT 用一个整文件 hash 替代 section / entry ownership identity。

---

# Part XVIII — `ges check` Contract

## 37. REQ-CHECK-001

`ges check` 是 read-only。

必须验证：

```text
project.yaml schema valid
repo-profile schema valid
lock schema valid
receipt schema valid
project Desired State can resolve
resolved capabilities == lock capability closure
no ownership conflict
all source SHAs are immutable
available source cache passes provenance verification
all managed FILE hashes match
all managed SECTION hashes match
all managed ENTRY identities match
AGENTS marker exactly one
all expected projections exist
no unexpected GES ownership collision
business-source guard clean
recompose from project Desired State produces NOOP
```

成功：

```text
GES_CHECK_PASS
```

失败：

```text
GES_CHECK_FAILED
```

`ges check` MUST NOT 通过修复文件来使自己通过。

---

# Part XIX — Legacy GES v5 Contract

## 38. REQ-LEGACY-001

Legacy ownership：

```text
recorded hash == current hash
→ OWNED_UNMODIFIED

recorded path absent
→ OWNED_ABSENT

hash mismatch / ownership unprovable
→ LEGACY_OWNERSHIP_UNKNOWN
→ PRESERVE + REPORT
```

普通 `ges init`：

```text
MUST NOT delete legacy files
```

### Acceptance

```text
A05 — Legacy Detection
```

---

# Part XX — Error Codes

## 39. Base Error Codes

继续保留：

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

## 40. Hardened Error Codes

新增：

```text
SPEC_SEMANTIC_GAP
SPEC_NOT_IMPLEMENTABLE
DESIRED_STATE_INVALID
PROJECTION_PATH_CONFLICT
SOURCE_CACHE_INTEGRITY_FAILED
TRANSACTION_ROLLBACK_FAILED
EVIDENCE_MISSING
```

---

# Part XXI — Acceptance Contract

## 41. Acceptance Status

每个 Acceptance 只能是：

```text
PASS
FAIL
SKIPPED
BLOCKED
```

规则：

```text
SKIPPED != PASS
BLOCKED != PASS
```

Release Gate 要求的 Acceptance：

```text
MUST be PASS
```

不能因为环境不满足而把 `SKIPPED` 计为通过。

## 42. A01–A16（保留并强化）

### A01 — Brownfield Detection

必须：

```text
repository_lifecycle = brownfield
repository_layout = monorepo
repository_kind = brownfield-monorepo
```

### A02 — Harness Detection

```text
cursor detected
codex detected
```

### A03 — Existing AGENTS Preservation

```text
outside-marker bytes after == outside-marker bytes before
```

### A04 — Existing Spec Kit Preservation

已有 `.specify/` 非 GES-owned 内容：

```text
byte-identical
```

### A05 — Legacy Detection

```text
legacy_ges = true
normal init = 0 legacy deletion
```

### A06 — Capability Recommendation

推荐来源必须可追踪到：

```text
Repo Profile
Product Profile
Catalog
```

### A07 — Recommended Capability Exclusion

用户可取消 `recommended` capability。

取消后：

```text
dependency validation PASS
ownership validation PASS
project.yaml requested set reflects choice
```

### A08 — Dependency Closure

自动补齐 required dependencies。

### A09 — Ownership Conflict

冲突：

```text
CAPABILITY_OWNERSHIP_CONFLICT
0 consumer mutations
```

### A10 — Selective Install

未 resolved capability：

```text
0 projection
```

### A11 — Upstream Lock

所有 source：

```text
HTTPS
40-char SHA
content identity
```

### A12 — Idempotent Apply

第一次 apply 后第二次：

```text
0 content change
GES_RECONCILE_NOOP
```

### A13 — Managed Update

只改变对应 GES-owned artifact scope。

### A14 — User Modification Conflict

修改 managed scope：

```text
MANAGED_CONTENT_MODIFIED
0 silent overwrite
```

### A15 — Remove

无 drift：

```text
all GES-owned projection removed
all user-owned content preserved
```

### A16 — Business Source Guard

```text
0 files changed
0 bytes changed
```

---

# Part XXII — Hardened Acceptance A17–A27

## 43. A17 — Preview / Read-only Command Purity

对：

```text
ges analyze
ges diff
ges check
ges legacy inspect
ges init before confirmation
```

验证：

```text
consumer tree before == consumer tree after
```

## 44. A18 — Desired State Authority

准备：

```text
project.yaml requested = X
Product Profile current defaults = X + Y
```

执行：

```text
ges diff
ges apply
```

期望：

```text
Y MUST NOT be automatically added
resolved direct selection derives from X
```

## 45. A19 — Optional Selection Semantics

`superpowers.executing-plans`：

首次 init recommendation：

```text
default_selected = false
```

只有显式 enable 后才进入 `requested`。

## 46. A20 — Section-scoped Hashing

步骤：

1. apply；
2. 只修改 AGENTS marker 外用户文本；
3. check / diff / apply。

期望：

```text
NO MANAGED_CONTENT_MODIFIED
outside-marker change preserved
```

然后只修改 marker 内：

```text
MANAGED_CONTENT_MODIFIED
```

## 47. A21 — Failure Atomicity

准备已有：

```text
.ges/project.yaml
.ges/lock.json
.ges/install-receipt.json
```

记录 T0 snapshot。

分别在多 commit point 注入 failure。

期望：

```text
after rollback == T0
```

特别验证：

```text
pre-existing .ges MUST remain byte-identical
```

## 48. A22 — Remove Drift Protection

步骤：

1. apply managed skill；
2. 用户修改该 skill；
3. `ges remove`。

期望：

```text
MANAGED_CONTENT_MODIFIED
0 repo mutations
modified skill preserved
```

## 49. A23 — Source Cache Integrity / Provenance

步骤：

1. fetch pinned cache；
2. 手工修改 cache selected source file；
3. offline resolve。

期望：

```text
SOURCE_CACHE_INTEGRITY_FAILED
```

不得信任目录名或 SHA path。

## 50. A24 — Projection Collision

构造两个 producer 输出同 path、不同 content。

期望：

```text
PROJECTION_PATH_CONFLICT
0 apply mutation
```

## 51. A25 — Analyzer Schema + Script Detection

Fixture 包含：

```text
apps/web/package.json scripts.test
apps/web/package.json scripts.build
apps/web/package.json scripts.lint
apps/web/tsconfig.json
```

期望 Repo Profile 精确输出。

另构造只有 `apps/` 目录但无 TypeScript evidence：

```text
typescript MUST NOT be detected
```

## 52. A26 — Spec Kit Pinned Adoption

在已有 `.specify/` 项目：

```text
existing user .specify files preserved
selected command copies live under .specify/.ges/commands
generated wrappers point to exact managed command
wrapper carries source SHA/path identity
```

## 53. A27 — Golden Consumer Real End-to-End

目标：

```text
smc-copilot
```

前置：

```text
clean git worktree
record HEAD
```

完整执行：

```text
legacy inspect
→ init preview
→ confirmed apply
→ check
→ second apply
→ managed upgrade simulation
→ check
→ remove
→ restore validation
```

期望：

```text
A01-A26 all applicable tests PASS
business source byte-identical
after second apply == after first apply
after remove == before install for all non-GES-owned content
```

如果 Golden Consumer dirty：

```text
A27 = SKIPPED or BLOCKED
Release Gate = FAIL
```

不得标记：

```text
Golden Consumer accepted
Composer Bootstrap complete
```

---

# Part XXIII — Evidence Contract

## 54. Acceptance Evidence Artifact

每次正式 acceptance run 必须输出：

```text
audit/ges6/acceptance/<timestamp>.json
audit/ges6/golden-consumer/<timestamp>.json
```

Schema 至少：

```json
{
  "schema": "ges.acceptance-evidence.v1",
  "ges_version": "6.0.0-alpha.1-spec-hardened",
  "repo": "...",
  "repo_head": "...",
  "started_at": "...",
  "finished_at": "...",
  "results": [
    {
      "acceptance_id": "A21",
      "status": "PASS",
      "requirement_ids": ["REQ-TXN-001", "REQ-TXN-002", "REQ-TXN-003"],
      "test_ids": ["TEST-A21-01"],
      "command": "pytest ...",
      "exit_code": 0,
      "observed_error_code": null,
      "pre_state_digest": "...",
      "post_state_digest": "...",
      "evidence_files": []
    }
  ]
}
```

## 55. Evidence Rule

任何 DoD 项：

```text
MUST map to >= 1 Acceptance
MUST have PASS evidence
```

只有代码存在、函数存在、测试文件存在：

```text
NOT sufficient evidence
```

`pytest` 未运行：

```text
NOT PASS
```

Golden Consumer 被跳过：

```text
NOT PASS
```

---

# Part XXIV — PRD → Plan Contract

## 56. Plan Generation Gate

`.plan.md` 生成前必须做：

```text
Requirement Coverage Check
Semantic Gap Check
Acceptance Coverage Check
Evidence Coverage Check
```

发现任何：

```text
MUST without AC
AC without oracle
state mutation without side-effect contract
failure behavior without failure-path acceptance
ambiguous ownership/hash scope
```

必须：

```text
BLOCK PLAN GENERATION
```

## 57. Plan Todo Contract

每个实现 Todo 必须至少包含：

```yaml
id:
requirement_refs:
acceptance_refs:
files_or_symbols:
implementation_goal:
failure_cases:
verification:
status:
evidence:
```

允许的 status：

```text
planned
implemented
verified
blocked
```

语义：

```text
implemented
= code has been written

verified
= mapped Acceptance has PASS execution evidence
```

禁止仅因为：

```text
code written
test file created
plan step executed
```

就把 status 写成 `verified`。

## 58. Final Verify Todo

Plan 中最终验证步骤必须生成真实 Evidence。

示例：

```yaml
id: final-verify
requirement_refs:
  - REQ-TXN-003
acceptance_refs:
  - A21
status: verified
evidence:
  command: "pytest -q tests/ges6/test_failure_atomicity.py"
  exit_code: 0
  artifact: "audit/ges6/acceptance/....json"
```

如果没有 evidence：

```text
status MUST remain implemented or blocked
```

---

# Part XXV — Requirement Traceability Matrix

## 59. Core Matrix

| Requirement | Invariant / Contract | Acceptance |
|---|---|---|
| REQ-STATE-001 | project.yaml authoritative | A18 |
| REQ-CAP-001 | required/recommended/optional/forbidden semantics | A07, A19 |
| REQ-ANALYZE-001 | zero-LLM deterministic analysis | A01, A02 |
| REQ-ANALYZE-002 | evidence-based language/scripts detection | A25 |
| REQ-CMD-001 | read-only command purity | A17 |
| REQ-RESOLVE-001 | dependency closure | A08 |
| REQ-RESOLVE-002 | single owner | A09 |
| REQ-SOURCE-001 | pinned immutable SHA | A11 |
| REQ-SOURCE-002 | cache provenance verify | A23 |
| REQ-SOURCE-003 | path/symlink safety | A23 |
| REQ-PROJ-001 | collision rejection | A24 |
| REQ-PROJ-AGENTS-001 | marker section ownership | A03 |
| REQ-PROJ-AGENTS-002 | section-only hash | A20 |
| REQ-SPECKIT-001 | adopt existing `.specify` | A04, A26 |
| REQ-RECON-001 | deterministic diff actions | A12, A13 |
| REQ-RECON-002 | managed drift behavior | A14 |
| REQ-TXN-001 | transaction scope | A21 |
| REQ-TXN-002 | preview/stage/commit ordering | A17, A21 |
| REQ-TXN-003 | exact rollback | A21 |
| REQ-REMOVE-001 | hash-safe removal | A15, A22 |
| REQ-REMOVE-002 | no partial remove on conflict | A22 |
| REQ-GUARD-001 | business source zero-byte | A16 |
| REQ-CHECK-001 | read-only full consistency check | A12, A17, A27 |
| REQ-LEGACY-001 | preserve unknown ownership | A05 |

---

# Part XXVI — Implementation Phases

## 60. Phase H0 — Spec / Schema Freeze

先完成：

```text
project v2 schema
repo-profile v2 schema
product-profile v2 schema
install-receipt v2 schema
source-cache-manifest v1
acceptance-evidence v1
```

不得先写 reconciler 再反推 schema。

## 61. Phase H1 — Pure Analyze / Desired State

完成：

```text
read-only analyze
read-only diff
Desired State authority
selection-class semantics
```

验收：

```text
A17
A18
A19
A25
```

## 62. Phase H2 — Projection Ownership Model

完成：

```text
FILE / SECTION / ENTRY
AGENTS section hash
projection collision
```

验收：

```text
A03
A20
A24
```

## 63. Phase H3 — Source + Spec Kit Provenance

完成：

```text
cache manifest
content digest verify
Spec Kit pinned adoption
```

验收：

```text
A11
A23
A26
```

## 64. Phase H4 — Transactional Reconciler

完成：

```text
pre-state snapshot
stage
commit
rollback
receipt atomicity
```

验收：

```text
A12
A13
A14
A21
```

## 65. Phase H5 — Safe Remove

完成：

```text
preflight all removal
drift blocks full remove
```

验收：

```text
A15
A22
```

## 66. Phase H6 — Golden Consumer

只有 synthetic fixture 全 PASS 后，才能运行：

```text
A27
```

---

# Part XXVII — Definition of Done

## 67. Spec Hardening DoD

```text
[ ] 所有实现级 MUST 有 REQ-ID
[ ] 所有 REQ 有 Acceptance
[ ] 所有 Acceptance 有 deterministic oracle
[ ] 所有 failure semantics 有 failure-path test
[ ] project.yaml 是唯一 Desired State
[ ] optional 默认不启用
[ ] read-only commands 0 consumer mutation
[ ] AGENTS hash scope 仅 marker section
[ ] existing .ges 可在 apply failure 后 byte-identical 恢复
[ ] remove 不删除用户修改过的 managed artifact
[ ] cache hit 验证 source provenance + content digest
[ ] projection collision BLOCK
[ ] analyzer scripts / language detection 有明确 evidence rule
[ ] existing .specify adopt contract 明确
[ ] A01-A27 全部有测试或 Golden Consumer evidence
[ ] `SKIPPED` 不计入 PASS
[ ] Plan status 区分 implemented / verified
[ ] Final Verify 必须携带真实 evidence artifact
```

## 68. Composer Bootstrap Release DoD

只有以下全部满足：

```text
A01-A27 required items = PASS
Golden Consumer A27 = PASS
ges check = GES_CHECK_PASS
second apply = GES_RECONCILE_NOOP
business source = byte-identical
failure rollback = verified
remove drift protection = verified
source cache tamper = detected
```

才允许标记：

```text
COMPOSER_BOOTSTRAP_COMPLETE
```

---

# Part XXVIII — Non-Goals

## 69. Alpha.1 仍不实现

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
Plan generation runtime
TDD orchestration
Review orchestration
OS-crash-safe transaction journal
force delete of user-modified managed artifacts
```

---

# Part XXIX — 安全规则

## 70. Supply-chain / Filesystem Safety

必须：

```text
immutable SHA
HTTPS upstream
source provenance verification
cache content digest verification
path traversal rejection
symlink rejection for Alpha.1 selected source content
projection root containment
no writes outside allowed repo paths
no arbitrary post-install execution
business-source denylist
```

---

# Part XXX — Final Architecture Principle

## 71. Frozen Principles

```text
1. Business project stores Desired State, lock and receipt — not GES Core.
2. project.yaml is user intent SOT.
3. Repo Profile is observation, not Desired State.
4. Engineering capabilities are composed, not bundled wholesale.
5. Every engineering domain has one Owner.
6. Optional means disabled by default unless explicitly enabled.
7. Capability dependencies are explicit.
8. Ownership conflicts fail before projection.
9. Source identity means SHA + verified content provenance.
10. Projection ownership has explicit FILE / SECTION / ENTRY scope.
11. Shared files are section/entry managed, never whole-file assumed.
12. User-managed content wins on drift.
13. Preview/read-only commands never mutate the consumer repo.
14. Apply state metadata is part of the same transaction as projection.
15. Rollback restores pre-existing state; it never destroys prior valid state.
16. Remove is drift-safe and preflighted.
17. Business source code is outside Composer write scope.
18. No implementation claim is equivalent to verification evidence.
19. SKIPPED acceptance is not PASS.
20. PRD ambiguity blocks Plan generation instead of being silently inferred.
21. GES consumes engineering artifacts/evidence; it does not reproduce engineering reasoning.
22. Governance happens at outcome boundaries, not every Agent turn.
```

---

# Appendix A — 原 Alpha.1 PRD 的 Hardening Delta

本版本重点补齐以下原先未冻结的系统语义：

```text
Desired State authority
Capability selection class semantics
Command mutation contract
Repo analyzer output contract
Managed artifact ownership type
AGENTS marker hash scope
Projection collision behavior
Source cache provenance
Spec Kit pinned adoption
Transaction boundary
Rollback postcondition
Remove under drift
Acceptance status semantics
Golden Consumer skip semantics
Evidence artifact
PRD → Plan traceability
Plan implemented vs verified state
```

这些修改是 **Specification Hardening**，不是产品架构重构。

# Appendix B — 推荐的后续 Plan 生成输入

新的 `.plan.md` MUST 使用本 PRD，并至少读取：

```text
REQ-STATE-001
REQ-CAP-001
REQ-CMD-001
REQ-PROJ-AGENTS-001/002
REQ-SOURCE-001/002/003
REQ-PROJ-001
REQ-SPECKIT-001
REQ-TXN-001/002/003
REQ-REMOVE-001/002
REQ-CHECK-001
A17-A27
```

Plan Agent MUST NOT 把未验证的陈述写成：

```text
completed
verified
atomic
safe
proven
```

除非存在对应 Evidence。
