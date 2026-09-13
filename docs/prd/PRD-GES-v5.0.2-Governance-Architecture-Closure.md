---
title: "GES Governance Architecture Closure PRD"
prd_version: "v5.0.2"
work_item_id: "GES-GOV-CLOSURE-5.0.2"
status: "DRAFT"
review_verdict: "PENDING"
governance_profile: "FULL"
previous_governance_profile: "FULL"
source_revision: "loudon84/smc-delivery-governance@98cdb89ed3007d630f2d401030c36757bbd8c362"
grounded_commit: "98cdb89ed3007d630f2d401030c36757bbd8c362"
canonical_path: "engineeing-skills/"
source_prd: "docs/prd/PRD-GES-v5.0.1-Acceptance-Hardening.md"
current_candidate: "PRD v5.0.1 / Bundle 5.0.0 bytes with Acceptance Hardening deltas"
accepted_baseline_bundle: "4.1.2"
commit_policy: "post_review"
scope_mode: "ARCHITECTURE_CLOSURE_ONLY"
effect_validation: "FORBIDDEN"
baseline_promotion: "FORBIDDEN"
---

# GES Governance Architecture Closure PRD v5.0.2

> Repository: `loudon84/smc-delivery-governance`  
> Canonical Path: `engineeing-skills/`  
> Grounded Source Revision: `master@98cdb89ed3007d630f2d401030c36757bbd8c362`  
> Parent PRD: `PRD-GES-v5.0.1-Acceptance-Hardening.md`  
> 本 PRD 目标：**只完成治理流程整个架构闭环，不执行治理落地效果验证。**

## 0. 强制边界

本 PRD 的最高优先级约束：

> **只完成 Governance Architecture Closure。禁止在本 PRD 中执行 Consumer Pilot、真实 A/B 成本 Benchmark、生产效果验证、Accepted Baseline Promotion。**

允许：

- 修复治理代码 correctness；
- 完成 CI / Package Gate / Branch Ruleset 架构闭环；
- 完成 deterministic regression test；
- 将 Acceptance/Benchmark tooling 从 skeleton 建成真正可执行的框架；
- 使用 synthetic fixture / temporary repo 验证治理机制本身；
- 建立 3 Consumer / 12 delivery Pilot 的 specification、schema、runner contract、case manifest；
- 建立 Benchmark 算法和阈值判断逻辑；
- 完成 Harness Telemetry contract 与 completeness contract。

禁止：

- 实际在 3 个真实 Consumer 上执行 12 次交付；
- 实际收集 4.4.1 vs 5.x 的生产 Token/Cost 数据；
- 根据真实 Pilot/Benchmark 结果宣称 GES 5 降低 Token；
- 修改 `BASELINE.md` 将 GES 5 提升为 ACCEPTED；
- 创建“成本收益已验证”“生产稳定性已验证”等结论；
- 因验证方便而削弱 Frozen Invariants。

因此，本 PRD 中“Acceptance / Benchmark 完成”只表示：

```text
framework executable
schema complete
deterministic governance cases executable
real pilot/benchmark inputs defined
```

不表示：

```text
real-world effect proven
```

# 1. 当前状态

当前 v5.0.1 Candidate 准确状态：

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

当前已存在的基础能力：

- `GES Package Gate / validate-package` workflow job；
- `research_only` hint-only + authority-fact gate；
- shared `domain-runtime/risk_signals.py`；
- `Risk Facts Snapshot`；
- Domain enum / conditional validator primitives；
- `install-lock.v2` 初版；
- `runtime_metrics.py` 初版；
- `acceptance/run_acceptance.py` G01-G30 初版；
- `acceptance/run_benchmark.py` skeleton；
- Candidate 文档仍未替换 Accepted `BASELINE.md`。

当前最重要 Remaining Findings：

1. P0 — Package/CI 自身仍红；
2. P0 — Plan Review Router 中 current hard-risk 优先级低于 stale PASS→DELTA；
3. P0 — `master` 仍未被 Ruleset/Protection 实际保护；
4. P1 — Work Facts 仍缺 authoritative provenance binding；
5. P1 — Domain 层仍有全文 broad regex，且 Approved PRD Intent 与 Plan Ledger 未做语义绑定；
6. P1 — install-lock provenance digest / transaction-finalization 仍存在一致性问题；
7. P1 — Acceptance/Benchmark 是 skeleton，部分 G16-G22 只是 presence test。

# 2. Objective

本 PRD 的唯一目标是：

> 将当前 v5.0.1 Candidate 从“主要功能已出现但仍存在治理断点”推进到“治理架构闭环完整、关键 correctness 风险关闭、工具链可执行、但真实落地效果尚未验证”的状态。

完成后系统必须形成以下闭环：

```text
Authoritative Work Context
          ↓
Bound Work Facts
          ↓
Work Router
          ↓
Structured Risk SOT
          ↓
PRD / Domain Preplan
          ↓
Approved PRD
          ↓
Bound Risk + Domain Intent
          ↓
Canonical Plan
          ↓
Static Validator
          ↓
Semantic Review Router
          ↓
Engineering Runtime
          ↓
Delivery Truth
          ↓
Package / Installer Provenance
          ↓
Repository Release Gate
          ↓
Protected master
```

并同时完成：

```text
Governance Regression Framework
Telemetry Completeness Contract
Benchmark Computation Engine
Pilot Specification
```

但不执行真实效果验证。

# 3. Out of Scope

本 PRD 明确不做：

- Consumer Pilot 实际执行；
- 4.4.1 vs 5.x 真实 Benchmark；
- Token 节省比例结论；
- Reviewer Seat 节省比例结论；
- Production regression-rate 结论；
- `BASELINE.md` promotion；
- Release tag promotion；
- Accepted Enterprise Baseline 宣告；
- Spec Kit / Superpowers 作为并行 Runtime 引入；
- 新建第二 PRD / Plan / Delivery SOT；
- 重构 Frozen Delivery State Machine；
- Provider-specific Harness 实现；
- semantic duplicate code 向量检索；
- 批量迁移历史 Plan / Evidence / Review。

# 4. Frozen Invariants

本 PRD 禁止改变：

1. Canonical PRD 唯一；
2. Canonical Plan 唯一；
3. `smc-plan-delivery` 是唯一 governed delivery orchestrator；
4. Static PASS != Implementation Complete；
5. Todo Complete != Plan Proven；
6. Completion Audit 独立；
7. Implementation Review 独立；
8. Blocking Verification 必须 fresh PASS；
9. Content change stales prior proof；
10. `post_review` commit boundary；
11. Roadmap DONE 晚于 implementation commit；
12. Single Writer / ownership-aware slicing；
13. Production skip-gates forbidden；
14. Blocking failure integrity；
15. Acceptance Scenario binding；
16. LIVE Environment/Candidate provenance；
17. Engineering Method artifact 仍为 working memory；
18. TDD RED 不属于 Final Verification FAIL；
19. Domain Provider 不拥有 Delivery State；
20. LEAN 不得削弱 Delivery Truth。

# 5. Change Classification

| Change ID | Priority | Capability | Action | Canonical Owner |
|---|---|---|---|---|
| C01 | P0 | CI / Package Integrity Closure | MODIFY | `.github/workflows` + package manifest builder |
| C02 | P0 | Plan Review Risk Precedence | MODIFY | `smc-plan-review` |
| C03 | P0 | Repository Protection Closure | MODIFY external repo policy + ADD desired-state spec | GitHub Ruleset / repo governance |
| C04 | P1 | Work Facts Authority Binding | ADD + MODIFY | `using-superpowers` |
| C05 | P1 | Domain Deterministic Semantics + Intent Binding | MODIFY | domain-runtime + domain packs |
| C06 | P1 | Install Provenance Finalization | MODIFY | installer suite |
| C07 | P1 | Acceptance / Telemetry / Benchmark Executability | MODIFY + ADD | acceptance tooling + delivery telemetry |

# 6. Production Owner

不新增第二生产 Owner。

```text
Work classification owner:
  using-superpowers

PRD Risk owner:
  smc-prd-grounding

Plan validation owner:
  smc-plan-validator

Plan semantic review owner:
  smc-plan-review

Domain policy owner:
  domain-runtime + selected Domain Pack

Installation owner:
  install_v500 lineage

Delivery truth owner:
  smc-plan-delivery

Repository release owner:
  GitHub CI + repository ruleset

Acceptance tooling:
  test/control-plane tooling only
  NOT a delivery-state owner
```

# 7. C01 — CI / Package Integrity Closure

## 7.1 当前缺口

当前 workflow 已存在：

```text
GES Package Gate / validate-package
```

但当前 source revision 上 package integrity check 会因：

```text
PACKAGE_MANIFEST_MISMATCH
```

失败。

原 `validate` Job 还执行：

```bash
python -m pip install -e . pytest
```

而仓库采用 flat layout，多顶层目录触发 setuptools auto-discovery 失败。

## 7.2 目标状态

CI 必须成为稳定、确定、无隐式 package discovery 的两层 Gate：

```text
validate
GES Package Gate / validate-package
```

### Repository Validate

负责：root Python dependency bootstrap、registry、feature validation、state invariants、root pytest、central SOT mutation check。

### GES Package Gate

负责：deterministic package inventory、manifest/checksum、GES full validator、no unexpected mutation。

## 7.3 修复 pyproject 架构

仓库不是传统单 Python application package。禁止依赖 setuptools 自动发现 top-level packages。

推荐明确声明 metadata-only/dependency package：

```toml
[build-system]
requires = ["setuptools>=77", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = []
```

保留项目 dependencies。这样：

```bash
python -m pip install -e . pytest
```

只安装项目 metadata/dependencies，不把 `audit/`、`skills/`、`schemas/`、`features/` 等目录自动当成 Python distribution packages。

不建议在 CI 中重复硬编码 PyYAML/jsonschema 版本。

## 7.4 Package Manifest builder

修改 `build_package_manifest.py`：

```text
package_version := core/manifest.json.bundle
```

避免 Core Bundle 与 Package Manifest version 漂移。

Builder 写模式：

```bash
python engineeing-skills/build_package_manifest.py
```

校验模式：

```bash
python engineeing-skills/build_package_manifest.py --check
```

实现代码变更最后一步必须：

```text
regenerate manifest
→ regenerate SHA256SUMS
→ check
```

## 7.5 CI mutation contract

Package Gate：

```bash
python engineeing-skills/build_package_manifest.py --check
python engineeing-skills/validate_package.py
git diff --check
git diff --exit-code
```

不得在 CI 中自动 regenerate。CI 必须发现 developer 忘记更新 package identity，而不是自动替 developer 修改仓库。

## 7.6 Architecture Closure AC

- C01-AC01：`pip install -e . pytest` 不再 auto-discovery fail；
- C01-AC02：manifest version 来自 Core Manifest；
- C01-AC03：package bytes 改变但 manifest 未更新必须 FAIL；
- C01-AC04：regenerate 后 `--check` 可稳定读取同一结果；
- C01-AC05：CI 不自动修 manifest；
- C01-AC06：validator 执行后产生 tracked mutation 必须 FAIL。

# 8. C02 — Plan Review Router：Current Risk 必须优先于 STALE PASS

## 8.1 当前缺口

当前 Router 存在 stale prior PASS 先于 current hard risk 的顺序风险。prior PASS 后若 Plan 新增 schema/security/public contract risk，当前 Plan 可能先进入 DELTA。

## 8.2 强制决策序

Plan Review Route 的优先顺序冻结为：

```text
1. prior unresolved/non-PASS
      → FULL

2. current structured risk contradiction / ambiguity
      → FULL

3. current hard risk
      → FULL

4. current risk facts missing/invalid where current contract requires them
      → FULL

5. fresh PASS bound to current semantic hash
      → NONE

6. stale prior PASS + current low-risk
      → DELTA

7. first LEAN + deterministic acceptance clearance
      → DELTA / LIGHT_FIRST_REVIEW

8. legacy low-risk compatible path
      → NONE

9. unknown/FULL
      → FULL
```

关键规则：

> `risk_forces_full` 永远先于 `STALE_PASS -> DELTA`。

## 8.3 Delta Eligibility

DELTA 必须同时满足：

```text
prior verdict = PASS
prior record = stale only because Plan semantic changed
current structured facts = complete
current high-risk = false
current contradiction errors = none
current profile != FULL-forced
```

否则 FULL。

## 8.4 Required regression

新增真实回归：

```text
Plan V1:
  safe LEAN
  review PASS

Plan V2:
  semantic changed
  risk snapshot schema_migration=true

Expected:
  prior status = STALE
  review depth = FULL
  not DELTA
```

并覆盖 `public_contract=true`、`security_boundary=true`、`live_acceptance=true`。

## 8.5 Architecture Closure AC

- C02-AC01：STALE PASS + current hard risk = FULL；
- C02-AC02：STALE PASS + current contradiction = FULL；
- C02-AC03：STALE PASS + current safe = DELTA；
- C02-AC04：Fresh PASS 对 current identical semantic Plan 仍可 NONE；
- C02-AC05：不改变 review freshness contract。

# 9. C03 — master Ruleset / Protection Operational Closure

## 9.1 当前缺口

当前：

```text
master protected = false
rulesets = []
```

因此 CI 只是 post-fact observer，不是 merge boundary。

## 9.2 目标

建立 repository-level desired-state policy，并由 GitHub Admin 实际启用。

推荐 Ruleset：

```text
GES Master Governance
```

Target：`master`。

Required：

```text
Require pull request
Require status checks:
  validate
  GES Package Gate / validate-package
Block force pushes
Block branch deletion
Restrict direct update
```

`Require 1 approval`、conversation resolution 可由组织级 Repo Governance 决定，不在 GES Core 强写。

## 9.3 Desired-State Spec

建议新增：

```text
governance/github/master-ruleset.json
```

示例：

```json
{
  "schema": "smc.repo.ruleset.v1",
  "target_branch": "master",
  "require_pull_request": true,
  "required_checks": [
    "validate",
    "GES Package Gate / validate-package"
  ],
  "allow_force_push": false,
  "allow_delete": false,
  "direct_update": "restricted"
}
```

## 9.4 Drift Checker

建议新增 read-only：

```text
tools/check_repo_governance.py
```

输出：

```text
REPO_GOVERNANCE_PASS
REPO_GOVERNANCE_DRIFT
REPO_GOVERNANCE_UNAVAILABLE
```

此工具只读，不持有管理员写权限。

## 9.5 Activation

Ruleset 激活属于本 PRD 架构闭环的一部分：

1. C01 两个 status context 名称冻结；
2. CI 已修掉已知结构错误；
3. GitHub Admin 启用 Ruleset；
4. read-only checker 可确认 desired state。

这不是“落地效果 Benchmark”，属于 Governance Control Plane 自身配置完成。

## 9.6 Architecture Closure AC

- C03-AC01：tracked desired-state ruleset spec 存在；
- C03-AC02：master actual Ruleset/Protection enabled；
- C03-AC03：Required Checks 使用稳定 job name；
- C03-AC04：force push / delete 被禁；
- C03-AC05：drift checker 不持有写权限。

# 10. C04 — Work Facts Authority Binding

## 10.1 当前缺口

当前 Router 已要求：

```text
governed
retained_production_change
production_write_requested
durable_product_artifact_requested
```

但它们仍是普通调用方 JSON 字段。问题从单一 self-declared flag 变成了 self-declared multi-fact envelope，尚未建立 Trust Boundary。

## 10.2 目标

引入：

```text
smc.ges.work-facts.v1
```

它不是第二 SOT，而是基于 Canonical Artifact + Orchestrator Request 派生的 content-bound routing receipt。

## 10.3 新组件

建议：

```text
engineeing-skills/.agents/skills/using-superpowers/
├── scripts/
│   ├── work_facts.py
│   └── test_work_facts.py
└── references/
    └── work-facts-authority-contract.md
```

## 10.4 Authority Sources

允许：

```text
ROADMAP
FEATURE
PRD
PLAN
ORCHESTRATOR_REQUEST
DERIVED
```

禁止：

```text
WORKER_ASSERTION
MODEL_GUESS
PROMPT_TEXT_ONLY
```

作为 `governed=false` 的单独权威来源。

## 10.5 Bound Envelope

```json
{
  "schema": "smc.ges.work-facts.v1",
  "work_item_id": "RM-001",
  "facts": {
    "existing_owner": true,
    "existing_capability": true,
    "bounded_writes": true,
    "deterministic_verification": true,
    "new_owner": false,
    "public_contract": false,
    "security_boundary": false,
    "schema_migration": false,
    "protocol_change": false,
    "external_dependency": false,
    "lifecycle_change": false,
    "cross_domain_ownership": false,
    "live_acceptance": false,
    "research_intent": true,
    "governed": false,
    "retained_production_change": false,
    "production_write_requested": false,
    "durable_product_artifact_requested": false
  },
  "provenance": {
    "governed": {
      "source_kind": "ROADMAP",
      "source_ref": "roadmap#RM-001",
      "source_sha256": "sha256:...",
      "authority": "AUTHORITATIVE"
    }
  },
  "facts_digest": "sha256:..."
}
```

## 10.6 Authority Resolution

### governed

`true` if any current canonical governed artifact exists：

```text
Roadmap governed entry
Stage PRD
Canonical Plan
Delivery State
```

`false` 只有在 authoritative orchestrator 指示 research 且没有 governed artifact / retained production change 时成立。

### production_write_requested

来自 request envelope、Canonical Change Classification 或 Plan Writes。Worker 自报不能把 true 改 false。

### retained_production_change

只要 request 将产生 source code、config、schema、production behavior docs、release artifact，则 true。

### durable_product_artifact_requested

只要输出进入 project/release/production durable tree，则 true。

## 10.7 Conservative Merge

多个 authority source 冲突时：

```text
风险/生产影响字段：true wins
governed：存在任一 canonical governed artifact → true
```

## 10.8 Route API

保留：

```python
route(facts)
```

用于 unit test / backwards-compatible library call。

新增 production entry：

```python
route_bound(envelope)
```

CLI 默认必须使用 bound envelope。Raw facts 仅允许：

```text
--unsafe-raw-facts
```

用于开发/selftest，不得由 production orchestrator 使用。

## 10.9 Freshness

Bound facts 记录 `source_ref`、`source_sha256`、`facts_digest`。任一 authoritative source 改变：

```text
WORK_FACTS_STALE
```

必须重新 bind。

可选工作内存位置：

```text
.smc/runs/<work-item>/routing/work-facts.json
```

它是 derived receipt，不是 Canonical Artifact。

## 10.10 Architecture Closure AC

- C04-AC01：production routing 不接受无 provenance 的 research authority；
- C04-AC02：存在 Plan/PRD 时 `governed=false` 不可能生效；
- C04-AC03：production write 不能被 Worker 降 false；
- C04-AC04：source hash 变化使 work facts stale；
- C04-AC05：不引入第二 Roadmap/PRD/Plan SOT。

# 11. C05 — Domain Validator：移除全文 broad regex

## 11.1 原则

Domain escalation 必须来自 parsed table values + structured Routing Facts，不得扫描整个 PRD/Plan 文本推断 FULL。

## 11.2 Frontend Structured Tokens

保持现有列，收紧 token grammar。

### Framework

```text
REACT
VUE
GENERIC
N/A:<reason>
```

### Layout

```text
UNCHANGED:<detail>
MODIFY:<detail>
NEW_HIERARCHY:<detail>
```

### Component Map

至少一个：

```text
REUSE:<component>
EXTEND:<component>
NEW:<component>
REMOVE:<component>
N/A:<reason>
```

### State Ownership

```text
UNCHANGED:<owner>
LOCAL:<owner>
SHARED:<owner>
NEW_OWNER:<owner>
MOVE_OWNER:<from->to>
N/A:<reason>
```

### Responsive

```text
UNCHANGED
MODIFY:<detail>
NEW_ARCHITECTURE:<detail>
N/A:<reason>
```

### Visual Verification

```text
STATIC
COMPONENT
INTERACTION
LIVE_VISUAL
N/A:<reason>
```

Frontend FULL 只根据 row token 与 structured risk：`NEW_HIERARCHY`、`NEW_OWNER/MOVE_OWNER`、`NEW_ARCHITECTURE`、new design-system primitive 等。

## 11.3 Backend FULL

只根据 parsed enum：

```text
Contract=BREAKING_CHANGE
Auth=NEW_BOUNDARY
Data/Transaction=MIGRATION
Idempotency/Concurrency=MODIFIED where boundary changes
```

以及 structured Routing Facts 的 `new_owner`、`external_dependency`、`protocol_change`。

不得使用 whole-document `re.search("MIGRATION", text)`。

## 11.4 Ops FULL

只根据：

```text
Deployment Impact in {TOPOLOGY_CHANGE,IRREVERSIBLE}
Compatibility=BREAKING
Live Verification in {LIVE,EXTERNAL}
Migration Order structured non-N/A when migration applies
```

不得全文 regex。

# 12. C05 — PRD Intent ↔ Plan Ledger Binding

## 12.1 当前问题

Approved PRD 已冻结 Domain Design Intent，但 Plan Quality Ledger 目前主要只校验 enum 与 Change ID coverage，未强制证明 Plan 仍实现 Approved PRD 的同一 Domain decision。

## 12.2 设计原则

禁止复制整份 PRD 形成第二 SOT。采用：

```text
source PRD binding
+
normalized domain intent digest
+
declared field mapping
```

## 12.3 Plan Frontmatter Binding

新 Plan v3.7 增加：

```yaml
source_prd: docs/prd/<file>.md
source_prd_sha256: sha256:...
domain_intent_digest: sha256:...
```

Existing in-flight v3.7 不批量迁移，缺 binding 时 semantic review fail-closed 到 FULL。

## 12.4 Domain Pack Binding Map

Domain Pack v2 增加 optional `intent_bindings`。

Backend 示例：

```json
{
  "intent_bindings": {
    "Contract": {"plan_column": "Contract", "mode": "EXACT"},
    "Auth": {"plan_column": "Auth", "mode": "EXACT"}
  }
}
```

Frontend binding：`Framework`、`State Ownership`、`Design System`、`Visual Verification`。

Backend binding：`Owner`、`Contract`、`Data/Transaction`、`Auth`、`Idempotency/Concurrency`。

Ops binding：`Deployment Impact`、`Compatibility`、`Environment/Config`、`Migration Order`、`Rollback`。

## 12.5 Generic Runtime

`domain_runtime.py` 新增：

```text
normalize_domain_intent()
domain_intent_digest()
validate_intent_binding()
```

Plan validator：

```text
read source PRD
verify source_prd_sha256
recompute domain_intent_digest
compare Plan Quality Ledger according to pack bindings
```

错误：

```text
PLAN_SOURCE_PRD_MISSING
PLAN_SOURCE_PRD_STALE
PLAN_DOMAIN_INTENT_STALE
PRD_STALE_OR_CONFLICTING
```

## 12.6 Child Error Propagation

当前 generic `DOMAIN_PREPLAN_FAILED` 不应吞掉 child canonical code。

应传播：

```text
BACKEND_PREPLAN_FULL_REQUIRED
OPS_PREPLAN_ROLLBACK_REQUIRED
FRONTEND_PREPLAN_ENUM_INVALID
```

上层 Harness/CI/Acceptance 可以稳定断言。

## 12.7 Architecture Closure AC

- C05-AC01：Domain FULL escalation 不再 scan whole document；
- C05-AC02：否定描述不会从 Domain 层重新产生假 FULL；
- C05-AC03：Plan source PRD hash 绑定；
- C05-AC04：Plan ledger 与 PRD intent 冲突必须阻断；
- C05-AC05：binding map 在 Domain Pack 声明，不在 Core 硬编码 Domain；
- C05-AC06：child error code 不被泛化吞掉；
- C05-AC07：Domain Provider 仍不拥有 Delivery State。

# 13. C06 — install-lock Provenance Finalization

## 13.1 当前问题

当前两个核心问题：

1. `package_manifest_sha256` 是 re-serialized manifest object hash，不是 `PACKAGE-MANIFEST.json` exact bytes hash；
2. `transaction_manifest_sha256` 在最终 PASS journal 重写之前计算，active lock 与最终 transaction bytes 不一致。

## 13.2 目标模型

拆分：

```text
Mutable Transaction Journal
Immutable Install Receipt
Install Lock
```

### Mutable Transaction Journal

只用于 rollback、step tracking、`PENDING / ROLLED_BACK / PASS`，允许 transaction 生命周期更新，不再作为 immutable release identity。

### Immutable Install Receipt

新增：

```text
.smc/ges-install-receipts/<install_id>.json
```

Schema：

```text
smc.ges.install-receipt.v1
```

在 files copied、stale reconciliation complete、all install validations pass 后生成一次，写后不再修改。

### Install Lock

`install-lock.v2` 引用：

```text
install_receipt_path
install_receipt_sha256
```

不再使用 mutable transaction journal sha 充当 immutable provenance。

# 14. Exact Release Identity

必须计算：

```text
package_manifest_sha256 = sha256(PACKAGE-MANIFEST.json exact bytes)
```

同时保存：

```text
bundle
source_commit
source_tree_dirty
package_manifest_sha256
package_file_count
installer_sha256
```

如果 source tree dirty：

```text
install 可用于开发
release_eligible = false
```

禁止解释为 immutable Release。

# 15. Install Receipt Schema

```json
{
  "schema": "smc.ges.install-receipt.v1",
  "install_id": "...",
  "bundle": "5.x",
  "release_identity": {
    "source_commit": "...",
    "source_tree_dirty": false,
    "package_manifest_sha256": "...",
    "package_file_count": 215,
    "installer_sha256": "..."
  },
  "profile": {
    "id": "...",
    "version": "...",
    "sha256": "..."
  },
  "domains": {},
  "policy_digest": "sha256:...",
  "managed_file_set_sha256": "sha256:...",
  "validation": {
    "status": "PASS",
    "commands_digest": "sha256:..."
  },
  "stale_reconciliation": {
    "deleted": [],
    "blocked": []
  },
  "finalized_at": "..."
}
```

Receipt 不包含自己的 SHA；Lock 负责 hash receipt bytes。

# 16. Install Order

冻结为：

```text
1. verify source PACKAGE-MANIFEST / SHA256SUMS
2. resolve profile/packs
3. preflight
4. create transaction backup
5. copy managed files
6. install GES metadata
7. repair mirror
8. update gitignore
9. transaction journal = INSTALLED_PENDING_VALIDATION
10. run install validation
11. reconcile stale package-owned files
12. verify final managed tree
13. create immutable install receipt
14. build install-lock.v2 using exact manifest bytes hash + receipt bytes hash
15. write install-lock transactionally
16. transaction journal = PASS
```

Lock 不再 hash mutable final journal，因此不存在 circular/finality mismatch。

失败发生在 1–15 任一步：restore all recorded files，journal=`ROLLED_BACK`，不得留下新 active lock。

## 16.1 Architecture Closure AC

- C06-AC01：manifest SHA 使用 exact bytes；
- C06-AC02：active lock 引用 immutable receipt；
- C06-AC03：receipt finalization 后不被重写；
- C06-AC04：mutable journal 与 immutable provenance 分离；
- C06-AC05：stale deletion rollback 可恢复；
- C06-AC06：Consumer-local file 不进入 owned set；
- C06-AC07：dirty source 明确 `release_eligible=false`。

# 17. C07 — Acceptance / Telemetry / Benchmark Executability Closure

## 17.1 边界

本项只完成：

```text
executable governance test framework
telemetry completeness framework
benchmark computation framework
pilot specification
```

禁止执行：

```text
real Consumer Pilot
real 4.4.1 vs 5.x Benchmark
production effectiveness validation
```

# 18. G16–G22 从 Presence Test 改为 Real Deterministic Test

## G16 Duplicate Hotspot

构造临时 Plan：

```text
T1 Writes: app.py#save
T2 Writes: app.py#save
```

执行真实 ownership/static validator，预期 duplicate ownership/hotspot BLOCK。不得只 grep source code。

## G17 Out-of-Scope Write

```text
workspace snapshot
→ mutate file outside Plan-owned write set
→ workspace inspect / completion precheck
```

预期 `unexpected_dirty` + `pass=false`，并断言 canonical error。

## G18 TDD Stale

```text
TDD RED
→ production fix
→ TDD GREEN receipt
→ mutate bound test/source
→ tdd-check
```

预期 `TDD_SCOPE_STALE` 或现有 canonical stale error。

## G19 Review Stale

```text
record Plan Review PASS
→ mutate semantic Plan content
→ latest_status(plan)
```

预期 `STALE`。

## G20 Evidence Stale

```text
create blocking proof bound to current scope
→ mutate bound production content
→ evidence current-status
```

预期 `STALE`。

## G21 LIVE Candidate Mismatch

不得继续拿 `TELEMETRY_INCOMPLETE` 替代。

```text
candidate=A
LIVE evidence SUT/candidate=B
→ final verification/candidate guard
```

预期 candidate mismatch BLOCK。

## G22 Debug Escalation

```text
REPRODUCTION
ROOT_CAUSE
FIX_ATTEMPT failed #1
FIX_ATTEMPT failed #2
FIX_ATTEMPT failed #3
```

预期 `DEBUG_ARCHITECTURE_ESCALATION`。不得只检查源码包含字符串。

# 19. Telemetry Completeness Contract

## 19.1 Dispatch Identity

所有 Harness dispatch 必须有 `dispatch_id`。

Dispatch：

```json
{
  "schema": "smc.execution.telemetry.v1",
  "dispatch_id": "...",
  "kind": "dispatch",
  "todo": "T1",
  "phase": "IMPLEMENT",
  "requested_tier": "STANDARD"
}
```

Result：

```json
{
  "dispatch_id": "...",
  "kind": "result",
  "actual_tier": "STANDARD",
  "provider": "...",
  "model": "...",
  "fallback": false,
  "fallback_reason": "",
  "prompt_tokens": 0,
  "completion_tokens": 0,
  "cache_read_tokens": 0,
  "cache_write_tokens": 0,
  "latency_ms": 0,
  "retry_count": 0,
  "outcome": "PASS"
}
```

## 19.2 Completeness

`complete=true` 必须满足：

```text
every governed dispatch has exactly one terminal result
requested_tier present
actual_tier present OR explicit fallback/unsupported marker
provider/model present OR explicit unavailable marker
outcome present
token accounting present OR TOKEN_ACCOUNTING_UNAVAILABLE marker
no malformed duplicate terminal event
```

否则 `TELEMETRY_INCOMPLETE`。

Cache-hit/reviewer-seat 事件不能单独使 telemetry complete。

## 19.3 Privacy

继续禁止记录 prompt body、source body、secret、API key、password、token value、customer payload。

# 20. Generic Harness Adapter Contract

GES 不写死 provider。新增：

```text
smc-plan-delivery/references/harness-telemetry-contract.md
```

Harness 调用：

```text
runtime_metrics dispatch
runtime_metrics result
runtime_metrics cache-hit
runtime_metrics cache-miss
runtime_metrics reviewer-seat
```

或 JSON ingestion：

```text
runtime_metrics ingest --event-json <file>
```

Provider-specific adapter 属于 Consumer/Harness，不属于 Core GES。

# 21. Benchmark Engine：从 stub 变为真正计算器

`run_benchmark.py` 必须实现 paired comparison，但本 PRD 不提供真实数据。

## 21.1 Input

```json
{
  "case_id": "B01",
  "cohort": "A",
  "class": "BOUNDED",
  "outcome": "PASS",
  "prompt_tokens": 10000,
  "completion_tokens": 2000,
  "cache_read_tokens": 0,
  "reviewer_seats": 2,
  "fix_rounds": 1,
  "escaped_defect": 0
}
```

Cohort：A=baseline，B=candidate；要求 `case_id` paired。

## 21.2 Calculations

```text
total_tokens = prompt_tokens + completion_tokens
paired_delta = B - A
reduction_pct = (A - B) / A * 100
```

计算 median by：all、BOUNDED、NORMAL、BUG_FIX、HIGH_RISK。

Reviewer 计算 median reviewer-seat reduction。

Safety/Quality 计算 false lean、false spike、ownership escape、stale proof accepted、escaped defect。

## 21.3 Output

```text
BENCHMARK_READY
BENCHMARK_THRESHOLD_MET
BENCHMARK_THRESHOLD_NOT_MET
TELEMETRY_INCOMPLETE
UNPAIRED_CASES
```

本 PRD 不运行真实数据，不产生真实 benchmark verdict；只用 synthetic fixture 验证计算器。

# 22. Threshold Schema 完整化

扩展为：

```json
{
  "schema": "smc.ges.acceptance.thresholds.v2",
  "safety": {
    "high_risk_false_lean": 0,
    "governed_production_false_spike": 0,
    "ownership_escape": 0,
    "scope_drift_accepted": 0,
    "stale_tdd_accepted": 0,
    "stale_review_accepted": 0,
    "stale_evidence_accepted": 0,
    "live_candidate_mismatch_pass": 0,
    "package_integrity_bypass": 0,
    "consumer_owned_file_silent_delete": 0
  },
  "quality": {
    "duplicate_production_owner": 0,
    "blocking_ac_without_proof": 0,
    "domain_invalid_enum_accepted": 0
  },
  "efficiency": {
    "bounded_median_token_reduction_pct": 30,
    "normal_risk_reviewer_seat_reduction_pct": 25,
    "repeated_source_context_read_reduction_pct": 30
  }
}
```

本 PRD 只实现 evaluator，不判断真实 GES 是否达到阈值。

# 23. 3 Consumer / 12 Delivery Pilot：只完成 Specification，不执行

建立：

```text
engineeing-skills/acceptance/pilot/
├── pilot.schema.json
├── pilot-matrix.json
├── result.schema.json
└── run_pilot.py
```

Matrix：

```text
Consumer A: Frontend
  LEAN
  BEHAVIOR_CHANGE
  BUG_FIX
  HIGH_RISK

Consumer B: Backend
  LEAN
  BEHAVIOR_CHANGE
  BUG_FIX
  HIGH_RISK

Consumer C: Ops
  LEAN
  BEHAVIOR_CHANGE
  BUG_FIX
  HIGH_RISK
```

共 12 slots。

`run_pilot.py` 本 PRD 只支持：

```bash
run_pilot.py --validate-matrix
run_pilot.py --validate-result <result.json>
run_pilot.py --summarize <results-dir>
```

禁止本 PRD 提供/调用真实 Consumer 执行模式。

Pilot 状态保持：

```text
NOT_PROVEN / NOT_EXECUTED
```

# 24. Package Validation Registry

`validate_package_v500.py` 必须纳入：

```text
work facts authority selftest
risk precedence selftest
domain semantic/binding selftests
installer provenance selftest
telemetry completeness selftest
benchmark computation synthetic selftest
acceptance G01-G30
```

Package Gate 不得执行：

```text
real Consumer Pilot
real benchmark
production Harness
```

Package Gate 的职责是证明治理架构与 deterministic contracts 没坏，而不是证明落地收益。

# 25. Required Files / Source Anchors

## C01

```text
pyproject.toml
.github/workflows/governance-ci.yml
engineeing-skills/build_package_manifest.py
engineeing-skills/PACKAGE-MANIFEST.json
engineeing-skills/SHA256SUMS
```

## C02

```text
engineeing-skills/.agents/skills/smc-plan-review/scripts/assess_plan_review.py
engineeing-skills/.agents/skills/smc-plan-review/scripts/*
```

## C03

```text
governance/github/master-ruleset.json
tools/check_repo_governance.py
.github/workflows/governance-ci.yml
```

## C04

```text
engineeing-skills/.agents/skills/using-superpowers/scripts/work_router.py
engineeing-skills/.agents/skills/using-superpowers/scripts/work_facts.py
engineeing-skills/.agents/skills/using-superpowers/scripts/test_work_facts.py
engineeing-skills/.agents/skills/using-superpowers/references/work-facts-authority-contract.md
```

## C05

```text
engineeing-skills/domain-runtime/domain_table.py
engineeing-skills/domain-runtime/domain_runtime.py
engineeing-skills/domain-runtime/risk_signals.py
engineeing-skills/domain-packs/frontend/*
engineeing-skills/domain-packs/backend/*
engineeing-skills/domain-packs/ops/*
engineeing-skills/.agents/skills/smc-frontend-preplan/scripts/validate_prd_intent.py
engineeing-skills/.agents/skills/smc-frontend-review/scripts/validate_plan_extension.py
engineeing-skills/.agents/skills/smc-backend-preplan/scripts/validate_prd_intent.py
engineeing-skills/.agents/skills/smc-backend-review/scripts/validate_plan_extension.py
engineeing-skills/.agents/skills/smc-ops-preplan/scripts/validate_prd_intent.py
engineeing-skills/.agents/skills/smc-ops-review/scripts/validate_plan_extension.py
engineeing-skills/.agents/skills/smc-plan-from-approved-prd-ponytail/scripts/create_plan_seed_v37.py
engineeing-skills/.agents/skills/smc-plan-validator/scripts/validate_plan_v37.py
```

## C06

```text
engineeing-skills/install_v430.py
engineeing-skills/install_v500.py
engineeing-skills/tests/test_package_v500.py
```

## C07

```text
engineeing-skills/.agents/skills/smc-plan-delivery/scripts/runtime_metrics.py
engineeing-skills/.agents/skills/smc-plan-delivery/scripts/source_context.py
engineeing-skills/.agents/skills/smc-plan-delivery/scripts/review_record.py
engineeing-skills/.agents/skills/smc-plan-delivery/references/harness-telemetry-contract.md
engineeing-skills/acceptance/run_acceptance.py
engineeing-skills/acceptance/run_benchmark.py
engineeing-skills/acceptance/metrics.schema.json
engineeing-skills/acceptance/thresholds.json
engineeing-skills/acceptance/pilot/*
```

# 26. Failure Semantics

新增/冻结：

```text
# Work Facts
WORK_FACTS_INVALID
WORK_FACTS_UNBOUND
WORK_FACTS_AUTHORITY_MISSING
WORK_FACTS_STALE
WORK_FACTS_CONFLICT

# Review
PLAN_REVIEW_CURRENT_RISK_FULL_REQUIRED
PLAN_REVIEW_DELTA_INELIGIBLE

# Domain
PLAN_SOURCE_PRD_MISSING
PLAN_SOURCE_PRD_STALE
PLAN_DOMAIN_INTENT_STALE
PRD_STALE_OR_CONFLICTING

# Installer
INSTALL_RELEASE_IDENTITY_INVALID
INSTALL_RECEIPT_INVALID
INSTALL_RECEIPT_HASH_MISMATCH
INSTALL_SOURCE_DIRTY_NOT_RELEASE_ELIGIBLE
INSTALL_STALE_OWNED_FILE_MODIFIED

# Telemetry
TELEMETRY_DISPATCH_UNPAIRED
TELEMETRY_RESULT_DUPLICATE
TELEMETRY_MODEL_IDENTITY_MISSING
TELEMETRY_TOKEN_ACCOUNTING_MISSING
TELEMETRY_INCOMPLETE

# Benchmark
BENCHMARK_INPUT_INVALID
BENCHMARK_UNPAIRED_CASES
BENCHMARK_TELEMETRY_INCOMPLETE
BENCHMARK_THRESHOLD_MET
BENCHMARK_THRESHOLD_NOT_MET

# Repo Governance
REPO_GOVERNANCE_DRIFT
REPO_GOVERNANCE_UNAVAILABLE
```

# 27. Migration Policy

## Existing Work Router callers

- `route(facts)` 保持兼容；
- production CLI / orchestrator 改走 `route_bound()`；
- unbound raw facts 仅 development compatibility，不是 production contract。

## Existing v3.7 Plan

- 不批量改；
- 新 Plan 写 `source_prd` / digest；
- 旧 Plan 缺 binding 时 fail closed 到 semantic FULL；
- 不自动重写 historical Plan。

## Existing Domain Intent

- 新文档收紧 token grammar；
- 旧 in-flight document compatible read；
- 不 silently reinterpret invalid free-text 为 structured safe。

## Existing install-lock.v1

- 保持 v1 → v2 non-destructive first upgrade；
- 不用缺 provenance 的 v1 lock 自动删除 stale file。

## Existing install-lock.v2 初版

- loader 兼容读取；
- 没有 `install_receipt_sha256` 时不宣称 release-grade provenance；
- 下一次 successful install 生成完整 receipt-bound v2 lock。

## Existing telemetry

- 老 events 可读；
- 缺 dispatch pairing 时 summary=`TELEMETRY_INCOMPLETE`；
- 不补造历史 model/token 数据。

# 28. Architecture-Level Test Strategy

本 PRD允许执行的是治理架构 deterministic test：

```text
L1 unit tests
L2 contract tests
L3 temp-repo destructive regression
L4 installer fixture
L5 package validation
L6 CI gate
L7 repository protection state check
```

禁止：

```text
L8 real Consumer Pilot
L9 real Cost Benchmark
L10 production effectiveness conclusion
```

# 29. Minimum Architecture Validation Chain

实现完成时允许且必须运行：

```bash
python engineeing-skills/build_package_manifest.py --check
python engineeing-skills/validate_package.py
python engineeing-skills/domain-runtime/test_risk_signals.py
python engineeing-skills/acceptance/run_acceptance.py
git diff --check
git diff --exit-code
```

以及新增加的 component selftests。

这属于 architecture correctness，不是 effect validation。

# 30. GitHub Gate Target

代码闭环后 GitHub 必须具备稳定的：

```text
validate                             PASS
GES Package Gate / validate-package PASS
```

然后启用：

```text
master
  Require PR
  Require validate
  Require GES Package Gate / validate-package
  no force push
  no branch deletion
  no unreviewed direct push
```

本步骤属于 Governance Architecture 本身，不属于 Consumer 效果评估。

# 31. PRD Acceptance Criteria — 只判断架构闭环

## C01

- AC01：root CI dependency bootstrap 不再 auto-discovery fail；
- AC02：Package Manifest/SHA 可 deterministic regenerate/check；
- AC03：CI 不自动修改 manifest；
- AC04：Package Gate stable contract 完成。

## C02

- AC05：current hard risk 优先于 stale PASS DELTA；
- AC06：current safe stale PASS 才能 DELTA；
- AC07：fresh review semantics 不回退。

## C03

- AC08：tracked ruleset desired state 存在；
- AC09：actual `master` Ruleset/Protection enabled；
- AC10：Required Checks 固定；
- AC11：force push/delete 被阻止。

## C04

- AC12：production Work Router 输入必须 provenance-bound；
- AC13：canonical artifact 可把 `governed` 强制为 true；
- AC14：authority source 改变使 bound facts stale；
- AC15：raw Worker assertion 不能产生 production NONE。

## C05

- AC16：Domain FULL trigger 不再 scan whole document；
- AC17：PRD Domain Intent 与 Plan Ledger 有 content-bound binding；
- AC18：PRD changed 后 Plan binding stale；
- AC19：Plan/PRD Domain semantic conflict 被阻断；
- AC20：child semantic error code 可传播。

## C06

- AC21：Package Manifest digest 使用 exact bytes；
- AC22：Install Receipt immutable；
- AC23：Active Lock 引用 receipt hash；
- AC24：mutable journal 与 immutable provenance 分离；
- AC25：rollback/stale owned safety 保持。

## C07

- AC26：G16-G22 变成真实 behavior/destructive tests；
- AC27：Telemetry completeness 使用 dispatch/result pairing；
- AC28：Benchmark engine 实际计算 paired median/reduction；
- AC29：Threshold evaluator 可用 synthetic fixture deterministic 测试；
- AC30：3 Consumer/12 delivery Pilot matrix/schema/runner contract 完成；
- AC31：本 PRD 不产生任何真实 Consumer Pilot evidence；
- AC32：本 PRD 不产生任何真实 Benchmark cost verdict。

## Frozen Regression

- AC33：Todo completion interlock 不回退；
- AC34：TDD/debug freshness 不回退；
- AC35：Completion Audit/Review/Verification freshness 不回退；
- AC36：`post_review` commit boundary 不回退；
- AC37：`BASELINE.md` 不被本 PRD promotion。

# 32. Definition of Done

本 PRD DoD 是“治理架构完成”，不是“落地效果已经证明”。

```text
[ ] C01 CI/package architecture closed
[ ] C02 review-risk precedence fixed
[ ] C03 master ruleset/protection active
[ ] C04 authoritative work facts binding implemented
[ ] C05 Domain structured escalation implemented
[ ] C05 PRD↔Plan Domain intent binding implemented
[ ] C06 receipt-bound install provenance implemented
[ ] C07 G16-G22 real deterministic cases implemented
[ ] C07 telemetry completeness implemented
[ ] C07 benchmark computation engine implemented
[ ] C07 pilot matrix/schema/runner contract implemented
[ ] Package manifest regenerated
[ ] Package deterministic gates pass
[ ] No Frozen Invariant changed
[ ] BASELINE.md unchanged
[ ] Consumer Pilot remains NOT_EXECUTED
[ ] Cost Benchmark remains NOT_EXECUTED
[ ] Baseline Promotion remains BLOCKED
```

# 33. Target State After This PRD

```text
PRD v5.0.2

Implementation:
  ARCHITECTURE_COMPLETE

Governance Architecture:
  C01 COMPLETE
  C02 COMPLETE
  C03 COMPLETE
  C04 COMPLETE
  C05 COMPLETE
  C06 COMPLETE
  C07 EXECUTABLE_FRAMEWORK_COMPLETE

Package Gate:
  ARCHITECTURALLY_CLOSED

Repository Protection:
  ACTIVE

Acceptance Corpus:
  DETERMINISTIC_FRAMEWORK_COMPLETE

Telemetry:
  CONTRACT_COMPLETE

Benchmark Engine:
  EXECUTABLE_NOT_RUN

Consumer Pilot:
  SPECIFIED_NOT_EXECUTED

Cost Benchmark:
  NOT_EXECUTED

Effect Validation:
  OUT_OF_SCOPE

Accepted Baseline Promotion:
  BLOCKED_BY_DESIGN
```

不能写成：

```text
GES 5 accepted
Token reduction proven
Pilot passed
Production stability proven
```

# 34. 下一阶段边界

只有另一个明确授权的独立阶段，才允许：

```text
Consumer Pilot
→ 4.4.1 vs 5.x Benchmark
→ Acceptance Review
→ BASELINE Promotion
```

本 PRD 到此为止。

# 35. Versioning Note

本文件 PRD 版本：

```text
v5.0.2
```

不等于最终 Bundle 必须 `5.0.2`。由于可能加入 Work Facts binding、Domain intent binding、Install Receipt、Benchmark engine、repository governance desired-state tooling，最终 Bundle SemVer 仍由 Release Review 按 `VERSIONING.md` 判定。

本 PRD 不进行 Release Promotion。

# 36. Clarification Ledger

| ID | Impact | Question | Decision | Status |
|---|---|---|---|---|
| Q01 | HIGH | 是否执行 3 Consumer / 12 delivery Pilot？ | 否，只完成 matrix/schema/runner contract。 | CLOSED |
| Q02 | HIGH | 是否运行真实 4.4.1 vs 5.x Benchmark？ | 否，只完成计算器和 synthetic selftest。 | CLOSED |
| Q03 | HIGH | G16-G22 是否允许执行？ | 允许，因为它们是 deterministic governance regression，不是业务落地效果验证。 | CLOSED |
| Q04 | HIGH | 是否更新 BASELINE.md？ | 否，严格禁止 promotion。 | CLOSED |
| Q05 | HIGH | master protection 是否属于效果验证？ | 否，它属于治理架构自身的 control-plane closure，必须完成。 | CLOSED |
| Q06 | MEDIUM | Work Facts 是否成为第二 SOT？ | 否，是 content-bound derived routing receipt。 | CLOSED |
| Q07 | MEDIUM | Install transaction journal 是否继续作为 provenance？ | 否，新增 immutable install receipt；journal 只做 transaction/rollback。 | CLOSED |

# 37. 最终架构

```text
┌──────────────────────────────────────────────────────┐
│           Authoritative Request / Roadmap            │
│            PRD / Plan / Orchestrator                 │
└──────────────────────────┬───────────────────────────┘
                           │
                           ▼
                 Work Facts Binder
              provenance + content hash
                           │
                           ▼
                    Work Router
                  NONE / LEAN / FULL
                           │
                           ▼
                 Structured Risk Runtime
                           │
                    ┌──────┴──────┐
                    │             │
                    ▼             ▼
               PRD Grounding   Domain Preplan
                    │             │
                    └──────┬──────┘
                           ▼
                     APPROVED PRD
                           │
          source hash + domain intent digest
                           │
                           ▼
                    Canonical Plan
                           │
             Static + Domain Binding Gate
                           │
                           ▼
                Semantic Review Router
          current hard risk > stale PASS delta
                           │
                           ▼
                 Engineering Runtime
                           │
                 Delivery Truth / Evidence
                           │
                           ▼
              Immutable Install Receipt
                           │
                    Install Lock v2
                           │
                           ▼
                   Package Identity
                           │
                           ▼
                    CI Package Gate
                           │
                           ▼
                  Protected master

Control-plane Test Layer:
  Golden deterministic cases
  Chaos deterministic cases
  Telemetry completeness
  Benchmark computation engine
  Pilot specification

NOT EXECUTED IN THIS PRD:
  Real Consumer Pilot
  Real A/B Benchmark
  Effect Validation
  Baseline Promotion
```

# 38. Final Requirement

本 PRD 完成后，GES 必须已经能够从架构上可靠回答：

1. 当前 Work Facts 是谁提供的，来源是否仍 fresh？
2. 为什么一个任务可以 NONE/LEAN/FULL，而不是 Worker 自报？
3. 当前 Plan 即使 prior Review PASS，新增高风险后为什么一定回到 FULL？
4. Domain FULL escalation 来自哪个结构化字段，而不是全文关键字？
5. Plan Domain Ledger 是否仍然符合 Approved PRD Intent？
6. Consumer 安装的 package identity 与 immutable install receipt 是什么？
7. CI 为什么可以阻止坏 package 进入受保护 master？
8. Telemetry 什么时候才是真正 complete？
9. Benchmark engine 是否能对 paired cohort 正确计算结果？
10. Pilot framework 是否已准备好，但没有被本 PRD 偷偷执行？

只有以上架构问题全部具有 deterministic answer，本 PRD 才算完成。
