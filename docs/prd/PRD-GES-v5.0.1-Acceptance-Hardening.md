---
title: "GES Acceptance Hardening 工程方案 PRD"
prd_version: "v5.0.1"
work_item_id: "GES-AH-5.0.1"
status: "DRAFT"
review_verdict: "PENDING"
governance_profile: "FULL"
previous_governance_profile: "FULL"
source_revision: "loudon84/smc-delivery-governance@fc5dfcfe93f4f845c9d68eee413f778b0fd3ec0d"
grounded_commit: "fc5dfcfe93f4f845c9d68eee413f778b0fd3ec0d"
canonical_path: "engineeing-skills/"
current_bundle: "5.0.0-candidate"
accepted_baseline_bundle: "4.1.2"
target_release: "Acceptance Hardening Candidate"
commit_policy: "post_review"
---

# GES Acceptance Hardening 工程方案 PRD v5.0.1

> 项目：`loudon84/smc-delivery-governance`  
> 目标目录：`engineeing-skills/`  
> 当前源码基线：`master@fc5dfcfe93f4f845c9d68eee413f778b0fd3ec0d`  
> 当前 Bundle：GES `5.0.0 Candidate`  
> 当前 Accepted Baseline：Bundle `4.1.2` / Plan Contract `smc.plan.v3.3`  
> 本 PRD 版本：`v5.0.1`  
> 治理级别：`FULL`

---

## 0. 文档定位与版本说明

本 PRD 用于将当前 GES 5.0.0 从“架构已基本闭环、可进入 Pilot”的 Candidate，推进到可被公司接受为企业级工程治理基线的 **Acceptance Hardening** 阶段。

本 PRD 不重构现有核心治理架构，不改变 Frozen Invariants，不创建新的 PRD/Plan/Delivery Owner，不建立第二套交付状态机。所有工作围绕当前已经形成的三层体系进行可靠性、确定性、发布完整性和成本可观测性加固：

```text
Spec/Intent Layer
  PRD Grounding / Clarification / Domain Preplan
        ↓
Engineering Method Layer
  Source Context / TDD / Debug / Harness / Review
        ↓
GES Delivery Truth
  Audit / Review / Verification / Evidence / Commit / Roadmap
```

### 0.1 PRD 版本与 Bundle 版本必须分离

本文件版本固定为 `PRD v5.0.1`。

是否将最终 Bundle 发布为 `5.0.1`，必须在 Release Review 时按照 `engineeing-skills/VERSIONING.md` 决定：

- 如果所有变化被认定为 bug fix、false-positive/false-negative 修复、rollback/reliability hardening，且没有新增强制迁移，可发布为 `5.0.1`；
- 如果 `install-lock.v2`、Telemetry、Risk Facts 等被定义为新的向后兼容能力而不是纯 hardening，则 Bundle SHOULD 按版本策略发布为 `5.1.0`；
- 无论最终 Bundle SemVer 如何，本 PRD 版本仍保持 `v5.0.1`。

禁止为了满足版本号而弱化实际 contract/version 变化。

---

# 1. 背景与问题

当前 GES 5.0.0 已经具备较完整的企业 AI Coding 治理能力：

- 单一 Canonical PRD；
- 单一 Canonical Plan；
- `smc-plan-delivery` 独占 Delivery Truth；
- `LEAN/FULL` 自适应治理；
- Domain Pack v2；
- Frontend / Backend / Ops Preplan；
- React / Vue 前端工程治理；
- Engineering Method Runtime v2；
- TDD / Debug command-bound receipt；
- Todo completion deterministic interlock；
- Source Context Capsule；
- Adaptive Semantic Plan Review；
- Completion Audit；
- Whole Implementation Review；
- Final Verification；
- Evidence Freshness；
- `post_review` Commit；
- 独立 Roadmap DONE；
- Package Manifest / SHA256SUMS；
- Transactional Installer / Rollback。

但在进入 Accepted Baseline 前，仍存在六类高价值缺口：

1. **GES 自身仓库发布治理弱于 GES 对 Consumer 的要求**：`master` 尚未通过 branch protection + required package gate 强制保护。
2. **Work Router 的 `research_only` 仍可由调用方单字段自报**，存在错误进入 `SPIKE/NONE` 的风险。
3. **PRD / Plan / Review 的风险识别仍大量依赖 broad regex**，可能把 “No schema migration”等否定描述误判为高风险，导致不必要 FULL。
4. **Domain Preplan validator 主要验证 Markdown 表格结构完整**，对 Framework、Verification、Contract、Auth、Migration 等语义值缺少 deterministic 校验。
5. **Consumer Installer 缺少强 provenance 和旧 package-owned 文件自动对账**，无法严格证明两个 `bundle=5.0.0` Consumer 安装的是完全相同的字节集合。
6. **Harness 模型分层与 Token 优化缺少运行态 Telemetry**，当前只能证明“存在优化机制”，不能量化证明“节省了多少 Token / Reviewer / Turn”。

---

# 2. Objective

本 PRD 的目标是：

> 在不改变 GES Frozen Invariants 和 Canonical Ownership 的前提下，为 GES 5 系列补齐 Release Gate、Routing Trust、Structured Risk、Domain Semantic Validation、Installer Provenance、Harness Telemetry 六个 Acceptance Hardening 能力，并建立一套可重复执行的治理效果验证方法，使 GES 是否值得升级为 Accepted Baseline 可以通过工程证据而不是主观判断决定。

具体目标：

1. GES 自身 `master` 只能在 package integrity、full validation、tests 全部 PASS 后合并；
2. `research_only` 不再是可直接决定 `SPIKE/NONE` 的单一自报字段；
3. Risk Routing 以结构化事实为主，以文本扫描为 fallback/contradiction detector；
4. Domain Preplan 从“表格非空”升级到“表格结构 + 语义合法 + 条件关系合法”；
5. Consumer installation 可以精确回答“安装了哪个 release identity、哪些 package-owned files、哪些旧文件被安全删除”；
6. Harness 可以记录 requested tier、actual model、Token、retry、cache hit、reviewer seat 等，并用于 4.4.1 与 5.0 系列的真实成本 Benchmark；
7. 建立 Golden Corpus + Chaos Governance + Consumer Pilot + Cost Benchmark 四层 Acceptance Test；
8. 任何 hardening 都不能削弱当前 Delivery Truth。

---

# 3. Out of Scope

以下内容不属于本 PRD：

- 不改变 `smc-plan-delivery` 为唯一 Delivery Orchestrator；
- 不新增第二个 PRD、Plan 或 Delivery SOT；
- 不改变 `commit_policy: post_review`；
- 不取消 Completion Audit、Implementation Review、Final Verification；
- 不允许 LEAN 跳过 Final Delivery Truth；
- 不将 TDD RED 变成 Final Verification Evidence；
- 不把 Engineering working-memory 变成 durable final evidence；
- 不在 Core Governance 中写死 OpenAI / DeepSeek / Kimi / Claude 等 provider/model ID；
- 不引入向量数据库来解决 semantic duplicate code；
- 不在本轮重构所有旧 v3.3-v3.6 Plan；
- 不批量重写历史 Review / Evidence；
- 不让 Domain Pack 获得交付状态所有权；
- 不要求 Telemetry 缺失时阻塞正常产品交付；Telemetry 只对 Benchmark/Acceptance 完整性负责；
- 不把视觉审美、像素细节默认提升为 Blocking Governance。

---

# 4. Frozen Invariants

本 PRD 实施期间以下规则不可改变：

1. Canonical Plan 唯一；
2. Static PASS != implementation complete；
3. Todo completed != implemented-and-proven；
4. production `path#symbol` 只有一个 WRITE_OWNER；
5. Plan Author owns Todo id/content；
6. Delivery owns runtime status；
7. Completion Audit 独立于 Todo 自报；
8. Implementation Review 面向当前 whole Plan-owned diff；
9. Blocking Verification 必须 fresh PASS；
10. Content Change 必须使相关旧 proof stale；
11. `post_review` commit 必须晚于 Audit + Review + Verification + Freshness；
12. Roadmap DONE 必须晚于 implementation commit；
13. LIVE / FAULT / EXTERNAL 必须绑定 Scenario / Environment / Candidate；
14. Evidence reuse 必须显式 inheritance；
15. Domain Provider 不拥有 Delivery State；
16. Engineering Method artifact 仍为 working memory；
17. `TDD RED` 仍不是 Final Verification FAIL；
18. `DEBUG_ARCHITECTURE_ESCALATION` 三次失败规则保持；
19. Consumer-local skills/files 必须受到保护；
20. Production skip-gates 禁止。

---

# 5. Production Owner

本 PRD 不建立新的顶层 Owner。各 Change 继续归属现有组件：

| Capability | Canonical Owner |
|---|---|
| Repository CI / release gate | `.github/workflows/` + GitHub branch/ruleset |
| Work classification | `using-superpowers` |
| PRD risk/profile | `smc-prd-grounding` |
| Plan risk/static validation | `smc-plan-validator` |
| Semantic Plan Review routing | `smc-plan-review` |
| Domain runtime | `domain-runtime` |
| Frontend semantics | `smc-frontend-preplan` / `smc-frontend-review` |
| Backend semantics | `smc-backend-preplan` / `smc-backend-review` |
| Ops semantics | `smc-ops-preplan` / `smc-ops-review` |
| Consumer installation | `install_v500.py` lineage / installer suite |
| Runtime execution context | `smc-plan-delivery/scripts/` |
| Harness task execution | `subagent-driven-development` / Consumer execution policy |
| Package validation | `validate_package.py` / `validate_package_v500.py` lineage |
| Acceptance benchmark | New acceptance tooling under `engineeing-skills/acceptance/`，仅为测试工具，不成为 Delivery Owner |

---

# 6. Routing Facts

当前 work item 必须使用 FULL：

```json
{
  "existing_owner": true,
  "existing_capability": true,
  "bounded_writes": true,
  "deterministic_verification": true,
  "new_owner": false,
  "public_contract": false,
  "security_boundary": false,
  "schema_migration": true,
  "protocol_change": false,
  "external_dependency": false,
  "lifecycle_change": true,
  "cross_domain_ownership": true,
  "live_acceptance": false,
  "research_only": false,
  "governed": true
}
```

理由：

- `install-lock.v1 -> v2` 涉及 metadata schema evolution；
- Release lifecycle / branch protection 会改变治理发布路径；
- Risk Runtime 同时影响 PRD、Plan、Review；
- Telemetry 同时连接 GES Runtime 与 Harness Consumer。

---

# 7. Change Classification

| Change ID | Capability | Action | Production Owner | Target State |
|---|---|---|---|---|
| C01 | Repository Release Gate | MODIFY | GitHub Workflow / Ruleset | master 必须经过稳定 package gate |
| C02 | Work Router Research Trust | MODIFY | using-superpowers | `research_only` 不再单字段决定 NONE |
| C03 | Structured Risk Runtime | MODIFY + minimal ADD | domain-runtime + PRD/Plan/Review adapters | structured-signal-first，regex fallback |
| C04 | Domain Semantic Validation | MODIFY | domain-runtime + Domain validators | enum / conditional / escalation 可确定校验 |
| C05 | Installer Provenance & Reconciliation | MODIFY | installer suite | install-lock.v2 + safe stale-file reconciliation |
| C06 | Harness Telemetry & Benchmark | ADD + MODIFY | Delivery execution context + Harness adapter + acceptance tooling | 可量化 Token/Model/Retry/Cache/Reviewer 成本 |

---

# 8. C01 — master Branch Protection + Required Package Gate

## 8.1 问题

当前仓库存在 CI workflow，但 GES package validator 不是稳定 required merge gate；`master` 如果没有 branch/ruleset enforcement，可以出现：

```text
代码已合并
但 engineeing-skills package 未完整验证
```

这与 GES 对 Consumer 的强治理要求不一致。

## 8.2 目标

建立稳定的 GitHub status context，例如：

```text
GES Package Gate / validate-package
```

该 status 必须成为 `master` Required Status Check。

任何修改以下路径的 PR：

```text
engineeing-skills/**
.github/workflows/**
```

都必须执行完整 GES package gate。

## 8.3 CI Pipeline

建议在现有 `.github/workflows/governance-ci.yml` 增加独立 Job，避免另一个 workflow 与状态名称漂移：

```text
validate-governance-repo
        +
ges-package-gate
```

`ges-package-gate` 最低步骤：

```bash
python engineeing-skills/build_package_manifest.py --check
python engineeing-skills/validate_package.py
git diff --check
git diff --exit-code
```

要求：

- Python 3.12；
- `PYTHONUTF8=1`；
- `PYTHONDONTWRITEBYTECODE=1`；
- package validation 后仓库不得出现未预期 mutation；
- Job 名称固定，不允许每版更名导致 branch protection 丢失。

## 8.4 Branch Protection / Ruleset

`master` 必须：

- Require pull request before merge；
- Require `GES Package Gate / validate-package`；
- 禁止 force push；
- 禁止 branch deletion；
- direct push 默认禁止；
- bypass 只允许明确的 break-glass 角色；
- break-glass 使用必须留下 Audit Evidence。

是否 Require 1 个 approval 可由公司 Repo Governance 统一策略决定，不强写入 GES Core。

## 8.5 验证

必须构造：

1. package manifest 被篡改；
2. 一个 Python selftest 失败；
3. validator 执行后修改 tracked file；
4. GitHub PR 不包含 required status；
5. direct push 尝试。

预期全部不能形成正常 merge path。

## 8.6 Acceptance Criteria

- AC-C01-01：GES package gate 成为稳定 required status；
- AC-C01-02：破坏 package manifest 时 PR 不可合并；
- AC-C01-03：package validation mutation 被检测；
- AC-C01-04：force push 被规则阻止；
- AC-C01-05：ruleset/protection 配置可导出为 Acceptance Evidence。

---

# 9. C02 — 修复 `research_only` 可自报问题

## 9.1 当前问题

当前 Work Router 中：

```text
research_only=true
+ previous_profile=None/NONE
```

可以较早进入：

```text
SPIKE / NONE
```

如果调用方错误或恶意地把 production change 标成 research_only，就可能绕过正常 governed flow。

## 9.2 核心原则

`research_only` 只能是 **hint**，不能是 authoritative fact。

Router 必须计算：

```text
effective_research_only
```

而不是直接信任：

```text
facts.research_only
```

## 9.3 Work Facts v2

建议兼容增加以下字段：

```json
{
  "research_intent": true,
  "governed": false,
  "retained_production_change": false,
  "production_write_requested": false,
  "durable_product_artifact_requested": false
}
```

规则：

```text
effective_research_only =
    research_intent == true
AND governed == false
AND retained_production_change == false
AND production_write_requested == false
AND durable_product_artifact_requested == false
AND previous_profile in {None, NONE}
```

任何字段：

```text
true / unknown / missing
```

只要可能表示 production/governed work，就禁止 `SPIKE/NONE`。

## 9.4 Governance Source

`governed` SHOULD 来自：

- Roadmap/Feature/Work Item 是否已经进入治理；
- Canonical artifact presence；
- Orchestrator request type；

不能由负责 implementation 的同一个 Worker 临时解释。

## 9.5 冲突处理

例如：

```json
{
  "research_intent": true,
  "governed": true
}
```

不得猜测。

返回：

```text
ARCHITECTURAL / FULL
reason = RESEARCH_ONLY_CONTRADICTS_GOVERNED_WORK
```

例如：

```json
{
  "research_intent": true,
  "production_write_requested": true
}
```

返回：

```text
FULL
reason = RESEARCH_ONLY_PRODUCTION_WRITE_CONFLICT
```

## 9.6 Backward Compatibility

旧 `research_only` 字段继续可读，但只作为 `research_intent` alias。

旧调用如果没有新的 authority facts：

```text
不能自动 NONE
```

而是 fail closed。

## 9.7 Tests

新增：

- governed + research_only => FULL；
- production write + research_only => FULL；
- durable output + research_only => FULL；
- unknown governed => FULL；
- pure analysis + all false => SPIKE/NONE；
- previous LEAN/FULL 不允许 research 降级；
- retained production change false-positive/contradiction；
- legacy research_only without v2 facts => not NONE。

## 9.8 Acceptance Criteria

- AC-C02-01：`research_only=true` 单独不能产生 NONE；
- AC-C02-02：任何 retained production change 都不能路由 SPIKE/NONE；
- AC-C02-03：旧调用 fail closed；
- AC-C02-04：纯研究请求仍可低成本 SPIKE/NONE；
- AC-C02-05：FULL/LEAN monotonicity 保持。

---

# 10. C03 — Structured Risk First，Regex 仅 fallback / contradiction detector

## 10.1 当前问题

风险检测在多处重复：

- Work Router；
- PRD Profile；
- Plan Validator；
- Semantic Review Router。

并且大量使用文本 regex。

例如：

```text
No schema migration.
No new service.
Authentication boundary unchanged.
```

可能因为包含高风险词而误升级 FULL。

结果：

```text
假风险
→ FULL PRD
→ FULL Plan
→ FULL Review
→ Token/Reviewer 成本上升
```

## 10.2 设计目标

建立共享 Risk Runtime：

```text
engineeing-skills/domain-runtime/risk_signals.py
```

逻辑顺序固定：

```text
1. Structured Facts
2. Consistency Check
3. Negation-aware Text Hint
4. Fallback
5. Escalation
```

## 10.3 Canonical Risk Keys

沿用 Work Router 已存在风险键，禁止另外建立一套同义字段：

```text
new_owner
public_contract
security_boundary
schema_migration
protocol_change
external_dependency
lifecycle_change
cross_domain_ownership
live_acceptance
```

加上能力前提：

```text
existing_owner
existing_capability
bounded_writes
deterministic_verification
```

## 10.4 PRD

PRD 中 `## Routing Facts` 仍是 structured SOT。

`prd_profile.py`：

- Structured facts 完整时，按字段判定；
- 不再对整个 PRD 做主判据 broad regex；
- Text scanner 只负责 contradiction detection；
- structured=false 但存在明确肯定高风险语句时 => `RISK_FACT_CONTRADICTION`；
- “no/none/unchanged/not required/without”等否定上下文不得作为肯定风险。

## 10.5 Plan

新生成 v3.7 Plan 在 `## Governance Profile` 中增加 derived snapshot：

```text
Risk Facts Snapshot: <canonical JSON>
Source: approved PRD Routing Facts
```

该 Snapshot：

- 是 PRD 风险事实的 Plan projection；
- 不是第二个 SOT；
- Plan Author 不得修改其语义；
- existing v3.7 Plan 没有 Snapshot 时继续兼容，使用 legacy fallback；
- 不要求 bulk migrate in-flight Plan。

## 10.6 Plan Validator

`validate_plan_v37.py`：

```text
Risk Facts Snapshot exists
    → structured validation
    → contradiction detector
else
    → conservative legacy fallback
```

如果：

```text
governance_profile=LEAN
AND structured high-risk=true
```

返回：

```text
PLAN_LEAN_FULL_REQUIRED
```

## 10.7 Semantic Plan Review

`assess_plan_review.py` 不再以 broad keyword 为第一来源。

Review depth：

```text
structured high-risk
    → FULL

structured safe + fresh prior PASS
    → NONE / DELTA based on freshness

structured safe + first LEAN review
    → 按 acceptance structure policy 决定 DELTA/LIGHT 或 FULL

missing/contradictory
    → FULL
```

## 10.8 首次 LEAN Plan Review 成本问题

当前新 v3.7 Plan 一般携带：

```text
acceptance_contract: smc.acceptance.v1
```

因此首次 Review 容易直接 FULL。

本 PRD要求：

- 不删除 Acceptance Gate；
- 新增 deterministic acceptance structure check；
- 对满足以下条件的 LEAN Plan：

```text
existing owner
no contract/boundary/lifecycle risk
no LIVE/FAULT/EXTERNAL
blocking AC 全部映射
blocking Verification 完整
structured facts complete
```

允许进入：

```text
DELTA/LIGHT_FIRST_REVIEW
```

如果系统无法建立可信 deterministic clearance，则仍 FULL。

## 10.9 Text Risk Hint

建议统一实现：

```text
AFFIRMATIVE
NEGATED
AMBIGUOUS
ABSENT
```

禁止简单：

```python
if re.search("schema migration", text):
    FULL
```

示例：

| Text | Expected |
|---|---|
| `schema migration required` | AFFIRMATIVE |
| `add schema migration` | AFFIRMATIVE |
| `no schema migration` | NEGATED |
| `schema migration is not required` | NEGATED |
| `migration impact TBD` | AMBIGUOUS -> FULL |
| no mention | ABSENT |

## 10.10 Acceptance Criteria

- AC-C03-01：`No schema migration` 不再导致假 FULL；
- AC-C03-02：structured `schema_migration=true` 永远 FULL；
- AC-C03-03：structured false + affirmative contradiction => FULL；
- AC-C03-04：缺失 structured facts 的旧 artifact 继续 fail-closed；
- AC-C03-05：PRD / Plan / Review 使用同一风险解析模块；
- AC-C03-06：没有第二套风险 SOT；
- AC-C03-07：LEAN 首次 review 的 Token 成本可下降且不减少 blocking acceptance 检查。

---

# 11. C04 — Domain Preplan Semantic Validators

## 11.1 当前问题

共享 `domain_table.validate_table()` 已经能验证：

- section；
- columns；
- separator；
- row shape；
- required field 非空；
- 禁止 `<DECIDE>` / `TBD` / `???`；
- Change ID duplicate。

但不能回答：

```text
Framework=BANANA 是否合法？
Visual Verification=WHATEVER 是否合法？
Contract=Maybe 是否合法？
Auth=NEW_BOUNDARY 时 LEAN 是否应该阻塞？
Migration Order=N/A 但 Deployment Impact=IRREVERSIBLE 是否矛盾？
```

## 11.2 设计原则

Core Domain Runtime 只提供通用语义校验 primitives，不硬编码 frontend/backend/ops 业务值。

建议扩展：

```text
domain-runtime/domain_table.py
```

增加：

```text
validate_enum()
validate_enum_or_na()
validate_required_if()
validate_forbidden_if()
validate_pair()
validate_na_with_reason()
```

Domain-specific rules 仍由各 Domain validator 定义。

---

## 11.3 Frontend Semantic Contract

### Framework

```text
React
Vue
Generic
N/A
```

### Visual Verification

```text
STATIC
COMPONENT
INTERACTION
LIVE_VISUAL
N/A
```

### Component Map

必须至少包含以下 action token 之一：

```text
REUSE
EXTEND
NEW
REMOVE
N/A
```

如果 `NEW`：

- 必须说明新 Component Owner；
- 不得与现有 primitive 重复，语义 Review 仍负责最终判断。

### FULL Frontend Preplan trigger

以下任一成立时，Preplan 必须要求 FULL intent：

- new page；
- layout hierarchy change；
- navigation change；
- state owner/store change；
- responsive architecture change；
- new design-system primitive；
- multi-panel/workspace structure change。

### N/A

`N/A` 必须是明确适用场景，不能用来逃避字段决定。

例如：

```text
text/token-only change
```

可以：

```text
State Ownership = N/A
```

但：

```text
new interactive component
```

不可。

---

## 11.4 Backend Semantic Contract

建议标准化：

### Contract

```text
UNCHANGED
COMPATIBLE_EXTEND
BREAKING_CHANGE
N/A
```

### Auth

```text
UNCHANGED
NONE
MODIFY
NEW_BOUNDARY
N/A
```

### Data / Transaction

允许：

```text
NONE
READ_ONLY
WRITE
TRANSACTIONAL
MIGRATION
N/A
```

### Idempotency / Concurrency

```text
NOT_APPLICABLE
UNCHANGED
REQUIRED
MODIFIED
```

### Hard escalation

以下任一：

```text
BREAKING_CHANGE
NEW_BOUNDARY
MIGRATION
new external dependency
new service/store/client/protocol owner
```

必须：

```text
governance_profile=FULL
```

LEAN 时直接：

```text
BACKEND_PREPLAN_FULL_REQUIRED
```

---

## 11.5 Ops Semantic Contract

建议：

### Deployment Impact

```text
NONE
CONFIG_ONLY
RESTART
ROLLING_CHANGE
TOPOLOGY_CHANGE
IRREVERSIBLE
```

### Compatibility

```text
UNCHANGED
BACKWARD_COMPATIBLE
WINDOW_REQUIRED
BREAKING
```

### Live Verification

```text
NOT_REQUIRED
STATIC
SMOKE
LIVE
EXTERNAL
```

### Hard escalation

```text
TOPOLOGY_CHANGE
IRREVERSIBLE
BREAKING
migration order required
LIVE/EXTERNAL
```

必须 FULL 或明确 Acceptance Scenario。

### Rollback conditional

如果：

```text
Deployment Impact != NONE
```

则 `Rollback` 不能是无理由 `N/A`。

如果：

```text
IRREVERSIBLE
```

必须显式标记：

```text
Rollback = NOT_POSSIBLE:<reason>
```

并强制 FULL。

---

## 11.6 Plan Quality Ledger

Preplan semantic decisions 由 Approved PRD 冻结。

Plan Quality Ledger：

- 绑定 exact implementation target；
- 不重新定义 Domain Design Intent；
- validator 检查 Plan row 与 Preplan decision 是否冲突；
- conflict => `PRD_STALE_OR_CONFLICTING`，不得在 Plan 层偷偷改需求。

## 11.7 Tests

每个 Domain 至少增加：

- valid normal row；
- unknown enum；
- placeholder；
- N/A misuse；
- conditional missing；
- FULL_REQUIRED signal；
- Change ID missing/duplicate；
- PRD intent ↔ Plan quality contradiction；
- Vue / React；
- backend migration；
- ops irreversible change。

## 11.8 Acceptance Criteria

- AC-C04-01：`Framework=BANANA` 必须 FAIL；
- AC-C04-02：Frontend invalid visual level 必须 FAIL；
- AC-C04-03：Backend breaking contract + LEAN 必须 FULL_REQUIRED；
- AC-C04-04：Ops irreversible + no rollback decision 必须 FAIL；
- AC-C04-05：Core Runtime 不硬编码 Domain ID；
- AC-C04-06：Domain Provider 不获得 Delivery State ownership。

---

# 12. C05 — install-lock.v2 + Release Provenance + stale package-owned reconciliation

## 12.1 当前问题

现有 install lock 主要记录：

```text
bundle
profile
domains
```

它不能证明：

```text
同一个 bundle string
==
完全相同 package bytes
```

也不能可靠清理：

```text
旧版本 package 中存在
新版本 package 中删除
Consumer 本地仍残留
```

的 ghost package files。

## 12.2 install-lock.v2

建议：

```json
{
  "schema": "smc.ges.install-lock.v2",
  "bundle": "5.x.x",
  "profile": {
    "id": "generic",
    "version": "2.0.0",
    "sha256": "..."
  },
  "domains": {
    "frontend": {
      "version": "2.0.0",
      "sha256": "..."
    }
  },
  "release_identity": {
    "source_commit": "...",
    "package_manifest_sha256": "...",
    "package_file_count": 200,
    "installer_sha256": "..."
  },
  "policy_digest": "sha256:...",
  "transaction_manifest_sha256": "...",
  "installed_at": "...",
  "owned_files": [
    {
      "path": ".agents/skills/...",
      "installed_sha256": "..."
    }
  ]
}
```

## 12.3 Release Identity 的 circular hash 处理

禁止把“当前 Git commit SHA”直接写入一个属于该 commit 的 tracked manifest 再反复 commit；这会产生 commit identity recursion。

定义两种模式：

### Repo Install Mode

Installer 从 Git checkout 运行：

```text
source_commit = git rev-parse HEAD
```

并检查：

```text
engineeing-skills package files 与 PACKAGE-MANIFEST 一致
```

如果 repo dirty：

- package bytes 仍可通过 manifest verify；
- `source_commit` 只能作为 source reference；
- lock 必须额外记录 `source_tree_dirty=true`；
- Release Acceptance 不接受 dirty source install。

### Release Bundle Mode

Release Pipeline 在 source commit 已确定之后生成外部 release metadata：

```text
RELEASE-IDENTITY.json
```

内容：

```text
bundle
source_commit
package_manifest_sha256
tag
```

该 metadata 不参与 source manifest 的递归 identity；它作为 Release Asset / Distribution Metadata 提供。

## 12.4 owned_files

`owned_files` 只记录 package 明确拥有的文件。

绝不能把 Consumer local skill 当 package-owned。

## 12.5 Safe stale-file reconciliation

升级算法：

```text
old_owned = old install-lock.v2 owned_files
new_owned = current package managed files

stale = old_owned - new_owned
```

对每个 stale：

### Case A

```text
current_sha == old_installed_sha
```

说明 Consumer 未修改：

```text
安全删除
```

### Case B

```text
current_sha != old_installed_sha
```

说明 Consumer 修改过旧 package file：

```text
禁止删除
INSTALL_STALE_OWNED_FILE_MODIFIED
```

要求显式 resolution。

### Case C：old lock v1

没有 owned_files：

```text
不做破坏性自动删除
LEGACY_LOCK_RECONCILIATION_SKIPPED
```

本次安装成功生成 v2 lock 后，下一次升级才具备完整 reconciliation。

## 12.6 Transaction / Rollback

被删除的 stale file 也必须：

- `record_before()`；
- 进入 transaction manifest；
- rollback 可以恢复；
- failure 后自动 rollback。

## 12.7 Package Manifest

继续使用：

```text
PACKAGE-MANIFEST.json
SHA256SUMS
```

Installer 运行前：

```text
verify()
```

不允许跳过。

## 12.8 Acceptance Criteria

- AC-C05-01：install lock 可证明 package manifest identity；
- AC-C05-02：v2 -> v2 升级能自动删除未修改的 stale package-owned file；
- AC-C05-03：Consumer 修改过的 stale file 不被静默删除；
- AC-C05-04：v1 lock 第一次升级不进行危险清理；
- AC-C05-05：rollback 恢复被删除文件；
- AC-C05-06：Consumer-owned skill 永不进入 package stale deletion；
- AC-C05-07：两个 Consumer 的 lock 可以判断是否是同一 release bytes。

---

# 13. C06 — Harness Runtime Telemetry + 4.4.1 vs 5.0 Benchmark

## 13.1 当前问题

当前已经有：

```text
FAST
STANDARD
REASONING
```

并且 Source Context Capsule、Unified Reviewer、Task Brief、Engineering Method 已具备成本优化能力。

但 GES 无法证明：

```text
请求 FAST
Harness 实际用了什么？
是否 fallback？
用了多少 Prompt Token？
多少 Completion Token？
多少 cache token？
重试了几次？
Source Context 命中了几次？
Reviewer seat 减少了多少？
```

## 13.2 原则

Telemetry：

- 不成为 Final Evidence；
- 不成为 Delivery Truth；
- 不记录源码内容；
- 不记录完整 Prompt；
- 不记录 secret；
- 正常产品交付允许 Telemetry unavailable；
- Acceptance Benchmark 要求 Telemetry 完整，否则该 case 无效。

## 13.3 Telemetry Schema

新增建议：

```text
smc.execution.telemetry.v1
```

存储：

```text
.smc/runs/<plan_id>/telemetry/events.jsonl
```

建议字段：

```json
{
  "schema": "smc.execution.telemetry.v1",
  "at": "...",
  "plan_id": "...",
  "todo": "T1",
  "dispatch_id": "...",
  "agent": "...",
  "phase": "IMPLEMENT|TASK_REVIEW|FINAL_REVIEW|DEBUG|TDD",
  "requested_tier": "FAST|STANDARD|REASONING",
  "actual_tier": "FAST|STANDARD|REASONING|UNKNOWN",
  "provider": "provider-id-or-unknown",
  "model": "model-id-or-unknown",
  "fallback": false,
  "fallback_reason": "",
  "prompt_tokens": 0,
  "completion_tokens": 0,
  "cache_read_tokens": 0,
  "cache_write_tokens": 0,
  "latency_ms": 0,
  "retry_count": 0,
  "source_context_hits": 0,
  "source_context_misses": 0,
  "reviewer_seats": 0,
  "outcome": "PASS|FAIL|BLOCKED|ERROR"
}
```

## 13.4 Runtime API

建议新增：

```text
smc-plan-delivery/scripts/runtime_metrics.py
```

CLI：

```bash
runtime_metrics.py dispatch ...
runtime_metrics.py result ...
runtime_metrics.py cache-hit ...
runtime_metrics.py cache-miss ...
runtime_metrics.py reviewer-seat ...
runtime_metrics.py summarize <PLAN>
```

Harness Adapter 调用这些接口。

GES Core 不直接调用 provider API。

## 13.5 Tier Binding

Consumer Profile：

```json
"execution_policy": {
  "model_tiers": {
    "FAST": "fast",
    "STANDARD": "standard",
    "REASONING": "reasoning"
  }
}
```

仍然只定义 logical tier。

Harness 返回：

```text
requested_tier
actual_tier
actual_provider
actual_model
```

如果 Harness 不支持 tier：

```text
actual_tier=UNKNOWN
fallback=true
fallback_reason=SESSION_MODEL_ONLY
```

## 13.6 Source Context Metrics

`source_context.py` 在 `get`：

```text
valid capsule -> cache hit
missing/stale -> cache miss
```

只记录计数和 path key hash，不记录 source body。

## 13.7 Reviewer Metrics

记录：

```text
UNIFIED = reviewer_seats +1
INDEPENDENT = reviewer_seats +2
Final whole implementation review = +1
```

用于证明普通 Todo reviewer seat 是否降低。

---

# 14. Acceptance Benchmark

## 14.1 Benchmark 目标

不是证明：

```text
5.0 Token 少
```

而是证明：

```text
5.0 Token 少
AND governance safety 不下降
AND rework 不上升
AND escaped defect 不增加
```

## 14.2 Cohort

主比较：

```text
A = GES 4.4.1 reproducible baseline
B = GES 5.0.0 repaired candidate @ fc5dfcfe...
```

Hardening 完成后补充：

```text
C = PRD v5.0.1 implementation candidate
```

要求：

- 同一个需求；
- 同一个 Consumer repo revision；
- 尽量同一模型能力池；
- 同一 Acceptance Oracle；
- 不把 4.4.1 源码修改成 5.0 行为来“方便对比”；
- Telemetry 由共同 Harness adapter 收集。

如果 4.4.1 package identity 无法完全重现，Benchmark Report 必须明确标记 `BASELINE_REPRODUCIBILITY_LIMITATION`。

## 14.3 Case Set

最低 20 个真实/半真实 case：

```text
5 × mechanical
5 × normal behavior
5 × bug fix
5 × high risk
```

并额外执行 Golden Governance Corpus。

## 14.4 Metrics

每个 Case 记录：

| Metric | 含义 |
|---|---|
| Prompt Tokens | 总输入 |
| Completion Tokens | 总输出 |
| Cache Read Tokens | provider cache |
| Total Tokens | 总 Token |
| Dispatch Count | Worker 调度 |
| Reviewer Seats | reviewer 数 |
| File Reads | Harness 可观测时记录 |
| Source Context Hits | Capsule 命中 |
| Source Context Misses | Capsule 未命中 |
| Clarification Questions | 前半程问题数 |
| Plan Review Depth | NONE/DELTA/FULL |
| Fix Rounds | 修改轮数 |
| Retry Count | Harness retry |
| Wall Time | 完成交付时间 |
| Plan Revisions | Plan 返工 |
| Final Diff LOC | 实现膨胀指标 |
| Generated Files | 新建文件数 |
| Blocking Verification Runs | 最终 proof 次数 |
| Acceptance Outcome | PASS/FAIL |
| Escaped Defect | acceptance 后发现缺陷 |

---

# 15. Golden Governance Corpus

至少固定以下 deterministic cases：

| ID | 场景 | 预期 |
|---|---|---|
| G01 | 纯研究 | SPIKE/NONE |
| G02 | governed item 自报 research_only | FULL/禁止 NONE |
| G03 | production write + research_only | FULL |
| G04 | 已有组件改文案 | LEAN |
| G05 | 已有 Service 普通行为 | LEAN |
| G06 | Vue 新页面/Layout | Frontend FULL Preplan |
| G07 | React State Owner 改动 | Frontend FULL |
| G08 | API bug | BUG_FIX + TDD + Debug |
| G09 | 新公开 API | FULL |
| G10 | Auth boundary | FULL/HIGH_RISK |
| G11 | DB schema migration | FULL |
| G12 | Docker config | Ops |
| G13 | Topology change | Ops FULL |
| G14 | Frontend + Backend | 两 Domain 激活 |
| G15 | Frontend + Backend + Ops | 三 Domain 激活 |
| G16 | 同 path#symbol 两 Todo | BLOCK |
| G17 | Worker 写 scope 外文件 | BLOCK |
| G18 | GREEN 后改测试 | TDD_STALE |
| G19 | Review PASS 后改 Plan semantic | Review STALE |
| G20 | Evidence 后改 production | Evidence STALE |
| G21 | LIVE candidate 不匹配 | BLOCK |
| G22 | 三次 failed debug fix | DEBUG_ARCHITECTURE_ESCALATION |
| G23 | `No schema migration` | 不得假 FULL |
| G24 | structured false + affirmative schema migration | CONTRADICTION/FULL |
| G25 | Framework=BANANA | Domain FAIL |
| G26 | Backend breaking contract + LEAN | FULL_REQUIRED |
| G27 | Ops irreversible + no rollback | FAIL |
| G28 | stale package-owned untouched file | 自动删除 |
| G29 | stale package-owned locally modified | BLOCK/PRESERVE |
| G30 | old v1 install lock | 不做 destructive cleanup |

---

# 16. Chaos / Adversarial Governance Tests

主动破坏：

```text
Plan Review PASS 后改 Plan
TDD GREEN 后改测试
Debug VERIFIED 后改 source
Completion Audit PASS 后改 production
Implementation Review PASS 后改 whole diff
删除 TDD receipt
篡改 semantic snapshot
篡改 Evidence Manifest
换 LIVE candidate
两个 Agent 同时写 hotspot
Worker 写 Plan 外文件
把 HIGH_RISK override 成 MECHANICAL
把 BUG_FIX override 成 TDD_NOT_APPLICABLE
把 governed production work 标 research_only
伪造 bundle version 但换 package bytes
```

预期：

```text
全部 fail closed
并返回稳定、可断言的 error code
```

Acceptance 不能只判断“非 0”，必须断言正确 failure reason。

---

# 17. Consumer Pilot

选择至少三个 Consumer：

```text
A. React/Vue UI Consumer
B. Python/Node/Java Backend Consumer
C. Docker/Nginx/Compose Ops Consumer
```

每个至少执行：

```text
1 × LEAN
1 × BEHAVIOR_CHANGE
1 × BUG_FIX
1 × HIGH_RISK/FULL
```

最低：

```text
12 个真实 governed deliveries
```

每个 Pilot 保存：

- route result；
- PRD Review；
- Domain Preplan；
- Plan Review Depth；
- Engineering Method；
- actual model telemetry；
- Completion Audit；
- Implementation Review；
- Verification/Evidence；
- implementation commit；
- Roadmap DONE commit；
- token/cost summary；
- post-delivery regression observation。

---

# 18. Quantitative Acceptance Thresholds

## 18.1 Safety — 必须 100%

```text
high-risk false-LEAN                = 0
governed production false-SPIKE    = 0
ownership escape                    = 0
scope drift accepted                = 0
stale TDD accepted                  = 0
stale debug verification accepted   = 0
stale Plan review accepted          = 0
stale final evidence accepted       = 0
method gate bypass                  = 0
LIVE candidate mismatch pass        = 0
package integrity bypass            = 0
rollback data loss                  = 0
consumer-owned file silent delete   = 0
```

## 18.2 Quality

```text
duplicate production owner          = 0
blocking AC without proof           = 0
uncontrolled Plan semantic rewrite  = 0
Domain invalid enum accepted        = 0
```

## 18.3 Efficiency

建议作为 Accepted Baseline 的目标门槛：

```text
BOUNDED median total-token reduction >= 30%
normal-risk reviewer-seat reduction >= 25%
repeated source-context reads reduction >= 30%
median fix rounds <= baseline
median implementation turns <= baseline
```

如果未达到成本目标但 Safety/Quality 达标：

```text
允许继续 Candidate
不直接宣称“成本优化已验证”
```

## 18.4 Stability

```text
completion reopen rate <= 4.4.1
post-delivery regression rate <= 4.4.1
installer rollback success = 100%
package validation pass reproducibility = 100%
```

---

# 19. Source Anchors

当前实现基线主要锚点：

### Release / Package

```text
.github/workflows/governance-ci.yml
engineeing-skills/build_package_manifest.py
engineeing-skills/PACKAGE-MANIFEST.json
engineeing-skills/SHA256SUMS
engineeing-skills/install.py
engineeing-skills/install_v500.py
engineeing-skills/install_v430.py
engineeing-skills/validate_package.py
engineeing-skills/validate_package_v500.py
engineeing-skills/VERSIONING.md
engineeing-skills/tests/test_package_v500.py
```

### Work Router / PRD

```text
engineeing-skills/.agents/skills/using-superpowers/SKILL.md
engineeing-skills/.agents/skills/using-superpowers/scripts/work_router.py
engineeing-skills/.agents/skills/using-superpowers/scripts/test_work_router.py
engineeing-skills/.agents/skills/using-superpowers/references/work-routing-contract.md

engineeing-skills/.agents/skills/smc-prd-grounding/SKILL.md
engineeing-skills/.agents/skills/smc-prd-grounding/scripts/prd_profile.py
engineeing-skills/.agents/skills/smc-prd-grounding/scripts/test_prd_profile.py
```

### Plan / Review

```text
engineeing-skills/.agents/skills/smc-plan-from-approved-prd-ponytail/scripts/create_plan_seed_v37.py
engineeing-skills/.agents/skills/smc-plan-validator/scripts/validate_plan_v37.py
engineeing-skills/.agents/skills/smc-plan-review/scripts/assess_plan_review.py
engineeing-skills/.agents/skills/smc-plan-review/scripts/build_review_packet.py
```

### Domain Runtime

```text
engineeing-skills/domain-runtime/domain_runtime.py
engineeing-skills/domain-runtime/domain_table.py

engineeing-skills/.agents/skills/smc-frontend-preplan/scripts/validate_prd_intent.py
engineeing-skills/.agents/skills/smc-frontend-review/scripts/validate_plan_extension.py

engineeing-skills/.agents/skills/smc-backend-preplan/scripts/validate_prd_intent.py
engineeing-skills/.agents/skills/smc-backend-review/scripts/validate_plan_extension.py

engineeing-skills/.agents/skills/smc-ops-preplan/scripts/validate_prd_intent.py
engineeing-skills/.agents/skills/smc-ops-review/scripts/validate_plan_extension.py
```

### Engineering / Harness

```text
engineeing-skills/.agents/skills/smc-plan-delivery/scripts/engineering_method.py
engineeing-skills/.agents/skills/smc-plan-delivery/scripts/execution_context.py
engineeing-skills/.agents/skills/smc-plan-delivery/scripts/source_context.py
engineeing-skills/.agents/skills/smc-plan-delivery/scripts/plan_state.py
engineeing-skills/.agents/skills/smc-plan-delivery/scripts/validate_delivery_completion.py
engineeing-skills/.agents/skills/subagent-driven-development/SKILL.md
engineeing-skills/consumers/generic.json
engineeing-skills/consumers/smc-copilot-work.json
```

---

# 20. Suggested New Files

本 PRD允许的最小新增文件：

```text
engineeing-skills/domain-runtime/risk_signals.py

engineeing-skills/.agents/skills/smc-plan-delivery/scripts/runtime_metrics.py

engineeing-skills/acceptance/
├── README.md
├── metrics.schema.json
├── thresholds.json
├── run_acceptance.py
├── run_benchmark.py
└── cases/
    ├── work-router/
    ├── risk-routing/
    ├── domain-semantics/
    ├── installer/
    └── delivery-chaos/
```

不建议为了本轮再新增顶层生产 Skill。

---

# 21. Test Strategy

测试层次必须分离：

## T1 Unit Contract Tests

覆盖：

```text
Work Router v2
Risk resolver
Negation-aware text hint
Domain semantic enum
Installer reconciliation
Telemetry schema
```

## T2 Package Regression

执行：

```bash
python engineeing-skills/build_package_manifest.py --check
python engineeing-skills/validate_package.py
```

## T3 Fixture Consumer

验证：

```text
install dry-run
install apply
v1 -> v2 lock
v2 -> v2 upgrade
stale file cleanup
modified stale file block
rollback
mirror integrity
consumer-local preservation
```

## T4 Golden Governance Corpus

G01-G30。

## T5 Chaos Governance

主动破坏 freshness、scope、receipt、candidate、ownership。

## T6 Real Consumer Pilot

12 个真实交付。

## T7 Benchmark

4.4.1 vs 5.0.0，完成后再确认 Hardening 版本没有性能回退。

---

# 22. Rollout Plan

## Phase A — Deterministic Hardening

先实现：

```text
C02 research trust
C03 structured risk
C04 domain semantics
```

原因：

这些改变 Router/PRD/Plan 判断，应先稳定行为再测成本。

## Phase B — Installer Integrity

实现：

```text
C05 install-lock.v2
stale reconciliation
```

先做 fixture，不直接升级所有 Consumer。

## Phase C — Telemetry

实现：

```text
C06 runtime metrics
Harness adapter
```

Telemetry 必须默认低侵入。

## Phase D — Repository Release Gate

将 package validator 接入 CI，确认稳定后再配置 required check。

注意：

```text
先让 check 连续稳定 PASS
再把它设置为 required
```

避免因为 workflow 名称/环境问题锁死 master。

## Phase E — Acceptance

运行：

```text
Golden Corpus
Chaos
3 Consumer Pilot
Benchmark
```

## Phase F — Baseline Promotion

只有所有 Blocking AC PASS 后：

```text
更新 BASELINE.md
生成 accepted release identity
创建 release/tag
```

---

# 23. Migration Policy

## Existing PRD

- 不强制 bulk migrate；
- 新 risk runtime 可读取旧文本；
- 缺 structured facts 时 conservative fallback。

## Existing v3.7 Plan

- 不要求批量增加 Risk Facts Snapshot；
- in-flight plan 保持可读；
- 新 Plan Author 才写 structured projection；
- Review/Validator 对旧 Plan fallback。

## Existing v3.6 and older Plan

继续使用现有 compatible-read 策略，不因本 PRD 强行升级。

## Consumer install-lock.v1

第一次使用新 installer：

```text
不 destructive cleanup
生成 v2 lock
```

下一次才启用完整 stale reconciliation。

## Telemetry

没有 Harness adapter：

```text
正常 Delivery 不阻塞
Benchmark case 标记 TELEMETRY_INCOMPLETE
```

---

# 24. Failure Semantics

新增稳定错误码建议：

```text
WORK_RESEARCH_AUTHORITY_MISSING
RESEARCH_ONLY_CONTRADICTS_GOVERNED_WORK
RESEARCH_ONLY_PRODUCTION_WRITE_CONFLICT

RISK_FACTS_MISSING
RISK_FACTS_INVALID
RISK_FACT_CONTRADICTION
RISK_TEXT_AMBIGUOUS

FRONTEND_PREPLAN_ENUM_INVALID
FRONTEND_PREPLAN_CONDITIONAL_INVALID
BACKEND_PREPLAN_FULL_REQUIRED
BACKEND_PREPLAN_ENUM_INVALID
OPS_PREPLAN_FULL_REQUIRED
OPS_PREPLAN_ROLLBACK_REQUIRED

INSTALL_RELEASE_IDENTITY_INVALID
INSTALL_LOCK_V2_INVALID
INSTALL_STALE_OWNED_FILE_MODIFIED
INSTALL_LEGACY_RECONCILIATION_SKIPPED

TELEMETRY_SCHEMA_INVALID
TELEMETRY_INCOMPLETE
BENCHMARK_BASELINE_NOT_REPRODUCIBLE
BENCHMARK_THRESHOLD_NOT_MET
```

错误码一旦进入测试 contract，不应随意改名。

---

# 25. Observability

Acceptance Report 最终必须输出：

```text
Routing:
  NONE / LEAN / FULL distribution
  false FULL
  false LEAN

Engineering:
  method profile distribution
  TDD cycles
  debug escalations
  fix rounds

Cost:
  tokens by tier
  model fallback rate
  cache hit rate
  reviewer seats
  dispatch count

Governance:
  audit blocks
  review blocks
  evidence stale blocks
  scope drift blocks
  ownership blocks

Installer:
  release identity
  stale files deleted
  modified stale files blocked
  rollback result
```

---

# 26. Security / Privacy

Telemetry 禁止记录：

- API Key；
- access token；
-完整用户 prompt；
-完整源码；
-数据库密码；
- secrets/env content；
- private customer data。

允许：

- logical tier；
- provider/model identifier；
- token count；
- duration；
- retry；
- hashed path key；
- status/error code；
- numeric cache metrics。

---

# 27. Acceptance Criteria

本 PRD 的 Blocking Acceptance Criteria：

### Release Governance

- AC-01：`master` 有 required GES package gate；
- AC-02：package validator fail 时不能 merge；
- AC-03：force push/default direct push 被限制。

### Work Routing

- AC-04：research_only 单字段不能路由 NONE；
- AC-05：governed/production conflict 必须 FULL；
- AC-06：纯 research 仍能 NONE。

### Risk Routing

- AC-07：structured facts 是主判据；
- AC-08：`No schema migration` 不产生假 FULL；
- AC-09：structured/text contradiction fail closed；
- AC-10：旧 artifact fallback 不产生安全降级。

### Domain

- AC-11：Frontend invalid enum deterministic FAIL；
- AC-12：Backend hard signal deterministic FULL_REQUIRED；
- AC-13：Ops rollback/migration conditional deterministic FAIL；
- AC-14：Domain validator 不获取 Delivery ownership。

### Installer

- AC-15：install-lock.v2 包含 release provenance；
- AC-16：untouched stale package file 自动清理；
- AC-17：modified stale file preserved + blocked；
- AC-18：v1 upgrade 不 destructive；
- AC-19：rollback 100% 恢复。

### Telemetry / Benchmark

- AC-20：requested/actual model tier 可观测；
- AC-21：Token/retry/cache/reviewer 可汇总；
- AC-22：Telemetry 不含 prompt/source/secrets；
- AC-23：4.4.1 vs 5.0 Benchmark 可重复；
- AC-24：Safety Threshold 全部 0 违规；
- AC-25：BOUNDED median token reduction 目标 >=30%，否则不得宣称成本收益已经验证。

### Delivery Truth Regression

- AC-26：现有 Frozen Invariants tests 全部 PASS；
- AC-27：Todo completion interlock 不回退；
- AC-28：TDD/debug freshness 不回退；
- AC-29：Completion Audit/Review/Verification freshness 不回退；
- AC-30：`post_review` commit boundary 不回退。

---

# 28. Definition of Done

只有同时满足以下条件，本 PRD 才可进入 DONE：

```text
[ ] C01-C06 均有 code + test
[ ] Package manifest / SHA256SUMS regenerated
[ ] Full package validator PASS
[ ] Golden Corpus PASS
[ ] Chaos Governance PASS
[ ] Installer v1/v2 migration fixture PASS
[ ] 3 Consumer Pilot / 12 deliveries PASS
[ ] Benchmark report generated
[ ] Safety thresholds 100% PASS
[ ] Quality thresholds PASS
[ ] Cost metrics有可解释结论
[ ] Release identity complete
[ ] Branch protection required check active
[ ] No Frozen Invariant changed
[ ] Baseline promotion review completed
```

注意：

```text
Package Validator PASS
!=
Acceptance DONE
```

---

# 29. Release Decision

最终只允许以下三个 Verdict：

```text
ACCEPT
  Safety/Quality/Release/Consumer Pilot 全部 PASS，
  且没有 Blocking Finding。

ACCEPT_WITH_COST_GAP
  Safety/Quality 全 PASS，
  但 Token/Reviewer 优化未达到目标；
  可继续 Candidate，不得宣称成本目标已完成。

REJECT
  任意 safety invariant、freshness、ownership、scope、
  installer data safety 或 package release identity 出现 Blocking Failure。
```

`ACCEPT_WITH_COST_GAP` 不得自动更新 `BASELINE.md` 为“成本优化已验证”。

---

# 30. Clarification Ledger

| ID | Impact | Question | Decision | Status |
|---|---|---|---|---|
| Q01 | HIGH | PRD v5.0.1 是否等于 Bundle 必须 5.0.1？ | 否。PRD 版本与 Bundle SemVer 分离，Release Review 按 VERSIONING.md 决定。 | CLOSED |
| Q02 | HIGH | Telemetry 是否成为 Final Evidence？ | 否，仅作为运行可观测/Benchmark 数据。 | CLOSED |
| Q03 | HIGH | Structured Risk 是否完全取消 regex？ | 否。Structured 为主，regex 变为 negation-aware fallback/contradiction detector。 | CLOSED |
| Q04 | MEDIUM | v1 install lock 是否立即做 stale cleanup？ | 否，第一次升级 fail-safe，不 destructive；生成 v2 后下次启用。 | CLOSED |
| Q05 | MEDIUM | 是否新增顶层 Skill？ | 否，本轮原则上只加 runtime/test tooling。 | CLOSED |

---

# 31. Architecture Decision Summary

最终目标架构：

```text
                    Request / Roadmap
                           │
                           ▼
                 Work Facts Authority
                           │
                  Work Router v2
                           │
          ┌────────────────┴────────────────┐
          │                                 │
     SPIKE / NONE                      LEAN / FULL
                                            │
                                            ▼
                                  Canonical Stage PRD
                               Routing Facts = risk SOT
                                            │
                      Domain Preplan Semantic Validators
                                            │
                                            ▼
                                     PRD Review
                                            │
                                            ▼
                                    APPROVED PRD
                                            │
                               Risk Facts Snapshot
                                            │
                                            ▼
                                  Canonical Plan v3.7
                                            │
                         Static + Semantic Adaptive Review
                                            │
                                            ▼
             Source Context + Engineering Method + Harness
                       │                      │
                    TDD/Debug           Runtime Telemetry
                       │                      │
                       └──────────┬───────────┘
                                  ▼
                            Delivery Truth
                                  │
                  Audit → Review → Verification
                                  │
                              Evidence
                                  │
                           post_review Commit
                                  │
                           Roadmap DONE

Release Plane:
GitHub Required Package Gate
        +
Package Manifest / SHA
        +
Install Lock v2 / Provenance
        +
Acceptance Corpus / Benchmark
```

---

# 32. Final Product Requirement

本 PRD 交付完成后的 GES 必须能够用工程证据回答六个问题：

1. **这次工作为什么是 NONE / LEAN / FULL？**
2. **风险判断来自什么结构化事实，而不是哪个模型的主观猜测？**
3. **Frontend / Backend / Ops 的设计值是否不仅“填了”，而且“合法”？**
4. **这个 Consumer 到底安装的是哪一组 GES bytes？**
5. **AI 实际使用了哪个模型、多少 Token、多少 retry、多少 cache？**
6. **GES 5 相比 4.4.1 到底是否更便宜，同时没有降低交付质量？**

只有六个问题都能通过 deterministic artifact、test result、telemetry 或 release identity 回答，GES 5 系列才具备进入 Accepted Enterprise Governance Baseline 的充分条件。
