---
title: "GES 6.0-alpha.1 Bootstrap Closure PRD"
subtitle: "Spec Kit Functional Runtime + Golden Consumer + Cursor Discovery"
prd_id: "PRD-GES-6.0-A1-BOOTSTRAP-CLOSURE"
version: "1.0"
status: "APPROVED_FOR_PLAN"
product: "GES 6 Composer Bootstrap"
repository: "loudon84/smc-delivery-governance"
branch: "feat/ges-v6.0"
owner: "GES"
reviewers:
  - "Product / Architecture"
  - "Independent Engineering Reviewer"
created_at: "2026-09-16"
updated_at: "2026-09-16"
target_release: "GES 6.0.0-alpha.1 Bootstrap Closure"
change_type:
  - "BROWNFIELD_CHANGE"
  - "INTEGRATION"
  - "BUGFIX"
golden_consumer: 'E:\git\smc-copilot-desktop'
related_docs:
  - "GES-v6.0-alpha.1-Composer-Governance-Backplane-PRD.md"
  - "ges_v6_composer_bootstrap_bdcfcd0f.plan.md"
  - "需求PRD工程模板.md"
supersedes: "仅替代 Alpha.1 Bootstrap 中 Spec Kit Functional、Golden Consumer、Cursor Discovery 三项 Release Gate 定义；不替代 GES 6 总体架构基线。"
---

# GES 6.0-alpha.1 Bootstrap Closure PRD

> 本 PRD 是 GES 6.0-alpha.1 Bootstrap 的 **Release Closure Engineering Contract**。
>
> 本次不扩大 Composer 产品范围，只关闭三个已确认的 Release Blocker：
>
> 1. `SPEC KIT FUNCTIONAL: FAIL / NOT PROVEN`
> 2. `GOLDEN CONSUMER: BLOCKED`
> 3. `CURSOR DISCOVERY: NOT PROVEN`
>
> 本 PRD 遵循 No-Inference Rule：Plan Agent / Coding Agent 不得自行替换 Spec Kit Runtime、不允许把文件存在等价为功能可用、不允许用 Synthetic Fixture 替代真实 Golden Consumer、不允许把目录扫描等价为 Cursor Runtime Discovery。

---

# 0. 文档使用规则

## 0.1 Normative Keywords

本 PRD 使用：

```text
MUST
MUST NOT
SHOULD
SHOULD NOT
MAY
```

任何 `MUST / MUST NOT` 必须映射到 Acceptance、Test 与 Evidence。

## 0.2 No-Inference Rule

如果 Plan / Coding Agent 无法唯一确定：

```text
Spec Kit Runtime 来源
Spec Kit CLI identity
Golden Consumer identity
Golden Consumer 测试工作区
Cursor CLI 选择规则
Cursor Discovery Oracle
允许写入范围
Evidence 与 Commit 绑定方式
PASS / BLOCKED 条件
```

则必须：

```text
report SPEC_SEMANTIC_GAP
block plan / implementation
MUST NOT 自行选择“合理默认值”
```

---

# 1. 一句话目标

让 GES 6.0-alpha.1 在 `E:\git\smc-copilot-desktop` 的 **immutable committed HEAD** 上，通过官方 pinned Spec Kit Runtime、真实 Cursor Agent Runtime Probe 与隔离 Golden Worktree，证明 Spec Kit 可实际工作、Cursor 可实际发现并使用 GES 投影的 Skills、Golden Consumer 全链路通过，同时保证原始 Consumer 工作区和业务源码 0 字节修改。

---

# 2. 背景与问题定义

## 2.1 Current State

当前 `feat/ges-v6.0` 已具备：

```text
Repo Analyzer
Capability Resolver
Source Cache / SHA Pin
Matt / Spec Kit / Superpowers Source Adapter
Cursor / Codex Harness Adapter
Desired State / Lock / Receipt
Collision Protection
Managed Hash
Transaction / Rollback
ges check
ges doctor
Synthetic Acceptance
Golden Bootstrap Runner
```

当前 Bootstrap 已能证明大部分 Composer 结构与事务安全，但 Release Gate 仍存在三项缺口。

### 2.1.1 Spec Kit 当前问题

当前实现生成：

```text
.specify/.ges/runtime/scripts/<command>.py
```

其行为主要是输出固定 JSON / capability 名称。

该实现可以让：

```text
ges doctor
```

得到：

```text
spec_kit_runtime = PASS
```

但它没有证明官方 Spec Kit 的实际 project initialization、template resolution、feature state、Cursor integration skills 与 workflow semantics 可执行。

因此：

```text
STRUCTURAL_PASS != FUNCTIONAL_PASS
```

### 2.1.2 Golden Consumer 当前问题

旧 Golden Consumer：

```text
E:\git\smc-copilot
```

Golden Runner 以主工作区 `git status --porcelain` 非空作为整体 BLOCK 条件，导致真实 consumer 上：

```text
A-BOOT
A-CHECK
A-DOCTOR
A-CURSOR
A-IDEMP
```

全部无法执行。

新的 Golden Consumer 冻结为：

```text
E:\git\smc-copilot-desktop
```

Release Acceptance 必须针对其 **committed HEAD**，而不是依赖主 checkout 必须 clean。

### 2.1.3 Cursor Discovery 当前问题

当前 A-CURSOR 只检查：

```text
.agents/skills/<name>/
```

或 `SKILL.md` 文件存在。

这只能证明：

```text
projection exists
```

不能证明：

```text
Cursor Agent runtime discovered the skill
```

## 2.2 Problem

```text
P-001:
GES 自己生成并验证自己的 Spec Kit stub，
导致 runtime smoke 存在 self-validation false positive。

P-002:
Golden Consumer 验收与主工作区 clean 状态耦合，
导致存在真实代码但 Release Gate 无法执行。

P-003:
Cursor Discovery 使用 filesystem existence 作为 Oracle，
无法证明 Cursor Agent Runtime 实际加载、发现或可调用 Skill。
```

## 2.3 Impact

```text
工程影响：
无法对 BOOTSTRAP_ALPHA_READY 做可信声明。

AI Coding 影响：
Cursor 可能看到投影文件，但无法确认 Spec Kit / Matt / Superpowers
是否作为 Agent Skills 真正进入运行时。

治理影响：
Synthetic Evidence 可以绿色，但 Real-world Evidence 仍然 BLOCKED。

发布影响：
Release Gate 缺少可独立复验的 Runtime Evidence。
```

---

# 3. Scope

## 3.1 In Scope

```text
SCOPE-001
替换当前 Spec Kit stub runtime 为官方 pinned Spec Kit CLI staging 输出。

SCOPE-002
将 Spec Kit Cursor integration 冻结为官方 integration key:
cursor-agent

SCOPE-003
将 selected Spec Kit Cursor Skills 投影为官方 staging 生成结果，
不得由 GES 自行重写 Skill 方法论正文。

SCOPE-004
增加 Spec Kit CLI identity / version / functional readiness 验证。

SCOPE-005
Golden Consumer 改为：
E:\git\smc-copilot-desktop

SCOPE-006
Golden Acceptance 使用 consumer committed HEAD 创建隔离 detached worktree，
主工作区 dirty 不再自动 BLOCK。

SCOPE-007
增加真实 Cursor CLI Runtime Discovery Probe。

SCOPE-008
增加一次 bounded Spec Kit functional smoke，
由 Cursor Agent 在 disposable Golden worktree 中实际使用 speckit-specify。

SCOPE-009
Evidence 必须绑定：
GES commit SHA + Consumer commit SHA + Cursor CLI version +
Spec Kit source SHA + Specify CLI version。
```

## 3.2 Out of Scope

```text
NON-GOAL-001
MUST NOT 增加新的 Matt / Spec Kit / Superpowers capability。

NON-GOAL-002
MUST NOT 实现 Spec Kit tasks / implement / converge。

NON-GOAL-003
MUST NOT 改变 Single Owner：
Matt = Engineering Disciplines
Spec Kit = Intent
Superpowers = Execution

NON-GOAL-004
MUST NOT 改写 GES 6 Composer / Governance Backplane 总体架构。

NON-GOAL-005
MUST NOT 在 Golden Acceptance 中测试未提交的 consumer 工作区内容。

NON-GOAL-006
MUST NOT 用 Synthetic Fixture 替代 Golden Consumer。

NON-GOAL-007
MUST NOT 把“目录存在”“SKILL.md 存在”单独作为 Cursor Runtime Discovery PASS。

NON-GOAL-008
MUST NOT 在 Golden Source Workspace
E:\git\smc-copilot-desktop
直接运行 destructive init / functional smoke。
```

## 3.3 Architecture Boundary

| Domain | Owner | Input | Output | 不负责 |
|---|---|---|---|---|
| Engineering discovery | Matt Skills | repo / docs | engineering understanding | Feature Spec SOT |
| Intent / Spec | Spec Kit | feature description / constitution | Spec artifacts | implementation execution |
| Execution | Superpowers | approved spec / plan | code/test/review evidence | feature intent SOT |
| Composition | GES | repo facts / capability catalog | projected capabilities / lock / receipt | Spec/Code reasoning |
| Cursor Runtime | Cursor | project skills / prompt | Agent execution | GES governance truth |
| Release Proof | GES Acceptance | immutable GES + Consumer commits | machine-readable evidence | modifying business source |

---

# 4. Terminology / Domain Model

```text
Official Spec Kit Runtime
= 由 pinned github/spec-kit source identity 对应的 specify-cli
  官方 init / integration renderer 生成的 runtime 与 Cursor skills。

Pinned Spec Kit CLI
= git+https://github.com/github/spec-kit.git
  @1d5106f59e1b148ee23ab136638932dd790ff1b6
  对应 specify-cli version 1.0.8.dev0。

Spec Kit Structural Ready
= 官方 staging 输出成功，选定文件已按 hash 投影，
  但尚未证明 Cursor 实际执行。

Spec Kit Functional Ready
= Cursor Agent 在隔离 Golden worktree 中实际使用
  speckit-specify 完成 bounded smoke，并满足 postconditions。

Golden Source Workspace
= E:\git\smc-copilot-desktop
  只作为 committed HEAD 的来源，不作为 Acceptance mutation target。

Golden Consumer Commit
= Golden Source Workspace 执行 git rev-parse HEAD 得到的 immutable commit。

Golden Test Worktree
= 从 Golden Consumer Commit 创建的 temporary detached git worktree。

Cursor Structural Discovery
= required Skill path + SKILL.md frontmatter 满足 Cursor Agent Skills contract。

Cursor Runtime Discovery
= Cursor Agent CLI 在 Golden Test Worktree 中启动后，
  能通过真实 Agent runtime 识别 required project skills。

Runtime Probe
= 通过 Cursor CLI 执行的黑盒验证，不由 GES 直接解析 SKILL.md 后伪造结果。

PASS
= Acceptance Oracle 实际值等于期望值，且存在对应 Evidence。

BLOCKED
= Acceptance 因前置条件不满足无法执行；BLOCKED != PASS。

FAIL
= Acceptance 已执行但 Oracle 不满足。

STALE_EVIDENCE
= Evidence 的 GES commit 或 Consumer commit 不等于当前 Release Candidate。
```

---

# 5. System Context

## 5.1 Context Diagram

```text
smc-delivery-governance @ GES_HEAD
              │
              │ GES Composer
              ▼
      Spec Kit Source Pin
 github/spec-kit @ immutable SHA
              │
              │ official specify-cli staging
              ▼
    Official Cursor Integration Output
              │
              │ selected projection
              ▼
Golden Test Worktree
(E:\git\smc-copilot-desktop @ CONSUMER_HEAD)
              │
       ┌──────┴────────┐
       ▼               ▼
   ges check       Cursor Agent CLI
                       │
                 Discovery Probe
                       │
                 Spec Kit Smoke
                       ▼
              Machine Evidence
                       │
                       ▼
              Release Gate
```

## 5.2 System Boundary

```text
Inside boundary:
- ges/source_adapters/speckit*
- Spec Kit staging renderer / manifest compare
- ges doctor / preflight
- Golden Bootstrap runner
- Cursor runtime probe
- bootstrap closure evidence writer

Outside boundary:
- Cursor model implementation
- github/spec-kit internal business logic
- smc-copilot-desktop application business logic

External dependency:
- Git
- Python >= 3.11
- uv / uvx
- Cursor Agent CLI
- github/spec-kit pinned source
- network/auth required by Cursor Runtime Probe

Trusted input:
- GES capability catalog
- pinned source SHA
- current GES Git HEAD
- Golden Consumer committed HEAD

Untrusted input:
- current consumer working tree changes
- unmanaged project files
- Cursor model output
- network response
```

---

# 6. Authoritative State / Source of Truth

| State | Role | Type | Authoritative? | Writer | Reader | 自动覆盖 |
|---|---|---|---:|---|---|---:|
| `.ges/project.yaml` | desired capability selection | DESIRED_STATE | YES | GES init/user-confirmed config | Composer | NO after Alpha.1 freeze |
| `.ges/lock.json` | resolved capabilities/source SHA | RESOLVED_STATE | YES | GES | check/doctor | YES only by reconcile |
| `.ges/install-receipt.json` | last applied ownership/hash | LAST_APPLIED_STATE | YES | GES apply | plan/check | YES by successful transaction |
| Spec Kit pinned SHA | upstream identity | RESOLVED_STATE | YES | capabilities/sources catalog | adapter/check | NO at runtime |
| Spec Kit staging output | official generated reference | RUNTIME_STATE | YES for projection content | official specify-cli | SpecKitAdapter | disposable |
| Golden Consumer HEAD | real consumer identity | EVIDENCE_STATE | YES | Git | Golden runner | NO |
| Golden Source dirty state | informational only | OBSERVED_STATE | NO | Git | evidence | NO |
| Golden Test Worktree | test execution state | RUNTIME_STATE | NO | Golden runner | tests | disposable |
| Cursor Runtime Probe output | discovery/runtime observation | EVIDENCE_STATE | YES for Cursor AC | Cursor CLI | evidence parser | NO |
| bootstrap closure evidence | release proof | EVIDENCE_STATE | YES | acceptance runner | release gate | append-only |

Rule:

```text
Golden Source dirty state MUST NOT override Golden Consumer HEAD identity.
Release proof is always against committed HEAD.
```

---

# 7. State Machine

## 7.1 Bootstrap Closure State

```text
UNVERIFIED
   │
   ├─ official Spec Kit staging PASS
   ▼
SPECKIT_STRUCTURAL_READY
   │
   ├─ Cursor structural + runtime discovery PASS
   ▼
CURSOR_RUNTIME_READY
   │
   ├─ Spec Kit bounded functional smoke PASS
   ▼
SPECKIT_FUNCTIONAL_READY
   │
   ├─ full Golden chain PASS
   ▼
GOLDEN_VERIFIED
   │
   ├─ evidence commit binding PASS
   ▼
BOOTSTRAP_ALPHA_READY
```

任何 required acceptance：

```text
FAIL
BLOCKED
SKIPPED
STALE_EVIDENCE
```

均不得进入下一状态。

## 7.2 Recovery

```text
BLOCKED
→ fix prerequisite
→ rerun acceptance from immutable GES_HEAD + CONSUMER_HEAD

FAIL
→ fix implementation
→ new GES commit
→ previous evidence becomes STALE
→ rerun full required chain
```

---

# 8. Data / Schema Contract

## 8.1 New Evidence Schema

```text
schema id:
ges.bootstrap-closure-evidence.v1

additionalProperties:
false
```

Required top-level fields:

```yaml
schema: ges.bootstrap-closure-evidence.v1
run_id: string
started_at: RFC3339
finished_at: RFC3339

ges:
  repository: loudon84/smc-delivery-governance
  branch: string
  commit_sha: 40-char git sha
  product_version: 6.0.0-alpha.1
  distribution_version: string

golden_consumer:
  source_path: 'E:\git\smc-copilot-desktop'
  repo_identity: string
  source_branch: string
  commit_sha: 40-char git sha
  source_worktree_dirty: boolean
  source_worktree_status_digest: sha256
  test_worktree_path: string
  test_worktree_clean_at_start: true

spec_kit:
  repo: https://github.com/github/spec-kit.git
  commit_sha: 1d5106f59e1b148ee23ab136638932dd790ff1b6
  specify_cli_version: 1.0.8.dev0
  integration: cursor-agent
  official_render_manifest_digest: sha256
  projected_manifest_digest: sha256

cursor:
  executable: string
  version: string
  structural_discovery: PASS|FAIL|BLOCKED
  runtime_discovery: PASS|FAIL|BLOCKED

acceptances:
  - acceptance_id: string
    requirement_ids: [string]
    test_ids: [string]
    status: PASS|FAIL|BLOCKED|SKIPPED
    command: string
    exit_code: integer
    oracle:
      type: string
      expected: any
      actual: any
    evidence_files: [string]

release_gate:
  status: PASS|FAIL|BLOCKED
```

## 8.2 Cursor Skill Structural Contract

每个 required Skill：

```text
<skill-root>/<skill-name>/SKILL.md
```

`SKILL.md` 必须有 YAML frontmatter：

```yaml
name: <skill-name>
description: <non-empty>
```

规则：

```text
name MUST match parent directory name
name MUST use lowercase letters / numbers / hyphens
description MUST be non-empty
```

Required probe set：

```text
grill-with-docs
speckit-specify
writing-plans
```

Expected roots：

```text
grill-with-docs
  → .agents/skills/grill-with-docs/SKILL.md

speckit-specify
  → .cursor/skills/speckit-specify/SKILL.md

writing-plans
  → .agents/skills/writing-plans/SKILL.md
```

---

# 9. Requirement Units

# REQ-SPECKIT-FUNC-001 — Official Pinned Spec Kit Staging Renderer

## Goal

消除 GES 自生成 stub runtime 的 self-validation，使 Spec Kit projection 由官方 pinned implementation 产生。

## Normative Requirement

```text
MUST use official specify-cli source:
git+https://github.com/github/spec-kit.git
@1d5106f59e1b148ee23ab136638932dd790ff1b6

MUST verify:
specify-cli version == 1.0.8.dev0

MUST use integration:
cursor-agent

MUST use Python script mode:
--script py

MUST execute official init in an isolated staging directory.

MUST NOT run official specify init directly against Golden Source Workspace.

MUST NOT generate replacement resolver_script() stubs
as the functional runtime.

MUST derive selected Cursor Spec Kit skills from official staging output.

MUST project only selected GES capabilities:
constitution
specify
clarify
plan

MUST preserve user-owned Spec / constitution / extension content
according to ownership rules.
```

Canonical staging command semantics：

```text
specify init
--here
--force
--non-interactive
--ignore-agent-tools
--integration cursor-agent
--script py
```

The CLI binary used by the renderer MUST resolve to the pinned source identity above.

## Inputs

```text
Spec Kit source SHA
selected capabilities
consumer observed .specify state
consumer observed .cursor state
GES receipt ownership
```

## Preconditions

```text
PRE-SK-001 Python >= 3.11
PRE-SK-002 Git available
PRE-SK-003 pinned Spec Kit source resolvable or verified local cache available
PRE-SK-004 staging path outside consumer repository
```

## Authoritative State

```text
SOT:
official staging output generated from pinned source

Observed:
consumer current files

Derived:
selected projection manifest
```

## State Transition

```text
Before:
current desired projection may contain GES stub runtime

Event:
compose / init with updated SpecKitAdapter

After:
Desired State contains official selected Cursor integration artifacts
and required shared Spec Kit runtime;
stub runtime is no longer authoritative.
```

## Allowed Side Effects

```text
ALLOW:
- temporary staging directory write
- source cache read/write
- network to fetch pinned source if cache missing
- target repo writes only during existing GES transaction
```

## Forbidden Side Effects

```text
DENY:
- business source write
- original user specs write during staging
- direct official init on target repo
- global tool installation by ges init
```

## Ownership Scope

```text
FILE:
- GES-projected official Spec Kit managed infrastructure
- .cursor/skills/speckit-{constitution,specify,clarify,plan}/**

USER_OWNED:
- specs/**
- existing user-authored constitution
- unrelated .cursor/**
- unrelated .specify custom content
```

## Idempotency

```text
first run:
official manifest projected

second run:
same pin + same consumer observed state
→ projected manifest digest identical
→ GES_RECONCILE_NOOP
```

## Failure Semantics

```text
F-SK-001
trigger: pinned CLI cannot execute
expected state: 0 consumer mutation
error: SPEC_KIT_OFFICIAL_RENDER_FAILED
rollback: not required because failure occurs pre-commit
retryable: YES

F-SK-002
trigger: specify-cli version != 1.0.8.dev0
expected state: 0 consumer mutation
error: SPEC_KIT_CLI_IDENTITY_MISMATCH
rollback: none
retryable: after tool/source correction

F-SK-003
trigger: official staged output missing selected skill
expected state: 0 consumer mutation
error: SPEC_KIT_RUNTIME_INCOMPLETE
rollback: none

F-SK-004
trigger: selected official target collides with unmanaged different file
expected state: 0 consumer mutation
error: UNMANAGED_PATH_CONFLICT
rollback: none
```

## Postconditions

```text
POST-SK-001
No selected Spec Kit Skill is produced by GES handwritten wrapper content.

POST-SK-002
Every projected selected Spec Kit Skill hash equals
the corresponding official staging output hash.

POST-SK-003
official_render_manifest_digest is persisted in Evidence.

POST-SK-004
business source digest unchanged.
```

## Invariants

```text
INV-SK-001
Pinned source identity uniquely determines official renderer.

INV-SK-002
Official staging executes outside consumer repo.

INV-SK-003
Spec Kit selected projection is reproducible from:
source SHA + integration + selected capability set.
```

## Error Codes

```text
SPEC_KIT_OFFICIAL_RENDER_FAILED
SPEC_KIT_CLI_IDENTITY_MISMATCH
SPEC_KIT_RUNTIME_INCOMPLETE
UNMANAGED_PATH_CONFLICT
```

## Acceptance

```text
A-SK-001
A-SK-002
A-SK-003
```

## Evidence

```text
required test:
TEST-A-SK-001
TEST-A-SK-002
TEST-A-SK-003

required artifact:
official staging manifest
projection manifest
hash comparison report

required runtime output:
specify version / feature identity
```

---

# REQ-SPECKIT-FUNC-002 — Remove GES Stub Runtime Authority

## Goal

避免旧 Alpha.1 stub 与官方 Spec Kit runtime 同时存在并产生双重事实源。

## Normative Requirement

```text
MUST remove from Desired State:
.specify/.ges/runtime/scripts/{constitution,specify,clarify,plan}.py
when those files are GES-owned old stub artifacts.

MUST remove obsolete GES-owned Spec Kit wrappers under:
.agents/skills/speckit-*/

MUST NOT delete an old path if GES cannot prove ownership.

If old GES-owned file current hash != last_applied_hash:
MUST BLOCK with MANAGED_CONTENT_MODIFIED.

Capability selection MUST remain frozen;
projection implementation migration MUST NOT be treated as user reconfiguration.
```

## Inputs

```text
current receipt
current file hashes
new official projection
```

## Preconditions

```text
PRE-SKM-001 prior receipt is readable when old managed artifacts exist
```

## Authoritative State

```text
SOT: current install receipt for old ownership
Desired: official new projection
```

## State Transition

```text
old GES-owned stub
→ transactional removal
→ official Cursor Spec Kit projection
```

## Allowed Side Effects

```text
Only GES-owned old stub paths may be removed.
```

## Forbidden Side Effects

```text
Unowned / drifted old paths MUST NOT be deleted.
```

## Ownership Scope

```text
FILE
```

## Idempotency

```text
after migration:
second init → NOOP
```

## Failure Semantics

```text
drifted old managed artifact
→ MANAGED_CONTENT_MODIFIED
→ 0 mutation
```

## Postconditions

```text
No GES-owned obsolete stub remains in managed receipt.
No obsolete wrapper remains GES-owned.
```

## Invariants

```text
INV-SKM-001
Migration never uses last-writer-wins.
```

## Acceptance

```text
A-SKM-001
A-SKM-002
```

## Evidence

```text
before / after managed artifact list
T0 / after tree digest
```

---

# REQ-CURSOR-001 — Cursor Structural Discovery Contract

## Goal

保证 GES 投影满足 Cursor Agent Skills 的可发现文件协议。

## Normative Requirement

```text
MUST validate project-level Cursor skill roots:
.agents/skills/
.cursor/skills/

MUST validate required SKILL.md frontmatter.

MUST validate name == parent directory.

MUST validate required probe set:
grill-with-docs
speckit-specify
writing-plans

MUST NOT mark Cursor Runtime Discovery PASS
based only on this structural validation.
```

## Inputs

```text
Golden Test Worktree projected files
```

## Preconditions

```text
GES apply PASS
```

## Authoritative State

```text
Observed:
filesystem

Derived:
structural_discovery status
```

## State Transition

```text
projected
→ structurally discoverable
```

## Side Effects

```text
0 mutation
```

## Ownership Scope

```text
NONE
```

## Failure Semantics

```text
missing skill:
CURSOR_SKILL_STRUCTURE_INVALID

invalid frontmatter:
CURSOR_SKILL_STRUCTURE_INVALID
```

## Postconditions

```text
all required probe skills structurally conform
```

## Invariants

```text
INV-CURSOR-001
Structural PASS alone never satisfies A-CURSOR-RUNTIME.
```

## Acceptance

```text
A-CURSOR-STRUCT-001
```

## Evidence

```text
path list
frontmatter parse result
skill identity list
```

---

# REQ-CURSOR-002 — Real Cursor Runtime Discovery Probe

## Goal

证明 Cursor Agent Runtime 实际启动并能识别 GES 投影的 project skills。

## Normative Requirement

Cursor executable resolution MUST use this deterministic precedence:

```text
1. GES_CURSOR_CLI absolute executable path, if explicitly set
2. "agent" found in PATH
3. "cursor-agent" found in PATH
4. otherwise CURSOR_CLI_NOT_FOUND
```

Runtime Probe MUST：

```text
run inside Golden Test Worktree
use non-interactive print mode
use Ask/read-only mode when supported by selected executable
request structured JSON output
record Cursor CLI version
record exact command argv
record exit code
```

Probe target set：

```text
grill-with-docs
speckit-specify
writing-plans
```

Probe prompt MUST require the Agent to return a machine-readable object:

```json
{
  "probe": "GES_CURSOR_DISCOVERY_PROBE_V1",
  "skills": {
    "grill-with-docs": true,
    "speckit-specify": true,
    "writing-plans": true
  }
}
```

GES evidence parser MUST NOT infer missing values.

Expected：

```text
all three == true
```

## Inputs

```text
Golden Test Worktree
Cursor executable
project skills
```

## Preconditions

```text
PRE-CURSOR-001 structural discovery PASS
PRE-CURSOR-002 Cursor authentication/session available
PRE-CURSOR-003 network/runtime prerequisites available
```

## Authoritative State

```text
Observed:
Cursor CLI runtime output

Evidence SOT:
raw stdout/stderr + parsed JSON + command + exit code
```

## State Transition

```text
STRUCTURAL_READY
→ runtime probe
→ CURSOR_RUNTIME_READY
```

## Allowed Side Effects

```text
Ask-mode probe:
0 file write required
network MAY be used by Cursor service
Cursor local runtime cache MAY change outside repo
```

## Forbidden Side Effects

```text
MUST NOT modify Golden Source Workspace.
MUST NOT modify business source in Golden Test Worktree.
```

## Ownership Scope

```text
NONE
```

## Idempotency

```text
same worktree + same required skills:
repeat probe MUST still report all required skills true.
```

## Failure Semantics

```text
F-CURSOR-001
trigger: no CLI
error: CURSOR_CLI_NOT_FOUND
status: BLOCKED

F-CURSOR-002
trigger: CLI auth/network unavailable
error: CURSOR_RUNTIME_UNAVAILABLE
status: BLOCKED

F-CURSOR-003
trigger: CLI exits 0 but one required skill false/missing
error: CURSOR_DISCOVERY_FAILED
status: FAIL

F-CURSOR-004
trigger: output not parseable as expected schema
error: CURSOR_DISCOVERY_OUTPUT_INVALID
status: FAIL
```

## Postconditions

```text
runtime_discovery = PASS
raw output retained
business source digest unchanged
```

## Invariants

```text
INV-CURSOR-002
Filesystem existence cannot substitute runtime output.

INV-CURSOR-003
BLOCKED / SKIPPED != PASS.
```

## Acceptance

```text
A-CURSOR-RUNTIME-001
A-CURSOR-RUNTIME-002
```

## Evidence

```text
cursor --version output
probe command
stdout
stderr
parsed result
before/after source digest
```

---

# REQ-SPECKIT-FUNC-003 — Bounded End-to-End Spec Kit Functional Smoke

## Goal

从“Cursor 能发现 Skill”进一步证明 `speckit-specify` 能在真实 Brownfield consumer 中执行最小 Feature Spec 工作流。

## Normative Requirement

Functional Smoke MUST run only in Golden Test Worktree.

Before launching Cursor, the test environment MUST provide the pinned Spec Kit CLI identity required by the official skill.

The smoke feature directory MUST be unique per run:

```text
specs/_ges-smoke/<run_id>
```

The process environment MUST explicitly set：

```text
SPECIFY_FEATURE_DIRECTORY=specs/_ges-smoke/<run_id>
```

Cursor prompt MUST explicitly require：

```text
Use the speckit-specify skill.
Create only a specification for the smoke feature.
Do not implement code.
Do not modify business source.
```

Smoke feature description MUST be deterministic：

```text
"GES bootstrap acceptance smoke:
define a non-production diagnostic preference
with one actor, one setting and one success criterion."
```

Expected artifacts：

```text
specs/_ges-smoke/<run_id>/spec.md
specs/_ges-smoke/<run_id>/checklists/requirements.md
.specify/feature.json
```

Expected `.specify/feature.json`：

```json
{
  "feature_directory": "specs/_ges-smoke/<run_id>"
}
```

`spec.md` MUST：

```text
exist
be non-empty
contain no unresolved template placeholder from the active spec template
contain at least one Functional Requirement
contain at least one Success Criterion
```

MUST NOT require code implementation.

## Inputs

```text
official projected speckit-specify skill
pinned specify-cli
Cursor runtime
Golden Test Worktree
```

## Preconditions

```text
A-CURSOR-RUNTIME-001 PASS
A-SK-001 PASS
```

## Authoritative State

```text
Runtime output + generated Spec artifacts
```

## State Transition

```text
CURSOR_RUNTIME_READY
→ invoke speckit-specify
→ generated bounded spec
→ SPECKIT_FUNCTIONAL_READY
```

## Allowed Side Effects

Only inside Golden Test Worktree：

```text
ALLOW:
specs/_ges-smoke/<run_id>/**
.specify/feature.json
Spec Kit-owned metadata required by this invocation
```

## Forbidden Side Effects

```text
DENY:
apps/**
src/**
services/**
packages/** business code
contracts/** business contract
Golden Source Workspace
GES repository source
```

## Ownership Scope

```text
TEST_GENERATED / disposable
```

## Idempotency

Each run uses a unique run_id. Re-running the same Release Candidate MUST produce the same acceptance semantics; text bytes MAY vary due to model generation and are not used as equality Oracle.

## Failure Semantics

```text
F-SKF-001
Cursor cannot invoke / use speckit-specify
→ SPEC_KIT_FUNCTIONAL_SMOKE_FAILED

F-SKF-002
required artifacts absent
→ SPEC_KIT_FUNCTIONAL_SMOKE_FAILED

F-SKF-003
business source digest changed
→ BUSINESS_SOURCE_MODIFICATION_FORBIDDEN

F-SKF-004
unexpected write outside allowlist
→ GOLDEN_UNEXPECTED_MUTATION
```

## Postconditions

```text
required artifacts exist
business source unchanged
unexpected mutation set = empty
functional_smoke = PASS
```

## Invariants

```text
INV-SKF-001
Doctor cannot mark Spec Kit Functional Ready without this Runtime Evidence.

INV-SKF-002
A-SPECKIT structural test cannot substitute A-SKF functional test.
```

## Acceptance

```text
A-SKF-001
A-SKF-002
A-SKF-003
```

## Evidence

```text
Cursor command/output
generated artifact paths
artifact hashes
mutation allowlist report
business-source before/after digest
```

---

# REQ-GOLDEN-001 — Golden Consumer Identity and Detached Worktree

## Goal

让 Golden Consumer 可稳定执行真实验收，同时不要求开发者主工作区必须 clean。

## Normative Requirement

Golden Source Workspace MUST be：

```text
E:\git\smc-copilot-desktop
```

Runner MUST resolve：

```text
CONSUMER_HEAD = git -C E:\git\smc-copilot-desktop rev-parse HEAD
SOURCE_BRANCH = git symbolic-ref --short -q HEAD
SOURCE_DIRTY = git status --porcelain
```

`SOURCE_DIRTY`：

```text
MUST be recorded
MUST NOT automatically BLOCK Release Acceptance
MUST NOT be included in tested content
```

Runner MUST create：

```text
temporary detached git worktree
from CONSUMER_HEAD
```

Equivalent Git semantics：

```text
git worktree add --detach <temp_path> <CONSUMER_HEAD>
```

Golden tests MUST execute only inside `<temp_path>`.

## Inputs

```text
E:\git\smc-copilot-desktop
current committed HEAD
```

## Preconditions

```text
PRE-GOLDEN-001 source path exists
PRE-GOLDEN-002 valid Git repository
PRE-GOLDEN-003 HEAD resolves to 40-char commit
PRE-GOLDEN-004 temporary path writable
```

## Authoritative State

```text
Consumer SOT:
CONSUMER_HEAD

Informational:
SOURCE_DIRTY
```

## State Transition

```text
source repository
→ resolve immutable HEAD
→ create detached worktree
→ verify clean
→ run acceptance
→ write evidence
→ remove worktree
```

## Allowed Side Effects

```text
source repo .git/worktrees metadata MAY change due git worktree lifecycle
temporary worktree MAY be written
GES audit directory MAY receive evidence
```

## Forbidden Side Effects

```text
Golden Source Workspace tracked file bytes MUST NOT change.
Uncommitted user changes MUST NOT be copied into Golden Test Worktree.
```

## Ownership Scope

```text
RESOURCE:
temporary Golden Test Worktree
```

## Idempotency

Repeated acceptance against same GES_HEAD + CONSUMER_HEAD MUST create independent run_id worktrees and must not depend on source workspace dirty files.

## Failure Semantics

```text
invalid source path
→ GOLDEN_CONSUMER_NOT_FOUND
→ BLOCKED

HEAD unresolved
→ GOLDEN_CONSUMER_HEAD_UNRESOLVED
→ BLOCKED

worktree creation fails
→ GOLDEN_WORKTREE_CREATE_FAILED
→ BLOCKED

new worktree not clean at start
→ GOLDEN_WORKTREE_DIRTY
→ FAIL
```

## Postconditions

```text
test_worktree_clean_at_start = true
consumer_commit recorded
source dirty status digest recorded
original tracked file tree unchanged
```

## Invariants

```text
INV-GOLDEN-001
Golden Acceptance always tests an immutable Git commit.

INV-GOLDEN-002
Developer uncommitted changes never influence Release Evidence.

INV-GOLDEN-003
Synthetic Fixture never substitutes Golden Worktree.
```

## Acceptance

```text
A-GOLDEN-001
A-GOLDEN-002
```

## Evidence

```text
source path
source branch
source dirty flag + status digest
consumer HEAD
test worktree path
clean-at-start proof
original source tree before/after digest
```

---

# REQ-GOLDEN-002 — Full Golden Bootstrap Chain

## Goal

将此前被 dirty checkout 阻断的真实链路变成可执行且可判定的 Release Gate。

## Normative Requirement

Golden chain MUST execute in this order：

```text
1. resolve consumer HEAD
2. create detached test worktree
3. ges doctor --preflight
4. ges init <test_worktree> --yes
5. ges check <test_worktree>
6. ges doctor <test_worktree>
7. Cursor structural discovery
8. Cursor runtime discovery
9. Spec Kit functional smoke
10. verify business source unchanged
11. verify user-owned baseline content preserved
12. execute second ges init <test_worktree> --yes
13. require GES_RECONCILE_NOOP
14. write evidence
15. verify evidence commit binding
16. cleanup worktree
```

Matt setup semantics remain from the Bootstrap baseline.

If initial `ges doctor` after install reports：

```text
BOOTSTRAP_PENDING
```

the Golden chain MUST execute the defined Matt project bootstrap step before final doctor.

Final doctor MUST be：

```text
READY
```

Second init MUST be a real CLI invocation, not only：

```text
compose().plan.noop
```

## Inputs

```text
immutable Golden Test Worktree
```

## Preconditions

```text
REQ-GOLDEN-001 PASS
```

## Authoritative State

```text
Final release truth:
evidence from actual CLI/runtime execution
```

## State Transition

```text
UNINITIALIZED
→ INSTALLED
→ BOOTSTRAP_PENDING
→ READY
→ RUNTIME_VERIFIED
→ SECOND_INIT_NOOP
→ GOLDEN_VERIFIED
```

## Allowed Side Effects

Only Golden Test Worktree and GES audit evidence.

## Forbidden Side Effects

```text
original Golden Source tracked files
business source outside explicit smoke allowlist
```

## Idempotency

```text
second ges init:
exit 0
stdout contains GES_RECONCILE_NOOP
0 managed content mutation
```

## Failure Semantics

Any required step：

```text
FAIL/BLOCKED/SKIPPED
→ Golden Release Gate != PASS
→ process exit != 0
```

## Postconditions

```text
final doctor READY
Cursor runtime discovery PASS
Spec Kit functional smoke PASS
second init NOOP
business source unchanged
evidence commit binding PASS
```

## Invariants

```text
INV-GOLDEN-004
No synthetic result can upgrade a Golden status.

INV-GOLDEN-005
Second-init acceptance is based on real CLI execution.
```

## Acceptance

```text
A-GOLDEN-003
A-GOLDEN-004
A-GOLDEN-005
A-IDEMP-CLI-001
```

## Evidence

```text
command-by-command execution records
stdout/stderr
exit codes
tree digests
doctor payloads
check result
```

---

# REQ-EVID-001 — Immutable Release Evidence Binding

## Goal

避免 Evidence 记录 parent SHA / working-tree implementation，而不能证明最终 Release Candidate commit。

## Normative Requirement

Evidence MUST record current：

```text
GES_HEAD = git rev-parse HEAD in smc-delivery-governance
CONSUMER_HEAD = immutable Golden Consumer commit
```

Before Release Gate PASS：

```text
evidence.ges.commit_sha MUST equal current GES_HEAD
evidence.golden_consumer.commit_sha MUST equal tested CONSUMER_HEAD
```

If mismatch：

```text
status = STALE_EVIDENCE
Release Gate = BLOCKED
process exit != 0
```

Evidence MUST NOT convert whole-suite pytest exit 0 into automatic per-AC PASS.

Each required AC MUST have its own executed record.

## Inputs

```text
acceptance execution records
current GES_HEAD
tested CONSUMER_HEAD
```

## Preconditions

```text
all required tests executed or explicitly BLOCKED
```

## Authoritative State

```text
Evidence file
```

## Side Effects

```text
ALLOW:
audit/ges6/bootstrap-closure/<run_id>.json
related raw evidence files

DENY:
editing prior evidence record in-place
```

## Ownership Scope

```text
GENERATED_ONLY
```

## Failure Semantics

```text
commit mismatch
→ EVIDENCE_COMMIT_MISMATCH
→ BLOCKED

missing AC evidence
→ EVIDENCE_INCOMPLETE
→ BLOCKED
```

## Postconditions

```text
all required AC records have command/exit/oracle/evidence
release gate computed from records
```

## Invariants

```text
INV-EVID-001
SKIPPED != PASS
BLOCKED != PASS
STALE_EVIDENCE != PASS

INV-EVID-002
Suite green != per-acceptance evidence.

INV-EVID-003
Evidence proves immutable commits, not working tree state.
```

## Acceptance

```text
A-EVID-001
A-EVID-002
```

---

# 10. Side-Effect Contract

| Operation | Original Consumer Write | Golden Test Worktree Write | Network | Cache | Business Source |
|---|---:|---:|---:|---:|---:|
| resolve Golden HEAD | NO | NO | NO | NO | NO |
| create detached worktree | Git metadata only | YES create | NO | NO | NO |
| Spec Kit official staging render | NO | NO | MAY | MAY | NO |
| `ges init` on Golden Test Worktree | NO | YES | MAY | MAY | MUST remain unchanged |
| Cursor structural probe | NO | NO | NO | NO | NO |
| Cursor runtime discovery | NO | NO | YES | MAY | NO |
| Spec Kit functional smoke | NO | YES allowlist only | YES | MAY | MUST remain unchanged |
| second `ges init` | NO | expected NOOP | MAY | MAY | NO |
| evidence write | NO | NO | NO | NO | NO |
| cleanup worktree | Git metadata only | DELETE temp | NO | NO | NO |

Read-only scope clarification：

```text
"Original Consumer Write = NO"
means no tracked or untracked file under
E:\git\smc-copilot-desktop
may be created/modified/deleted by the Golden Acceptance runner.

Git worktree administrative metadata under .git/worktrees is allowed.
```

---

# 11. Ownership Contract

## 11.1 Spec Kit Ownership

```text
GES_MANAGED_FILE:
.cursor/skills/speckit-constitution/**
.cursor/skills/speckit-specify/**
.cursor/skills/speckit-clarify/**
.cursor/skills/speckit-plan/**
official shared runtime files selected from staging manifest

USER_OWNED:
specs/**
existing user constitution
unrelated .cursor/**
unrelated .agents/**
unrelated .specify custom files
```

## 11.2 Drift

```text
current managed hash == last_applied_hash
→ safe migration/update/remove

current managed hash != last_applied_hash
→ MANAGED_CONTENT_MODIFIED
→ BLOCK
→ 0 mutation
```

## 11.3 Golden Test Ownership

```text
Golden Test Worktree:
TEST_RESOURCE

Smoke artifacts:
TEST_GENERATED

Original Consumer:
USER_OWNED / read-only
```

---

# 12. Hash / Identity Contract

## 12.1 File Identity

Managed file identity：

```text
SHA256(raw file bytes)
```

No newline normalization.

## 12.2 Manifest Identity

For a set of files：

```text
for each relative path sorted lexicographically:
  relative_path UTF-8
  + NUL
  + SHA256(file_bytes)
  + LF

manifest_digest = SHA256(concatenated records)
```

Path rules：

```text
relative path uses forward slash
case preserved
no "." / ".."
no absolute path
```

## 12.3 Dirty Status Identity

```text
status_bytes = exact UTF-8 stdout of:
git status --porcelain

source_worktree_status_digest = SHA256(status_bytes)
```

## 12.4 Business Source Identity

Reuse existing GES business source snapshot contract：

```text
relative path
size
sha256(raw bytes)
```

Before / after map MUST be exactly equal.

---

# 13. Transaction Contract

## 13.1 Spec Kit Projection

Official staging render occurs before consumer T0 mutation.

Existing GES transaction remains authoritative：

```text
plan
→ stage
→ validate
→ snapshot T0
→ commit projection
→ ges check
→ business-source verify
→ receipt
```

New official Spec Kit files and old stub removal MUST participate in the same transaction.

If transaction fails：

```text
AfterRollback(managed_scope) == T0
```

## 13.2 Golden Acceptance Transaction

Golden Acceptance is not a business transaction; it is a disposable test lifecycle：

```text
create worktree
→ run
→ capture evidence
→ cleanup
```

Evidence MUST be written before cleanup.

If cleanup fails：

```text
GOLDEN_WORKTREE_CLEANUP_FAILED
Release Gate = FAIL
evidence retains test_worktree_path for manual cleanup
```

---

# 14. Failure / Conflict Contract

| Conflict / Failure | Detection | Behavior | Error | Mutation |
|---|---|---|---|---:|
| pinned specify CLI mismatch | version identity check | BLOCK | SPEC_KIT_CLI_IDENTITY_MISMATCH | 0 |
| official render fails | subprocess exit | BLOCK | SPEC_KIT_OFFICIAL_RENDER_FAILED | 0 consumer |
| official selected file missing | manifest validation | BLOCK | SPEC_KIT_RUNTIME_INCOMPLETE | 0 |
| unmanaged same path/different content | collision check | BLOCK | UNMANAGED_PATH_CONFLICT | 0 |
| old stub user drift | receipt/hash | BLOCK | MANAGED_CONTENT_MODIFIED | 0 |
| Golden source dirty | `git status` | RECORD, continue with HEAD | none | 0 source |
| Golden HEAD missing | git | BLOCK | GOLDEN_CONSUMER_HEAD_UNRESOLVED | 0 |
| Golden worktree dirty at start | git | FAIL | GOLDEN_WORKTREE_DIRTY | disposable |
| Cursor CLI absent | executable resolution | BLOCK | CURSOR_CLI_NOT_FOUND | 0 |
| Cursor runtime unavailable | CLI exit/auth | BLOCK | CURSOR_RUNTIME_UNAVAILABLE | 0 |
| Cursor skill missing at runtime | probe oracle | FAIL | CURSOR_DISCOVERY_FAILED | 0 |
| Spec Kit smoke writes business code | before/after digest | FAIL | BUSINESS_SOURCE_MODIFICATION_FORBIDDEN | disposable |
| second init changes files | actual CLI + tree diff | FAIL | GES_IDEMPOTENCY_FAILED | disposable |
| evidence commit mismatch | final gate | BLOCK | EVIDENCE_COMMIT_MISMATCH | 0 |

---

# 15. Compatibility / Migration

## 15.1 Existing Alpha.1 Stub State

Known old projection：

```text
.specify/.ges/commands/**
.specify/.ges/runtime/scripts/**
.agents/skills/speckit-*/SKILL.md
```

Migration rule：

```text
GES-owned + unmodified
→ REMOVE old projection transactionally

GES-owned + modified
→ MANAGED_CONTENT_MODIFIED

ownership unknown
→ PRESERVE + REPORT
→ MUST NOT DELETE
```

New Cursor Spec Kit target：

```text
.cursor/skills/speckit-<command>/SKILL.md
```

Capability IDs remain：

```text
speckit.constitution
speckit.specify
speckit.clarify
speckit.plan
```

Therefore：

```text
this migration is projection implementation migration
NOT capability reconfiguration
```

`RECONFIGURE_NOT_SUPPORTED` MUST NOT fire solely because path/layout changed while selected capability set is unchanged.

---

# 16. External Dependency Contract

## 16.1 Spec Kit

```text
name:
github/spec-kit

repo:
https://github.com/github/spec-kit.git

immutable identity:
1d5106f59e1b148ee23ab136638932dd790ff1b6

specify-cli version:
1.0.8.dev0

integration:
cursor-agent

required output:
.cursor/skills/speckit-<command>/SKILL.md
shared .specify runtime/infrastructure

failure:
BLOCK
```

## 16.2 Cursor

```text
name:
Cursor Agent CLI

executable resolution:
GES_CURSOR_CLI absolute path
→ agent
→ cursor-agent

version:
record exact runtime version in evidence

required feature:
non-interactive execution
structured output
project skill loading

failure:
BLOCK if runtime unavailable
```

## 16.3 Git

```text
required:
rev-parse
status --porcelain
worktree add --detach
worktree remove
```

---

# 17. Security Contract

| Threat | Control | Acceptance |
|---|---|---|
| Official `specify init --force` overwrites consumer | only run in isolated staging | A-SK-001 |
| Golden runner destroys active workspace | use detached temp worktree | A-GOLDEN-001 |
| Uncommitted developer files enter release proof | test committed HEAD only | A-GOLDEN-002 |
| Cursor smoke edits business source | before/after digest + mutation allowlist | A-SKF-003 |
| Unmanaged Skill overwritten | collision contract | A-SK-003 |
| Path traversal from staged manifest | existing containment guard | NEG-SK-001 |
| Evidence proves wrong commit | final commit binding | A-EVID-001 |
| Cursor CLI prompt executes uncontrolled changes | run only in disposable worktree | A-SKF-003 |

Credentials：

```text
Cursor auth credentials MUST NOT be written to evidence.
Environment variable values MUST NOT be dumped.
Only executable/version/auth availability status may be recorded.
```

---

# 18. Observability

Required stages：

```text
SPECKIT_CLI_VERIFY
SPECKIT_OFFICIAL_RENDER
SPECKIT_MANIFEST_COMPARE
GOLDEN_RESOLVE
GOLDEN_WORKTREE_CREATE
GES_PREFLIGHT
GES_INIT
GES_CHECK
GES_DOCTOR
CURSOR_STRUCTURAL_DISCOVERY
CURSOR_RUNTIME_DISCOVERY
SPECKIT_FUNCTIONAL_SMOKE
GES_SECOND_INIT
EVIDENCE_WRITE
GOLDEN_WORKTREE_CLEANUP
RELEASE_GATE
```

Each stage MUST log：

```text
run_id
stage
status
started_at
finished_at
exit_code if process
error_code if failure
```

Logs MUST NOT contain secrets or full prompt credentials.

---

# 19. Acceptance Contract

## A-SK-001 — Official Pinned Renderer

```text
Given:
Spec Kit pin = 1d5106f...

When:
official staging init executes

Then:
exit = 0
specify-cli version = 1.0.8.dev0
integration = cursor-agent
selected official skills exist

Oracle:
official_render.status == PASS
```

## A-SK-002 — Official Projection Hash Parity

```text
For each selected Spec Kit skill:
projected file hash == official staging file hash

Oracle:
mismatch_count == 0
```

## A-SK-003 — Official Render Has Zero Direct Consumer Mutation

```text
consumer tree before staging == consumer tree after staging

Oracle:
tree_digest_equal == true
```

## A-SKM-001 — Old Stub Safe Removal

```text
old GES-owned unmodified stub exists
→ new apply removes it
→ new official projection exists
```

## A-SKM-002 — Old Stub Drift Blocks

```text
modify old GES-owned stub
→ compose/apply BLOCK
→ MANAGED_CONTENT_MODIFIED
→ 0 mutation
```

## A-CURSOR-STRUCT-001 — Cursor Skill Structure

Required：

```text
grill-with-docs
speckit-specify
writing-plans
```

Oracle：

```text
all paths valid
all frontmatter valid
all name == parent
```

## A-CURSOR-RUNTIME-001 — Cursor Runtime Sees Required Skills

Oracle：

```json
{
  "probe": "GES_CURSOR_DISCOVERY_PROBE_V1",
  "skills": {
    "grill-with-docs": true,
    "speckit-specify": true,
    "writing-plans": true
  }
}
```

## A-CURSOR-RUNTIME-002 — Discovery Probe Is Non-Mutating

```text
Golden Test Worktree tree digest before probe
==
tree digest after probe
```

## A-SKF-001 — speckit-specify Generates Real Spec

Required generated：

```text
specs/_ges-smoke/<run_id>/spec.md
```

and required content checks PASS.

## A-SKF-002 — Spec Kit Feature State

```text
.specify/feature.json
feature_directory
==
specs/_ges-smoke/<run_id>
```

## A-SKF-003 — Functional Smoke Mutation Confinement

```text
unexpected write set == empty
business source before == after
```

## A-GOLDEN-001 — Correct New Consumer

```text
source_path == E:\git\smc-copilot-desktop
HEAD resolves
```

## A-GOLDEN-002 — Dirty Source Does Not Block Immutable Test

Case：

```text
source checkout dirty == true
```

Expected：

```text
detached worktree created from HEAD
worktree clean at start
acceptance continues
uncommitted bytes absent from test worktree
```

## A-GOLDEN-003 — Final Doctor Ready

```text
final ges doctor overall == READY
```

## A-GOLDEN-004 — Business Source Zero Bytes Changed

```text
business source snapshot before == after
```

## A-GOLDEN-005 — Original Golden Source Workspace Preserved

```text
original workspace tracked/untracked tree identity before == after
except .git/worktrees administrative metadata
```

## A-IDEMP-CLI-001 — Real Second Init NOOP

Actual command：

```text
ges init <golden-test-worktree> --yes
```

Expected：

```text
exit 0
stdout contains GES_RECONCILE_NOOP
tree digest before == after
```

## A-EVID-001 — Evidence Commit Binding

```text
evidence.ges.commit_sha == current GES_HEAD
evidence.consumer.commit_sha == tested CONSUMER_HEAD
```

## A-EVID-002 — Per-AC Evidence Completeness

Every required Acceptance MUST contain：

```text
requirement_ids
test_ids
command
exit_code
oracle.expected
oracle.actual
evidence_files
```

---

# 20. Edge-case Matrix

| Case | Source Dirty | Cursor CLI | Specify Identity | Existing Spec Kit Path | Expected |
|---|---:|---:|---:|---|---|
| 1 | NO | YES | MATCH | none | PASS chain |
| 2 | YES | YES | MATCH | none | test committed HEAD; continue |
| 3 | YES | NO | MATCH | none | CURSOR_CLI_NOT_FOUND / BLOCKED |
| 4 | NO | YES | MISMATCH | none | SPEC_KIT_CLI_IDENTITY_MISMATCH |
| 5 | NO | YES | MATCH | unmanaged different | UNMANAGED_PATH_CONFLICT |
| 6 | NO | YES | MATCH | unmanaged identical | adopt-identical if ownership contract allows |
| 7 | NO | YES | MATCH | old GES stub unmodified | migrate/remove old stub |
| 8 | NO | YES | MATCH | old GES stub drifted | MANAGED_CONTENT_MODIFIED |
| 9 | detached HEAD | YES | MATCH | none | valid; record source_branch=DETACHED |
| 10 | HEAD missing | YES | MATCH | none | GOLDEN_CONSUMER_HEAD_UNRESOLVED |
| 11 | Golden temp worktree dirty at start | YES | MATCH | none | FAIL |
| 12 | Cursor returns malformed JSON | YES | MATCH | none | CURSOR_DISCOVERY_OUTPUT_INVALID |
| 13 | Cursor sees 2/3 skills | YES | MATCH | none | CURSOR_DISCOVERY_FAILED |
| 14 | Spec smoke creates business code | YES | MATCH | none | BUSINESS_SOURCE_MODIFICATION_FORBIDDEN |
| 15 | second init plans changes | YES | MATCH | none | GES_IDEMPOTENCY_FAILED |
| 16 | evidence points to parent GES SHA | YES | MATCH | none | STALE_EVIDENCE / BLOCKED |

---

# 21. Negative Acceptance

```text
NEG-SK-001
staged output contains ../ traversal path
→ reject
→ 0 consumer mutation

NEG-SK-002
pinned specify version mismatch
→ SPEC_KIT_CLI_IDENTITY_MISMATCH

NEG-SKM-001
old managed stub drifted
→ MANAGED_CONTENT_MODIFIED
→ preserve file

NEG-CURSOR-001
required skill missing
→ CURSOR_DISCOVERY_FAILED

NEG-CURSOR-002
runtime probe output missing required key
→ CURSOR_DISCOVERY_OUTPUT_INVALID

NEG-GOLDEN-001
invalid Golden Source path
→ GOLDEN_CONSUMER_NOT_FOUND

NEG-GOLDEN-002
Golden temp worktree starts dirty
→ GOLDEN_WORKTREE_DIRTY

NEG-SKF-001
functional smoke writes apps/** or packages/** business source
→ BUSINESS_SOURCE_MODIFICATION_FORBIDDEN

NEG-IDEMP-001
second CLI init mutates file
→ GES_IDEMPOTENCY_FAILED

NEG-EVID-001
evidence ges_commit != current HEAD
→ EVIDENCE_COMMIT_MISMATCH
```

---

# 22. Failure Injection

Required injected failures：

```text
FI-001 after official Spec Kit render, before projection plan
Expected: consumer unchanged

FI-002 after first new Spec Kit projection write
Expected: rollback to T0

FI-003 after old stub removal, before new projection complete
Expected: rollback restores old stub + prior .ges state

FI-004 Cursor CLI process non-zero
Expected: Runtime Acceptance BLOCKED/FAIL; no source mutation

FI-005 Spec Kit smoke after creating spec.md but before checklist
Expected: functional smoke FAIL; disposable worktree retained until evidence captured

FI-006 evidence write before final commit binding check
Expected: Release Gate cannot PASS until binding succeeds

FI-007 worktree cleanup failure
Expected: evidence includes recovery path; Release Gate FAIL
```

---

# 23. Evidence Contract

## 23.1 Evidence Record

禁止：

```json
{
  "A-CURSOR": "PASS"
}
```

Required minimum：

```json
{
  "acceptance_id": "A-CURSOR-RUNTIME-001",
  "status": "PASS",
  "requirement_ids": ["REQ-CURSOR-002"],
  "test_ids": ["TEST-A-CURSOR-RUNTIME-001"],
  "command": "agent -p ...",
  "exit_code": 0,
  "oracle": {
    "type": "cursor_skill_runtime_probe_v1",
    "expected": {
      "grill-with-docs": true,
      "speckit-specify": true,
      "writing-plans": true
    },
    "actual": {
      "grill-with-docs": true,
      "speckit-specify": true,
      "writing-plans": true
    }
  },
  "evidence_files": [
    "cursor-discovery.stdout.json"
  ]
}
```

## 23.2 Evidence Integrity

Every run MUST record：

```text
GES repo
GES commit SHA
GES branch
GES product/distribution version
Consumer source path
Consumer repo identity
Consumer commit SHA
Consumer branch
Consumer dirty flag
Consumer dirty status digest
Golden test worktree path
Spec Kit repo / SHA / CLI version
Cursor executable / version
test commands
timestamps
exit codes
raw evidence file digests
```

Evidence output root：

```text
audit/ges6/bootstrap-closure/<run_id>/
```

Suggested files：

```text
evidence.json
spec-kit-official-manifest.json
spec-kit-projection-manifest.json
cursor-discovery.stdout.json
cursor-discovery.stderr.txt
speckit-smoke.stdout.json
speckit-smoke.stderr.txt
mutation-report.json
doctor-pre.json
doctor-final.json
second-init.txt
```

---

# 24. Requirement Traceability Matrix

| Requirement | Invariant | Acceptance | Test | Evidence | Release Gate |
|---|---|---|---|---|---|
| REQ-SPECKIT-FUNC-001 | INV-SK-001..003 | A-SK-001..003 | TEST-A-SK-001..003 | official/projection manifests | REQUIRED |
| REQ-SPECKIT-FUNC-002 | INV-SKM-001 | A-SKM-001..002 | TEST-A-SKM-001..002 | migration tree report | REQUIRED |
| REQ-CURSOR-001 | INV-CURSOR-001 | A-CURSOR-STRUCT-001 | TEST-A-CURSOR-STRUCT-001 | structural report | REQUIRED |
| REQ-CURSOR-002 | INV-CURSOR-002..003 | A-CURSOR-RUNTIME-001..002 | TEST-A-CURSOR-RUNTIME-001..002 | raw Cursor probe | REQUIRED |
| REQ-SPECKIT-FUNC-003 | INV-SKF-001..002 | A-SKF-001..003 | TEST-A-SKF-001..003 | generated spec + mutation report | REQUIRED |
| REQ-GOLDEN-001 | INV-GOLDEN-001..003 | A-GOLDEN-001..002 | TEST-A-GOLDEN-001..002 | worktree identity evidence | REQUIRED |
| REQ-GOLDEN-002 | INV-GOLDEN-004..005 | A-GOLDEN-003..005, A-IDEMP-CLI-001 | TEST-A-GOLDEN-003..005, TEST-A-IDEMP-CLI-001 | command chain | REQUIRED |
| REQ-EVID-001 | INV-EVID-001..003 | A-EVID-001..002 | TEST-A-EVID-001..002 | evidence.json | REQUIRED |

---

# 25. Release Gate

## 25.1 Required Acceptance Set

```text
A-SK-001
A-SK-002
A-SK-003
A-SKM-001
A-SKM-002
A-CURSOR-STRUCT-001
A-CURSOR-RUNTIME-001
A-CURSOR-RUNTIME-002
A-SKF-001
A-SKF-002
A-SKF-003
A-GOLDEN-001
A-GOLDEN-002
A-GOLDEN-003
A-GOLDEN-004
A-GOLDEN-005
A-IDEMP-CLI-001
A-EVID-001
A-EVID-002
```

Release status：

```text
PASS
FAIL
BLOCKED
```

Rules：

```text
all required AC == PASS
→ Release Gate PASS
→ process exit 0
→ may emit BOOTSTRAP_ALPHA_READY

any required AC == FAIL
→ Release Gate FAIL
→ process exit != 0

any required AC == BLOCKED / SKIPPED
→ Release Gate BLOCKED
→ process exit != 0

evidence commit mismatch
→ STALE_EVIDENCE
→ Release Gate BLOCKED
```

## 25.2 Forbidden Release Claims

When Gate != PASS, MUST NOT emit：

```text
BOOTSTRAP_ALPHA_READY
COMPOSER_BOOTSTRAP_COMPLETE
RELEASE_READY
```

## 25.3 Final Success Output

Only after all required AC PASS：

```text
GES 6.0-alpha.1 Bootstrap Closure: PASS

Spec Kit Functional: PASS
Cursor Structural Discovery: PASS
Cursor Runtime Discovery: PASS
Golden Consumer: PASS
Second Init NOOP: PASS
Evidence Binding: PASS

Golden Consumer:
E:\git\smc-copilot-desktop
@ <consumer_commit_sha>

GES:
@ <ges_commit_sha>

BOOTSTRAP_ALPHA_READY
```

---

# 26. Plan Generation Contract

PRD status：

```text
APPROVED_FOR_PLAN
```

允许生成新的 `.plan.md`。

Plan MUST NOT复用旧 plan 中以下证明方式：

```text
Spec Kit runtime smoke = execute GES stub only
Cursor discovery = folder exists
Golden consumer = dirty main checkout → skip all
second init = compose().plan.noop only
evidence = whole pytest suite green → all AC PASS
```

Every Plan Todo MUST contain：

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
status: planned
evidence: []
```

`verified` 只能在对应 Acceptance 已实际执行并存在 Evidence 后设置。

Suggested implementation groups：

```text
PLAN-01 Spec Kit official staging renderer
PLAN-02 old stub migration
PLAN-03 Spec Kit identity/check/doctor
PLAN-04 Cursor structural/runtime probe
PLAN-05 isolated Golden worktree runner
PLAN-06 bounded speckit-specify smoke
PLAN-07 per-AC evidence writer
PLAN-08 full Golden release gate
```

---

# 27. Definition of Done

```text
[ ] Current GES handwritten Spec Kit stub no longer counts as functional runtime
[ ] Spec Kit official pinned CLI identity frozen
[ ] specify-cli version 1.0.8.dev0 verified
[ ] cursor-agent integration official staging succeeds
[ ] selected Spec Kit projected hashes equal official staging hashes
[ ] old GES-owned stub artifacts safely migrated
[ ] drifted old artifacts block instead of delete
[ ] Cursor required Skill structure validates
[ ] real Cursor CLI runtime probe reports 3 required Skills
[ ] Cursor runtime probe causes 0 repo mutation
[ ] speckit-specify real bounded smoke generates spec artifact
[ ] Spec Kit smoke does not modify business source
[ ] Golden Consumer path is E:\git\smc-copilot-desktop
[ ] Golden runner tests committed HEAD, not uncommitted files
[ ] dirty Golden Source workspace no longer automatically blocks test
[ ] detached Golden Test Worktree starts clean
[ ] original Golden Source workspace is preserved
[ ] preflight PASS
[ ] first ges init PASS
[ ] ges check PASS
[ ] final ges doctor READY
[ ] second real ges init returns GES_RECONCILE_NOOP
[ ] business source before/after identical
[ ] every Required AC has individual Evidence
[ ] Evidence GES SHA equals tested current GES HEAD
[ ] Evidence Consumer SHA equals tested Consumer HEAD
[ ] no Required AC is SKIPPED/BLOCKED
[ ] Release Gate PASS
[ ] process exit 0
[ ] BOOTSTRAP_ALPHA_READY emitted
```

---

# 28. Final Engineering Contract

本 PRD 冻结以下三个 Release Truth：

```text
Truth 1 — Spec Kit Functional

PASS 不是：
"GES 生成了几个文件"
"stub script 能返回 capability"

PASS 必须是：
官方 pinned Spec Kit 生成的 Cursor integration
已经被 GES 正确投影，
并在真实 Cursor Runtime 中执行 bounded speckit-specify smoke 成功。
```

```text
Truth 2 — Golden Consumer

Golden Consumer 固定为：
E:\git\smc-copilot-desktop

验收对象固定为：
该 repo 的 immutable committed HEAD。

主工作区 dirty：
只记录，不直接 BLOCK。

任何测试 mutation：
只能发生在 disposable detached worktree。
```

```text
Truth 3 — Cursor Discovery

PASS 不是：
SKILL.md exists

PASS 必须同时满足：
Cursor-compatible Skill structure
+
真实 Cursor Agent Runtime Probe
+
required skill set 全部被 runtime 识别
+
0 business source mutation
```

最终 Release 判断只允许：

```text
Spec Kit Functional PASS
AND
Cursor Runtime Discovery PASS
AND
Golden Consumer PASS
AND
Evidence Binding PASS
→ BOOTSTRAP_ALPHA_READY
```

否则：

```text
BOOTSTRAP_RELEASE_BLOCKED
```
