---
title: "GES 6.0-alpha.2 — Governance Backplane Foundation & Merge Readiness PRD"
subtitle: "Work / Artifact / Evidence / Policy / Traceability / Gate A+B"
prd_id: "PRD-GES-6.0-A2-GOVERNANCE-BACKPLANE-MERGE-READINESS"
version: "1.0"
status: "APPROVED_FOR_PLAN"
product: "GES 6"
repository: "loudon84/smc-delivery-governance"
branch: "feat/ges-v6.0"
owner: "GES"
reviewers:
  - "Product / Architecture Owner"
  - "Independent Engineering Reviewer"
created_at: "2026-09-16"
updated_at: "2026-09-16"
target_release: "GES 6.0.0-alpha.2"
change_type:
  - "NEW_FEATURE"
  - "ARCHITECTURE_CHANGE"
  - "GOVERNANCE"
  - "INTEGRATION"
golden_consumer:
  path: 'E:\git\smc-copilot-desktop'
  repository: "loudon84/smc-copilot-desktop"
related_docs:
  - "需求PRD工程模板.md"
  - "GES-v6.0-alpha.1-Composer-Governance-Backplane-PRD.md"
  - "PRD-GES-v6.0-alpha.1-Bootstrap-Closure-v1.0.md"
  - "PRD-GES-v6.0-alpha.1-Release-Hardening-v1.0.md"
goal: "在 Alpha.1 Composer Bootstrap 之上建立第一版 Governance Backplane，使 GES 基于真实 Work、Artifact、Git Commit、GitHub PR、CI 与 Review Evidence 确定性计算 WORK_READY 和 MERGE_READY。"
---

# GES 6.0-alpha.2 — Governance Backplane Foundation & Merge Readiness PRD

> 本 PRD 按《需求PRD工程模板.md》输出。
>
> Alpha.1 解决：
>
> ```text
> 业务项目应该具备哪些 AI Engineering 能力，
> 以及这些能力如何安全安装和验证。
> ```
>
> Alpha.2 解决：
>
> ```text
> 一次软件变更属于哪个 Work？
> Spec / Plan / PR / Commit / CI / Review 是否可追溯？
> Evidence 是否属于当前 Commit？
> 当前 Work 是否可以进入开发？
> 当前 PR 是否具备合并资格？
> ```
>
> GES 只治理结果，不治理 Agent 如何思考。

---

# 0. PRD 使用原则

## 0.1 产品原则

GES 6 产品定位继续冻结：

```text
GES 6
=
Composer
+
Governance Backplane
```

Alpha.1 Composer 正式发布后进入：

```text
MAINTENANCE / BUGFIX ONLY
```

Alpha.2 MUST NOT继续扩展：

```text
AI Coding Methodology
LLM Runtime
Context Engine
Plan Engine
TDD Runtime
Review Reasoning
Agent Worker Runtime
```

Alpha.2 Backplane MUST：

```text
deterministic
pointer-only
Git/GitHub grounded
read-only at Gate evaluation
machine-verifiable
explainable
no LLM required
```

## 0.2 Normative Keywords

```text
MUST
MUST NOT
SHOULD
SHOULD NOT
MAY
```

所有 MUST / MUST NOT 必须映射 Acceptance。

## 0.3 No-Inference Rule

以下事项不得由 Plan / Coding Agent自行决定：

```text
Work 的事实源
Artifact 的 digest 范围
PR 与 Work 如何绑定
PR 与 Commit 如何绑定
Evidence 是否属于当前 Commit
哪些 CI 状态算 PASS
Review 什么状态算 PASS
HIGH Risk 是否能合并
GitHub unavailable 是 FAIL 还是 BLOCKED
Gate 是否允许自动修复
Evidence 是否可以手工声明 PASS
```

无法唯一确定：

```text
SPEC_SEMANTIC_GAP
→ BLOCK PLAN
```

---

# 1. 一句话目标

让 `smc-copilot-desktop` 等业务项目在已有 GES Composer 基础上，通过 `ges governance / work / artifact / evidence / trace / gate` 建立 Git/GitHub grounded 的治理闭环，使每个 Feature Work 能机器证明 Spec、Plan、PR、Commit、CI 与 Review 的关系，并确定性输出 `WORK_READY` 或 `MERGE_READY`，同时保证 Gate 0 业务源码修改、0 GitHub 写操作、0 LLM 判断、0 Evidence 自报。

---

# 2. 背景与问题定义

## 2.1 Current State

Alpha.1 已完成：

```text
Repo Analyze
Capability Resolve
Source Resolve
Matt / Spec Kit / Superpowers Projection
Cursor Runtime
Transactional Reconcile
ges check
ges doctor
Golden Consumer Bootstrap
```

当前 Governance Backplane 仅有概念模型：

```text
Work
ArtifactRef
Evidence
Policy
Risk
Ownership
Approval
Release
```

尚无运行时。

团队正式研发事实源已经明确为 Git / GitHub：

```text
Repo 中的 Spec / Plan
= 需求与技术意图

Git Commit
= 实现身份

GitHub Pull Request
= Merge Candidate

GitHub Checks / Actions
= Test / Build Evidence

GitHub Review Decision
= Review Evidence
```

## 2.2 Problem

当前没有统一系统回答：

```text
P1 这个代码变更属于哪个 Work？
P2 当前 Spec 和 Plan 是哪个精确版本？
P3 当前 PR HEAD 是否就是被测试、被 Review 的 Commit？
P4 Agent 自报“测试通过”是否被误当 Evidence？
P5 Review 文本存在是否被误当 APPROVED？
P6 PR HEAD 改变后旧 CI / Review 是否会被复用？
P7 Merge 被阻断时，缺少什么能否机器解释？
P8 Multica / Cursor / GitHub 如何消费同一个治理 Truth？
```

## 2.3 Impact

```text
业务影响：
合并条件依赖人工判断。

工程影响：
Spec → Plan → PR → Commit → Evidence 缺少统一 Traceability。

安全影响：
旧 Commit Evidence 可能被复用到新 Commit。

治理影响：
无法形成独立于 Agent 推理过程的 MERGE_READY Truth。

协作影响：
不同系统会重复实现 GitHub 状态解释逻辑。
```

---

# 3. Scope

## 3.1 In Scope

```text
SCOPE-A2-001 Governance bootstrap
SCOPE-A2-002 Work Registry v1
SCOPE-A2-003 Repo ArtifactRef v1：SPEC / PLAN
SCOPE-A2-004 Work Ownership v1
SCOPE-A2-005 Risk v1：LOW / MEDIUM / HIGH
SCOPE-A2-006 Policy Engine v1
SCOPE-A2-007 GitHub Provider v1
SCOPE-A2-008 Evidence Observation v1：CI_CHECK / REVIEW_DECISION
SCOPE-A2-009 Traceability Graph v1
SCOPE-A2-010 Gate A — WORK_READY
SCOPE-A2-011 Gate B — MERGE_READY
SCOPE-A2-012 Gate Explain
SCOPE-A2-013 Read-only Gate guarantees
SCOPE-A2-014 Synthetic Acceptance
SCOPE-A2-015 Golden Consumer：E:\git\smc-copilot-desktop
SCOPE-A2-016 External Gate Evidence
```

## 3.2 Out of Scope

```text
NON-GOAL-A2-001 Release Readiness / Gate C
NON-GOAL-A2-002 Production Deployment
NON-GOAL-A2-003 Release Rollback
NON-GOAL-A2-004 GES Approval Runtime
NON-GOAL-A2-005 Human Approval UI
NON-GOAL-A2-006 Central Backplane DB / Server
NON-GOAL-A2-007 Multica API integration
NON-GOAL-A2-008 PRD / Spec / Plan Authoring
NON-GOAL-A2-009 Coding / TDD / Debug / Review Reasoning
NON-GOAL-A2-010 LLM Policy Judgment
NON-GOAL-A2-011 Agent Scheduler
NON-GOAL-A2-012 Copy Spec / Plan / Review body into GES
NON-GOAL-A2-013 HIGH Risk MERGE_READY
NON-GOAL-A2-014 BUGFIX / HOTFIX / INCIDENT Work Kind
```

Alpha.2 正式 Work Kind：

```text
FEATURE only
```

## 3.3 Architecture Boundary

| Domain | Owner | Input | Output | 不负责 |
|---|---|---|---|---|
| Engineering Discovery | Matt | repo/docs | engineering understanding | governance |
| Intent / Spec | Spec Kit | intent | Spec / technical intent | merge gate |
| Execution | Superpowers / Cursor | approved intent | code/test/review workflow | policy |
| Code Truth | Git | files | commit identity | governance |
| Delivery Truth | GitHub | PR/check/review | observations | coding |
| Governance | GES | Work + refs + observations | Gate Truth | authoring/execution |
| Operations | Multica | future Gate events | team/agent operations | Alpha.2 SOT |
| Release | Alpha.3 | merge artifact | RELEASE_READY | Alpha.2 |

---

# 4. Terminology / Domain Model

## Work

```text
Work
= 一次需要被治理的软件变更。
```

Alpha.2：

```text
kind = FEATURE
```

Work 不是 Agent Run、Cursor Session、PR 或 Multica Task。

## ArtifactRef

```text
ArtifactRef
= pointer + type + identity/digest
```

Alpha.2持久 Artifact：

```text
SPEC
PLAN
```

GES 不复制正文。

## Evidence

```text
Evidence
= 外部系统针对某一 subject_sha 的可验证结果观察。
```

Alpha.2：

```text
CI_CHECK
REVIEW_DECISION
```

Evidence 不允许用户手工声明 PASS。

## Policy

```text
Policy
= deterministic rule set
```

MUST NOT 调用 LLM 或 consumer Python code。

## Risk

```text
LOW
MEDIUM
HIGH
```

HIGH：

```text
Gate B = BLOCKED
APPROVAL_REQUIRED_UNSUPPORTED
```

## Traceability

```text
WORK
→ SPEC
→ PLAN
→ PR
→ COMMIT
→ CI_CHECK / REVIEW_DECISION
```

## Gate

```text
Gate A → WORK_READY
Gate B → MERGE_READY
```

状态：

```text
PASS
FAIL
BLOCKED
```

---

# 5. System Context

```text
Human / Product
      │
      ▼
Spec Kit / Repo
 SPEC + PLAN
      │
      ▼
.ges/governance/
 Work + Policy
      │
      ▼
 GES Backplane
   │        │
   ▼        ▼
  Git     GitHub
           │
           ├─ PR
           ├─ head SHA
           ├─ Checks
           └─ Review Decision
      │
      ▼
Traceability Graph
   │          │
   ▼          ▼
Gate A      Gate B
WORK_READY  MERGE_READY
```

Inside boundary：

```text
Work Registry
Artifact Resolver
Policy Engine
Git Resolver
GitHub Provider
Evidence Resolver
Traceability
Gate Engine
CLI
Acceptance
```

Outside：

```text
Spec authoring
Plan authoring
Coding
Test execution itself
Review reasoning
GitHub branch protection configuration
Approval
Merge execution
Release / deployment
Multica runtime
```

---

# 6. Authoritative State / Source of Truth

| State | Role | Type | Authoritative? | Writer | Reader |
|---|---|---|---:|---|---|
| `.ges/governance/policy.yaml` | Rules | DESIRED_STATE | YES | Human/GES | Gate |
| `.ges/governance/works/<id>.yaml` | Work Declaration | DESIRED_STATE | YES | Human/GES | Registry/Gate |
| SPEC bytes | Intent body | OBSERVED_STATE | YES | Spec owner | Resolver |
| PLAN bytes | Plan body | OBSERVED_STATE | YES | Plan owner | Resolver |
| Git HEAD | local implementation identity | OBSERVED_STATE | YES | Git | Gate |
| GitHub PR | merge candidate | RUNTIME_STATE | YES | GitHub | Provider |
| PR head SHA | merge subject | RUNTIME_STATE | YES | GitHub | Gate |
| GitHub Checks | CI Evidence | EVIDENCE_STATE | YES | CI/GitHub | Evidence |
| Review Decision | Review Evidence | EVIDENCE_STATE | YES | GitHub | Evidence |
| Trace Graph | relationship | RUNTIME_STATE | DERIVED | GES | Gate/User |
| Gate Result | decision | EVIDENCE_STATE | DERIVED | GES | CI/User |

Rules：

```text
Gate Result MUST NOT become Desired State.
Evidence MUST NOT be persisted as user-editable PASS labels.
Gate MUST recompute from current facts.
```

---

# 7. State Machine

持久 Work 状态：

```text
OPEN
→ CLOSED
```

Alpha.2 不支持 reopen。

Gate 状态：

```text
NOT_EVALUATED
→ PASS | FAIL | BLOCKED
```

`WORK_READY` / `MERGE_READY`：

```text
derived only
MUST NOT persist as Work status
```

重新运行 Gate：

```text
always recompute
```

任何 Spec/Plan/PR/Commit/Check/Review 变化都影响下一次结果。

---

# 8. Data / Schema Contract

## 8.1 `ges.work.v1`

Path：

```text
.ges/governance/works/<work_id>.yaml
```

```yaml
schema: ges.work.v1
id: WI-WORK-0001
kind: FEATURE
title: "..."
status: OPEN
owner: "team-or-user"
risk: LOW
policy: default-v1
artifacts:
  - id: ART-SPEC
    type: SPEC
    pointer: repo://specs/example/spec.md
    digest: sha256:<64hex>
  - id: ART-PLAN
    type: PLAN
    pointer: repo://specs/example/plan.md
    digest: sha256:<64hex>
created_at: RFC3339
updated_at: RFC3339
```

Required all fields above。

Enums：

```text
kind: FEATURE
status: OPEN | CLOSED
risk: LOW | MEDIUM | HIGH
```

Work ID：

```text
^[A-Z][A-Z0-9._-]{2,63}$
```

`additionalProperties=false`

## 8.2 `ges.policy.v1`

```yaml
schema: ges.policy.v1
id: default-v1

intake:
  require_owner: true
  required_artifacts: [SPEC, PLAN]

merge:
  supported_risks: [LOW, MEDIUM]

  pr:
    require_open: true
    require_not_draft: true
    require_work_marker: true
    work_marker: "GES-Work: {work_id}"

  local:
    require_head_equals_pr_head: true
    require_clean_tracked_tree: true

  review:
    require_decision: APPROVED

  checks:
    min_successful: 1
    allow_pending: false
    allow_failed: false
    allow_cancelled: false
    allow_skipped_as_success: false
```

`additionalProperties=false`

## 8.3 ArtifactRef

```text
id
type = SPEC | PLAN
pointer = repo://relative/path
digest = sha256:<64hex>
```

Path MUST：

```text
repo relative
regular file
inside repo
not path traversal
not symlink escape
```

## 8.4 `ges.evidence-snapshot.v1`

Runtime output：

```json
{
  "schema": "ges.evidence-snapshot.v1",
  "work_id": "WI-WORK-0001",
  "repo": "owner/repo",
  "pr_number": 123,
  "subject_sha": "<40-char>",
  "review": {
    "type": "REVIEW_DECISION",
    "status": "PASS",
    "decision": "APPROVED"
  },
  "checks": []
}
```

## 8.5 `ges.trace.v1`

```text
nodes[]
edges[]
work_id
subject_sha
```

Required edge types：

```text
WORK_HAS_SPEC
WORK_HAS_PLAN
PR_DECLARES_WORK
PR_HEAD_IS_COMMIT
CHECK_VERIFIES_COMMIT
REVIEW_GOVERNS_PR
```

## 8.6 `ges.gate-result.v1`

```json
{
  "schema": "ges.gate-result.v1",
  "gate": "INTAKE",
  "work_id": "WI-WORK-0001",
  "status": "PASS",
  "verdict": "WORK_READY",
  "subject_sha": "",
  "reasons": [],
  "evaluated_at": "...",
  "tool_version": "..."
}
```

`additionalProperties=false`

---

# 9. Requirement Units

## REQ-A2-GOV-001 — Governance Bootstrap

### Goal

建立 Backplane 声明目录，不影响 Composer。

### Normative Requirement

新增：

```text
ges governance init <repo>
```

MUST 创建：

```text
.ges/governance/policy.yaml
.ges/governance/works/
```

已有合法治理目录：

```text
GOVERNANCE_ALREADY_INITIALIZED
0 content mutation
exit 0
```

未知冲突：

```text
GOVERNANCE_PATH_CONFLICT
0 partial mutation
```

MUST NOT 修改：

```text
.ges/project.yaml
.ges/lock.json
.ges/install-receipt.json
business source
.specify/**
.agents/**
.cursor/**
```

### Acceptance

```text
A-A2-GOV-001
A-A2-GOV-002
```

---

## REQ-A2-WORK-001 — Work Registry

### Goal

建立稳定 Governance Aggregate。

### Commands

```text
ges work create
ges work show
ges work update
ges work close
```

Create MUST require：

```text
--id
--title
--owner
--risk
```

Alpha.2：

```text
kind=FEATURE
status=OPEN
MUST NOT auto-generate Work ID
```

Update MAY change：

```text
title
owner
risk
policy
```

Close：

```text
OPEN → CLOSED
```

CLOSED → OPEN：

```text
WORK_STATE_TRANSITION_INVALID
```

Duplicate ID：

```text
WORK_ALREADY_EXISTS
0 mutation
```

### SOT

```text
.ges/governance/works/<id>.yaml
```

### Acceptance

```text
A-A2-WORK-001
A-A2-WORK-002
A-A2-WORK-003
```

---

## REQ-A2-ART-001 — Artifact Registry

### Goal

绑定 Spec / Plan 的精确字节版本。

### Command

```text
ges artifact link <work_id>
  --type SPEC|PLAN
  --path <repo-relative-path>
```

MUST：

```text
validate containment
reject symlink escape
read exact bytes
SHA256 exact bytes
store repo:// pointer + digest
```

每个 Work：

```text
exactly one SPEC
exactly one PLAN
```

重复相同：

```text
NOOP
```

更换：

```text
requires --replace
```

GES MUST NOT 修改 Spec/Plan body。

Gate 检查：

```text
current_sha256 == stored_digest
```

不相等：

```text
ARTIFACT_STALE
FAIL
```

### Acceptance

```text
A-A2-ART-001
A-A2-ART-002
A-A2-ART-003
```

---

## REQ-A2-POLICY-001 — Deterministic Policy Engine

### Goal

用确定规则计算 Gate。

### MUST

```text
schema validate policy
pure deterministic predicates
structured reason output
```

MUST NOT：

```text
LLM
eval()
arbitrary Python from consumer
auto-fix
```

Gate A requires：

```text
Work OPEN
owner non-empty
SPEC current
PLAN current
```

Gate B requires：

```text
Gate A PASS
risk LOW|MEDIUM
PR OPEN
PR not draft
exact Work marker
local HEAD == PR head
tracked tree clean
reviewDecision == APPROVED
>= min_successful SUCCESS checks
0 pending
0 failed
0 cancelled
SKIPPED does not count success
```

HIGH：

```text
BLOCKED
APPROVAL_REQUIRED_UNSUPPORTED
```

### Acceptance

```text
A-A2-POLICY-001
A-A2-POLICY-002
A-A2-POLICY-003
```

---

## REQ-A2-GH-001 — GitHub Provider v1

### Goal

读取真实 PR / Check / Review。

### Dependency

```text
gh CLI
```

Preflight：

```text
gh --version
gh auth status
```

Provider reads：

```text
PR number
state
isDraft
url
author
headRefOid
baseRefName
body
reviewDecision
statusCheckRollup
```

MUST NOT：

```text
create/edit/comment/approve/merge PR
rerun checks
```

GitHub unavailable：

```text
BLOCKED
GITHUB_PROVIDER_UNAVAILABLE
```

Auth unavailable：

```text
BLOCKED
GITHUB_AUTH_UNAVAILABLE
```

### Acceptance

```text
A-A2-GH-001
A-A2-GH-002
```

---

## REQ-A2-EVID-001 — Evidence Observation

### Goal

只接受 provider-backed Evidence。

### Command

```text
ges evidence collect <work_id> --pr <number> --json
```

Alpha.2 Evidence Types：

```text
CI_CHECK
REVIEW_DECISION
```

CI：

```text
SUCCESS → PASS
PENDING/IN_PROGRESS → PENDING
FAILURE/TIMED_OUT/CANCELLED/ACTION_REQUIRED → FAIL
SKIPPED/NEUTRAL → not PASS
```

Review：

```text
APPROVED → PASS
CHANGES_REQUESTED → FAIL
missing/required → MISSING
```

Every Evidence MUST：

```text
subject_sha == PR headRefOid
```

否则：

```text
EVIDENCE_SUBJECT_MISMATCH
```

Alpha.2 MUST NOT expose：

```text
ges evidence add --status PASS
```

### Acceptance

```text
A-A2-EVID-001
A-A2-EVID-002
A-A2-EVID-003
```

---

## REQ-A2-TRACE-001 — Traceability Graph

### Goal

从 Work 追到当前 merge candidate 与 Evidence。

### Command

```text
ges trace show <work_id> --pr <number> --json
```

Graph：

```text
WORK
 ├─ SPEC
 ├─ PLAN
 └─ PR
     └─ COMMIT
         ├─ CI_CHECK*
         └─ REVIEW_DECISION
```

Missing node：

```text
still emit graph
node.status=MISSING
```

Trace MUST be read-only。

### Acceptance

```text
A-A2-TRACE-001
A-A2-TRACE-002
```

---

## REQ-A2-GATE-001 — Gate A / Work Intake

### Command

```text
ges gate intake <work_id>
ges gate intake <work_id> --json
```

PASS requires：

```text
Work exists
status OPEN
owner non-empty
risk valid
policy valid
SPEC current
PLAN current
```

PASS：

```text
status=PASS
verdict=WORK_READY
exit=0
```

Policy fail：

```text
status=FAIL
verdict=BLOCKED
exit=2
```

Gate A：

```text
network=0
file write=0
```

### Acceptance

```text
A-A2-INTAKE-001
A-A2-INTAKE-002
A-A2-INTAKE-003
```

---

## REQ-A2-GATE-002 — Gate B / Merge Readiness

### Command

```text
ges gate merge <work_id> --pr <number>
ges gate merge <work_id> --pr <number> --json
```

Evaluation order MUST：

```text
1 Work
2 Policy
3 Gate A
4 local Git
5 GitHub PR
6 PR→Work marker
7 local HEAD→PR head
8 CI Evidence
9 Review Evidence
10 Risk
11 final verdict
```

PR body MUST contain exact：

```text
GES-Work: <work_id>
```

PASS requires：

```text
Gate A PASS
risk LOW/MEDIUM
PR OPEN
not draft
marker exact
local HEAD == PR headRefOid
tracked tree clean
reviewDecision == APPROVED
>=1 SUCCESS check
0 pending
0 failed
0 cancelled
all evidence bound to PR head
```

PASS：

```text
PASS
MERGE_READY
exit 0
```

Policy fail：

```text
FAIL
BLOCKED
exit 2
```

Provider unavailable：

```text
BLOCKED
exit 3
```

Schema/config invalid：

```text
exit 4
```

HIGH Risk：

```text
BLOCKED
APPROVAL_REQUIRED_UNSUPPORTED
exit 3
```

Gate MUST：

```text
repo write=0
GitHub write=0
```

### Concurrency

Capture：

```text
T0 local_head
T0 pr_head
```

Before verdict re-read both。

Changed：

```text
PR_HEAD_CHANGED_DURING_EVALUATION
or
LOCAL_HEAD_CHANGED_DURING_EVALUATION
→ BLOCKED
→ MUST NOT emit MERGE_READY
```

### Acceptance

```text
A-A2-MERGE-001
A-A2-MERGE-002
A-A2-MERGE-003
A-A2-MERGE-004
A-A2-MERGE-005
```

---

## REQ-A2-GATE-003 — Gate Explain

### Commands

```text
ges gate explain <work_id> --gate intake
ges gate explain <work_id> --gate merge --pr <number>
```

Reason schema：

```text
code
scope
expected
actual
source
remediation_hint
```

`remediation_hint` MUST：

```text
static deterministic
no LLM
no auto-fix
```

Reason ordering MUST deterministic。

### Acceptance

```text
A-A2-EXPLAIN-001
A-A2-EXPLAIN-002
```

---

## REQ-A2-READONLY-001 — Gate Read-only Guarantee

Read-only commands：

```text
work show
evidence collect
trace show
gate intake
gate merge
gate explain
```

MUST preserve：

```text
tracked tree
untracked tree
Git index
HEAD
Git refs
GitHub PR body/state/reviews/checks
```

Allowed：

```text
stdout/stderr
network read
OS temp/cache
explicit output path outside consumer repo
```

### Acceptance

```text
A-A2-RO-001
A-A2-RO-002
```

---

# 10. Side-Effect Contract

| Operation | Governance Write | Business Write | Git Write | GitHub Write | Network |
|---|---:|---:|---:|---:|---:|
| governance init | YES | NO | NO | NO | NO |
| work create/update/close | YES | NO | NO | NO | NO |
| artifact link | Work file only | NO | NO | NO | NO |
| work show | NO | NO | NO | NO | NO |
| evidence collect | NO | NO | NO | NO | YES read |
| trace show | NO | NO | NO | NO | YES read |
| gate intake | NO | NO | NO | NO | NO |
| gate merge | NO | NO | NO | NO | YES read |
| gate explain | NO | NO | NO | NO | MAY read |

Business source：

```text
apps/**
src/**
services/**
packages/**
contracts/**
```

---

# 11. Ownership Contract

```text
policy.yaml
→ governance FILE

works/<id>.yaml
→ governance FILE

SPEC / PLAN body
→ USER_OWNED

ArtifactRef in Work
→ GES/Human managed ENTRY

GitHub PR / Checks / Review
→ EXTERNAL

Trace / Evidence Snapshot / Gate Result
→ DERIVED
```

Artifact drift：

```text
current hash == stored digest
→ CURRENT

current hash != stored digest
→ ARTIFACT_STALE
→ Gate FAIL
```

Gate MUST NOT auto-refresh。

---

# 12. Hash / Identity Contract

Repo Artifact：

```text
SHA256(exact raw file bytes)
```

No newline normalization。

Pointer：

```text
repo://<relative-posix-path>
```

Normalization：

```text
\ → /
remove ./
reject ..
reject absolute path
```

Git Commit identity：

```text
40-char lowercase SHA
```

PR identity：

```text
github://<owner>/<repo>/pull/<number>
```

Evidence subject：

```text
PR headRefOid
```

New PR commit MUST invalidate prior evidence.

---

# 13. Transaction Contract

Mutation commands：

```text
governance init
work create
work update
work close
artifact link
```

Write flow：

```text
read T0
→ validate
→ build in memory
→ schema validate
→ temp file
→ atomic replace
→ reread/verify
```

Failure：

```text
persisted bytes == T0
```

Gate commands：

```text
no transaction
read-only
```

---

# 14. Conflict / Failure Contract

| Failure | Behavior | Code | Mutation |
|---|---|---|---:|
| duplicate Work | BLOCK | WORK_ALREADY_EXISTS | 0 |
| duplicate Artifact binding | BLOCK unless `--replace` | ARTIFACT_ALREADY_BOUND | 0 |
| Artifact drift | FAIL | ARTIFACT_STALE | 0 |
| PR marker missing | FAIL | PR_WORK_BINDING_MISSING | 0 |
| PR marker other Work | FAIL | PR_WORK_BINDING_CONFLICT | 0 |
| local HEAD != PR HEAD | FAIL | PR_HEAD_MISMATCH | 0 |
| stale evidence SHA | FAIL | EVIDENCE_SUBJECT_MISMATCH | 0 |
| Review not approved | FAIL | REVIEW_REQUIRED | 0 |
| pending check | FAIL | CI_CHECK_PENDING | 0 |
| HIGH Risk | BLOCK | APPROVAL_REQUIRED_UNSUPPORTED | 0 |
| gh unavailable | BLOCK | GITHUB_PROVIDER_UNAVAILABLE | 0 |
| PR head changes during gate | BLOCK | PR_HEAD_CHANGED_DURING_EVALUATION | 0 |

禁止：

```text
last writer wins
auto hash refresh
auto PR edit
auto approve
auto rerun CI
```

---

# 15. Compatibility / Migration

Existing Alpha.1 state：

```text
.ges/project.yaml
.ges/repo-profile.json
.ges/lock.json
.ges/install-receipt.json
```

Alpha.2：

```text
MUST preserve
MUST NOT migrate
MUST NOT change Composer semantics
```

新增：

```text
.ges/governance/**
```

如果已有未知 `.ges/governance`：

```text
PRESERVE
GOVERNANCE_PATH_CONFLICT
MUST NOT overwrite
```

---

# 16. External Dependency Contract

## Git

Required：

```text
rev-parse
status
remote
```

Record：

```text
git --version
```

## GitHub CLI

Required：

```text
gh --version
gh auth status
gh pr view ... --json
```

MUST record：

```text
gh version
target host
repo identity
```

MUST NOT log token。

Provider is read-only。

---

# 17. Security Contract

| Threat | Control | Acceptance |
|---|---|---|
| Artifact traversal | path containment | A-A2-SEC-001 |
| symlink escape | resolved path containment | A-A2-SEC-002 |
| arbitrary policy execution | schema-only DSL | A-A2-POLICY-001 |
| token leakage | secret redaction | A-A2-SEC-003 |
| GitHub mutation | read-only provider | A-A2-RO-002 |
| self-reported PASS | provider-only evidence | A-A2-EVID-003 |
| stale evidence | subject SHA binding | A-A2-EVID-002 |
| stale spec | exact digest | A-A2-INTAKE-002 |
| dirty tree | tracked-clean requirement | A-A2-MERGE-004 |

---

# 18. Observability

Stages：

```text
GOVERNANCE_INIT
WORK_LOAD
WORK_VALIDATE
ARTIFACT_RESOLVE
POLICY_LOAD
GIT_OBSERVE
GITHUB_OBSERVE
EVIDENCE_RESOLVE
TRACE_BUILD
GATE_INTAKE
GATE_MERGE
GATE_EXPLAIN
```

Gate logs：

```text
operation_id
work_id
gate
repo
local_head
pr_number
pr_head
policy_id
status
verdict
reason_codes
started_at
finished_at
tool_version
```

---

# 19. Acceptance Design

## A-A2-GOV-001 — Governance Init

```text
Given Alpha.1 repo + ges check PASS
When ges governance init .
Then policy + works dir exist
Oracle schema valid + business digest unchanged
```

## A-A2-GOV-002 — Governance Init Idempotent

```text
second run
→ 0 content changes
→ GOVERNANCE_ALREADY_INITIALIZED
```

## A-A2-WORK-001 — Work Create

```text
explicit id/title/owner/risk
→ valid ges.work.v1
```

## A-A2-WORK-002 — Duplicate Work

```text
same ID
→ WORK_ALREADY_EXISTS
→ original bytes unchanged
```

## A-A2-WORK-003 — Closed Cannot Reopen

```text
CLOSED → OPEN
→ WORK_STATE_TRANSITION_INVALID
```

## A-A2-ART-001 — Link Spec

```text
stored digest == SHA256(exact bytes)
```

## A-A2-ART-002 — Artifact Drift

```text
modify one byte
→ gate intake FAIL
→ ARTIFACT_STALE
```

## A-A2-ART-003 — Path Escape

```text
../ or outside symlink
→ reject
→ 0 mutation
```

## A-A2-POLICY-001 — No Executable Policy

Unknown executable/plugin fields：

```text
POLICY_SCHEMA_INVALID
```

## A-A2-POLICY-002 — LOW/MEDIUM May Pass

Valid facts：

```text
LOW / MEDIUM
→ may reach MERGE_READY
```

## A-A2-POLICY-003 — HIGH Blocks

```text
HIGH
→ BLOCKED
→ APPROVAL_REQUIRED_UNSUPPORTED
```

## A-A2-GH-001 — GitHub Read-only Observation

```text
required PR fields observed
repo tree unchanged
remote PR unchanged
```

## A-A2-GH-002 — Auth Missing

```text
GITHUB_AUTH_UNAVAILABLE
BLOCKED
```

## A-A2-EVID-001 — CI Success

```text
SUCCESS + subject=head
→ CI_CHECK PASS
```

## A-A2-EVID-002 — Stale Subject

```text
subject != PR head
→ EVIDENCE_SUBJECT_MISMATCH
→ FAIL
```

## A-A2-EVID-003 — Manual PASS Unsupported

```text
ges evidence add --status PASS
→ command unavailable or UNSUPPORTED_OPERATION
```

## A-A2-TRACE-001 — Complete Trace

Nodes：

```text
WORK SPEC PLAN PR COMMIT CI_CHECK REVIEW_DECISION
```

Edges all required。

## A-A2-TRACE-002 — Missing Node Visible

Review missing：

```text
trace emitted
review status=MISSING
```

## A-A2-INTAKE-001 — Work Ready

```text
valid Work + current SPEC + current PLAN
→ PASS / WORK_READY / exit 0
```

## A-A2-INTAKE-002 — Stale Spec

```text
FAIL / ARTIFACT_STALE / exit 2
```

## A-A2-INTAKE-003 — Missing Plan

```text
FAIL / REQUIRED_ARTIFACT_MISSING
```

## A-A2-MERGE-001 — Merge Ready

Given：

```text
Gate A PASS
MEDIUM
PR open/not draft
marker exact
HEAD match
clean tracked tree
review approved
>=1 success check
0 bad/pending checks
```

Then：

```text
PASS
MERGE_READY
exit 0
```

## A-A2-MERGE-002 — New Commit Invalidates Evidence

```text
PR head changes
→ old evidence rejected
```

## A-A2-MERGE-003 — Review Missing

```text
FAIL
REVIEW_REQUIRED
```

## A-A2-MERGE-004 — Dirty Tracked Tree

```text
FAIL
WORKTREE_DIRTY
```

## A-A2-MERGE-005 — Pending Check

```text
FAIL
CI_CHECK_PENDING
```

## A-A2-EXPLAIN-001 — Deterministic Reasons

Same snapshot：

```text
reason codes/order/expected/actual identical
```

## A-A2-EXPLAIN-002 — Explain Does Not Fix

Before/after repo + GitHub states identical。

## A-A2-RO-001 — Local Read-only

Read-only commands：

```text
tree/index/HEAD/refs identical before-after
```

## A-A2-RO-002 — Remote Read-only

```text
PR body/state/review/check state unchanged by GES
```

---

# 20. Acceptance Input Matrix

| Case | Spec | Plan | Risk | PR | Marker | HEAD | Review | Checks | Expected |
|---|---|---|---|---|---|---|---|---|---|
| 1 | current | current | LOW | open | exact | match | approved | success | MERGE_READY |
| 2 | stale | current | LOW | open | exact | match | approved | success | Intake FAIL |
| 3 | current | missing | LOW | - | - | - | - | - | Intake FAIL |
| 4 | current | current | HIGH | open | exact | match | approved | success | BLOCKED |
| 5 | current | current | LOW | draft | exact | match | approved | success | FAIL |
| 6 | current | current | LOW | open | missing | match | approved | success | FAIL |
| 7 | current | current | LOW | open | other Work | match | approved | success | FAIL |
| 8 | current | current | LOW | open | exact | mismatch | approved | success | FAIL |
| 9 | current | current | LOW | open | exact | match | missing | success | FAIL |
| 10 | current | current | LOW | open | exact | match | approved | pending | FAIL |
| 11 | current | current | LOW | open | exact | match | approved | skipped only | FAIL |
| 12 | current | current | LOW | open | exact | match | approved | success+fail | FAIL |
| 13 | current | current | LOW | provider unavailable | - | - | - | - | BLOCKED |
| 14 | current | current | LOW | open | exact | match | approved | old SHA | FAIL |
| 15 | current | current | MEDIUM | open | exact | match | approved | success | MERGE_READY |

---

# 21. Negative Acceptance

```text
NEG-A2-001 invalid Work ID → WORK_ID_INVALID
NEG-A2-002 ../ Artifact → ARTIFACT_PATH_INVALID
NEG-A2-003 symlink escape → ARTIFACT_PATH_UNSAFE
NEG-A2-004 executable policy field → POLICY_SCHEMA_INVALID
NEG-A2-005 PR marker other Work → PR_WORK_BINDING_CONFLICT
NEG-A2-006 user self-declared PASS → not accepted
NEG-A2-007 SKIPPED-only checks → not enough success
NEG-A2-008 gh unavailable → BLOCKED, never PASS
NEG-A2-009 Gate mutates repo → Acceptance FAIL
NEG-A2-010 HIGH + all green → still BLOCKED
```

---

# 22. Failure Injection

Mutation：

```text
FI-A2-001 work create before atomic replace
→ no partial Work file

FI-A2-002 artifact link before replace
→ T0 preserved

FI-A2-003 policy write failure
→ no partial policy
```

Gate/provider：

```text
FI-A2-004 gh timeout
→ BLOCKED / GITHUB_PROVIDER_UNAVAILABLE

FI-A2-005 malformed GitHub JSON
→ BLOCKED / GITHUB_PROVIDER_INVALID

FI-A2-006 PR head changes during evaluation
→ PR_HEAD_CHANGED_DURING_EVALUATION
→ no MERGE_READY

FI-A2-007 local HEAD changes during evaluation
→ LOCAL_HEAD_CHANGED_DURING_EVALUATION
→ no MERGE_READY
```

---

# 23. Evidence Contract

Gate JSON Evidence MUST include：

```text
work_id
policy_id
repo identity
local HEAD
PR number
PR head
SPEC digest
PLAN digest
CI observations
Review observation
reason codes
evaluated_at
GES version
gh version
git version
```

Alpha.2 Release Evidence MUST bind：

```text
GES candidate commit
Golden consumer repo
Golden PR number
Golden PR head SHA
Golden Work ID
policy digest
commands
exit codes
AC oracles
```

Release Evidence：

```text
external CI artifact / release asset
```

MUST NOT create Evidence self-reference commit。

---

# 24. Release Gate

Required groups：

```text
Governance Init
Work Registry
Artifact Registry
Policy
GitHub Provider
Evidence
Traceability
Gate A
Gate B
Read-only
Security
Golden Consumer
```

任何 Required AC：

```text
!= PASS
```

则：

```text
Alpha.2 Release Gate != PASS
process exit != 0
```

全部 PASS：

```text
GES 6.0-alpha.2 Governance Backplane Foundation: PASS

Work Registry: PASS
Artifact Registry: PASS
Evidence Registry: PASS
Policy Engine: PASS
Traceability: PASS
WORK_READY: PASS
MERGE_READY: PASS
Golden Consumer: PASS

BACKPLANE_ALPHA2_READY
```

---

# 25. Golden Consumer / Real-world Acceptance

Golden Consumer：

```text
E:\git\smc-copilot-desktop
loudon84/smc-copilot-desktop
```

Alpha.2 不自动创建、approve、merge PR。

Release Operator 提供：

```text
GES_ALPHA2_GOLDEN_PR=<number>
GES_ALPHA2_GOLDEN_WORK_ID=<work-id>
```

Golden PR MUST：

```text
belong to smc-copilot-desktop
OPEN
not draft
contain exact GES-Work marker
approved review
>=1 SUCCESS check
no pending/failing observation
```

Golden runner：

```text
resolve PR head
fetch commit
create detached worktree at PR head
Gate A
Evidence collect
Trace
Gate B
read-only verification
external Evidence
```

MUST NOT：

```text
edit PR
approve PR
merge PR
modify E:\git\smc-copilot-desktop source workspace
```

Golden Oracle：

```text
Gate A = WORK_READY
Trace complete
Evidence subject = PR head
Gate B = MERGE_READY
business source unchanged
source workspace unchanged
```

---

# 26. Requirement Traceability Matrix

| Requirement | Acceptance | Release |
|---|---|---|
| REQ-A2-GOV-001 | A-A2-GOV-001..002 | REQUIRED |
| REQ-A2-WORK-001 | A-A2-WORK-001..003 | REQUIRED |
| REQ-A2-ART-001 | A-A2-ART-001..003 | REQUIRED |
| REQ-A2-POLICY-001 | A-A2-POLICY-001..003 | REQUIRED |
| REQ-A2-GH-001 | A-A2-GH-001..002 | REQUIRED |
| REQ-A2-EVID-001 | A-A2-EVID-001..003 | REQUIRED |
| REQ-A2-TRACE-001 | A-A2-TRACE-001..002 | REQUIRED |
| REQ-A2-GATE-001 | A-A2-INTAKE-001..003 | REQUIRED |
| REQ-A2-GATE-002 | A-A2-MERGE-001..005 | REQUIRED |
| REQ-A2-GATE-003 | A-A2-EXPLAIN-001..002 | REQUIRED |
| REQ-A2-READONLY-001 | A-A2-RO-001..002 | REQUIRED |

Plan MUST 为每个 AC 创建独立 Test ID + Evidence。

---

# 27. Plan Generation Contract

仅：

```text
status = APPROVED_FOR_PLAN
```

允许 `.plan.md`。

Plan MUST NOT：

```text
实现 Gate C
实现 Approval
实现 Release Runtime
实现 Multica integration
实现 Agent orchestration
增加 Composer capability
```

建议分组：

```text
PLAN-A2-01 Governance Schemas / Storage
PLAN-A2-02 Work Registry CLI
PLAN-A2-03 Artifact Resolver
PLAN-A2-04 Policy Engine
PLAN-A2-05 Git / GitHub Provider
PLAN-A2-06 Evidence Observation
PLAN-A2-07 Traceability Graph
PLAN-A2-08 Gate A
PLAN-A2-09 Gate B / Explain
PLAN-A2-10 Read-only / Race Hardening
PLAN-A2-11 Synthetic Acceptance
PLAN-A2-12 smc-copilot-desktop Golden PR
PLAN-A2-13 External Release Evidence
```

Todo：

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

---

# 28. Code Review Contract

Review order：

```text
1 GES 是否侵入 Agent Runtime
2 Work / Policy SOT 是否唯一
3 Artifact 是否 pointer-only
4 Artifact digest 是否精确
5 Evidence 是否 provider-backed
6 Evidence 是否绑定 PR head
7 Gate A 是否 deterministic
8 Gate B 是否 read-only
9 Gate Explain 是否完整
10 HEAD race 是否检测
11 HIGH Risk 是否错误放行
12 GitHub unavailable 是否 BLOCKED
13 Traceability 是否完整
14 Synthetic / Golden 是否分离
15 Code quality
```

---

# 29. Definition of Done

Alpha.2 只有满足全部条件才允许：

```text
BACKPLANE_ALPHA2_READY
```

```text
[ ] Alpha.1 Composer semantics unchanged
[ ] governance init 与 Composer state 正交
[ ] ges.work.v1 complete
[ ] ges.policy.v1 complete
[ ] ges.evidence-snapshot.v1 complete
[ ] ges.trace.v1 complete
[ ] ges.gate-result.v1 complete

[ ] Work create/show/update/close
[ ] explicit Work ID
[ ] FEATURE only
[ ] owner required
[ ] risk enforced

[ ] SPEC pointer-only
[ ] PLAN pointer-only
[ ] exact SHA256 drift detection
[ ] traversal/symlink escape blocked

[ ] deterministic Policy
[ ] no LLM Policy
[ ] HIGH cannot MERGE_READY

[ ] gh preflight
[ ] GitHub Provider read-only
[ ] PR observation
[ ] Work marker validation
[ ] local HEAD == PR HEAD

[ ] SUCCESS only counts CI PASS
[ ] SKIPPED != PASS
[ ] pending/fail/cancel blocks merge
[ ] Review requires APPROVED
[ ] Evidence subject binds PR head
[ ] stale Evidence rejected
[ ] no manual PASS Evidence API

[ ] complete Trace graph
[ ] missing nodes visible

[ ] Gate A WORK_READY
[ ] Gate B MERGE_READY
[ ] Gate Explain deterministic
[ ] all Gate commands 0 repo mutation
[ ] all GitHub operations 0 remote mutation

[ ] local/PR HEAD race detected

[ ] Synthetic tests PASS
[ ] real smc-copilot-desktop Golden PR PASS
[ ] Golden Gate A WORK_READY
[ ] Golden Gate B MERGE_READY
[ ] Golden source unchanged
[ ] external Release Evidence valid

[ ] no Required AC BLOCKED/SKIPPED/FAIL
[ ] Release Gate PASS
```

---

# 30. Alpha.2 Product Completion Definition

完成 Alpha.2 后，GES 必须能稳定回答：

```text
Work 是什么？
→ Work Registry

需求和技术意图在哪里？
→ SPEC / PLAN ArtifactRef

当前 Merge Candidate 是什么？
→ GitHub PR

实现 Commit 是哪个？
→ PR head SHA

测试证明是什么？
→ GitHub CI Evidence

Review 证明是什么？
→ GitHub Review Decision

Evidence 是否属于当前 Commit？
→ subject SHA binding

能否进入开发？
→ WORK_READY

能否合并？
→ MERGE_READY

不能合并缺什么？
→ Gate Explain
```

GES 仍然不回答：

```text
PRD 写得好不好
代码方案是不是最佳
模型是否正确思考
Review 推理质量是否优秀
```

---

# 31. 下一阶段边界

Alpha.2 完成后才进入：

```text
GES 6.0-alpha.3
Release Truth & Release Readiness
```

候选能力：

```text
Approval Runtime
Gate C — Release Readiness
Build Artifact
Deployment Artifact
Release Artifact
Environment Identity
Release Approval
Release Evidence
Rollback Evidence
Audit / Release Truth
```

Alpha.2 MUST NOT 提前实现这些能力。

---

# 32. 最终产品原则

```text
1. Composer 决定项目需要什么工程能力。
2. Backplane 决定交付结果是否满足治理条件。
3. GES 不接管 Agent 推理。
4. GES 不复制 Spec / Plan / Review 正文。
5. Work 是 Governance Aggregate，不是 Agent Task。
6. Git/GitHub 是 Alpha.2 Delivery Truth。
7. Work / Policy 是版本化声明。
8. Evidence 是外部事实观察，不是可编辑 PASS 标签。
9. Gate Result 是派生结果。
10. Evidence 必须绑定当前 PR HEAD。
11. 新 Commit 必须使旧 Evidence 失效。
12. SKIPPED / BLOCKED / PENDING 不能进入 MERGE_READY。
13. HIGH Risk 在无 Approval Runtime 时必须 BLOCK。
14. Gate 必须 read-only。
15. Policy 必须 deterministic、可解释、无 LLM。
16. Traceability 必须从 Work 追到当前 Commit 与 Evidence。
17. Synthetic Fixture 不能替代真实 GitHub PR。
18. Multica 后续消费 GES Gate Truth，而不是重做治理规则。
19. Alpha.2 的产品证明是真实 PR 能得到可信 MERGE_READY。
20. Release Readiness 属于 Alpha.3。
