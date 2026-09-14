---
title: "GES Safety and Runtime Integration Closure PRD"
prd_version: "v5.0.3"
work_item_id: "GES-SAFETY-RUNTIME-CLOSURE-5.0.3"
status: "DRAFT"
review_verdict: "PENDING"
governance_profile: "FULL"
previous_governance_profile: "FULL"
source_revision: "loudon84/smc-delivery-governance@5edf00502c86d5cf3ad6d49f9025347b6a137445"
grounded_commit: "5edf00502c86d5cf3ad6d49f9025347b6a137445"
canonical_path: "engineeing-skills/"
source_prd: "docs/prd/PRD-GES-v5.0.2-Governance-Architecture-Closure.md"
current_bundle_manifest_version: "5.0.0"
accepted_baseline_bundle: "4.1.2"
target_release_semver: "DEFERRED_TO_RELEASE_REVIEW"
commit_policy: "post_review"
scope_mode: "SAFETY_AND_RUNTIME_INTEGRATION_CLOSURE"
pilot_execution: "FORBIDDEN"
benchmark_execution: "FORBIDDEN"
baseline_promotion: "FORBIDDEN"
---

# GES Safety and Runtime Integration Closure PRD v5.0.3

> Repository：`loudon84/smc-delivery-governance`  
> Canonical Path：`engineeing-skills/`  
> Grounded Source：`master@5edf00502c86d5cf3ad6d49f9025347b6a137445`  
> Parent PRD：`PRD-GES-v5.0.2-Governance-Architecture-Closure.md`  
> 本 PRD 目标：关闭安全 fail-open、澄清并落地三段式 Runtime 接入边界；本轮严禁完成 Pilot / Benchmark。

## 0. 强制边界

本 PRD 只允许安全修复、Runtime 适配、契约澄清、确定性回归与包完整性维护。

以下状态在整个 v5.0.3 工作项中必须保持不变：

```text
Consumer Pilot = NOT_EXECUTED
Cost Benchmark = NOT_EXECUTED
Pilot Verdict = UNAVAILABLE
Benchmark Verdict = UNAVAILABLE
Accepted Baseline Promotion = FORBIDDEN
```

禁止：

- 在任何真实 Consumer 上执行 Pilot；
- 创建或补录真实 Pilot result；
- 收集、导入或计算 4.4.1 与 5.x 的真实 Token、成本、Reviewer Seat 或生产质量对比；
- 把 synthetic/self-test 输出改写成 Pilot 或 Benchmark 证据；
- 修改 Pilot / Benchmark 状态为 `EXECUTED`、`PASS`、`READY` 或等价完成态；
- 基于本 PRD 宣称 Token 降低、成本降低、生产稳定性提升；
- 修改 `BASELINE.md`、创建 release tag 或宣告 Accepted Enterprise Baseline。

本轮保护路径如下；除非只为修复 package manifest 中的字节索引，否则不得修改其业务内容：

```text
engineeing-skills/acceptance/pilot/**
engineeing-skills/acceptance/run_benchmark.py
engineeing-skills/acceptance/thresholds.json
audit/**/pilot/**
audit/**/benchmark/**
```

现有 Package Gate 若包含纯算法 self-test，可以继续运行，但不得读取真实 Consumer 数据、生成效果结论或改变上述状态。

# 1. 文档定位与问题陈述

v5.0.2 已建立 GES 5 的主体治理闭环，但最新攻击性验证证明正常路径通过并不等于信任边界安全。

当前需要关闭的缺口：

1. Rollback manifest path 可越出项目根目录并删除外部文件；
2. Work Facts 缺少全字段 provenance、生产路由未强制 source freshness，且合并可把安全 `true` 降成 `false`；
3. Repository Protection verifier 用正向默认值补齐缺失证据，可能制造假 PASS；
4. Install Receipt 未纳入事务写集，后续失败时可能残留成功凭据；
5. v3.7 Plan 在全部 Intent Binding 字段缺失时跳过校验；
6. 路由文档仍指向 v3.6，且 seed 失败诊断可能被延迟；
7. Spec Kit 仅为理念借鉴，缺少可验证的外部接入；
8. Superpowers 方法已被吸收，但 GES Work Router 与官方同名 skill 造成职责和集成状态混淆。

当前最准确的架构描述是：

```text
Front UX:
  GES-native, Spec Kit-inspired
  external integration NOT VERIFIED

Middle Execution:
  GES-owned orchestration with Superpowers-inspired methods
  upstream/runtime provenance NOT VERIFIED

Back Delivery Truth:
  GES-owned and structurally complete
  safety closure BLOCKED by fail-open defects
```

# 2. Objective

本 PRD 的唯一目标是把上述状态推进到：

```text
Spec Kit capability
  → optional, isolated, provenance-bound UX provider
  → canonical Stage PRD remains the only requirement SOT

Superpowers capability
  → versioned method provider under GES execution control
  → canonical Plan and Delivery State remain GES-owned

GES Delivery Truth
  → fail-closed routing, validation, install and rollback
  → no external provider may mint delivery truth
```

完成后必须能够用机器证据回答：

1. 外部 Spec Kit / Superpowers 是否真的被调用，版本和能力是什么？
2. 外部输出如何被隔离、校验并导入，而没有形成第二 PRD / Plan / Delivery SOT？
3. Work Facts 的每个治理事实来自哪里，源变化后为什么一定 stale？
4. Rollback 为什么不能访问项目根目录之外的任何路径？
5. Repository Protection 的 PASS 是否完全来自显式证据，而非默认推断？
6. 安装任一步失败后，为什么不会残留成功 Receipt 或指针？
7. 任意 v3.7 Plan 为什么都不能绕过 PRD / Domain Intent Binding？

# 3. 外部能力事实基线

本节只冻结适配所依赖的官方能力，不授权外部工具成为治理 Owner。

## 3.1 Spec Kit

官方 Spec Kit 由 `github/spec-kit` 维护，`specify-cli` 提供版本与 capability discovery，Agent 侧暴露 `speckit-*` / `/speckit.*` 工作流。

v5.0.3 接入必须基于以下稳定探测面：

```text
specify version
specify version --features --json
```

官方参考：

- `https://github.com/github/spec-kit`
- `https://github.com/github/spec-kit/blob/main/docs/installation.md`
- `https://github.com/github/spec-kit/blob/main/docs/reference/core.md`

`specify init --here --force` 会在项目中安装 Spec Kit 资产，本 PRD 禁止安装器或 Delivery 在 Consumer 根目录隐式执行该命令。

## 3.2 Superpowers

官方 Superpowers 是 agent skill framework 与软件工程方法集合，不是 Delivery transaction API。

GES 只能在 skill/method provider 层接入，不能把 Superpowers 描述为可直接拥有 Commit、Evidence、Roadmap 或 Delivery State 的独立 Runtime。

官方参考：

- `https://github.com/obra/Superpowers`
- `https://github.com/obra/Superpowers/blob/main/skills/using-superpowers/SKILL.md`
- `https://github.com/obra/Superpowers/blob/main/skills/subagent-driven-development/SKILL.md`

# 4. Out of Scope

本 PRD 明确不做：

- Consumer Pilot 与真实 Benchmark；
- 效率、Token、Reviewer Seat 或生产回归率结论；
- Accepted Baseline Promotion 与 release tag；
- 用 Spec Kit 的 `spec.md` 替代 Stage PRD；
- 用 Spec Kit plan/tasks 替代 canonical `smc.plan.v3.7`；
- 允许 Spec Kit 或 Superpowers 直接编辑 Canonical Artifact；
- 允许外部 provider 转移 Todo 状态、Delivery State、Evidence Verdict、Commit 或 Roadmap 状态；
- 重构 Frozen Delivery State Machine；
- 自动安装、自动升级或联网下载第三方 Runtime；
- 把第三方不可用降级成虚假的 `EXTERNAL_VERIFIED`；
- 批量迁移历史 v3.3–v3.6 Plan；
- 修改与本报告无关的 Domain、Telemetry、Pilot 或 Benchmark 能力。

# 5. Frozen Invariants

v5.0.3 不得改变以下不变量：

1. Canonical Stage PRD 唯一；
2. Canonical Plan 唯一；
3. `smc-plan-delivery` 是唯一 governed delivery orchestrator；
4. Static PASS 不等于 Implementation Complete；
5. Todo Complete 不等于 Plan Proven；
6. Completion Audit 独立；
7. Implementation Review 独立；
8. Blocking Verification 必须 fresh PASS；
9. 内容变化使绑定的旧 proof stale；
10. `post_review` commit boundary 不变；
11. Roadmap DONE 晚于 implementation commit；
12. Single Writer / ownership-aware slicing 不变；
13. Production skip-gates 禁止；
14. Blocking failure integrity 不变；
15. LIVE Environment / Candidate provenance 不变；
16. TDD RED 不属于 Final Verification FAIL；
17. Engineering Method artifact 仍是 working memory；
18. LEAN 不得削弱 Delivery Truth；
19. 外部 Runtime 输出是不可信提案，不是治理真值；
20. Provider 不可用、超时、版本未知或输出不合法时必须显式降级或阻断，不能伪装成功；
21. 外部 provider 不能创建第二 `.specify/spec.md`、Plan、Task Ledger 或 Delivery Ledger；
22. Pilot / Benchmark 必须保持 `NOT_EXECUTED`。

# 6. Change Classification

| Change ID | Priority | Capability | Action | Canonical Owner |
|---|---:|---|---|---|
| C01 | P0 | Rollback Path Confinement | MODIFY | installer / rollback suite |
| C02 | P0 | Work Facts Trust Boundary | MODIFY | canonical Work Router |
| C03 | P0 | Repository Protection Evidence | MODIFY | repo governance verifier |
| C04 | P1 | Transactional Install Receipt | MODIFY | installer suite |
| C05 | P1 | Mandatory v3.7 Intent Binding | MODIFY | Plan seed / validator |
| C06 | P1 | Spec Kit Front UX Adapter | ADD + MODIFY | `smc-prd-grounding` |
| C07 | P1 | Superpowers Method Provider | ADD + MODIFY | `smc-plan-delivery` |
| C08 | P2 | Naming / Version / UX Closure | MODIFY | Work Router + routing docs |

# 7. 三段式目标架构

## 7.1 前半程：Spec Kit UX Provider

Spec Kit 只参与问题澄清、检查清单与跨字段一致性分析，输出受限 Proposal Envelope。

```text
User Request + Bound Work Facts + Source Context
                    ↓
         Spec Kit UX Provider（可选）
                    ↓
      smc.ges.ux-proposal.v1（working memory）
                    ↓
        smc-prd-grounding validate/import
                    ↓
             Canonical Stage PRD
```

## 7.2 中间：Superpowers Method Provider

Superpowers 只提供工程方法和任务执行策略；GES 负责上下文裁剪、写权限、状态转移和验证。

```text
Canonical Plan Todo + Source Capsule + Method Policy
                    ↓
      Superpowers Method Provider（可选）
                    ↓
    bounded result / TDD-debug events / task review
                    ↓
          GES method gate + workspace guard
                    ↓
            GES Delivery State transition
```

## 7.3 后半程：GES Delivery Truth

以下能力只允许 GES canonical owner 写入：

```text
Plan runtime status
Completion Audit verdict
Whole-diff Implementation Review verdict
Blocking Verification evidence
IMPLEMENTED_AND_PROVEN
post_review implementation commit
Roadmap DONE
Install / rollback truth
```

# 8. C01 — Rollback Path Confinement

## 8.1 Threat Model

`upgrade-manifest.json`、`--backup` 参数和备份目录内容都视为不可信输入。

攻击面至少包括：

```text
../escape
..\escape
/absolute/path
C:\absolute\path
\\server\share\path
mixed/separators\..\escape
symlink or junction parent escape
empty / dot / project-root target
duplicate normalized targets
backup source escape
```

`--force` 只能允许覆盖 post-install drift，永远不能绕过路径约束。

## 8.2 Canonical Resolver

新增唯一的 rollback path resolver；所有 preflight、hash、restore、unlink 和 backup source 查找都必须调用它。

输入必须满足：

1. 类型为非空字符串；
2. 使用 package-relative logical path；
3. 不是 absolute、drive-qualified 或 UNC；
4. normalized segment 不含 `.`、`..` 或空段；
5. resolved target 位于 `project.resolve()` 内部且不等于 project root；
6. resolved backup source 位于选定 backup root 内部且不等于 backup root；
7. Windows 比较采用 case-normalized resolved path；
8. 已存在的 symlink/junction 与不存在叶子的既有父目录都要做 containment 验证；
9. 同一 normalized target 只允许出现一次。

在任何文件系统写入前必须一次性验证全部 records。发现一个非法 record，整个 rollback 退出且零副作用。

## 8.3 Backup Boundary

默认和显式 `--backup` 都必须位于：

```text
<project>/.smc/skill-upgrade-backups/<transaction-id>/
```

若需要支持离线备份导入，必须先复制并校验到该目录，不允许 rollback 直接信任任意外部目录。

## 8.4 Failure Codes

```text
ROLLBACK_MANIFEST_INVALID
ROLLBACK_PATH_INVALID
ROLLBACK_PATH_ESCAPE
ROLLBACK_BACKUP_ESCAPE
ROLLBACK_DUPLICATE_TARGET
ROLLBACK_SYMLINK_ESCAPE
```

错误输出可以显示 logical path，但不得把未净化字符串插入 shell 命令。

## 8.5 Acceptance Criteria

```text
C01-AC01 ../victim、absolute、drive、UNC 全部 fail-closed
C01-AC02 symlink/junction escape fail-closed
C01-AC03 existed_before true/false 两条路径均受同一 resolver 保护
C01-AC04 --force 不绕过 containment
C01-AC05 任一 record 非法时零文件被复制、覆盖或删除
C01-AC06 合法安装事务仍可 dry-run、apply 并恢复原字节
```

# 9. C02 — Work Facts Trust Boundary

## 9.1 Complete Facts Contract

`smc.ges.work-facts.v1` 的 production envelope 必须包含 Router 所有 canonical facts，值只能为 boolean 或合同明确允许的 enum。

每一个事实必须有同名 provenance；禁止用一个无关字段的 provenance 为整个 envelope 授权。

```text
facts.keys == required_fact_keys
provenance.keys == facts.keys
unknown fact/provenance key = INVALID
missing fact/provenance key = UNBOUND
```

每个 provenance 至少包含：

```json
{
  "source_kind": "ROADMAP|FEATURE|PRD|PLAN|ORCHESTRATOR_REQUEST|DERIVED",
  "source_ref": "repo-relative path or immutable request id",
  "source_sha256": "sha256:...",
  "authority": "CANONICAL|ORCHESTRATOR|DERIVED",
  "derivation": "optional stable rule id"
}
```

`DERIVED` 必须引用可验证父事实，不能独立证明 `governed=false` 或所有生产风险为 false。

## 9.2 Source Freshness Is Mandatory

Production `route_bound` 必须显式接收 canonical repo root，并调用：

```text
verify_envelope(envelope, repo=<resolved repo>)
```

repo-relative `source_ref` 必须使用与 C01 同等级的 containment helper。源缺失、hash 改变、路径越界或 repo 未提供时，不得返回 `VERIFIED`。

`ORCHESTRATOR_REQUEST` 若不是文件，必须绑定 immutable request id + canonical serialized request SHA；空 `source_ref` 或空 SHA 不可授权 NONE。

## 9.3 Monotonic Conservative Merge

风险、生产和 governed facts 使用 lattice merge：

```text
true > unknown > false
```

任一来源为 `true`，合并结果必须为 `true`。verified envelope 的 `false` 不得覆盖调用者、canonical artifact scan 或 previous route 中的 `true`。

事实发生权威冲突时：

```text
WORK_FACTS_CONFLICT
→ FULL
```

不得选择更低治理级别。

## 9.4 Production API Boundary

保留 `route(facts)` 仅用于 library compatibility 和确定性单测；它不能产生 production `NONE` receipt。

生产入口只能调用：

```text
route_bound(repo, work_facts, previous_profile, caller_facts)
```

生产结果必须记录：

```text
facts_digest
authority_status=VERIFIED
repo_identity
source_digest_set
merge_decisions
governance_profile
reason_codes
```

## 9.5 Acceptance Criteria

```text
C02-AC01 每个 canonical fact 都有同名 provenance
C02-AC02 unrelated provenance 不能授权 governed=false
C02-AC03 源字节变化后 route_bound 返回 STALE/FULL
C02-AC04 route_bound 缺 repo 时 fail-closed
C02-AC05 caller true + envelope false 的结果仍为 true
C02-AC06 conflicting authority 只能 FULL
C02-AC07 raw route() 不能产 production NONE receipt
C02-AC08 v1 envelope 兼容读取但未补全时不得 NONE
```

# 10. C03 — Repository Protection Evidence

## 10.1 No Positive Defaults

Verifier 必须遵循：

```text
missing != true
protected=true != required checks present
ruleset name match != target master
HTTP success != governance PASS
```

任何缺失字段都保持 `MISSING/UNKNOWN`，禁止自动补成 required checks、force push blocked、deletion blocked 或 direct update restricted。

## 10.2 Canonical Evidence Schema

新增或固化 `smc.repo.protection-evidence.v1`：

```json
{
  "schema": "smc.repo.protection-evidence.v1",
  "source": "GITHUB_API|OFFLINE_FIXTURE",
  "repository": "owner/name",
  "repository_id": 0,
  "branch": "master",
  "ruleset_id": 0,
  "ruleset_target": "branch",
  "enforcement": "active",
  "include_refs": ["refs/heads/master"],
  "require_pr": true,
  "required_checks": ["validate", "GES Package Gate / validate-package"],
  "force_push_blocked": true,
  "deletion_blocked": true,
  "direct_update_restricted": true,
  "bypass_actors": [],
  "fetched_at": "RFC3339",
  "raw_evidence_sha256": "sha256:..."
}
```

API 模式必须解析 ruleset detail 中的实际 rule types、parameters、conditions 和 bypass actors，不能通过 JSON 文本包含某个单词来推断。

## 10.3 Verdicts

只允许：

```text
REPO_GOVERNANCE_PASS
REPO_GOVERNANCE_DRIFT
REPO_GOVERNANCE_UNAVAILABLE
REPO_GOVERNANCE_INVALID_EVIDENCE
```

无 Token、403、404、rate limit、schema 漂移、字段缺失和 stale evidence 都不能 PASS。

Offline fixture 只用于 deterministic test；除非带有可信来源与 freshness policy，否则不得用于发布级 live claim。

## 10.4 Operational Closure

代码级 verifier closure 与 GitHub 实际 Ruleset activation 分开记录：

```text
verifier_implementation = PASS|FAIL
live_master_protection = PASS|DRIFT|UNAVAILABLE
```

没有 GitHub 凭据时允许前者完成，但总体不得宣称 `REPOSITORY_GOVERNANCE_CLOSED`。

## 10.5 Acceptance Criteria

```text
C03-AC01 只有 protected=true 的残缺证据必须 INVALID/DRIFT
C03-AC02 缺 required checks 不自动补齐
C03-AC03 缺 force/deletion/direct-update 字段不自动补 true
C03-AC04 ruleset 未 target master 时 DRIFT
C03-AC05 inactive/evaluate ruleset 不等于 active
C03-AC06 bypass actor 被显式报告并按 policy 裁决
C03-AC07 API unavailable 永不 PASS
C03-AC08 live claim 必须绑定 fresh API evidence
```

# 11. C04 — Transactional Install Receipt

## 11.1 Required Property

Install Receipt 是成功安装证明；只要安装最终没有 PASS，Consumer 中就不能留下本次安装的 immutable receipt、兼容指针或引用它的 lock。

## 11.2 Transaction-Owned Writes

以下写入必须统一经过 installer transaction helper：

```text
.smc/ges-install-receipts/<install_id>.json
.smc/ges-install-receipt.json
.smc/ges-install-lock.json
```

每次写入前必须调用 `record_before`，记录：

```text
path
existed_before
original_sha256
installed_sha256
```

失败恢复必须删除本次新建文件或恢复先前字节。不得在 transaction records 之外直接 `write_text`。

## 11.3 Atomic Finalization

固定顺序：

```text
1. package/profile/domain preflight
2. transactional overlay
3. deterministic post-install validation PASS
4. stale ownership reconciliation
5. build receipt bytes in memory
6. transactional atomic write immutable receipt
7. transactional atomic write compatibility pointer
8. transactional atomic write install lock
9. finalize transaction journal PASS
```

步骤 6–9 任一步失败必须恢复 6–8 的全部写集。Atomic write 使用同目录临时文件 + replace，并确保临时文件也被清理。

Receipt 一旦 finalization 成功不可原地改写；重复 install id 必须报冲突。

## 11.4 Failure Injection Tests

必须在每个边界注入异常：

```text
after immutable receipt
after compatibility pointer
before lock write
after lock write
before journal PASS
```

每次都断言安装前字节完全恢复，且不存在本次成功凭据。

## 11.5 Acceptance Criteria

```text
C04-AC01 receipt/pointer/lock 全部进入 transaction records
C04-AC02 lock 写失败不残留 receipt 或 pointer
C04-AC03 journal finalization 失败不残留成功凭据
C04-AC04 既有 receipt/pointer/lock 可恢复原字节
C04-AC05 新文件失败时被删除
C04-AC06 successful install 仍生成 immutable receipt-bound lock
```

# 12. C05 — Mandatory v3.7 Intent Binding

## 12.1 v3.7 Minimum Binding

所有 `smc.plan.v3.7`，无论 Domain Pack 是否激活，都必须包含：

```text
source_prd
source_prd_sha256
Domain Intent Binding section
domain_activation_digest
domain_intent_digest
```

没有激活 Domain Pack 时也必须写入 canonical empty intent digest 和 `activation=NONE`，不能靠字段全部省略表示无 Domain。

全部缺失、部分缺失、空值和 placeholder 都必须是 hard error。

## 12.2 Seed Generation

v3.7 seed generator 必须在生成阶段完成绑定。任何 import、PRD parse、Domain runtime、digest 或 binding generation 异常都必须：

```text
PLAN_SEED_BINDING_GENERATION_FAILED
```

禁止 `except Exception: pass`。错误必须带 phase 与安全净化后的原因，不得生成看似可用但未绑定的 Plan。

## 12.3 Migration

已有缺 binding 的 v3.7 Plan 必须通过 Plan Author 的显式 repair 命令重新绑定当前 Approved PRD，并重新进入 static + semantic review。

禁止：

```text
--skip-binding
validator warning-only
Delivery 自动猜测 PRD
沿用 stale review/evidence
```

v3.3–v3.6 继续按各自既有合同读取，不被机械升格为 v3.7。

## 12.4 Acceptance Criteria

```text
C05-AC01 v3.7 全字段缺失 hard fail
C05-AC02 任一 binding 字段缺失 hard fail
C05-AC03 no-domain Plan 仍绑定 canonical empty intent
C05-AC04 source PRD 改变后 Plan stale
C05-AC05 domain activation/intent 改变后 Plan stale
C05-AC06 seed generation 异常立即 fail，不落残缺 Plan
C05-AC07 repaired v3.7 必须重新 review，旧 proof stale
```

# 13. C06 — Spec Kit Front UX Adapter

## 13.1 Integration Decision

v5.0.3 允许 Spec Kit 作为可选 UX provider，但不允许其拥有 Canonical Artifact。

支持三种明确状态：

```text
NATIVE_ONLY
ADAPTER_READY
EXTERNAL_VERIFIED
```

只有完成真实 capability probe、真实 provider dispatch 和合法结果导入后，才允许 `EXTERNAL_VERIFIED`。仅出现 `inspired by Spec Kit`、存在模板或 mock test 时最多为 `ADAPTER_READY`。

## 13.2 Provider Probe

Probe 必须只读、离线优先，并记录：

```text
provider=spec-kit
executable identity
version
feature set
agent integration/skill availability
probe command
probe exit code
stdout digest
probed_at
```

`specify version --features --json` 可用于 CLI capability discovery。Probe 不得运行 `init`、写 `.specify/` 或联网自更新。

## 13.3 Allowed Capability Scope

允许：

```text
clarify
checklist
analyze consistency
```

禁止：

```text
specify → 生成第二 requirement SOT
plan → 生成第二 Plan
tasks → 生成第二 Todo Ledger
implement → 绕过 smc-plan-delivery
converge → 直接写 Delivery truth
```

若官方 capability 不能在不创建第二 SOT 的条件下运行，adapter 必须在隔离临时 workspace 中运行，并只导入结构化 Proposal Envelope；临时 workspace 不得位于 Consumer root，结束后按安全清理策略处理。

## 13.4 UX Proposal Contract

外部输出转换为 `smc.ges.ux-proposal.v1`：

```json
{
  "schema": "smc.ges.ux-proposal.v1",
  "provider": "spec-kit",
  "provider_version": "...",
  "capability": "clarify|checklist|analyze",
  "work_item_id": "...",
  "source_prd": "...",
  "source_prd_sha256": "sha256:...",
  "work_facts_digest": "sha256:...",
  "questions": [],
  "decisions": [],
  "consistency_findings": [],
  "proposed_patch": [],
  "result_digest": "sha256:..."
}
```

该文件只存于：

```text
.smc/runs/<work_item_id>/ux/
```

它是 working memory，不进入 Canonical Artifact 集合。`smc-prd-grounding` 必须逐项验证并由 canonical writer 应用到同一 Stage PRD。

## 13.5 Context Budget

Provider 输入只包含：

```text
bounded user objective
Bound Work Facts summary
current Stage PRD relevant sections
minimal source anchors
open clarification ledger
```

禁止默认发送完整 repository、完整对话历史、完整 Plan/Delivery evidence。相同 source digest 的 clarification context 可复用，避免重复扫描。

## 13.6 Fallback

Provider 不存在或不兼容时：

```text
provider_status=UNAVAILABLE
integration_status=NATIVE_ONLY
```

GES 原生 clarify 流程可以继续，但不得宣称使用了 Spec Kit。Provider 输出 malformed/stale/conflicting 时，不自动降级应用，返回 `SPEC_KIT_RESULT_INVALID|STALE|CONFLICT`。

## 13.7 Acceptance Criteria

```text
C06-AC01 probe 不修改 Consumer root
C06-AC02 真实外部调用才可 EXTERNAL_VERIFIED
C06-AC03 provider 不能创建第二 PRD/Plan/Task SOT
C06-AC04 proposal 绑定 PRD + Work Facts 当前字节
C06-AC05 stale/malformed proposal 不能导入
C06-AC06 canonical writer 是 smc-prd-grounding
C06-AC07 unavailable 时 native fallback 明确且不虚报
C06-AC08 context packet 有稳定预算和复用规则
```

# 14. C07 — Superpowers Method Provider

## 14.1 Correct Integration Layer

Superpowers 在 GES 中是 method provider，不是 parallel delivery orchestrator。

接入至少覆盖以下能力映射：

```text
executing-plans
subagent-driven-development
test-driven-development
systematic-debugging
verification-before-completion
```

每个 vendored/adapted/external skill 必须记录：

```text
upstream repository
upstream commit or release
upstream file path
upstream sha256
local adaptation sha256
license
adaptation notes
capability id
```

没有该 provenance 时只能称为 `SUPERPOWERS_INSPIRED`，不能称为 verified integration。

## 14.2 Provider States

```text
GES_NATIVE
UPSTREAM_PINNED
EXTERNAL_VERIFIED
UNAVAILABLE
INCOMPATIBLE
```

Package 内经过 provenance 固定和 conformance test 的 method pack 可达到 `UPSTREAM_PINNED`。真实外部 skill/runtime dispatch 有版本和结果 receipt 时才达到 `EXTERNAL_VERIFIED`。

## 14.3 Dispatch Contract

由 `smc-plan-delivery` 构造最小任务包：

```text
plan_id
plan_semantic_hash
todo_id
write ownership
read scope
source context capsule ids
engineering method policy
required TDD/debug gates
focused verification command
forbidden state writes
```

Provider 返回：

```text
changed path/symbol summary
focused test result
TDD/debug event refs
task review findings
scope exceptions
provider/version/capability receipt
```

返回值不直接改变 Todo 或 Delivery State；GES controller 必须独立复核 workspace、method gates 和 result binding。

## 14.4 Forbidden Provider Writes

Provider 对以下路径/状态无写权限：

```text
canonical Plan structure or Todo identity
Delivery State ledger
Completion Audit verdict
Implementation Review verdict
Final Evidence verdict
implementation commit
Roadmap status
install/rollback receipt
```

检测到越权写入必须 `DELIVERY_SCOPE_DRIFT` 或更强阻断，不能因为 provider 自报成功而继续。

## 14.5 Freshness and Completion

Method result 必须绑定：

```text
provider identity
plan semantic hash
method epoch
owned-source fingerprint
test fingerprint
result digest
```

任何绑定对象变化都使 result stale。官方 `verification-before-completion` 可作为方法层检查，但最终 fresh PASS Evidence 仍只能由 GES evidence wrapper 签发。

## 14.6 Acceptance Criteria

```text
C07-AC01 method pack 有 upstream/version/license/checksum provenance
C07-AC02 external dispatch 有真实 provider receipt
C07-AC03 provider 不能推进 Delivery State
C07-AC04 out-of-scope write 被 workspace guard 阻断
C07-AC05 provider 自报 PASS 不能替代 GES final evidence
C07-AC06 stale method result 不能完成 Todo
C07-AC07 native fallback 与 external mode 结果状态可区分
C07-AC08 smc-plan-delivery 保持唯一 orchestrator
```

# 15. C08 — Naming、Version 与 UX Closure

## 15.1 Canonical Work Router Name

当前 GES `using-superpowers` 实际是 Work Router，而官方 Superpowers 同名 skill 是 skill-discovery 入口，两者语义冲突。

新增 canonical 名称：

```text
smc-work-router
```

迁移策略：

- 将 Work Facts、routing contract 与 production CLI 的 canonical owner 移到 `smc-work-router`；
- `using-superpowers` 保留一个 release 的 compatibility shim，只做无状态委派；
- shim 必须明确输出 deprecated warning；
- shim 不得复制 router 业务逻辑；
- 安装 profile、文档和内部引用改用 `smc-work-router`；
- 与官方 Superpowers provider 的资产必须放在单独 integration/method-provider namespace。

## 15.2 Plan Version Canonicalization

所有“Approved PRD, no Plan”路由必须指向：

```text
canonical smc.plan.v3.7
```

v3.6 只描述为 existing in-flight compatibility。文档、router 输出、seed generator、validator dispatcher 和测试 fixture 必须一致。

## 15.3 Capability Claim Vocabulary

文档只允许以下术语：

```text
INSPIRED       方法借鉴，无上游身份或调用证据
ADAPTER_READY  接口和 deterministic conformance 完成，未真实调用外部 provider
UPSTREAM_PINNED 已固定上游 skill bytes 并通过 conformance
EXTERNAL_VERIFIED 已真实调用外部 provider 并保存 receipt
```

不得用 `integrated` 同时表达上述四种不同状态。

## 15.4 Acceptance Criteria

```text
C08-AC01 新 Plan 路由只输出 v3.7
C08-AC02 v3.6 仅保留兼容语义
C08-AC03 using-superpowers shim 无重复业务逻辑
C08-AC04 GES Work Router 与官方 Superpowers skill 不再同名混淆
C08-AC05 README/Skill/lat/changes 使用统一 claim vocabulary
```

# 16. Cross-Cutting Failure Semantics

所有外部输入和治理证明遵循四态，不允许 boolean 模糊化：

```text
VERIFIED
UNAVAILABLE
STALE
INVALID / CONFLICT
```

通用规则：

```text
UNAVAILABLE != PASS
MISSING != false
MISSING != true
STALE != reusable
provider self-report != GES truth
--force != skip security boundary
```

新增或固化错误码：

```text
ROLLBACK_PATH_INVALID
ROLLBACK_PATH_ESCAPE
ROLLBACK_BACKUP_ESCAPE
ROLLBACK_DUPLICATE_TARGET
ROLLBACK_SYMLINK_ESCAPE

WORK_FACTS_FIELD_MISSING
WORK_FACTS_PROVENANCE_MISSING
WORK_FACTS_SOURCE_PATH_INVALID
WORK_FACTS_REPO_REQUIRED
WORK_FACTS_STALE
WORK_FACTS_CONFLICT

REPO_GOVERNANCE_INVALID_EVIDENCE
REPO_GOVERNANCE_DRIFT
REPO_GOVERNANCE_UNAVAILABLE

INSTALL_RECEIPT_TRANSACTION_ROLLBACK
INSTALL_RECEIPT_ALREADY_EXISTS
INSTALL_FINALIZATION_FAILED

PLAN_SOURCE_PRD_MISSING
PLAN_SOURCE_PRD_STALE
PLAN_DOMAIN_INTENT_BINDING_MISSING
PLAN_DOMAIN_INTENT_STALE
PLAN_SEED_BINDING_GENERATION_FAILED

SPEC_KIT_UNAVAILABLE
SPEC_KIT_INCOMPATIBLE
SPEC_KIT_RESULT_INVALID
SPEC_KIT_RESULT_STALE
SPEC_KIT_RESULT_CONFLICT

SUPERPOWERS_PROVIDER_UNAVAILABLE
SUPERPOWERS_PROVIDER_INCOMPATIBLE
SUPERPOWERS_RESULT_INVALID
SUPERPOWERS_RESULT_STALE
SUPERPOWERS_SCOPE_VIOLATION
```

已有稳定错误码若语义等价应保留 alias，一个 release 后再由 Release Review 决定移除。

# 17. Required Files / Source Anchors

## C01

```text
MODIFY engineeing-skills/rollback.py
ADD/MODIFY rollback traversal + symlink + failure atomicity tests
```

## C02 / C08

```text
ADD    engineeing-skills/.agents/skills/smc-work-router/
MOVE/SHIM engineeing-skills/.agents/skills/using-superpowers/
MODIFY work_facts.py
MODIFY work_router.py
MODIFY test_work_facts.py
MODIFY test_work_router.py
MODIFY package profiles and routing references
```

物理移动可以由实现 Plan 决定；若为降低风险选择暂不移动文件，canonical namespace 和 compatibility shim 语义仍必须成立。

## C03

```text
MODIFY engineeing-skills/acceptance/verify_repository_protection.py
MODIFY tools/check_repo_governance.py
ADD    strict evidence fixtures and negative tests
```

Repo-level checker 可以保留在 `tools/`，但 `engineeing-skills` package 必须携带消费者可用的 schema/validator 或明确声明 C03 为 repository-level external gate。

## C04

```text
MODIFY engineeing-skills/install_v500.py
MODIFY shared transaction helper only when no duplicate installer owner is created
ADD    install finalization failure-injection tests
```

## C05

```text
MODIFY create_plan_seed_v37.py
MODIFY validate_plan_v37.py
MODIFY v3.7 seed/validator tests
ADD    explicit v3.7 binding repair command only if required
```

## C06

```text
ADD engineeing-skills/integrations/spec-kit/provider.json
ADD engineeing-skills/integrations/spec-kit/probe/import/conformance tooling
ADD engineeing-skills/integrations/spec-kit/result schema
MODIFY smc-prd-grounding Skill and clarification contract
ADD isolated provider fixtures and integration tests
```

最终目录名可在 Plan 中调整，但 provider manifest、result schema、probe、import validator 和 tests 不得省略。

## C07

```text
ADD engineeing-skills/integrations/superpowers/provider.json
ADD upstream provenance / adaptation map / license record
ADD provider result schema and conformance tests
MODIFY smc-plan-delivery provider dispatch and method gates
MODIFY executing-plans / subagent-driven-development provenance docs
```

## C08 Documentation

```text
MODIFY artifact-state-routing.md: v3.6 → v3.7 for new Plan
MODIFY README / CHANGES / Skill docs
ADD lat.md v5.0.3 architecture section
```

# 18. Deterministic Test Strategy

测试必须调用真实 production function/CLI 并断言退出码、错误码、文件系统副作用和状态不推进。

禁止：

```text
仅 grep source
仅 callable()
仅 import 成功
只测 happy path
把 mock provider 调用标成 EXTERNAL_VERIFIED
```

## 18.1 Security Regression Corpus

至少覆盖：

```text
R01 ../ rollback delete attempt
R02 Windows drive / UNC rollback path
R03 symlink/junction rollback escape
R04 one invalid record among valid records => zero mutation
R05 incomplete Work Facts provenance
R06 mutated Work Facts source through route_bound
R07 caller true overridden by envelope false attempt
R08 minimal repository protection evidence false-positive attempt
R09 receipt written then lock failure
R10 pointer written then lock failure
R11 v3.7 all bindings absent
R12 seed digest provider exception
R13 stale Spec Kit proposal import
R14 Superpowers provider writes outside Todo ownership
R15 provider self-reported PASS without GES evidence
```

## 18.2 Provider Conformance

Spec Kit 和 Superpowers 分别需要：

```text
malformed output
unknown version
unsupported capability
timeout
non-zero exit
stale input digest
scope violation
unavailable provider
valid isolated result
```

Mock/fake provider 证明 adapter correctness；至少一次 pinned external/provider fixture 证明真实接入。两者证据必须分开，不能用 mock 替代 external receipt。

## 18.3 Delivery Frozen Regression

必须重跑：

```text
Plan v3.3–v3.6 compatibility
Plan v3.7 normal binding
workspace ownership and scope drift
TDD/debug freshness
Completion Audit
whole-diff Implementation Review
Final Evidence freshness
post_review commit boundary
separate Roadmap DONE
installer install + rollback normal path
package manifest integrity
```

Pilot / Benchmark 测试和结果生成不在本测试策略中。

# 19. Minimum Validation Chain

实现完成后至少运行：

```bash
python engineeing-skills/build_package_manifest.py --check
python -m pytest -q
python engineeing-skills/validate_package.py
lat check
git diff --check
```

另需显式运行：

```text
rollback security suite
Work Facts trust-boundary suite
repository protection strict-evidence suite
installer finalization failure-injection suite
v3.7 binding and seed-failure suite
Spec Kit adapter conformance suite
Superpowers provider conformance suite
Delivery frozen regression suite
```

若 `validate_package.py` 内部运行既有 Benchmark algorithm self-test，报告必须标注：

```text
algorithm self-test only
Benchmark remains NOT_EXECUTED
```

# 20. Implementation Sequence

固定顺序：

```text
Phase 0  Freeze source revision and preserve unrelated dirty bytes
Phase 1  C01 Rollback containment
Phase 2  C02 Work Facts provenance/freshness/merge
Phase 3  C03 strict repository evidence parser
Phase 4  C04 transactional receipt finalization
Phase 5  C05 mandatory v3.7 binding + seed diagnostics
Phase 6  C08 canonical smc-work-router + v3.7 UX docs
Phase 7  C06 Spec Kit UX adapter
Phase 8  C07 Superpowers method provider
Phase 9  Full deterministic/frozen regression
Phase 10 Update lat.md and release/change documentation
Phase 11 Regenerate PACKAGE-MANIFEST.json and SHA256SUMS once
Phase 12 Independent PRD/implementation review
```

不得出现 Pilot / Benchmark Phase。

# 21. Migration and Compatibility

## 21.1 Work Router

`using-superpowers` 作为兼容 shim 保留一个 release；canonical caller 迁移到 `smc-work-router`。生产 NONE 必须重新绑定完整 Work Facts。

## 21.2 Existing Work Facts

旧 envelope 可读取，但缺全字段 provenance 或 repo freshness 时只能 fail-closed 路由为 FULL，不自动伪造 provenance。

## 21.3 Existing v3.7 Plan

缺 binding 的 v3.7 Plan 必须显式 repair + review。修复工具不得替用户决定 Domain Intent。

## 21.4 Existing v3.3–v3.6 Plan

保持既有 validator；不得因为新文档统一为 v3.7 而批量重写在途 Plan。

## 21.5 Existing Receipts and Locks

旧 receipt/lock 继续只读验证和安全 rollback。下一次成功安装产生 transaction-owned receipt。旧凭据缺字段时不得补写为新 schema。

## 21.6 Provider Absence

未安装 Spec Kit/Superpowers 时 GES 原生路径继续工作，状态明确为 `NATIVE_ONLY` / `GES_NATIVE`。不得自动联网安装。

# 22. Security and Privacy

```text
- 所有 repo-relative path 必须 resolve + contain；
- 外部 provider 在最小权限、最小上下文下运行；
- provider input/output 不记录 secrets、完整 prompt 或无关源码；
- receipt 记录摘要、版本、能力和结果，不记录凭据；
- GitHub token 只能从环境/secret 获取；
- 外部工具不可修改 Canonical Artifact，导入由 canonical owner 完成；
- provider 临时 workspace 不得位于 Consumer root；
- temporary cleanup 也必须通过受限路径 helper；
- `--force` 不能绕过任何 trust boundary；
- 未知版本、未知字段、未知状态一律 fail-closed。
```

# 23. PRD Acceptance Criteria

```text
AC01 rollback traversal/absolute/UNC/symlink 全部被阻断
AC02 rollback 非法 manifest 零副作用

AC03 Work Facts 全字段 provenance 强制
AC04 production route 强制 repo/source freshness
AC05 risk/production/governed facts true-wins
AC06 raw facts 不能生成 production NONE receipt

AC07 repository verifier 无正向默认值
AC08 incomplete evidence 不能 PASS
AC09 unavailable live API 不被误报为 closed

AC10 receipt/pointer/lock 纳入同一事务
AC11 finalization 任一步失败恢复安装前字节
AC12 成功安装仍生成 immutable receipt-bound lock

AC13 所有 v3.7 Plan 强制 PRD + Domain Intent Binding
AC14 no-domain v3.7 使用 canonical empty binding
AC15 seed 异常立即失败且不落残缺 Plan

AC16 Spec Kit probe/result/import contract 可执行
AC17 只有真实 external receipt 才可 EXTERNAL_VERIFIED
AC18 Spec Kit 不创建或拥有第二 SOT

AC19 Superpowers method pack 有上游 provenance
AC20 provider 结果绑定 Plan/method/source 当前状态
AC21 provider 不能推进 GES Delivery State
AC22 provider PASS 不能替代 Final Evidence

AC23 canonical Work Router 命名不再与官方 using-superpowers 混淆
AC24 新 Plan 文档、router、seed、validator 全部统一 v3.7
AC25 Package Manifest 与最终 package bytes 一致
AC26 full deterministic regression PASS
AC27 lat check PASS

AC28 Consumer Pilot 保持 NOT_EXECUTED
AC29 Cost Benchmark 保持 NOT_EXECUTED
AC30 BASELINE.md 未 promotion
```

# 24. Definition of Done

```text
[ ] C01–C08 implementation complete
[ ] C01–C08 deterministic tests complete
[ ] 全部 P0 adversarial reproducer 从成功攻击变为明确阻断
[ ] rollback normal install/restore regression PASS
[ ] Work Facts production NONE trust boundary PASS
[ ] repository incomplete-evidence negative suite PASS
[ ] receipt failure-injection matrix PASS
[ ] v3.7 binding missing/partial/stale matrix PASS
[ ] Spec Kit adapter conformance PASS
[ ] Spec Kit integration status accurately recorded
[ ] Superpowers provider provenance/conformance PASS
[ ] Superpowers integration status accurately recorded
[ ] GES Delivery frozen regressions PASS
[ ] PACKAGE-MANIFEST/SHA256SUMS 最终生成且 check PASS
[ ] validate_package.py PASS
[ ] lat.md updated and lat check PASS
[ ] independent PRD review PASS
[ ] independent implementation whole-diff review PASS
[ ] Pilot status remains NOT_EXECUTED
[ ] Benchmark status remains NOT_EXECUTED
[ ] BASELINE.md unchanged
```

以下不构成本 PRD DONE 条件，也禁止在本轮执行：

```text
3 Consumer / 12 Delivery Pilot
4.4.1 vs 5.x Benchmark
Token/Cost benefit threshold
Pilot/Benchmark release verdict
Accepted Baseline Promotion
```

# 25. Target State After v5.0.3

```text
Security Correctness:
  rollback confinement               CLOSED
  Work Facts trust boundary          CLOSED
  repository evidence false PASS     CLOSED
  install receipt orphan             CLOSED
  v3.7 binding bypass                CLOSED

Runtime Architecture:
  Spec Kit front UX adapter          ADAPTER_READY or EXTERNAL_VERIFIED
  Superpowers method provider        UPSTREAM_PINNED or EXTERNAL_VERIFIED
  GES delivery truth ownership       UNCHANGED / VERIFIED

Operational Evidence:
  live master protection             PASS|DRIFT|UNAVAILABLE, never inferred
  Consumer Pilot                     NOT_EXECUTED
  Cost Benchmark                     NOT_EXECUTED
  Accepted Baseline                  4.1.2 unchanged
```

若实现只达到 `ADAPTER_READY` 或 `UPSTREAM_PINNED`，可以完成对应 adapter contract，但发布说明必须准确使用这些状态，不能写成完整外部 Runtime 已验证。

# 26. Versioning Note

PRD 版本 `v5.0.3` 不等于 Bundle 必须为 `5.0.3`。

Release Review 必须按 `VERSIONING.md` 判断：

- C01–C05 correctness 修复本身至少要求 Bundle PATCH；
- C06/C07 provider contract 与 C08 canonical router 是向后兼容新增能力时，Bundle SHOULD 评估 MINOR；
- 若删除 `using-superpowers` 兼容入口、改变 Frozen Delivery State 或替换 Canonical Owner，则属于 MAJOR，本 PRD 禁止。

各 Skill 只在实际合同或行为改变时升版，禁止机械全量升版。

# 27. Clarification Ledger

| ID | Question | Decision | Status |
|---|---|---|---|
| Q01 | 本轮是否执行 Pilot？ | 否，固定 `NOT_EXECUTED`。 | CLOSED |
| Q02 | 本轮是否执行 Benchmark？ | 否，固定 `NOT_EXECUTED`。 | CLOSED |
| Q03 | Spec Kit 是否成为第二 PRD/Plan SOT？ | 否，只能输出受限 proposal，由 GES canonical writer 导入。 | CLOSED |
| Q04 | Superpowers 是否成为并行 Delivery Runtime？ | 否，只作为 versioned method provider，GES 保留所有状态与真值。 | CLOSED |
| Q05 | 外部 Runtime 不存在时是否阻断全部 GES？ | 否，允许明确的 native fallback，但不得虚报 external integration。 | CLOSED |
| Q06 | 无 GitHub Token 是否可声称 master 已保护？ | 否，只能 `UNAVAILABLE`。 | CLOSED |
| Q07 | `--force` 是否可跳过 rollback containment？ | 否。 | CLOSED |
| Q08 | v3.7 无 Domain 激活时能否省略 binding？ | 否，必须绑定 canonical empty intent。 | CLOSED |

# 28. Final Requirement

v5.0.3 完成后，GES 的三段式描述必须是可验证事实，而不是品牌或方法口号：

```text
Spec Kit improves front UX
  only when provider capability and invocation receipt prove it;

Superpowers improves middle execution
  only when upstream/provider provenance and bounded dispatch prove it;

GES preserves back delivery truth
  because no provider can bypass routing, binding, workspace, review,
  evidence, install or rollback fail-closed gates.
```

本轮最终报告必须再次明确：

```text
Pilot / Benchmark were not executed.
No effect or cost benefit was claimed.
```
