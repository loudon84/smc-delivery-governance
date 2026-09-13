---
title: "GES Acceptance Closure / Remaining Findings Hardening PRD"
prd_version: "v5.0.2"
work_item_id: "GES-ACCEPTANCE-CLOSURE-5.0.2"
status: "DRAFT"
review_verdict: "PENDING"
governance_profile: "FULL"
previous_prd: "PRD-GES-v5.0.1-Acceptance-Hardening"
source_revision: "loudon84/smc-delivery-governance@98cdb89ed3007d630f2d401030c36757bbd8c362"
grounded_commit: "98cdb89ed3007d630f2d401030c36757bbd8c362"
canonical_path: "engineeing-skills/"
current_bundle_manifest_version: "5.0.0"
current_candidate: "BASELINE-CANDIDATE-v5.0.1"
accepted_baseline_bundle: "4.1.2"
accepted_plan_contract: "smc.plan.v3.3"
target_release_semver: "DEFERRED_TO_RELEASE_REVIEW"
commit_policy: "post_review"
---

# GES Acceptance Closure 工程方案 PRD v5.0.2

> Repository：`loudon84/smc-delivery-governance`  
> Canonical Branch：`master`  
> Canonical Path：`engineeing-skills/`  
> Grounded Source：`98cdb89ed3007d630f2d401030c36757bbd8c362`  
> Previous PRD：`PRD-GES-v5.0.1-Acceptance-Hardening`  
> 本 PRD：`v5.0.2`  
> 治理级别：`FULL`

## 0. 文档定位

本 PRD 是 v5.0.1 Acceptance Hardening 的闭环修订，不重新设计 GES 5 架构。目标是把当前“主体代码已落地、但 CI/正确性/发布治理/验证证据尚未闭环”的 Candidate，推进到真正可执行 Acceptance、Pilot 与 Benchmark 的状态。

本轮不以“代码已提交”为完成标准，而以：

```text
代码
+ deterministic test
+ CI evidence
+ repository protection evidence
+ install provenance
+ pilot evidence
+ benchmark evidence
```

共同作为完成标准。

当前实现状态必须继续保持为：

```text
PRD v5.0.1

Implementation:
  IN_PROGRESS

Static Feature Coverage:
  C01 PARTIAL
  C02 SUBSTANTIALLY_IMPLEMENTED
  C03 REVISE_REQUIRED
  C04 PARTIAL
  C05 REVISE_REQUIRED
  C06 PARTIAL

Package Gate:
  FAIL

Acceptance Corpus:
  PARTIAL

Consumer Pilot:
  NOT_PROVEN

Cost Benchmark:
  NOT_PROVEN

Baseline Promotion:
  BLOCKED
```

当前已确认生产事实：

```text
master protected = false
repository rulesets = empty

GitHub Actions:
  validate                              = FAIL
  GES Package Gate / validate-package  = FAIL

GES Package Gate failure:
  PACKAGE_MANIFEST_MISMATCH

Governance CI failure:
  pip install -e .
  → setuptools flat-layout multiple top-level package discovery failure
```

因此本 PRD 完成前，禁止修改 `BASELINE.md` 将 v5 Promote 为 Accepted Baseline。

## 1. 版本策略

### 1.1 PRD Version

本文件版本固定为 `v5.0.2`。

### 1.2 Bundle Version

本 PRD 不强制最终 Bundle 一定为 `5.0.2`。Release Review 必须按 `VERSIONING.md` 判定：

- 纯 correctness / false-positive / reliability hardening 可按 PATCH；
- 新增 Work Authority Binding、Domain Intent Binding、Install Receipt、Benchmark Contract 等向后兼容能力时 SHOULD 按 MINOR。

基于本 PRD 实际范围，Release Review SHOULD 重点评估 `5.1.0`。

### 1.3 Immutable Release Identity

最终 Accepted Release 必须继续满足：

```text
Bundle version
+
source commit
+
PACKAGE-MANIFEST.json byte SHA256
```

三者共同构成 immutable release identity。

## 2. Objective

本 PRD 关闭 7 个 Remaining Findings：

| ID | Priority | Finding | Closure Goal |
|---|---:|---|---|
| C07 | P0 | CI Determinism | Package/Repo CI 连续稳定 PASS |
| C08 | P0 | Plan Review precedence | current hard risk 永远高于 stale PASS→DELTA 优化 |
| C09 | P0 | Master protection | Ruleset/Protection 真正 active |
| C10 | P1 | Work Facts authority | SPIKE/NONE 只能由 authority-bound facts 产生 |
| C11 | P1 | Domain semantics | 去全文 blocking regex；PRD Intent ↔ Plan Ledger content-bound |
| C12 | P1 | Install provenance | manifest byte SHA + non-circular final install receipt |
| C13 | P1 | Acceptance/Benchmark | G16-G22 真行为测试；完整 telemetry；真实 A/B/C benchmark；12 Pilot |

最终 GES 必须能用机器证据回答：

```text
1. 为什么是 NONE / LEAN / FULL？
2. authority facts 来自谁？
3. hard risk 是否可能被 stale review 降级？
4. Domain PRD Intent 是否被 Plan 偷改？
5. Consumer 到底安装了哪个 exact release bytes？
6. master 是否物理上阻止未验证变更？
7. GES 5.x 是否真实更省成本且不降低质量？
```

## 3. Out of Scope

- 不重构三层架构；
- 不新增第二 PRD / Plan / Delivery SOT；
- 不改变 `smc-plan-delivery` 的 Delivery Truth ownership；
- 不改变 `post_review`；
- 不取消 Completion Audit / Implementation Review / Final Verification；
- 不让 Domain Provider 获得 Delivery State ownership；
- 不将 Telemetry 变成 Final Evidence；
- 不重写历史 v3.3–v3.6 Plan；
- 不做 semantic duplicate code 向量检索平台；
- 不把 GitHub admin token 写进 repository；
- 不在 CI 仍红时启用 required check 锁死 master。

## 4. Frozen Invariants

```text
FI-01 Canonical Plan 唯一。
FI-02 Static PASS != implementation complete。
FI-03 Todo completed != implementation proven。
FI-04 production path#symbol 只有一个 WRITE_OWNER。
FI-05 Plan Author owns Todo content/id。
FI-06 Delivery Runtime owns Todo runtime status。
FI-07 Completion Audit 必须独立。
FI-08 Final Implementation Review 基于当前 whole Plan-owned diff。
FI-09 Blocking Verification 必须 fresh PASS。
FI-10 Content change 使相关旧 proof stale。
FI-11 post_review commit 晚于 Audit + Review + Verification。
FI-12 Roadmap DONE 晚于 implementation commit。
FI-13 LIVE/FAULT/EXTERNAL 必须绑定 scenario/environment/candidate。
FI-14 TDD RED 不是 Final Verification FAIL。
FI-15 Engineering Method artifact 是 working memory。
FI-16 Domain Pack 不能成为 PRD/Plan/Delivery/Commit/Roadmap Owner。
FI-17 Production skip-gates 禁止。
FI-18 Evidence reuse 必须显式 inheritance。
FI-19 三次 failed fix 仍触发 DEBUG_ARCHITECTURE_ESCALATION。
FI-20 LEAN 只能降低前半程成本，不能降低 Final Delivery Truth。
```

## 5. Change Classification

| Change ID | Action | Canonical Owner |
|---|---|---|
| C07 | MODIFY | `.github/workflows/governance-ci.yml`, package builder, `pyproject.toml` |
| C08 | MODIFY | `smc-plan-review` |
| C09 | CONFIG + minimal ADD | GitHub Ruleset + acceptance verifier |
| C10 | ADD + MODIFY | `using-superpowers` / orchestration boundary |
| C11 | MODIFY + minimal ADD | `domain-runtime`, FE/BE/Ops, Plan seed/validator |
| C12 | MODIFY + minimal ADD | Installer / transaction / release identity |
| C13 | MODIFY + ADD | `engineeing-skills/acceptance/`, top-level `audit/` evidence |


# 6. C07 — CI Determinism Closure

## 6.1 问题

当前 `GES Package Gate / validate-package` 在 `build_package_manifest.py --check` 处失败，错误为：

```text
PACKAGE_MANIFEST_MISMATCH
```

说明 tracked manifest 与实际 package bytes 不一致。

普通 `validate` Job 同时在：

```text
python -m pip install -e . pytest
```

处失败，因为 repository 是 flat-layout，setuptools 发现多个 top-level package 目录后拒绝 editable build。

## 6.2 Package Manifest Required Flow

当前 manifest builder 已正确排除：

```text
PACKAGE-MANIFEST.json
SHA256SUMS
__pycache__
.pyc
.pyo
```

本轮禁止新增第二套 generator。

最终代码完成后必须严格执行：

```text
1. 完成所有 source changes
2. python engineeing-skills/build_package_manifest.py
3. review manifest/SHA diff
4. python engineeing-skills/build_package_manifest.py --check
5. python engineeing-skills/validate_package.py
6. git diff --check
```

CI 必须只执行 `--check`，不得在 CI 自动 regenerate 后继续 PASS。

建议增加 `--explain-diff`，仅作为诊断能力，输出 added/removed/content_changed/size_changed。

## 6.3 Python Packaging Decision

本 repository 是治理控制面与脚本仓库，不依赖 setuptools 自动 package discovery。

首选策略：

```toml
[tool.setuptools]
packages = []
py-modules = []
```

保留 `pip install -e .` 作为 dependency/metadata 安装入口，同时明确禁止自动发现根目录中的 `audit/skills/features/...`。

若当前 setuptools 对 metadata-only editable install 不兼容，则 fallback 为：

```text
显式 CI requirements / dependency install
```

但 Release Review 必须只接受一种 canonical 策略，禁止同时依赖“有时 editable、有时 scripts”。

## 6.4 Stable CI Contracts

必须稳定存在两个 status context：

```text
validate
GES Package Gate / validate-package
```

其中 Package Gate 固定执行：

```text
build_package_manifest.py --check
validate_package.py
git diff --check
git diff --exit-code
```

## 6.5 Ruleset 启用前置条件

Ruleset 启用前必须至少获得：

```text
一次 PR branch green run
一次 master push green run
```

证明两个 status 名称稳定。

## 6.6 Acceptance Criteria

```text
AC-C07-01 PACKAGE_MANIFEST_MISMATCH = 0
AC-C07-02 validate = PASS
AC-C07-03 GES Package Gate = PASS
AC-C07-04 CI 后 git diff clean
AC-C07-05 PR + master 两个独立 run 均 PASS
AC-C07-06 source drift 后 package check 稳定 FAIL
```

---

# 7. C08 — Plan Review Hard-Risk Precedence

## 7.1 当前 P0 correctness bug

当前 Router 顺序为：

```text
prior unresolved → FULL
FRESH_PASS → NONE
STALE previous PASS → DELTA
risk_forces_full → FULL
```

因此：

```text
Plan A review PASS
→ Plan B 新增 schema/security/public-contract risk
→ previous PASS 变 stale
→ Router 可能先命中 DELTA
```

这是禁止的。

## 7.2 Required Precedence

固定改为：

```text
R1 prior review verdict != PASS
   → FULL

R2 current semantic hash 已有 FRESH_PASS
   → NONE

R3 CURRENT risk_forces_full == true
   → FULL

R4 stale prior PASS
   → DELTA

R5 first acceptance-governed review
   → LIGHT_FIRST_REVIEW / FULL

R6 low-risk LEAN / compatible legacy
   → NONE

R7 unknown/FULL
   → FULL
```

`FRESH_PASS` 仍可以高于 hard risk，因为 current hard-risk Plan 已被针对当前 semantic hash 审过；`STALE_PASS` 不能高于 hard risk。

## 7.3 Required Tests

```text
T-R01 stale PASS + schema_migration=true → FULL
T-R02 stale PASS + security_boundary=true → FULL
T-R03 stale PASS + public_contract=true → FULL
T-R04 stale PASS + lifecycle_change=true → FULL
T-R05 stale PASS + safe current change → DELTA
T-R06 fresh current PASS + high risk → NONE
T-R07 stale prior REVISE + low risk → FULL
T-R08 risk contradiction + stale PASS → FULL
T-R09 snapshot tamper + stale PASS → FULL
```

必须构造真实 Plan、review record、semantic mutation，不得只断言函数存在。

## 7.4 Acceptance Criteria

```text
AC-C08-01 hard-risk stale Plan 永远不能 DELTA
AC-C08-02 low-risk stale prior PASS 仍允许 DELTA
AC-C08-03 fresh current PASS 不重复 FULL
AC-C08-04 unresolved review 不被 optimization 降级
AC-C08-05 Router reasons 明确记录 hard-risk precedence
```

---

# 8. C09 — Master Protection Operational Closure

## 8.1 Current State

```text
master protected = false
rulesets = []
```

这是 operational gap。

## 8.2 Required Ruleset

优先使用 Repository Ruleset：

```text
Name:
  GES Master Governance

Target:
  refs/heads/master

Enforcement:
  ACTIVE
```

必须：

```text
Require pull request before merge
Require check: validate
Require check: GES Package Gate / validate-package
Block force push
Block branch deletion
Restrict direct updates
```

默认建议 `required approving reviews = 1`。如果当前只有单维护者，允许 Governance Owner 书面批准 `0 approval + mandatory PR/status` 例外，但不得恢复 unrestricted direct push。

## 8.3 Activation Sequence

```text
1. 先完成 C07
2. PR CI PASS
3. merge
4. master CI PASS
5. 确认 status 名称稳定
6. 启用 Ruleset
7. 创建 verification PR
8. verification PR 必须被 required checks 约束
9. 尝试 direct push / force push 并确认拒绝
```

禁止在 CI 仍红时直接设 required。

## 8.4 Protection Verifier

建议新增：

```text
engineeing-skills/acceptance/verify_repository_protection.py
```

支持：

```text
--api
--evidence <github-ruleset.json>
```

输出至少：

```json
{
  "protected": true,
  "require_pr": true,
  "required_checks": ["validate", "GES Package Gate / validate-package"],
  "force_push_blocked": true,
  "deletion_blocked": true,
  "direct_update_restricted": true
}
```

Token 必须来自 secret，不得写入 repo。

## 8.5 Acceptance Criteria

```text
AC-C09-01 master protected=true
AC-C09-02 Ruleset ACTIVE
AC-C09-03 两个 required checks 存在
AC-C09-04 force push 被拒绝
AC-C09-05 direct ungoverned update 被拒绝
AC-C09-06 protection evidence 可被 Acceptance Runner 验证
```


# 9. C10 — Work Facts Authority Binding

## 9.1 问题

v5.0.1 已把 `research_only` 从 authoritative flag 降级为 hint，但 production Router 仍接受普通调用方 JSON：

```text
route(facts)
```

如果同一个 Worker 同时构造：

```text
governed=false
retained_production_change=false
production_write_requested=false
durable_product_artifact_requested=false
```

仍可能得到 SPIKE/NONE。

因此当前只是：

```text
single self-declared flag
→ multi-field self-declared object
```

尚未完成 trust boundary。

## 9.2 New Derived Contract

新增：

```text
smc.ges.work-authority.v1
```

它是 derived working-memory authority artifact：

```text
不是 Roadmap
不是 PRD
不是 Plan
不是第二 SOT
```

路径：

```text
.smc/work/<work_item_id>/work-authority.json
```

建议结构：

```json
{
  "schema": "smc.ges.work-authority.v1",
  "work_item_id": "RM-123",
  "repo_head": "<sha>",
  "generated_at": "...",
  "facts": {
    "governed": true,
    "retained_production_change": true,
    "production_write_requested": true,
    "durable_product_artifact_requested": true
  },
  "sources": [
    {
      "type": "ROADMAP|PRD|PLAN|ORCHESTRATOR_REQUEST",
      "path": "...",
      "sha256": "...",
      "authority": "CANONICAL|ORCHESTRATOR"
    }
  ],
  "authority_sha256": "sha256:..."
}
```

## 9.3 Authority Rules

`governed=true` 必须从以下任一得出：

```text
Canonical Roadmap item 已进入 governed stage
Canonical PRD exists
Canonical Plan exists
Orchestrator explicitly enters governed workflow
```

无可验证来源：

```text
UNKNOWN
```

不得默认为 false。

`production_write_requested` 来自 Orchestrator action contract / Plan Change Matrix / durable code-config mutation request。

`retained_production_change=true`：只要输出预计保留在 repository/product。

`durable_product_artifact_requested=true`：source/config/schema/deployment/product-behavior docs 等；纯 research note / throwaway spike 才允许 false。

## 9.4 SPIKE/NONE Rule

只有：

```text
research_intent=true
authority VERIFIED
governed=false
retained_production_change=false
production_write_requested=false
durable_product_artifact_requested=false
previous_profile ∈ {NONE,null}
```

才允许：

```text
SPIKE/NONE
```

authority missing/stale/digest mismatch/source changed 时：

```text
WORK_RESEARCH_AUTHORITY_MISSING
→ FULL
```

## 9.5 Route Binding

Route 输出增加：

```text
authority_sha256
authority_status=VERIFIED
```

authority source 改变后 route stale，必须重算。

## 9.6 Backward Compatibility

`route(facts)` 保留给 unit/library compatibility；production CLI 若想产生 NONE 必须 `--authority <file>`。

旧 caller 无 authority：

```text
可 fail-closed LEAN/FULL
不得 NONE
```

## 9.7 Tests

```text
T-W01 arbitrary JSON pure research, no authority → FULL
T-W02 valid authority pure research → NONE
T-W03 authority governed=true + caller false → FULL
T-W04 authority source digest stale → FULL
T-W05 existing Plan presence forces governed=true
T-W06 previous LEAN/FULL 不能降 NONE
T-W07 orchestrator production write 不能 NONE
T-W08 Worker 不能覆盖 authority facts
```

## 9.8 Acceptance Criteria

```text
AC-C10-01 production SPIKE/NONE 必须有 verified authority
AC-C10-02 Worker JSON 不能覆盖 canonical authority
AC-C10-03 authority source change 使 route stale
AC-C10-04 missing authority fail closed
AC-C10-05 不创建第二 governance SOT
```

---

# 10. C11 — Domain Structured Semantics + PRD Intent ↔ Plan Binding

## 10.1 Problem A：Domain 层重新引入 broad regex

当前 FE/BE/Ops Preplan 仍存在对整篇文本的 blocking regex。必须改成：

```text
parsed Domain row structured token
+
shared Routing Facts
```

作为唯一 blocking source。

全文 text scan 只能 advisory 或 legacy fallback，不得在 structured row 完整时产生 blocking FULL。

## 10.2 Frontend Structured Tokens

沿用现有字段，但定义 token prefix：

```text
Framework:
  REACT | VUE | GENERIC | N/A

Layout:
  UNCHANGED | EXTEND_EXISTING | NEW_HIERARCHY | NAVIGATION_CHANGE | MULTI_PANEL

Component Map:
  REUSE | EXTEND | NEW | REMOVE | N/A

State Ownership:
  UNCHANGED | LOCAL_EXISTING | EXTEND_OWNER | NEW_OWNER | STORE_CHANGE | N/A

Responsive:
  UNCHANGED | EXTEND | ARCHITECTURE_CHANGE | N/A

Visual Verification:
  STATIC | COMPONENT | INTERACTION | LIVE_VISUAL | N/A
```

允许：

```text
NEW_HIERARCHY: split workspace into left/main/right
```

但 hard trigger 只读取 prefix token。

Frontend FULL：

```text
Layout ∈ NEW_HIERARCHY/NAVIGATION_CHANGE/MULTI_PANEL
State Ownership ∈ NEW_OWNER/STORE_CHANGE
Responsive = ARCHITECTURE_CHANGE
```

## 10.3 Backend Structured Triggers

从 parsed row：

```text
Contract = BREAKING_CHANGE
Auth = NEW_BOUNDARY
Data/Transaction = MIGRATION
```

触发 FULL。

`new external dependency/new owner/cross-domain ownership` 从共享 Routing Facts 获取，不再全文扫描。

## 10.4 Ops Structured Triggers

```text
Deployment Impact ∈ TOPOLOGY_CHANGE/IRREVERSIBLE
Compatibility = BREAKING
Live Verification ∈ LIVE/EXTERNAL
```

触发 FULL。

`IRREVERSIBLE` 继续要求：

```text
Rollback = NOT_POSSIBLE:<reason>
```

## 10.5 Legacy Compatibility

旧 artifact 自由文本：

```text
LEGACY_SEMANTIC_FALLBACK
```

只能 fail closed，不得产生 false LEAN。

新 artifact 必须 structured token。

Domain Contract v2 可保持，Domain Pack SHOULD minor bump。

## 10.6 Problem B：PRD Intent 与 Plan Ledger 未 content-bound

新增：

```text
smc.ges.domain-intent-binding.v1
```

仍是 Approved PRD projection，不是第二 SOT。

Plan seed 生成：

```text
## Domain Intent Binding

| Domain | Change ID | Intent SHA256 | Source PRD SHA256 |
|---|---|---|---|
```

并记录：

```text
source_prd_sha256
domain_intent_binding_version
```

建议新增：

```text
domain-runtime/domain_intent.py
```

提供 deterministic normalization/hash。

每个 `pack.json` 可声明：

```json
"intent_binding": {
  "preplan_section": "...",
  "plan_section": "...",
  "fields": {
    "Contract": "Contract",
    "Auth": "Auth"
  }
}
```

Backend 映射 Owner/Contract/Data/Auth/Idempotency/Failure/Observability。

Ops 映射 Deployment/Compatibility/Env/Health/Migration/Rollback，并规定 `Live Verification` 与 Plan `Verification` 的兼容映射。

Frontend 至少映射 Framework/State Ownership/Design System/Visual Verification；Layout/Component/Responsive 若 Plan Ledger 无同名列，则由 Intent Hash 保留，Plan 不得重新定义其语义。

## 10.7 Validation

Plan validation：

```text
source PRD exists
→ recompute Source PRD SHA
→ recompute intent hash
→ compare Domain Intent Binding
→ compare mapped Plan Ledger fields
```

任何 mismatch：

```text
PRD_STALE_OR_CONFLICTING
```

不得由 Plan Author 静默修改 Approved PRD。

## 10.8 Tests

```text
T-D01 "No migration" 不触发 Domain FULL
T-D02 Backend MIGRATION + LEAN → FULL_REQUIRED
T-D03 Ops TOPOLOGY_CHANGE + LEAN → FULL_REQUIRED
T-D04 Frontend NEW_HIERARCHY + LEAN → FULL_REQUIRED
T-D05 PRD UNCHANGED / Plan BREAKING → PRD_STALE_OR_CONFLICTING
T-D06 PRD NEW_BOUNDARY / Plan UNCHANGED → conflict
T-D07 source PRD bytes changed → stale
T-D08 mapped fields unchanged → PASS
T-D09 legacy artifact → fail-closed compatibility
T-D10 new artifact free-text token → invalid
```

## 10.9 Acceptance Criteria

```text
AC-C11-01 Domain blocking decision 不依赖全文 regex
AC-C11-02 structured Domain row 是主判据
AC-C11-03 PRD Intent ↔ Plan Ledger content-bound
AC-C11-04 conflict 统一返回 PRD_STALE_OR_CONFLICTING
AC-C11-05 Domain Provider 不获得 Plan/Delivery truth ownership
```


# 11. C12 — Install / Release Provenance Closure

## 11.1 Current Issues

当前 `install-lock.v2` 已存在，但：

```text
package_manifest_sha256
```

来自重新序列化的 manifest object，不是 `PACKAGE-MANIFEST.json` raw bytes digest。

同时 `transaction_manifest_sha256` 在 Pending transaction 时被写入 lock，随后 transaction manifest 被改写为 PASS，导致 digest 与最终 transaction 不一致。

## 11.2 Canonical Package Manifest Digest

唯一合法定义：

```text
SHA256(raw bytes of engineeing-skills/PACKAGE-MANIFEST.json)
```

禁止：

```text
json.loads
→ reserialize
→ hash
```

作为 immutable release identity。

## 11.3 Release Identity

新增/固化：

```text
smc.ges.release-identity.v1
```

逻辑字段：

```json
{
  "bundle": "...",
  "source_commit": "...",
  "package_manifest_sha256": "...",
  "package_file_count": 0,
  "tag": "...",
  "source_tree_dirty": false
}
```

Repo install mode：`git rev-parse HEAD` + package scope dirty detection。

Release Acceptance 必须 `source_tree_dirty=false`。

Archive mode：从外部 release metadata `RELEASE-IDENTITY.json` 或 explicit CLI metadata 读取。该文件在 source commit 确定后作为 distribution metadata 生成，不参与 package manifest 的 recursive identity。

## 11.4 Non-circular Final Install Receipt

采用 final receipt，不让 lock 反向绑定最终 transaction manifest。

安装顺序固定：

```text
1. copy/update package-owned files
2. transaction manifest = INSTALLED_PENDING_VALIDATION
3. run validation
4. reconcile stale owned files
5. build/write install-lock.v2
6. finalize transaction manifest = PASS
7. hash final PASS transaction manifest
8. hash install-lock
9. write ges-install-receipt.json
```

Receipt：

```json
{
  "schema": "smc.ges.install-receipt.v1",
  "bundle": "...",
  "release_identity_sha256": "...",
  "install_lock_sha256": "...",
  "transaction_manifest_sha256": "...",
  "transaction_status": "PASS",
  "installed_at": "..."
}
```

Receipt 自身不得再次被 transaction manifest 纳入 hash，避免 circular dependency。

## 11.5 Stale Ownership

保持：

```text
old owned - new owned
```

如果 stale file：

```text
current_sha == old installed_sha
→ transactional delete

current_sha != old installed_sha
→ INSTALL_STALE_OWNED_FILE_MODIFIED
```

Consumer-local file 永不进入 owned set。

## 11.6 Tests

```text
T-I01 manifest byte SHA 与 release identity 一致
T-I02 reserialized JSON digest 不可代替 byte SHA
T-I03 final receipt 指向 PASS transaction manifest
T-I04 tamper final transaction → receipt verify FAIL
T-I05 tamper install lock → receipt verify FAIL
T-I06 v1 lock upgrade non-destructive
T-I07 untouched stale delete + rollback restore
T-I08 modified stale block + preserve
T-I09 consumer-local skill never deleted
T-I10 dirty source install 可运行但 Release Acceptance blocked
```

## 11.7 Acceptance Criteria

```text
AC-C12-01 release identity 使用 PACKAGE-MANIFEST bytes SHA
AC-C12-02 receipt 与 final PASS transaction 一致
AC-C12-03 不存在 hash circularity
AC-C12-04 stale reconciliation rollback-safe
AC-C12-05 两个 Consumer 可判断是否来自相同 exact release bytes
```

---

# 12. C13 — Acceptance / Benchmark / Pilot Executable Evidence

## 12.1 Acceptance Test Rule

Golden / Chaos 测试必须：

```text
Given 真实 fixture 状态
When 运行真实 governance function/CLI
Then 断言 return code + exact error code + state 未推进
```

禁止：

```text
仅 callable()
仅 grep source string
仅 import 成功
```

## 12.2 G16–G22 必须改成真实行为测试

### G16 Duplicate Hotspot

```text
T1 Writes app.py#save
T2 Writes app.py#save
→ run real validator
→ BLOCK / PLAN_WRITE_OWNERSHIP_CONFLICT
```

### G17 Worker Out-of-Scope

```text
T1 owns app.py#save
Worker modifies other.py
→ run workspace/execution guard
→ BLOCK / unexpected dirty or ownership conflict
```

不得用 Source Context outside-repo test 替代。

### G18 TDD Stale

```text
RED receipt
GREEN receipt
mutate bound test/source
tdd_check
→ STALE/FAIL
```

### G19 Review Stale

```text
record Plan PASS
mutate semantic Plan
latest_status
→ STALE
```

### G20 Evidence Stale

```text
record blocking evidence
mutate production
current_status
→ STALE
```

### G21 LIVE Candidate Mismatch

```text
Scenario + Environment + Candidate A
SUT Candidate B
run real preflight/completion gate
→ LIVE_SUT_MISMATCH
```

不得用 `TELEMETRY_INCOMPLETE` 代替。

### G22 Debug Escalation

```text
REPRODUCTION
ROOT_CAUSE
3 failed FIX_ATTEMPT
debug_check
→ DEBUG_ARCHITECTURE_ESCALATION
```

不得 grep 字符串。

## 12.3 Telemetry Completeness

新增 contract：

```text
smc.execution.telemetry-completeness.v1
```

每个 Harness dispatch 必须有 `dispatch_id`。

要求：

```text
1 dispatch
1 terminal result/error
```

Dispatch required：

```text
plan_id
todo
phase
requested_tier
dispatch_id
agent
```

Result required：

```text
dispatch_id
actual_tier
provider
model
outcome
retry_count
latency_ms
prompt_tokens
completion_tokens
cache_read_tokens
cache_write_tokens
```

Provider 不提供 usage 时必须给：

```text
usage_unavailable_reason
```

不得用 0 伪装缺失。

若 `actual_tier != requested_tier`：

```text
fallback=true
fallback_reason != empty
```

`complete=true` 只有在：

```text
所有 dispatch terminal
所有 required fields 完整
无 orphan dispatch/result
metrics non-negative
```

时成立。

只有 cache-hit event 的 telemetry 不得 complete=true。

## 12.4 Benchmark Contract

每个 case：

```json
{
  "case_id": "B03",
  "cohort": "A|B|C",
  "ges_release": "...",
  "consumer": "...",
  "consumer_revision": "...",
  "work_class": "...",
  "governance_profile": "...",
  "acceptance_oracle": "...",
  "metrics": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "cache_read_tokens": 0,
    "cache_write_tokens": 0,
    "reviewer_seats": 0,
    "dispatch_count": 0,
    "source_context_hits": 0,
    "source_context_misses": 0,
    "fix_rounds": 0,
    "wall_time_ms": 0,
    "escaped_defects": 0
  },
  "outcome": "PASS|FAIL|BLOCKED|TELEMETRY_INCOMPLETE"
}
```

Cohorts：

```text
A = GES 4.4.1 reproducible baseline
B = GES 5.0.0 repaired candidate
C = current hardening candidate
```

无法建立 4.4.1 reproducible baseline 时必须：

```text
BENCHMARK_BASELINE_NOT_REPRODUCIBLE
```

不得伪装成完整 A/B 对照。

## 12.5 Benchmark Computation

至少实际计算：

```text
total_tokens
median BOUNDED token reduction
median reviewer-seat reduction
source context hit rate
dispatch count
retry count
fix rounds
wall time
escaped defects
completion reopen
post-delivery regression
```

匹配 case：

```text
reduction_pct = (A - C) / A * 100
```

成本下降但质量恶化：

```text
不得 ACCEPT
```

## 12.6 Thresholds

完整 thresholds 至少覆盖：

```text
Safety:
  high_risk_false_lean = 0
  governed_production_false_spike = 0
  hard_risk_stale_review_delta = 0
  ownership_escape = 0
  scope_drift_accepted = 0
  stale_tdd_accepted = 0
  stale_review_accepted = 0
  stale_evidence_accepted = 0
  live_candidate_mismatch_pass = 0
  package_integrity_bypass = 0
  consumer_owned_file_silent_delete = 0

Quality:
  blocking_ac_without_proof = 0
  domain_invalid_semantics_accepted = 0
  prd_plan_domain_intent_drift = 0
  uncontrolled_plan_rewrite = 0

Efficiency:
  bounded_median_token_reduction_pct >= 30
  normal_risk_reviewer_seat_reduction_pct >= 25
  source_context_repeat_reduction_pct >= 30

Stability:
  installer_rollback_success_pct = 100
  completion_reopen_rate <= baseline
  post_delivery_regression_rate <= baseline
```

## 12.7 Benchmark Verdicts

只允许：

```text
BENCHMARK_PASS
BENCHMARK_COST_GAP
BENCHMARK_REJECT
TELEMETRY_INCOMPLETE
BENCHMARK_BASELINE_NOT_REPRODUCIBLE
```

`COST_GAP` 只允许在 Safety/Quality/Stability PASS、Efficiency 未达标时出现。

## 12.8 Consumer Pilot

至少：

```text
Pilot A — React/Vue frontend
Pilot B — Python/Node/Java backend
Pilot C — Docker/Nginx/Compose ops
```

每个：

```text
1 × LEAN
1 × BEHAVIOR_CHANGE
1 × BUG_FIX
1 × HIGH_RISK/FULL
```

总计：

```text
>= 12 governed deliveries
```

动态 evidence 放：

```text
audit/ges/acceptance/<candidate>/pilots/
```

每次记录：

```text
route summary
authority digest
PRD review
domain intent
plan review depth
engineering method
telemetry summary
completion audit
implementation review
blocking verification
implementation commit
roadmap done commit
post-delivery observation
```

不得记录完整 prompt/source/secrets。

## 12.9 Acceptance Criteria

```text
AC-C13-01 G16-G22 全部是真实 behavior tests
AC-C13-02 Telemetry completeness deterministic
AC-C13-03 Benchmark 实际计算 A/B/C metrics
AC-C13-04 thresholds 被程序执行
AC-C13-05 >=12 Pilot 有完整 evidence
AC-C13-06 Safety fail 永远不能被 cost benefit 覆盖
```


# 13. File-Level Implementation Matrix

| File / Area | Required Change |
|---|---|
| `.github/workflows/governance-ci.yml` | 修 packaging；保持两个稳定 jobs |
| `pyproject.toml` | 禁止 setuptools auto-discovery |
| `engineeing-skills/build_package_manifest.py` | deterministic check；可选 explain diff |
| `engineeing-skills/PACKAGE-MANIFEST.json` | 最后生成 |
| `engineeing-skills/SHA256SUMS` | 最后生成 |
| `smc-plan-review/scripts/assess_plan_review.py` | hard risk 高于 STALE→DELTA |
| `using-superpowers/scripts/work_router.py` | production NONE authority-bound |
| `using-superpowers/scripts/work_authority.py` | 建议新增 |
| `using-superpowers/scripts/test_work_router.py` | authority tests |
| `domain-runtime/risk_signals.py` | 保持共享 Risk SOT；补双向 contradiction |
| `domain-runtime/domain_table.py` | structured token helper |
| `domain-runtime/domain_intent.py` | 建议新增 normalize/hash/bind |
| `domain-runtime/domain_runtime.py` | intent binding verify；child error propagation |
| FE/BE/Ops Preplan & Review | 去全文 blocking regex；structured tokens |
| Plan seed v3.7 | source PRD SHA + Domain Intent Binding |
| Plan validator v3.7 | intent binding verification |
| `install_v500.py` lineage | manifest byte SHA；final receipt |
| transaction installer suite | PASS finalize 后生成 receipt |
| `acceptance/run_acceptance.py` | G16-G22 真实测试 |
| `runtime_metrics.py` | dispatch correlation + completeness |
| `acceptance/run_benchmark.py` | 聚合、median、threshold verdict |
| `acceptance/metrics.schema.json` | 完整 metrics |
| `acceptance/thresholds.json` | Safety/Quality/Efficiency/Stability |
| `acceptance/verify_repository_protection.py` | 建议新增 |
| `audit/ges/acceptance/...` | Pilot/Benchmark/Ruleset evidence |

# 14. Error Codes

```text
CI_PACKAGE_MANIFEST_DRIFT
CI_REPOSITORY_PACKAGING_INVALID

PLAN_REVIEW_HARD_RISK_FULL_REQUIRED

WORK_AUTHORITY_MISSING
WORK_AUTHORITY_INVALID
WORK_AUTHORITY_STALE
WORK_AUTHORITY_CONFLICT

DOMAIN_SEMANTIC_TOKEN_INVALID
DOMAIN_SEMANTIC_LEGACY_FULL_REQUIRED
PRD_STALE_OR_CONFLICTING
DOMAIN_INTENT_BINDING_MISSING
DOMAIN_INTENT_BINDING_STALE

INSTALL_RELEASE_IDENTITY_INVALID
INSTALL_MANIFEST_BYTE_DIGEST_MISMATCH
INSTALL_RECEIPT_INVALID
INSTALL_RECEIPT_TRANSACTION_MISMATCH
INSTALL_STALE_OWNED_FILE_MODIFIED

TELEMETRY_ORPHAN_DISPATCH
TELEMETRY_ORPHAN_RESULT
TELEMETRY_REQUIRED_FIELD_MISSING
TELEMETRY_USAGE_UNAVAILABLE
TELEMETRY_INCOMPLETE

BENCHMARK_BASELINE_NOT_REPRODUCIBLE
BENCHMARK_THRESHOLD_NOT_MET
BENCHMARK_COST_GAP
```

已有稳定错误码不得随意改名。

# 15. Migration Policy

## Work Router

旧 `route(facts)` 保持 library/test compatibility。Production CLI 只有 authority-bound 才可 SPIKE/NONE。

## Plan Review

无 contract migration，仅修 precedence correctness。

## Domain

Domain Contract v2 可保持；Domain Pack SHOULD minor bump。旧 in-flight artifact 允许 legacy fail-closed fallback；新 artifact 必须 structured token。

## Installer

`install-lock.v1` 第一次升级不 destructive。`install-lock.v2` 继续 readable。新增 final proof `install-receipt.v1`。

## Telemetry

Telemetry 缺失不阻塞正常 Delivery，但 Benchmark case 标 `TELEMETRY_INCOMPLETE`，不得计入成本结论。

# 16. Security / Trust Model

```text
- Work Authority 不能由 implementation Worker 无来源覆盖；
- GitHub admin token 只能 secret 注入；
- Telemetry 禁止记录 prompt/source/secrets/API keys；
- Release receipt 只记录 hash/metadata；
- Consumer source path 可 hash，不向集中审计泄露源码；
- Installer 不得删除 Consumer-local files。
```

# 17. Implementation Sequence

```text
Phase 0 — 从 98cdb89... 创建 hardening branch
Phase 1 — C07 CI Closure
Phase 2 — C08 P0 Review Router correctness
Phase 3 — C10/C11 authority + structured domain + intent binding
Phase 4 — C12 provenance + final receipt
Phase 5 — C13 real acceptance + telemetry completeness + benchmark
Phase 6 — 最终 regenerate PACKAGE-MANIFEST / SHA256SUMS
Phase 7 — PR green → merge → master green
Phase 8 — C09 启用 Ruleset + negative verification
Phase 9 — 3 Consumer / 12 Delivery Pilot
Phase 10 — 4.4.1 vs 5.x Benchmark
Phase 11 — Acceptance Review / Release Review
Phase 12 — 仅 ACCEPT 后 Baseline Promotion
```

# 18. Minimum Validation Chain

```bash
python engineeing-skills/build_package_manifest.py --check

python engineeing-skills/validate_package.py

python engineeing-skills/domain-runtime/test_risk_signals.py

python engineeing-skills/acceptance/run_acceptance.py

git diff --check
git diff --exit-code
```

GitHub 必须同时出现：

```text
validate                              PASS
GES Package Gate / validate-package  PASS
```

此外必须显式运行：

```text
Work Authority tests
Plan Review hard-risk precedence tests
Domain Intent Binding tests
Installer receipt/provenance tests
Telemetry completeness tests
Benchmark threshold tests
Repository protection verifier
```

# 19. Acceptance Thresholds

## Safety

```text
high_risk_false_lean                = 0
governed_production_false_spike     = 0
hard_risk_stale_review_delta        = 0
ownership_escape                    = 0
scope_drift_accepted                = 0
stale_tdd_accepted                  = 0
stale_review_accepted               = 0
stale_evidence_accepted             = 0
live_candidate_mismatch_pass        = 0
package_integrity_bypass            = 0
consumer_owned_file_silent_delete   = 0
```

## Quality

```text
blocking_ac_without_proof           = 0
domain_invalid_semantics_accepted   = 0
prd_plan_domain_intent_drift        = 0
uncontrolled_plan_rewrite           = 0
```

## Efficiency

```text
BOUNDED median token reduction >= 30%
normal-risk reviewer-seat reduction >= 25%
source-context repeat reduction >= 30%
```

## Stability

```text
installer rollback success = 100%
completion reopen rate <= baseline
post-delivery regression rate <= baseline
```

# 20. PRD Acceptance Criteria

```text
AC-01 PACKAGE-MANIFEST 与 package bytes 完全一致
AC-02 validate PASS
AC-03 GES Package Gate PASS
AC-04 PR + master 至少两个稳定 green run
AC-05 master Ruleset active
AC-06 required checks operational
AC-07 force/direct ungoverned update 被阻止

AC-08 stale PASS + current hard risk → FULL
AC-09 stale PASS + safe current delta → DELTA
AC-10 fresh current PASS 不重复 review

AC-11 SPIKE/NONE 必须 authority-bound
AC-12 arbitrary Worker JSON 不能授权 NONE
AC-13 stale authority 不能复用

AC-14 Domain blocking trigger 不扫描全文
AC-15 new Domain artifact 使用 structured tokens
AC-16 PRD Intent ↔ Plan Ledger content-bound
AC-17 conflict → PRD_STALE_OR_CONFLICTING

AC-18 package manifest byte digest 正确
AC-19 install receipt 指向 final PASS transaction
AC-20 receipt/lock/transaction tamper 可检测
AC-21 stale cleanup rollback-safe

AC-22 G16-G22 全是真实 behavior tests
AC-23 Telemetry completeness deterministic
AC-24 Benchmark 实际计算 median/reduction
AC-25 thresholds 被程序执行
AC-26 3 Consumer / >=12 Delivery Pilot 完整
AC-27 Safety/Quality 全 PASS
```

# 21. Definition of Done

```text
[ ] C07–C13 code complete
[ ] C07–C13 deterministic tests complete
[ ] PACKAGE-MANIFEST 最终 regenerate
[ ] SHA256SUMS 最终 regenerate
[ ] build_package_manifest.py --check PASS
[ ] validate_package.py PASS
[ ] validate job PASS
[ ] GES Package Gate PASS
[ ] Plan Review P0 suite PASS
[ ] Work Authority suite PASS
[ ] Domain structured semantic suite PASS
[ ] Domain Intent Binding suite PASS
[ ] Installer receipt/provenance suite PASS
[ ] G16-G30 real acceptance corpus PASS
[ ] Chaos Governance PASS
[ ] master Ruleset active
[ ] required checks operational
[ ] >=3 Consumer Pilot complete
[ ] >=12 real governed deliveries complete
[ ] 4.4.1 vs 5.x Benchmark complete
[ ] Safety thresholds PASS
[ ] Quality thresholds PASS
[ ] Stability thresholds PASS
[ ] Efficiency verdict available
[ ] Bundle SemVer decision recorded
[ ] Source commit recorded
[ ] PACKAGE-MANIFEST byte SHA recorded
```

注意：

```text
Package Validator PASS != PRD DONE
Acceptance Runner PASS != PRD DONE
Pilot PASS != PRD DONE
必须全部闭环。
```

# 22. Release Verdict

只允许：

```text
ACCEPT
ACCEPT_WITH_COST_GAP
REJECT
```

`ACCEPT`：CI/Protection/Safety/Quality/Stability/Pilot/Benchmark 全部闭环，无 Blocking Finding。

`ACCEPT_WITH_COST_GAP`：Safety/Quality/Stability/Pilot PASS，但 Efficiency 未达到目标；不得宣称成本收益已验证。

`REJECT`：任意 P0 correctness、Safety、provenance、rollback、branch protection、stale-proof failure。

# 23. Baseline Promotion Gate

当前 `engineeing-skills/BASELINE.md` 必须保持现有 Accepted Baseline，直到本 PRD Verdict = `ACCEPT`。

之后才允许单独提交 Baseline Promotion Commit，记录：

```text
Governance Baseline version
Accepted Bundle version
Plan Contract
Domain Contract
Consumer Profile Contract
Source Commit
Release Tag
PACKAGE-MANIFEST byte SHA256
Acceptance Report digest
Benchmark Report digest
Pilot Evidence digest
```

Baseline Promotion 不得与实现代码 commit 混在一起。

# 24. Expected Final Architecture

```text
User / Roadmap / Orchestrator
          │
          ▼
Work Authority Builder
content-bound authority facts
          │
          ▼
Work Router
SPIKE / LEAN / FULL
          │
          ▼
Canonical Stage PRD
Routing Facts
          │
Domain Structured Intent
          │
PRD Review / Approve
          │
          ▼
Canonical Plan v3.7
Risk Snapshot + Intent Binding
          │
Static + Semantic Review
hard risk > stale-review optimization
          │
          ▼
Engineering Runtime
TDD / Debug / Harness / Source Context
          │
Runtime Telemetry
          │
          ▼
Delivery Truth
Audit → Review → Verification
          │
Evidence
          │
post_review Commit
          │
Roadmap DONE

Release Plane:
deterministic package manifest
+ green CI
+ active master ruleset
+ immutable release identity
+ install receipt
+ executable acceptance/pilot/benchmark
```

# 25. Final Engineering Requirement

本 PRD 完成后，GES 必须能用 deterministic evidence 回答：

```text
- 这个 request 为什么不是 self-declared research？
- 当前 Plan 的 hard risk 为什么一定 FULL？
- stale review 为什么不能覆盖新增风险？
- PRD 中的 Domain Intent 是否被 Plan 保真？
- 这个 Consumer 安装的是哪一个 exact package？
- install transaction 最终 PASS receipt 是否可信？
- master 是否真的无法绕开 CI？
- G16-G22 是否真正破坏状态并被阻断？
- GES 5.x 相比 4.4.1 的 Token、Reviewer、Retry、质量到底变化多少？
```

只有这些问题都有机器可验证答案，GES 5 系列才具备从 Candidate 晋升为 Accepted Enterprise Governance Baseline 的条件。
