---
title: "GES 6.0-alpha.1 Release Hardening PRD"
subtitle: "Immutable Evidence + Strict Spec Kit Smoke + Native Cursor Discovery + Release Hygiene"
prd_id: "PRD-GES-6.0-A1-RELEASE-HARDENING"
version: "1.0"
status: "APPROVED_FOR_PLAN"
product: "GES 6"
repository: "loudon84/smc-delivery-governance"
branch: "feat/ges-v6.0"
current_baseline_commit: "9fdfa400ffc66ad48f861bc65c55087c3092da70"
owner: "GES"
reviewers:
  - "Product / Architecture Owner"
  - "Independent Engineering Reviewer"
created_at: "2026-09-16"
updated_at: "2026-09-16"
target_release: "ges-v6.0.0-alpha.1"
change_type:
  - "RELEASE_HARDENING"
  - "ACCEPTANCE_HARDENING"
golden_consumer:
  path: 'E:\git\smc-copilot-desktop'
  repository: "loudon84/smc-copilot-desktop"
related_docs:
  - "需求PRD工程模板.md"
  - "PRD-GES-v6.0-alpha.1-Bootstrap-Closure-v1.0.md"
  - "GES-v6.0-alpha.1-spec-hardened-PRD.md"
supersedes:
  - "Alpha.1 中将 committed evidence 文件作为当前 HEAD Release Truth 的做法"
  - "Spec Kit smoke 在被测流程失败后由 runner 自动补写 feature.json 的做法"
  - "Cursor runtime probe 直接给出 Skill 文件路径的弱发现证明"
goal: "在不扩大 Alpha.1 Composer 功能范围的前提下，完成正式 Tag 前的 Release Evidence、Smoke Oracle、Cursor Native Discovery 与 CI/文档状态硬化。"
---

# GES 6.0-alpha.1 Release Hardening PRD

> 本 PRD 按《需求PRD工程模板.md》输出。
>
> 本版本不是新的 Composer 功能版本，也不是 `6.0-alpha.2`。
>
> 本版本唯一目标是：
>
> **把已经功能闭环的 GES 6.0-alpha.1 Bootstrap，从“真实运行已 PASS”提升为“最终 immutable release commit 可以被独立、不可自引用地证明并正式打 tag”。**

---

# 0. PRD 使用原则

## 0.1 本 PRD 只解决四类问题

```text
RH-01 Evidence SHA 自引用问题

RH-02 Spec Kit Functional Smoke 自动补答案问题

RH-03 Cursor Runtime Discovery 强度不足问题

RH-04 Release Hygiene
      ├─ CI / Release Gate 没有进入正式 GitHub Release 流程
      └─ LAT / 文档状态仍保留旧的 Golden BLOCKED 描述
```

任何新增需求如果属于：

```text
Governance Backplane
Work Registry
Evidence Registry
Policy
Risk
Approval
Merge Readiness
Release Readiness
Capability Upgrade
Capability Reconfigure
GES v5 Migration
```

必须进入后续版本，不得写入本 PRD。

## 0.2 Normative Keywords

```text
MUST
MUST NOT
SHOULD
SHOULD NOT
MAY
```

所有 `MUST / MUST NOT` 必须映射到至少一个 Acceptance。

## 0.3 No-Inference Rule

Plan Agent / Coding Agent 不得自行决定：

```text
什么 Commit 被视为 Release Candidate
Evidence 存在哪里
Evidence 是否要 commit 回代码仓库
Tag 指向哪个 Commit
Smoke 缺少 feature.json 时是否允许补写
Cursor Discovery 是否允许给具体 SKILL.md path
哪些 CI 结果构成 Release Gate
什么时候允许输出 BOOTSTRAP_ALPHA_READY
旧 LAT 文档是否可继续保留 BLOCKED 描述
```

无法从本 PRD 唯一确定时：

```text
SPEC_SEMANTIC_GAP
→ BLOCK PLAN
```

---

# 1. 文档元数据与当前基线

当前 `feat/ges-v6.0` 产品代码已经完成 Bootstrap Closure。

当前代码基线：

```text
9fdfa400ffc66ad48f861bc65c55087c3092da70
```

此前 Golden Closure PASS Evidence：

```text
audit/ges6/bootstrap-closure/20260916T072944Z/evidence.json
```

该 Evidence 实际绑定：

```text
GES commit:
d799bdb580f0e206fe5bb75178474d0394116c1e

Golden Consumer:
E:\git\smc-copilot-desktop
@ 737409b14e7499723db25fcb0414fa3e7026a86f
```

因此当前存在：

```text
Evidence PASS
but
Evidence GES SHA != current branch HEAD
```

这不是 Bootstrap 功能失败，而是 Release Evidence 模型需要硬化。

---

# 2. 一句话目标

让 `ges-v6.0.0-alpha.1` 的正式 Release Candidate Commit 在不修改自身 Git SHA 的情况下，由外部不可变 Evidence 证明：Synthetic CI PASS、真实 `smc-copilot-desktop` Golden Closure PASS、Spec Kit Smoke 没有测试补写、Cursor Agent 能通过原生 Skill 名称发现机制使用 GES Skills、文档状态与 Release Truth 一致，之后 Tag 精确指向被验证的 Candidate Commit。

---

# 3. 背景与问题定义

## 3.1 Current State

当前已经证明：

```text
Official Spec Kit staging        PASS
Spec Kit version pin             PASS
Cursor structural discovery      PASS
Cursor runtime probe             PASS
Spec Kit functional smoke        PASS
Golden Consumer                  PASS
ges doctor                       READY
second ges init                  GES_RECONCILE_NOOP
business source guard            PASS
```

但存在四个 Release-level 质量问题。

## 3.2 Problem A — Evidence SHA Self-reference

当前典型流程：

```text
Commit C
↓
在 C 工作区运行 Golden
↓
生成 evidence(C)
↓
把 evidence.json commit 进仓库
↓
产生 Commit C2
```

此时：

```text
evidence.ges.commit_sha = C
current HEAD = C2
```

如果再次对 C2 运行并 commit Evidence：

```text
C2
↓ test
↓ evidence(C2)
↓ commit
C3
```

会无限产生：

```text
Evidence 永远落后当前 HEAD 一个 Commit
```

问题本质：

> **Evidence 本身不能同时成为“被验证代码 Commit 的组成部分”和“证明该 Commit 不变的证据”。**

## 3.3 Problem B — Spec Kit Smoke Auto-answer

当前 Functional Smoke 在：

```text
spec.md exists
AND
.specify/feature.json missing
```

时会再次调用 Cursor：

```text
Write only .specify/feature.json ...
```

这导致测试 Runner 在 System Under Test 没完成要求时：

```text
主动补全缺失结果
```

然后：

```text
A-SKF-002 仍可能 PASS
```

违反：

```text
Acceptance Observer MUST NOT repair the system under test.
```

## 3.4 Problem C — Runtime Discovery 仍包含路径提示

当前 Cursor probe prompt 会直接告诉 Agent：

```text
.agents/skills/grill-with-docs/SKILL.md
.cursor/skills/speckit-specify/SKILL.md
.agents/skills/writing-plans/SKILL.md
```

这种 Probe 已经比“目录存在”更强，但证明的是：

```text
Cursor runtime 可以按指定路径读取并 follow Skill
```

而不是：

```text
Cursor project Skill registry / automatic skill loading
可以通过 Skill identity 本身发现 Skill
```

因此 Runtime Acceptance 应验证：

```text
Skill Name → Runtime Discovery / Invocation
```

而不是：

```text
File Path → Runtime Read
```

## 3.5 Problem D — Release Hygiene

### D1. CI / Release Gate

当前 `feat/ges-v6.0` 没有形成正式的：

```text
Candidate Commit
→ CI
→ Windows Golden Closure
→ External Evidence
→ Tag
```

发布链。

Golden Closure 当前主要依赖开发者本机运行。

### D2. 文档状态不一致

部分 LAT 文档仍保留：

```text
A27 remains BLOCKED
Golden Consumer dirty
```

但当前真实 Bootstrap Closure 已经：

```text
Golden PASS
BOOTSTRAP_ALPHA_READY
```

出现：

```text
Runtime Truth != Documentation Truth
```

---

# 4. Scope

## 4.1 In Scope

```text
SCOPE-RH-001
定义 immutable Release Candidate Commit。

SCOPE-RH-002
Evidence 从“代码 commit 内容”改为“外部 Release Artifact”。

SCOPE-RH-003
建立 candidate SHA → evidence → tag 的唯一发布顺序。

SCOPE-RH-004
移除 Functional Smoke 自动补写 feature.json。

SCOPE-RH-005
强化 A-SKF-001/002/003 Oracle。

SCOPE-RH-006
Cursor Runtime Probe 从 path-directed 改为 name-directed/native-discovery probe。

SCOPE-RH-007
保留 Cursor structural discovery 与 runtime discovery 两层验证。

SCOPE-RH-008
增加普通 Synthetic CI workflow。

SCOPE-RH-009
增加 Windows Golden Release Gate workflow / controlled runner contract。

SCOPE-RH-010
Golden Evidence 作为 CI Artifact / GitHub Release Asset 保存。

SCOPE-RH-011
正式 Tag 必须指向已经通过全部 Release Gate 的 Candidate Commit。

SCOPE-RH-012
更新 LAT / Release Status 文档到 Alpha.1 COMPLETE。

SCOPE-RH-013
清除文档中的过期 Golden BLOCKED 状态。
```

## 4.2 Out of Scope

```text
NON-GOAL-RH-001
不新增 Composer capability。

NON-GOAL-RH-002
不新增 Spec Kit tasks/implement/converge。

NON-GOAL-RH-003
不实现 GES Governance Backplane Runtime。

NON-GOAL-RH-004
不实现 Work/Artifact/Evidence Registry 产品模块。

NON-GOAL-RH-005
不实现 capability upgrade / reconfigure。

NON-GOAL-RH-006
不改变 smc-copilot-desktop 业务代码。

NON-GOAL-RH-007
不要求将 Golden Evidence 再 commit 回被验证的 Candidate Commit。

NON-GOAL-RH-008
不以 Git branch protection 配置本身作为 Alpha.1 产品代码 Requirement；
但 CI Result MUST 成为 Tag Release Gate。
```

---

# 5. Architecture Boundary

| Domain | Owner | Input | Output | 不负责 |
|---|---|---|---|---|
| Candidate Identity | Git | branch HEAD | immutable commit SHA | 判断功能正确 |
| Synthetic CI | GitHub Actions | candidate SHA | unit/synthetic result | Golden Runtime |
| Golden Closure | GES Acceptance Runner | candidate SHA + Golden HEAD | closure evidence | 修改 Candidate Commit |
| Evidence Storage | CI Artifact / Release Asset | evidence files | immutable evidence reference | 代码逻辑 |
| Spec Kit Smoke | Golden Runner + Cursor | projected runtime | observed Spec output | 修复被测结果 |
| Cursor Runtime | Cursor Agent | project Skill identity | native runtime proof | GES projection |
| Release Tag | Git | verified candidate SHA | `ges-v6.0.0-alpha.1` | 修改代码 |
| LAT Docs | GES Docs | Release truth | architecture/current status | 运行时证明 |

---

# 6. Terminology

```text
Release Candidate Commit / RC Commit
  准备打 Alpha.1 tag 的 immutable Git Commit。

Candidate SHA
  RC Commit 的完整 40-char SHA。

Code-bound Evidence
  Evidence 放在被验证仓库 commit 内容中。
  Alpha.1 正式发布 MUST NOT 使用它作为最终 Release Truth。

External Evidence
  不改变 Candidate SHA 的外部证据：
  GitHub Actions Artifact、GitHub Release Asset、
  或其他 immutable evidence store。

Evidence Manifest
  对本次 Release Gate 所有 Evidence Artifact 的身份、SHA256 和来源进行记录的机器可读 manifest。

Golden Evidence
  在真实 smc-copilot-desktop committed HEAD 上运行 Golden Closure 的证据。

Native Skill Discovery
  Cursor Agent 未被告知 SKILL.md 路径的情况下，
  根据 Skill identity / project Skill registry 识别并使用项目 Skill。

Path-directed Probe
  Prompt 明确告诉 Cursor SKILL.md 文件路径。
  Alpha.1 Release Gate MUST NOT 以此作为 Native Discovery PASS。

Observer
  Acceptance Runner。

System Under Test / SUT
  GES projection + Cursor Runtime + Spec Kit workflow。

Test Repair
  Acceptance Runner 在 SUT 失败后主动写入期望结果使测试继续。
  MUST NOT。

Release Truth
  Candidate SHA + CI Evidence + Golden Evidence + Tag identity。
```

---

# 7. Authoritative State / Source of Truth

| State | Role | Authoritative | Writer | Location |
|---|---|---:|---|---|
| Candidate SHA | RELEASE_CODE_STATE | YES | Git | Git object database |
| Golden Consumer SHA | CONSUMER_STATE | YES | Git | `E:\git\smc-copilot-desktop` HEAD |
| Synthetic CI Result | EVIDENCE_STATE | YES for synthetic gate | CI | GitHub Actions |
| Golden Closure Evidence | EVIDENCE_STATE | YES for runtime gate | Golden workflow | external artifact |
| Evidence Manifest | EVIDENCE_STATE | YES | Release pipeline | artifact/release |
| Release Tag | RELEASE_STATE | YES | release operator/workflow | Git tag |
| LAT Current Status | DOCUMENTATION_STATE | NO for executable truth | docs | repository |
| old committed bootstrap evidence | HISTORICAL_EVIDENCE | NO for final tag gate | repository | `audit/**` |

Rules：

```text
Candidate SHA is immutable.

Evidence MUST point to Candidate SHA.

Evidence MUST NOT require creating a new code Commit.

Tag MUST point exactly to Candidate SHA.

Tag MUST be created only after Evidence PASS.

Committed old evidence MAY remain as historical audit,
but MUST NOT be used as final Alpha.1 Release Truth.
```

---

# 8. State Machine

```text
DEVELOPMENT
   │
   │ freeze code/docs
   ▼
RC_CANDIDATE
   │
   ├─ Synthetic CI
   ▼
SYNTHETIC_PASS
   │
   ├─ Golden Closure
   ▼
GOLDEN_PASS
   │
   ├─ Evidence Binding
   ▼
RELEASE_EVIDENCE_PASS
   │
   ├─ Tag candidate SHA
   ▼
ALPHA1_TAGGED
```

失败：

```text
SYNTHETIC_FAIL
GOLDEN_FAIL
GOLDEN_BLOCKED
EVIDENCE_STALE
DOC_STATUS_STALE
```

任一失败：

```text
MUST NOT TAG
MUST NOT emit RELEASE_READY
```

如果 Candidate Commit 后发生任何代码或受管文档修改：

```text
new commit SHA
→ previous evidence becomes STALE
→ state returns RC_CANDIDATE
→ all Required Gate rerun
```

---

# 9. Schema Contracts

## 9.1 `ges.release-evidence-manifest.v1`

```json
{
  "schema": "ges.release-evidence-manifest.v1",
  "release": "ges-v6.0.0-alpha.1",
  "candidate": {
    "repository": "loudon84/smc-delivery-governance",
    "commit_sha": "<40-char sha>",
    "branch": "feat/ges-v6.0"
  },
  "golden_consumer": {
    "repository": "loudon84/smc-copilot-desktop",
    "commit_sha": "<40-char sha>"
  },
  "synthetic": {
    "status": "PASS",
    "workflow_run_id": "<id>",
    "artifact_name": "<name>",
    "sha256": "<sha256>"
  },
  "golden": {
    "status": "PASS",
    "workflow_run_id": "<id>",
    "artifact_name": "<name>",
    "evidence_sha256": "<sha256>"
  },
  "documentation": {
    "status": "PASS"
  },
  "release_gate": "PASS"
}
```

Schema rule：

```text
additionalProperties = false
```

## 9.2 Final Golden Evidence

现有：

```text
ges.bootstrap-closure-evidence.v1
```

继续使用，但正式 Release Gate 必须：

```text
evidence.ges.commit_sha == Candidate SHA
```

并由 External Evidence Store 保存。

---

# 10. Requirement Units

## REQ-RH-EVID-001 — Immutable Candidate Evidence Model

### Goal

彻底消除 Evidence SHA 自引用。

### Normative Requirement

Release Pipeline MUST 冻结：

```text
candidate_sha = git rev-parse HEAD
```

之后：

```text
MUST run Synthetic CI against candidate_sha.
MUST run Golden Closure against candidate_sha.
MUST store Evidence outside candidate Git tree.
MUST NOT commit final Release Evidence back into candidate branch.
MUST verify evidence.ges.commit_sha == candidate_sha.
```

允许 External Evidence：

```text
GitHub Actions Artifact
GitHub Release Asset
immutable artifact store
```

Alpha.1 推荐：

```text
GitHub Actions Artifact
+
最终 Tag 后附加 GitHub Release Asset
```

### Inputs

```text
candidate_sha
synthetic result
golden result
```

### Preconditions

```text
PRE-EVID-001 candidate working tree has no uncommitted release code/doc changes
PRE-EVID-002 candidate SHA is resolvable
```

### State Transition

```text
RC_CANDIDATE
→ evidence execution
→ RELEASE_EVIDENCE_PASS
```

### Allowed Side Effects

```text
CI artifact storage
GitHub release asset storage
```

### Forbidden Side Effects

```text
MUST NOT write final evidence into candidate Git tree and commit it.
MUST NOT amend candidate commit after evidence execution.
```

### Idempotency

对同一：

```text
Candidate SHA
Golden Consumer SHA
tool versions
```

重复执行可产生不同 run_id，但：

```text
all evidence candidate bindings MUST remain identical.
```

### Failure Semantics

```text
candidate changed during gate
→ EVIDENCE_CANDIDATE_MOVED
→ BLOCK

evidence SHA mismatch
→ EVIDENCE_COMMIT_MISMATCH
→ BLOCK

artifact upload missing
→ EVIDENCE_ARTIFACT_MISSING
→ BLOCK
```

### Postconditions

```text
Candidate SHA unchanged.
External Evidence exists.
Evidence points to Candidate SHA.
```

### Acceptance

```text
A-RH-EVID-001
A-RH-EVID-002
A-RH-EVID-003
```

---

## REQ-RH-EVID-002 — Release Tag Binding

### Goal

确保正式 Alpha.1 Tag 指向实际被验证的 Commit。

### Normative Requirement

Tag：

```text
ges-v6.0.0-alpha.1
```

MUST：

```text
be created only after Release Gate PASS
point exactly to candidate_sha
```

推荐 annotated tag：

```text
tag name: ges-v6.0.0-alpha.1
message includes:
- Candidate SHA
- Golden Consumer SHA
- Evidence Run / Artifact reference
```

Tag 创建后：

```text
git rev-list -n 1 ges-v6.0.0-alpha.1
==
candidate_sha
```

### Failure

```text
tag points different commit
→ RELEASE_TAG_COMMIT_MISMATCH
→ Release FAIL
```

### Acceptance

```text
A-RH-TAG-001
A-RH-TAG-002
```

---

## REQ-RH-SMOKE-001 — Acceptance Observer Must Not Repair Spec Kit Output

### Goal

保证 Spec Kit Functional Smoke 是纯观察和验证，而不是测试帮助被测系统通过。

### Normative Requirement

当前以下 fallback MUST DELETE：

```text
if spec.md exists
and .specify/feature.json missing:
    invoke Cursor again
    write .specify/feature.json
```

Functional Smoke MUST：

```text
run one primary speckit-specify workflow
observe result
validate all required postconditions
```

如果：

```text
spec.md exists
feature.json missing
```

则：

```text
A-SKF-001 MAY PASS if spec contract pass
A-SKF-002 MUST FAIL
overall functional smoke MUST FAIL
```

Runner MUST NOT：

```text
write feature.json
ask Cursor to write feature.json after missing-state detection
create checklist after workflow
repair spec content
fill placeholder
retry by changing expected result
```

### Inputs

```text
single Cursor workflow result
workspace before/after
```

### Preconditions

```text
Cursor runtime ready
Spec Kit projected
```

### Authoritative State

```text
Actual files produced by primary SUT invocation.
```

### Allowed Side Effects

Only SUT-generated allowlist：

```text
specs/_ges-smoke/<run_id>/**
.specify/feature.json
```

### Forbidden Side Effects

Observer：

```text
0 repo writes
```

### Failure Semantics

```text
spec missing
→ SPEC_KIT_SMOKE_SPEC_MISSING

feature.json missing
→ SPEC_KIT_SMOKE_FEATURE_STATE_MISSING

feature.json invalid
→ SPEC_KIT_SMOKE_FEATURE_STATE_INVALID

unexpected write
→ GOLDEN_UNEXPECTED_MUTATION
```

### Postconditions

PASS requires all：

```text
spec.md valid
feature.json exists without repair
feature_directory exact
mutation allowlist exact
business source unchanged
```

### Acceptance

```text
A-RH-SMOKE-001
A-RH-SMOKE-002
A-RH-SMOKE-003
A-RH-SMOKE-004
```

---

## REQ-RH-SMOKE-002 — One Primary Invocation Defines Functional Truth

### Goal

禁止通过多轮 corrective prompts 把 workflow 拼成 PASS。

### Normative Requirement

每次 Functional Smoke 必须记录：

```text
primary_invocation_count = 1
repair_invocation_count = 0
```

如果 Cursor / provider transient failure：

```text
MAY retry the exact same primary invocation
```

但 retry 规则必须：

```text
same prompt
same environment
same expected artifacts
fresh disposable smoke directory
```

不得：

```text
根据上一次缺失结果改变 prompt 来补答案
```

### Acceptance

```text
A-RH-SMOKE-005
```

---

## REQ-RH-CURSOR-001 — Native Skill Discovery Probe

### Goal

证明 Cursor Agent 能通过 project Skill registry / Skill identity 发现能力，而不是只会按显式文件路径读取。

### Normative Requirement

保留 Structural Probe：

```text
文件结构
frontmatter
name
description
```

新增/替换 Runtime Probe 为 Native Probe。

Native Probe MUST NOT 在 Prompt 中包含：

```text
.agents/skills/
.cursor/skills/
SKILL.md
具体文件路径
```

Runtime Prompt MAY 包含：

```text
Skill name
目标行为
输出 schema
```

推荐 Probe 分三次独立执行：

```text
Probe 1:
Use project skill "grill-with-docs".
Return only discovery proof; do not modify files.

Probe 2:
Use project skill "speckit-specify".
Do not create a feature; return discovery proof only.

Probe 3:
Use project skill "writing-plans".
Return only discovery proof; do not modify files.
```

每个 Probe 输出：

```json
{
  "probe": "GES_CURSOR_NATIVE_SKILL_PROBE_V2",
  "requested_skill": "speckit-specify",
  "available": true,
  "recognized_name": "speckit-specify",
  "description": "<runtime-observed description>"
}
```

### Stronger Oracle

仅 Agent 自报 `available=true` 不够。

因此每个 required Skill 在测试前必须从实际 `SKILL.md` 提取：

```text
name
description_sha256
```

Probe 要求 Agent：

```text
返回 skill 的 declared name
以及 description 的原始文本
```

Evidence Runner 在外部计算：

```text
SHA256(agent_returned_description)
==
SHA256(actual SKILL.md frontmatter.description)
```

注意：

```text
Prompt MUST NOT 向 Agent 提供 expected description。
```

### Required Probe Set

```text
grill-with-docs
speckit-specify
writing-plans
```

### Preconditions

```text
structural discovery PASS
Cursor CLI available
Ask/read-only mode available
```

### Side Effects

```text
repo write = 0
```

### Failure Semantics

```text
skill not recognized
→ CURSOR_NATIVE_DISCOVERY_FAILED

description mismatch
→ CURSOR_SKILL_METADATA_MISMATCH

malformed output
→ CURSOR_DISCOVERY_OUTPUT_INVALID

CLI unavailable
→ CURSOR_RUNTIME_UNAVAILABLE / BLOCKED
```

### Acceptance

```text
A-RH-CURSOR-001
A-RH-CURSOR-002
A-RH-CURSOR-003
A-RH-CURSOR-004
```

---

## REQ-RH-CURSOR-002 — Native Discovery and Functional Invocation Separation

### Goal

避免把“能发现 Skill”和“某个具体流程碰巧运行成功”混成一个 Oracle。

### Normative Requirement

必须保留两个独立结论：

```text
CURSOR_NATIVE_DISCOVERY
SPEC_KIT_FUNCTIONAL
```

Release Gate：

```text
CURSOR_NATIVE_DISCOVERY = PASS
AND
SPEC_KIT_FUNCTIONAL = PASS
```

两者不得相互替代。

---

## REQ-RH-CI-001 — Synthetic CI Gate

### Goal

让 Alpha.1 Candidate 在进入昂贵 Golden Runtime Gate 前先通过可重复、无需 Cursor 登录的 deterministic 测试。

### Normative Requirement

新增 GitHub Actions Workflow：

建议：

```text
.github/workflows/ges-alpha1-ci.yml
```

Triggers：

```text
pull_request
push to feat/ges-v6.0
workflow_dispatch
```

Required jobs：

```text
schema-validation
pytest-ges6
bootstrap-synthetic
closure-synthetic
```

最低 required command：

```text
python -m pytest tests/ges6 -q
```

CI MUST 使用：

```text
GES_SOURCE_OFFLINE=1
official staging fixtures
```

Synthetic CI MUST NOT：

```text
require Cursor login
require Golden local E:\ drive
call live Cursor model
```

输出 Artifact：

```text
ges-alpha1-synthetic-<candidate_sha>
```

包含：

```text
pytest junit/xml or text
synthetic evidence
candidate SHA
tool versions
```

### Failure

任一 required job fail：

```text
RELEASE_CANDIDATE_SYNTHETIC_FAILED
→ MUST NOT run/tag release as PASS
```

### Acceptance

```text
A-RH-CI-001
A-RH-CI-002
```

---

## REQ-RH-CI-002 — Windows Golden Release Gate

### Goal

把当前本机 Golden Closure 提升为受控、可复验的 Release Gate。

### Normative Requirement

新增：

```text
.github/workflows/ges-alpha1-golden.yml
```

初始版本 MAY 使用：

```text
workflow_dispatch
```

Runner：

```text
self-hosted
Windows
具有：
- E:\git\smc-copilot-desktop
- git
- Python >= 3.11
- uv/uvx
- Cursor agent CLI
- 已授权 Cursor session
```

Workflow input：

```yaml
candidate_sha:
  required: true
```

Job MUST：

```text
checkout exact candidate_sha in detached mode
assert git rev-parse HEAD == candidate_sha

resolve Golden Consumer committed HEAD
run Golden Closure
verify all Required AC PASS
verify evidence GES SHA == candidate_sha
upload evidence externally
```

Golden Workflow MUST NOT：

```text
commit generated evidence back to branch
modify E:\git\smc-copilot-desktop original workspace
auto-create release tag before PASS
```

Artifact name：

```text
ges-alpha1-golden-<candidate_sha>-<consumer_sha>
```

### Acceptance

```text
A-RH-GOLDEN-CI-001
A-RH-GOLDEN-CI-002
A-RH-GOLDEN-CI-003
```

---

## REQ-RH-REL-001 — Release Evidence Manifest

### Goal

让正式发布可从一个 manifest 确定：

```text
验证了什么 Commit
Golden 是哪个 Consumer
证据在哪里
Tag 应该指向哪里
```

### Normative Requirement

当：

```text
Synthetic CI PASS
Golden CI PASS
Docs Status PASS
```

后生成：

```text
ges.release-evidence-manifest.v1
```

Manifest MUST 存储为：

```text
external CI Artifact
```

在 Tag / Release 创建后 SHOULD 同时上传为：

```text
GitHub Release Asset
```

Manifest MUST NOT 被要求 commit 回 Candidate Commit。

### Acceptance

```text
A-RH-REL-001
A-RH-REL-002
```

---

## REQ-RH-DOC-001 — Documentation Truth Synchronization

### Goal

消除运行时已经 READY、文档仍称 Golden BLOCKED 的事实源冲突。

### Normative Requirement

在 Candidate Freeze 前必须检查：

```text
lat.md/ges6/**
README / release-status related docs
Alpha.1 PRD status metadata
```

必须删除/更新过期状态：

```text
A27 remains BLOCKED while the Golden Consumer is dirty
Golden Consumer BLOCKED
Bootstrap Closure NOT READY
```

当前状态应该表达：

```text
Alpha.1 Bootstrap Functionally Complete

Official Spec Kit staging:
PASS

Cursor runtime:
PASS

Golden Consumer:
PASS

Tag:
PENDING RELEASE HARDENING
```

正式 Tag 后：

```text
Tag:
ges-v6.0.0-alpha.1
```

### Documentation Ownership

文档只描述 Release Truth：

```text
MUST NOT 成为可执行 Release Gate SOT。
```

### Acceptance

```text
A-RH-DOC-001
A-RH-DOC-002
```

---

## REQ-RH-TAG-001 — Alpha.1 Formal Tag Gate

### Goal

确保只有经过最终 hardening 的 immutable commit 被标记为 Alpha.1。

### Preconditions

以下必须 PASS：

```text
A-RH-EVID-001..003
A-RH-SMOKE-001..005
A-RH-CURSOR-001..004
A-RH-CI-001..002
A-RH-GOLDEN-CI-001..003
A-RH-REL-001..002
A-RH-DOC-001..002
```

### Normative Requirement

正式 tag：

```text
ges-v6.0.0-alpha.1
```

Tag Target：

```text
exact candidate_sha
```

Tag 创建前再次执行：

```text
git rev-parse candidate_sha
```

Tag 创建后执行：

```text
git rev-list -n 1 ges-v6.0.0-alpha.1
```

必须：

```text
tag_target == candidate_sha
```

### Release Asset

至少附：

```text
release-evidence-manifest.json
golden-evidence.json
synthetic-test-evidence.*
```

### Acceptance

```text
A-RH-TAG-001
A-RH-TAG-002
```

---

# 11. Side-Effect Contract

| Operation | GES Repo Write | Candidate Commit Change | Golden Source Write | Temp Worktree | External Artifact |
|---|---:|---:|---:|---:|---:|
| Synthetic CI | NO | NO | N/A | MAY | YES |
| Golden Closure | NO | NO | NO | YES | YES |
| Native Discovery | NO | NO | NO | read-only | YES evidence |
| Spec Kit Smoke | NO | NO | NO | allowlist | YES evidence |
| Evidence Manifest | NO | NO | NO | NO | YES |
| Tag creation | Git ref only | NO | NO | NO | MAY |
| Release Asset upload | NO | NO | NO | NO | YES |
| LAT update before candidate freeze | YES | new candidate SHA | NO | NO | NO |

关键约束：

```text
Candidate Freeze 之后：
代码和 Release-owned docs 都不允许修改。

任何修改：
→ Candidate SHA changes
→ previous Evidence STALE
→ rerun all gates.
```

---

# 12. Ownership Contract

```text
Candidate Commit:
GIT_IMMUTABLE

External Evidence:
GENERATED_EVIDENCE

Release Tag:
RELEASE_REF

Golden Source:
USER_OWNED_READ_ONLY

Golden Test Worktree:
DISPOSABLE_TEST_RESOURCE

Smoke Generated Artifacts:
TEST_GENERATED

LAT Docs:
GES_MANAGED_DOCUMENTATION
```

---

# 13. Identity / Hash Contract

## 13.1 Candidate Identity

```text
candidate_sha =
git rev-parse HEAD
```

必须 40-char。

## 13.2 Evidence Identity

每个外部 Artifact：

```text
artifact_sha256 = SHA256(raw artifact bytes)
```

Release Evidence Manifest 必须保存每个 Artifact digest。

## 13.3 Tag Identity

```text
tag_target_commit =
git rev-list -n 1 ges-v6.0.0-alpha.1
```

## 13.4 Cursor Skill Metadata Identity

Native Discovery stronger oracle：

```text
expected_description_digest =
SHA256(UTF-8 exact frontmatter description value)

actual_description_digest =
SHA256(UTF-8 agent returned description)
```

二者必须相等。

不做：

```text
trim/case folding/punctuation normalization
```

---

# 14. Transaction Contract

本 PRD不新增 Consumer installation transaction。

Release Transaction 定义：

```text
freeze candidate
→ synthetic gate
→ golden gate
→ evidence manifest
→ tag
→ release assets
```

如果在 Tag 前任一 gate fail：

```text
No Tag
```

如果 Tag 已创建但 Release Asset upload fail：

```text
Release MUST NOT be marked published/complete
```

推荐：

```text
evidence first
tag second
release publish last
```

禁止：

```text
tag first
tests later
```

---

# 15. Conflict / Failure Contract

| Failure | Behavior | Error | Release Result |
|---|---|---|---|
| current HEAD != candidate_sha | BLOCK | EVIDENCE_CANDIDATE_MOVED | BLOCKED |
| evidence SHA != candidate | BLOCK | EVIDENCE_COMMIT_MISMATCH | BLOCKED |
| smoke feature.json missing | FAIL | SPEC_KIT_SMOKE_FEATURE_STATE_MISSING | FAIL |
| observer writes feature.json | FAIL | ACCEPTANCE_OBSERVER_MUTATED_SUT | FAIL |
| native skill metadata mismatch | FAIL | CURSOR_SKILL_METADATA_MISMATCH | FAIL |
| Cursor unavailable | BLOCK | CURSOR_RUNTIME_UNAVAILABLE | BLOCKED |
| Synthetic CI fail | BLOCK release | RELEASE_CANDIDATE_SYNTHETIC_FAILED | FAIL |
| Golden Gate fail | BLOCK release | GOLDEN_RELEASE_GATE_FAILED | FAIL |
| external artifact missing | BLOCK | EVIDENCE_ARTIFACT_MISSING | BLOCKED |
| docs stale | BLOCK tag | RELEASE_DOCUMENTATION_STALE | BLOCKED |
| tag target mismatch | FAIL | RELEASE_TAG_COMMIT_MISMATCH | FAIL |

---

# 16. Compatibility / Migration

## 16.1 Historical Evidence

已有：

```text
audit/ges6/bootstrap-closure/**
```

MAY 保留历史记录。

但必须明确：

```text
HISTORICAL_ONLY
NOT FINAL RELEASE SOT
```

无需删除。

## 16.2 Existing Golden Runner

继续复用：

```text
ges/acceptance/run_golden_closure.py
```

但必须：

```text
删除 Smoke repair fallback
升级 Cursor runtime probe
支持 external artifact evidence flow
```

## 16.3 Existing committed Closure Evidence

旧 Evidence：

```text
d799... PASS
```

保留作为：

```text
development acceptance history
```

不能作为：

```text
ges-v6.0.0-alpha.1 final release evidence
```

---

# 17. External Dependency Contract

## 17.1 GitHub Actions

职责：

```text
Synthetic workflow
Golden workflow
Artifact retention
Release Asset
```

Alpha.1 不要求完全自动创建 Release，但 Tag Gate 必须机器可验证。

## 17.2 Cursor Agent

Native Probe 依赖：

```text
agent CLI
Ask/read-only execution
project Skills auto loading
```

Cursor project Skill roots：

```text
.agents/skills/
.cursor/skills/
```

Native Probe 不得直接提供路径。

## 17.3 Golden Machine

```text
Windows
E:\git\smc-copilot-desktop
Cursor authenticated
uvx available
```

---

# 18. Security Contract

| Threat | Control | Acceptance |
|---|---|---|
| CI Evidence 泄露 Cursor token | environment secret never serialized | A-RH-SEC-001 |
| Golden runner 修改开发工作区 | detached test worktree | A-RH-GOLDEN-CI |
| Uncommitted developer files进入 release proof | test committed HEAD only | A-RH-GOLDEN-CI |
| Native Probe 意外写文件 | Ask/read-only + before/after digest | A-RH-CURSOR-004 |
| Smoke 修改业务源码 | mutation allowlist + business digest | A-RH-SMOKE-004 |
| Release Asset 被替换无法检测 | SHA256 in manifest | A-RH-REL-002 |
| Tag 指错 Commit | exact target verify | A-RH-TAG-001 |
| Workflow 运行错误 branch HEAD | checkout explicit candidate_sha | A-RH-GOLDEN-CI-001 |

Secrets：

```text
MUST NOT store:
Cursor auth token
GitHub token
environment secret value
machine user credential
```

---

# 19. Observability

新增 Release stages：

```text
RC_FREEZE
SYNTHETIC_CI
GOLDEN_CI
CURSOR_NATIVE_DISCOVERY
SPECKIT_STRICT_SMOKE
EVIDENCE_BIND
DOC_STATUS_CHECK
TAG_VERIFY
RELEASE_ASSET
```

每个 stage：

```text
run_id
candidate_sha
stage
status
started_at
finished_at
exit_code
error_code
artifact_refs
```

---

# 20. Acceptance Design

## A-RH-EVID-001 — Evidence Does Not Change Candidate SHA

### Given

```text
candidate_sha = C
```

### When

Synthetic + Golden Evidence generated and stored。

### Then

```text
git rev-parse HEAD == C
```

### Oracle

```text
before_candidate_sha == after_candidate_sha
```

---

## A-RH-EVID-002 — External Evidence Binds Candidate

```text
evidence.ges.commit_sha == candidate_sha
```

且：

```text
evidence artifact exists outside Candidate Git tree
```

---

## A-RH-EVID-003 — Committing Evidence Is Not Required

Final Gate 可以在：

```text
git status of candidate repo == clean
```

且没有新增 final release evidence commit 的情况下 PASS。

---

## A-RH-TAG-001 — Tag Target Exact

```text
git rev-list -n 1 ges-v6.0.0-alpha.1
==
candidate_sha
```

---

## A-RH-TAG-002 — Release Asset Binds Same Candidate

Release manifest：

```text
candidate.commit_sha == tag_target
```

---

## A-RH-SMOKE-001 — Missing Feature State Fails

Given：

```text
primary Spec Kit run creates spec.md
but not .specify/feature.json
```

Expected：

```text
A-SKF-002 = FAIL
SPEC_KIT_SMOKE_FEATURE_STATE_MISSING
```

Runner 不产生任何 corrective prompt。

---

## A-RH-SMOKE-002 — Observer Zero Write

在 primary invocation 完成后进入 evaluate 阶段：

```text
workspace_digest_before_evaluate
==
workspace_digest_after_evaluate
```

---

## A-RH-SMOKE-003 — Valid Feature State Pass

```text
feature.json exists
JSON valid
feature_directory == specs/_ges-smoke/<run_id>
```

---

## A-RH-SMOKE-004 — Business Source Preserved

```text
business_source_before == business_source_after
```

---

## A-RH-SMOKE-005 — No Repair Invocation

Evidence：

```text
repair_invocation_count == 0
```

不得存在：

```text
"Write only .specify/feature.json ..."
```

类型 corrective prompt。

---

## A-RH-CURSOR-001 — Native Probe Contains No Skill Paths

Probe command/prompt：

```text
MUST NOT contain:
.agents/skills
.cursor/skills
SKILL.md
```

---

## A-RH-CURSOR-002 — Native Skill Identity

Required skills：

```text
grill-with-docs
speckit-specify
writing-plans
```

每个：

```text
available == true
recognized_name == requested_skill
```

---

## A-RH-CURSOR-003 — Native Metadata Proof

对每个 Skill：

```text
sha256(agent_returned_description)
==
sha256(actual_skill_frontmatter_description)
```

expected description 不得出现在 prompt。

---

## A-RH-CURSOR-004 — Native Probe Read-only

```text
tree_before == tree_after
```

---

## A-RH-CI-001 — Synthetic Workflow

真实 GitHub Workflow Run：

```text
candidate SHA exact
pytest tests/ges6 PASS
artifact uploaded
```

---

## A-RH-CI-002 — Synthetic Failure Blocks Release

注入 failing test：

```text
workflow != PASS
release gate != PASS
```

---

## A-RH-GOLDEN-CI-001 — Explicit Candidate Checkout

Golden runner machine：

```text
git rev-parse HEAD == workflow input candidate_sha
```

---

## A-RH-GOLDEN-CI-002 — Golden Artifact External

Golden workflow PASS 后：

```text
Golden Evidence uploaded
candidate source tree unchanged
```

---

## A-RH-GOLDEN-CI-003 — All Golden AC PASS

包括已有 Closure Required AC，且新增：

```text
A-RH-SMOKE
A-RH-CURSOR
```

均 PASS。

---

## A-RH-REL-001 — Evidence Manifest Complete

Required fields 全存在且 schema valid。

---

## A-RH-REL-002 — Artifact Digest Verification

读取 synthetic/golden Artifact：

```text
computed sha256 == manifest sha256
```

---

## A-RH-DOC-001 — No Stale Golden Blocked Statement

搜索 Current Status / LAT docs：

```text
"A27 remains BLOCKED while the Golden Consumer is dirty"
"Golden Consumer: BLOCKED"
```

当前状态上下文中不得存在。

历史 PRD/历史 Evidence 可以保留，不纳入 Current Status scan。

---

## A-RH-DOC-002 — Current Status Matches Gate

Tag 前：

```text
Alpha.1 Functionally Complete
Release Hardening PASS
Tag Pending / Candidate
```

Tag 后：

```text
Release tag = ges-v6.0.0-alpha.1
```

---

# 21. Acceptance Input Matrix

| Case | Candidate | Evidence | Feature JSON | Cursor Prompt | CI | Expected |
|---|---|---|---|---|---|---|
| R1 | unchanged | external | valid | no paths | PASS | Release PASS |
| R2 | changed after test | external | valid | no paths | PASS | STALE/BLOCK |
| R3 | unchanged | committed back | valid | no paths | PASS | final release model invalid |
| R4 | unchanged | external | missing | no paths | PASS | Smoke FAIL |
| R5 | unchanged | external | runner repairs | no paths | PASS | Observer FAIL |
| R6 | unchanged | external | valid | explicit SKILL paths | PASS | Native Discovery FAIL |
| R7 | unchanged | external | valid | names only + metadata match | PASS | Native PASS |
| R8 | unchanged | external | valid | names only | synthetic FAIL | no tag |
| R9 | unchanged | external | valid | names only | Golden BLOCKED | no tag |
| R10 | unchanged | external | valid | names only | all PASS but stale LAT | tag BLOCK |
| R11 | unchanged | external | valid | names only | all PASS + tag points other SHA | FAIL |
| R12 | unchanged | artifact missing | valid | names only | PASS | BLOCK |

---

# 22. Negative Acceptance

```text
NEG-RH-001
Generate final Evidence → git add/commit evidence
→ final gate rejects code-bound Evidence model

NEG-RH-002
Change one source file after Golden PASS
→ candidate SHA changes
→ previous Evidence STALE

NEG-RH-003
Remove .specify/feature.json after primary smoke
→ Smoke FAIL
→ no corrective invocation

NEG-RH-004
Native Probe contains ".cursor/skills"
→ A-RH-CURSOR-001 FAIL

NEG-RH-005
Agent returns expected skill name but wrong description
→ CURSOR_SKILL_METADATA_MISMATCH

NEG-RH-006
Synthetic workflow fail
→ tag creation blocked

NEG-RH-007
Golden external artifact upload fail
→ Release Gate BLOCKED

NEG-RH-008
LAT current-status page still says Golden BLOCKED
→ RELEASE_DOCUMENTATION_STALE

NEG-RH-009
Tag points parent/child instead of Candidate
→ RELEASE_TAG_COMMIT_MISMATCH
```

---

# 23. Failure Injection

```text
FI-RH-001
Golden PASS 后修改 candidate repo 文档
→ Evidence STALE

FI-RH-002
Evidence upload network failure
→ no tag

FI-RH-003
Smoke primary invocation returns spec.md only
→ no repair; FAIL

FI-RH-004
Cursor Native Probe returns malformed JSON
→ FAIL

FI-RH-005
Cursor Native Probe says available=true but description mismatch
→ FAIL

FI-RH-006
Synthetic test intentionally fail
→ Golden MAY be skipped; Tag blocked

FI-RH-007
Golden runner returns BLOCKED because Cursor auth unavailable
→ Tag blocked

FI-RH-008
Tag created against wrong SHA in dry-run fixture
→ tag verification fails
```

---

# 24. Evidence Contract

## 24.1 Artifact Layout

推荐 CI Artifact：

```text
ges-alpha1-release-evidence/
├── release-evidence-manifest.json
├── synthetic/
│   ├── test-result.xml
│   ├── synthetic-evidence.json
│   └── logs.txt
└── golden/
    ├── evidence.json
    ├── cursor-native-discovery.json
    ├── spec-kit-smoke.json
    ├── mutation-report.json
    ├── doctor-final.json
    └── second-init.txt
```

## 24.2 Evidence Naming

```text
ges-alpha1-rc-<candidate_sha[0:12]>-golden-<consumer_sha[0:12]>
```

## 24.3 Evidence Binding

所有顶层 Evidence：

```text
candidate_sha
consumer_sha
run_id
workflow_run_id
created_at
```

## 24.4 Evidence Retention

Alpha.1 Release Evidence：

```text
SHOULD be retained as GitHub Release Asset
```

而不是只依赖短期 Actions retention。

---

# 25. Release Gate

## 25.1 Required Gate

```text
GATE-1 Candidate Freeze
GATE-2 Synthetic CI
GATE-3 Golden Runtime
GATE-4 Evidence Binding
GATE-5 Documentation Truth
GATE-6 Tag Binding
```

## 25.2 Status

```text
PASS
FAIL
BLOCKED
STALE
```

规则：

```text
all pre-tag gates PASS
→ tag may be created

any FAIL/BLOCKED/STALE
→ MUST NOT tag
```

Tag 完成后：

```text
GATE-6 PASS
→ ALPHA1_RELEASED
```

## 25.3 Release Sequence

唯一允许顺序：

```text
1. 完成所有代码与文档修改
2. Commit Candidate C
3. Freeze C
4. Synthetic CI(C)
5. Golden Closure(C, Golden Consumer HEAD)
6. 生成 external Evidence(C)
7. 验证 Evidence(C)
8. 验证 Current Status docs
9. 创建 tag ges-v6.0.0-alpha.1 → C
10. 验证 tag target == C
11. 发布 Release
12. 上传 Release Evidence Assets
```

禁止：

```text
Tag first → test later
Evidence commit → new candidate without rerun
```

---

# 26. Golden Consumer Contract

Golden Consumer：

```text
E:\git\smc-copilot-desktop
```

Golden test 继续使用：

```text
committed HEAD
+
detached disposable worktree
```

原工作区：

```text
MUST remain unchanged
```

Golden Closure 必须至少证明：

```text
official Spec Kit staging PASS
ges init PASS
ges check PASS
ges doctor READY
Cursor Structural PASS
Cursor Native Discovery PASS
Strict Spec Kit Functional Smoke PASS
second ges init NOOP
business source unchanged
external Evidence bind Candidate SHA
```

---

# 27. Requirement Traceability Matrix

| Requirement | Acceptance | Evidence | Release Gate |
|---|---|---|---|
| REQ-RH-EVID-001 | A-RH-EVID-001..003 | external Evidence + SHA | REQUIRED |
| REQ-RH-EVID-002 | A-RH-TAG-001..002 | tag + release manifest | REQUIRED |
| REQ-RH-SMOKE-001 | A-RH-SMOKE-001..004 | smoke evidence | REQUIRED |
| REQ-RH-SMOKE-002 | A-RH-SMOKE-005 | invocation evidence | REQUIRED |
| REQ-RH-CURSOR-001 | A-RH-CURSOR-001..004 | native probe evidence | REQUIRED |
| REQ-RH-CURSOR-002 | Cursor + smoke outcomes | separate states | REQUIRED |
| REQ-RH-CI-001 | A-RH-CI-001..002 | Actions artifact | REQUIRED |
| REQ-RH-CI-002 | A-RH-GOLDEN-CI-001..003 | Golden artifact | REQUIRED |
| REQ-RH-REL-001 | A-RH-REL-001..002 | release manifest | REQUIRED |
| REQ-RH-DOC-001 | A-RH-DOC-001..002 | doc scan | REQUIRED |
| REQ-RH-TAG-001 | A-RH-TAG-001..002 | tag identity | REQUIRED |

---

# 28. Plan Generation Contract

只有本 PRD：

```text
APPROVED_FOR_PLAN
```

允许生成实施 Plan。

Plan MUST 至少拆分：

```text
PLAN-RH-01 Remove Smoke Repair Fallback
PLAN-RH-02 Native Cursor Discovery V2
PLAN-RH-03 External Evidence Model
PLAN-RH-04 Synthetic CI Workflow
PLAN-RH-05 Windows Golden Workflow
PLAN-RH-06 Release Evidence Manifest
PLAN-RH-07 LAT / Current Status Sync
PLAN-RH-08 Final Candidate + Tag Gate
```

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
status: planned
evidence: []
```

不得在代码写完时标记：

```text
verified
```

必须实际 AC PASS。

---

# 29. Code Review Contract

本版本 Review 顺序：

```text
1. Final Evidence 是否仍写回 Candidate Git tree
2. Evidence 是否绑定 exact Candidate SHA
3. Smoke 是否存在任何 corrective / repair prompt
4. feature.json 缺失是否真实 FAIL
5. Runtime Probe 是否仍泄露 Skill path
6. Native metadata proof 是否由 Agent 实际返回
7. Probe 是否 0 mutation
8. Synthetic CI 是否不依赖 Cursor
9. Golden CI 是否 checkout explicit Candidate SHA
10. Golden Evidence 是否 externalized
11. LAT Current Status 是否过期
12. Tag 是否只能指已验证 Candidate
13. 最后检查代码质量
```

---

# 30. PRD Quality Gate

## Architecture

```text
[x] 不扩大 Alpha.1 产品边界
[x] Release Candidate / Evidence / Tag Owner 明确
[x] External Evidence 与 Candidate 分离
```

## State

```text
[x] Candidate SHA 唯一 SOT
[x] Evidence 状态独立
[x] Tag 状态独立
```

## Side Effects

```text
[x] Smoke Observer 0 write
[x] Native Probe read-only
[x] Golden Source 0 write
[x] Evidence 不修改 Candidate
```

## Failure

```text
[x] missing feature.json = FAIL
[x] Cursor unavailable = BLOCK
[x] candidate moved = STALE
[x] artifact upload fail = BLOCK
[x] stale docs = BLOCK
```

## Acceptance

```text
[x] 每个 MUST 有 AC
[x] Negative AC 已定义
[x] Failure Injection 已定义
[x] Oracle 可机器判断
```

## Evidence

```text
[x] Evidence externalized
[x] Artifact SHA 定义
[x] Candidate SHA binding 定义
[x] Release Tag binding 定义
```

---

# 31. Definition of Done

正式允许创建：

```text
ges-v6.0.0-alpha.1
```

前必须全部满足：

```text
[ ] Alpha.1 代码和 Release 文档冻结为 Candidate C
[ ] Candidate C immutable
[ ] Smoke 不存在自动补 feature.json
[ ] Smoke Observer evaluate 阶段 0 write
[ ] feature.json 缺失会 FAIL
[ ] no repair invocation
[ ] Cursor Runtime Probe 不包含 .agents/skills path
[ ] Cursor Runtime Probe 不包含 .cursor/skills path
[ ] Cursor Runtime Probe 不包含 SKILL.md path
[ ] grill-with-docs Native Discovery PASS
[ ] speckit-specify Native Discovery PASS
[ ] writing-plans Native Discovery PASS
[ ] Native Skill description digest matches actual Skill metadata
[ ] Native Probe tree before == after
[ ] Synthetic CI PASS against Candidate C
[ ] Windows Golden Gate PASS against Candidate C
[ ] Golden Consumer uses E:\git\smc-copilot-desktop committed HEAD
[ ] Spec Kit Strict Functional Smoke PASS
[ ] ges doctor READY
[ ] second ges init = GES_RECONCILE_NOOP
[ ] business source unchanged
[ ] Golden Evidence stored outside Candidate Git tree
[ ] Evidence.ges.commit_sha == Candidate C
[ ] Evidence artifact SHA recorded
[ ] Release Evidence Manifest schema PASS
[ ] LAT current status no longer says Golden BLOCKED
[ ] Current Status says Alpha.1 Functionally Complete / Release Hardening PASS
[ ] no Required Gate is FAIL/BLOCKED/STALE
[ ] tag ges-v6.0.0-alpha.1 created
[ ] tag target == Candidate C
[ ] Release Asset includes final manifest + Golden Evidence
```

---

# 32. Final Release Contract

Alpha.1 正式发布的最终 Truth 固定为：

```text
Candidate Commit C
        │
        ├── Synthetic CI(C) = PASS
        │
        ├── Golden Closure(C, smc-copilot-desktop@G) = PASS
        │
        ├── Cursor Native Discovery = PASS
        │
        ├── Strict Spec Kit Smoke = PASS
        │
        ├── External Evidence(C,G) = VALID
        │
        └── Documentation Truth = CURRENT
        │
        ▼
tag ges-v6.0.0-alpha.1 → C
        │
        ▼
Release Asset:
Evidence Manifest + Golden Evidence
```

禁止再使用：

```text
Code Commit C
→ generate Evidence
→ commit Evidence
→ call new HEAD validated
```

禁止再使用：

```text
SUT missed expected artifact
→ runner writes expected artifact
→ PASS
```

禁止再使用：

```text
Tell Cursor exact SKILL.md path
→ Cursor reads path
→ claim native discovery PASS
```

正式 Alpha.1 只有同时满足：

```text
IMMUTABLE CANDIDATE
+
STRICT ORACLE
+
NATIVE RUNTIME PROOF
+
EXTERNAL EVIDENCE
+
RELEASE HYGIENE
```

才允许：

```text
ALPHA1_RELEASED
```

---

# 33. 下一阶段边界

完成本 PRD并打：

```text
ges-v6.0.0-alpha.1
```

后：

```text
Alpha.1 Composer Bootstrap MUST FREEZE.
```

除重大 Bootstrap Bug 外，不再继续增加 Composer 功能。

下一正式需求进入：

```text
GES 6.0-alpha.2
Governance Backplane Foundation
+ Work / Artifact / Evidence
+ Merge Readiness
```

本 PRD不得提前实现 Alpha.2 功能。
