# SMC Governance Engineering Skills — Governance Standard v1.0

> **Normative document.** 本文定义 `smc-delivery-governance/engineeing-skills` 的公司级维护与演进规则。出现冲突时，本文优先于单个业务项目中的本地说明。

## 1. 身份与唯一权威源

产品名称：**SMC Governance Engineering Skills**（简称 **GES**）。

唯一权威源（Canonical Source of Truth / SOT）：

```text
Repository : loudon84/smc-delivery-governance
Branch     : master
Directory  : engineeing-skills/
```

`engineeing-skills` 是当前已经投入使用的物理目录名。虽然英文拼写历史上存在偏差，但从本治理基线开始将其视为**稳定仓库路径**。任何重命名都必须作为显式迁移实施，不允许工程师在普通重构中自行改名。

业务仓库中的 `.agents/skills`、`.cursor/skills`、生成的 ZIP、临时 patch、个人分支中的复制件都属于 **consumer copy / release artifact**，不得成为反向覆盖中央 SOT 的依据。

## 2. 产品定位

GES 是公司内部项目开发使用的统一 **AI/Agent 工程治理工作流标准**，不是 NodeSkClaw 专属 Skill 包。

标准流程：

```text
Architecture
  -> Roadmap
  -> Stage PRD
       -> Grounding
       -> Review
       -> Converge
  -> APPROVED PRD
  -> Canonical Plan
  -> Plan Delivery
       -> Static Gate
       -> Semantic Gate
       -> Execution
       -> Completion Audit
       -> Implementation Review
       -> Verification
       -> Evidence Freshness
       -> post_review Commit
       -> Roadmap Update
```

业务项目可以使用不同技术栈、目录布局、测试命令和项目级 validator；但不得通过项目定制改变上述治理语义。

## 3. Core 与 Consumer 的边界

GES 必须按两层维护：

### 3.1 Core Governance Baseline

公司所有接入项目共同遵守，包含：

- Architecture / Roadmap / PRD / Plan / Delivery 生命周期；
- Artifact owner；
- Plan、Todo runtime、Proof、Delivery 四类状态分离；
- Static / Semantic / Execution / Audit / Review / Verification 门禁；
- evidence freshness；
- `post_review` commit policy；
- canonical Plan 单一性；
- Review / Verification 与 working-tree content fingerprint 绑定；
- Roadmap DONE 必须由真实 implementation commit 与可审计 evidence 支撑。

### 3.2 Consumer Integration Profile

项目或项目族自行定义，但必须服从 Core：

- Skill 安装目录；
- 是否存在 `.cursor/skills` 镜像；
- 项目级 baseline dependency；
- 项目级 validator；
- 项目自身 references / rules / lock 文件；
- build/test/lint/typecheck 命令；
- durable evidence 的项目落点；
- 允许保留的项目自有 Skill。

`nodeskclaw` 是第一个 Consumer Profile，不是 Core Governance 的定义者。

## 4. 不可弱化的工程不变量

以下规则属于 **Frozen Invariants**。任何 Skill、脚本或 consumer adapter 都不得通过“兼容”“简化流程”“提高效率”等理由静默绕过：

1. **Single Canonical Plan**：同一 delivery item 只允许一个 canonical Plan identity。
2. **Static PASS != Implementation Complete**。
3. **Todo completed != Plan proven != Implementation committed != Roadmap DONE**。
4. **Semantic Review 必须独立于 Static Validator**。
5. **Completion Audit 必须重新核对 Plan × actual diff**，不得只相信 Todo 状态。
6. **Implementation Review 必须基于当前实现内容**。
7. **Blocking Verification 必须产生可核验 evidence**。
8. **Evidence / Review / Audit 必须具备 FRESH / STALE / MISSING 语义**。
9. **实现内容发生变化后旧 proof 必须失效**。
10. **`post_review`**：implementation commit 只能发生在 Audit + Review + Verification 全部通过之后。
11. **Roadmap DONE 是后续 delivery state update，不得与实现证明混为一层状态**。
12. **Single Writer / ownership-aware slicing 不得被并行执行破坏**。
13. 不得新增第二个与 `smc-plan-delivery` 并列的 production delivery owner。
14. 不得以 `--skip-*`、`--no-*` 选项作为生产成功路径；诊断逃生口不能成为验收策略。

改变上述任一规则均属于 **MAJOR governance change**。

## 5. Artifact Ownership

| Artifact / State | Canonical Owner |
|---|---|
| Architecture Decision | `smc-architecture-decision` |
| Architecture Review | `smc-architecture-review` |
| Roadmap / Delivery state | `smc-roadmap` |
| Stage PRD grounding | `smc-prd-grounding` |
| Stage PRD review | `smc-prd-review` |
| Stage PRD converge / approval | `smc-prd-converge` |
| Canonical Plan author | `smc-plan-from-approved-prd-ponytail` |
| Plan static truth | `smc-plan-validator` |
| Plan semantic truth | `smc-plan-review` |
| Plan delivery sequencing | `smc-plan-delivery` |
| Todo implementation | `executing-plans` / `subagent-driven-development` |
| Implementation semantic review | `code-review-and-quality` |
| Verification truthfulness | `verification-before-completion` + delivery evidence layer |

Skill 可以调用其它 owner，但不得夺取其 canonical state 写权限。

## 6. 中央修改原则

所有 Core 变更必须首先发生在中央 SOT：

```text
central proposal / issue
  -> branch
  -> code + contract + tests
  -> package validation
  -> consumer compatibility validation
  -> review
  -> merge to master
  -> immutable release
  -> consumer upgrade
```

禁止：

```text
consumer repo local edit
  -> "看起来可用"
  -> copy back to central master
```

如果问题最先在 consumer 项目中发现，可以先制作最小复现或临时 patch，但正式修复必须重新落回中央分支、补回归测试并通过发布门禁。

## 7. 兼容原则

GES 必须同时考虑：

- Contract compatibility；
- Skill version compatibility；
- Consumer integration compatibility；
- OS/path compatibility；
- historical in-flight artifact compatibility。

Legacy artifact 不做无理由批量迁移。迁移必须：

- 显式；
- 可验证；
- fail-closed；
- 保留原始语义；
- 不把历史状态伪装成新流程 PASS。

## 8. 安全失败原则

所有治理门禁默认 **fail-closed**。

允许失败并回滚；不允许失败后继续标记成功。

安装器、迁移器、commit guard、Roadmap updater 等写操作必须满足：

- dry-run/preflight；
- 原状态可恢复；
- 写入过程可审计；
- post-write validation；
- failure rollback；
- 不自动伪造 commit / evidence / PASS verdict。

## 9. Consumer Validator 的定位

项目级 validator 属于 **Consumer Acceptance Gate**，不等同于 Core Package Self-Test。

因此报告必须区分：

```text
CORE_VALIDATION
CONSUMER_INTEGRATION_VALIDATION
```

例如 consumer 的 `.agents` / `.cursor` 全树镜像 drift 可以导致 consumer acceptance 失败，但不能反向证明 `smc-plan-delivery` self-test 失败。

安装仍应 rollback，因为目标项目未达到声明的 acceptance contract；但根因必须归类到正确层级。

## 10. Governance 文档权威顺序

发生语义冲突时按以下顺序解释：

1. `GOVERNANCE.md`
2. `governance/baseline.yaml`
3. `BASELINE.md`
4. `docs/PIPELINE-CONTRACT.md`
5. Skill 自身 `SKILL.md` / references contract
6. `CONSUMER-INTEGRATION.md`
7. consumer project local documentation

consumer 文档不得覆盖 Core Frozen Invariants。
