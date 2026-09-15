---
title: "GES v5.0.8 可自适应治理激活与上下文预算强制 PRD"
prd_version: "v5.0.8"
work_item_id: "GES-ADAPTIVE-GOVERNANCE-CONTEXT-BUDGET-5.0.8"
status: "DRAFT"
baseline: "GES v5.0.7"
scope: "Feature Complexity 派生回执 + v3.7 LEAN 闭环 + 阶段化上下文预算 + 缓存新鲜度 + Consumer 事务验收"
language: "简体中文"
supersedes: "patchs/GES-v5.0.8-Feature-Complexity-Router-Lean-Governance-Context-Budget-PRD.md"
governance_profile: "FULL"
source_revision: "e9ae7d4c972aa5d49483c9a095168bf81bfa70c8"
source_prd: "docs/prd/PRD-GES-v5.0.7-Frontend-Context-Scoped-Install.md"
current_feature_slice: "v5.0.7"
current_bundle_version: "5.0.0"
accepted_baseline_bundle: "4.1.2"
target_release_semver: "DEFERRED_TO_RELEASE_REVIEW"
commit_policy: "POST_REVIEW"
pilot_execution: "FORBIDDEN"
benchmark_execution: "FORBIDDEN"
baseline_promotion: "FORBIDDEN"
---

# GES v5.0.8 可自适应治理激活与上下文预算强制 PRD

## 0. 决策摘要

本 PRD 将 v5.0.8 定义为对既有 v5.0.7 能力的闭环增强，而非新建一套 Feature Router、Lean Plan 或交付流水线。目标是在不降低 GES 后半程交付真值的前提下，让风险明确且范围受限的工作以 LEAN 上游路径运行，并对上下文选择、缓存和预算超限施加可审计约束。

必须复用以下权威边界：

- `smc-work-router` 是唯一的工作分类、Work Facts 绑定和治理档位判定者；不得新增 `engineeing-skills/complexity-router/` 或第二个分类真源。
- `smc.plan.v3.7` 是 LEAN 与 FULL 共用的唯一 Plan 契约；不得新增 `smc.ges.lean-plan.v1`。
- `smc-plan-delivery` 是执行、whole-diff review、证据新鲜度、提交门禁和 Roadmap DONE 的唯一真源；LEAN 只能压缩上游材料，不能跳过下游不变量。
- `context-engine` 是预算策略和上下文缓存的唯一实现域；不得创建平行的顶层 `context-budget/` 产品目录。
- v5.0.7 的 Consumer Runtime、Feature Scope、Application Registry 和受限安装语义必须保持兼容。

在锚定提交上，`build_package_manifest.py --check` 已报告 `PACKAGE_MANIFEST_MISMATCH`。包身份恢复是任一 v5.0.8 功能验收、安装或发布准备的 P0 前置条件；不能用功能测试通过掩盖完整性失败。

## 1. 基线与问题陈述

### 1.1 已有能力

v5.0.7 已具备 `smc.ges.work-route.v3`（`SPIKE` / `BOUNDED` / `ARCHITECTURAL` 和 `NONE` / `LEAN` / `FULL`）、Work Facts/仓库绑定、`PROVISIONAL → FROZEN/ESCALATED` 分类状态、统一的 `smc.plan.v3.7`、不削弱 LEAN 交付门禁的 `smc-plan-delivery`、初始 token 策略与内存缓存、以及前端 Application / Feature Scope / Consumer Runtime 受限安装能力。

### 1.2 待闭合缺口

1. Router 尚缺面向 Feature Scope / Consumer 消费的派生回执及统一失败、升级语义。
2. LEAN Plan 已存在，但部分路由文档仍用旧表述暗示不存在受限 Plan 契约，可能诱导重复创建 Plan 类型或绕过 v3.7 必填项。
3. `context-engine` 仍以定性档位和进程内缓存为主，缺少按阶段上限、超限处理、缓存新鲜度、隔离和运行遥测闭环。
4. Consumer 的安装事务、回滚、Feature Scope 隔离和非前端通用路径尚未针对上述闭环给出可验证契约。

### 1.3 不得作出的承诺

- 缓存命中只可减少重复模型上下文，不能免除文件读取、内容校验、测试或证据。
- LEAN 绝不表示“不需要独立审查”或“不需要完整交付验收”。
- Spec Kit 当前为 `ADAPTER_READY` / `UNAVAILABLE`，Superpowers 为 `UPSTREAM_PINNED` 方法提供者；本 PRD 不得把二者表述为外部 Runtime 已执行或 `EXTERNAL_VERIFIED`。
- 本 PRD 不执行 Pilot、Benchmark、真实业务 Consumer 安装或基线版本晋升，只定义仓库级确定性验证。

## 2. 目标与成功判定

为每一个受治理工作项生成由既有 Work Facts 绑定的复杂度/治理派生回执；据此在不削弱交付门禁的前提下选择 LEAN 或 FULL 的上游材料深度，并以可审计的上下文预算控制模型上下文装载。

成功条件：

- 相同且仍新鲜的 Work Facts、仓库内容和 Feature Scope 必须产生确定性一致结论。
- 不完整、未知、过期、越界或高风险事实必须 fail-closed 到 `ARCHITECTURAL/FULL`，或以明确错误阻断。
- 任何保留在生产交付物中的修改都不得进入 SPIKE；“修改按钮文字”只能是 BOUNDED 或因未知/风险提升为 ARCHITECTURAL。
- BOUNDED 工作继续生成并验证 `smc.plan.v3.7`；只可裁剪被规则证明不适用的 FULL 专属叙述深度。
- 预算超限时必须优先复用新鲜缓存、缩小到授权范围，随后升级 FULL 或显式阻断；不得跳过必须证据、审查或验证。
- 安装、更新和回滚必须保持 v5.0.7 Consumer 的应用隔离；新增运行时文件必须纳入事务和 `owned_files` 回滚记录。

## 3. 修订后的目标结构

```text
已绑定 Work Facts + 仓库内容 + 可选 Feature Scope v1
                         |
                         v
              smc-work-router（唯一分类权威）
                         |
                         +--> smc.ges.work-route.v3（既有权威路由）
                         |
                         +--> smc.ges.feature-complexity.v1（派生回执，非第二分类器）
                         v
  context-engine（预算策略、范围裁剪、缓存新鲜度、阶段遥测）
                         |
                         v
PRD Grounding / smc.plan.v3.7（LEAN 或 FULL 上游深度）
                         |
                         v
smc-plan-delivery（不变：执行、独立审查、验证、证据、提交门禁）
                         |
                         v
                    Delivery Truth
```

Feature Scope 是前端工作的重要输入，但不是 Router 的前置单点依赖。没有前端 Scope 的后端、运维或通用工作仍依赖 Work Facts 正常路由；只有请求明确声称受某应用/Surface 约束但 Scope 无法验证时，才升级或阻断。

## 4. 范围、非范围与不变量

### 4.1 In Scope

1. 恢复并强制检查包清单的字节级身份一致性。
2. 在既有 `smc-work-router` 内补足 Feature Complexity 派生回执、失败码和升级语义。
3. 统一 v3.7 LEAN/FULL 的入口说明、校验和交付闭环，修正过时路由文档。
4. 在既有 `context-engine` 内增加阶段预算策略、缓存新鲜度/隔离、超限处理和最小遥测。
5. 扩展 Consumer Runtime 的受限安装、事务回滚和验收覆盖。

### 4.2 Out of Scope

- 新建独立 `complexity-router/`、`context-budget/`、`smc.ges.lean-plan.v1`、第二份 Plan Validator 或第二条 Delivery Pipeline。
- 变更 Work Facts 的授权模型、绕过 provenance、将调用者 `true` 的安全事实降为 `false`，或改变既有 fail-closed 边界。
- 降低 `smc-plan-delivery` 的 whole-diff review、验证、证据新鲜度、提交门禁或 Roadmap DONE。
- 将 Spec Kit 或 Superpowers 标记为外部 Runtime 已验证，或引入未经验证的外部 CLI 依赖。
- 执行 Pilot、Benchmark、生产调用、真实项目安装或 accepted baseline / bundle 发布版本升级。

### 4.3 不变量

| ID | 不变量 |
| --- | --- |
| I01 | Router 只存在一个权威实现：`smc-work-router`。 |
| I02 | `smc.plan.v3.7` 是 LEAN/FULL 唯一 Plan Schema，公共必填项不可用 `N/A` 规避。 |
| I03 | LEAN 仅减少上游上下文和非适用 FULL 专属材料；交付后半程关口全部保留。 |
| I04 | 未知、陈旧、缺 provenance、作用域越界和高风险均不得导向 LEAN。 |
| I05 | 缓存复用前必须验证内容摘要、作用域、解析器/策略版本和仓库身份。 |
| I06 | 预算控制只能减少重复模型上下文，不能删除必需证据、测试、审查或验证。 |
| I07 | Consumer 安装/回滚只能触及受管路径，并保持事务原子性。 |

## 5. 变更包与权威归属

| 变更 | 归属 | 结果 | 禁止的平行实现 |
| --- | --- | --- | --- |
| C30 包身份恢复 | manifest 与安装验证 | 清单和已跟踪文件摘要一致 | 忽略/默认值掩盖 mismatch |
| C31 分类派生回执 | `smc-work-router` | 基于 `work-route.v3` 的 `feature-complexity.v1` | 新 Router、独立重算 |
| C32 LEAN 链路闭环 | Plan author / validator / delivery | 统一 `smc.plan.v3.7` | `lean-plan.v1`、LEAN 专属 delivery |
| C33 阶段预算策略 | `context-engine` | `context-budget.v1` 决策与超限规则 | 顶层 `context-budget/` 产品域 |
| C34 缓存与上下文胶囊 | `context-engine` 与 source context | 可验证的新鲜复用与失效 | 无摘要 app+path 缓存 |
| C35 Consumer、遥测与验收 | Consumer Runtime / metrics / acceptance | 可安装、可回滚、可断言闭环 | 仅文档声明的升级 |

## 6. C30：包身份恢复（P0）

在 C31-C35 的任一实现或发布验收前，必须运行：

```powershell
python engineeing-skills/build_package_manifest.py --check
```

命令必须返回 `PACKAGE_MANIFEST_VALID`。`PACKAGE_MANIFEST_MISMATCH` 所列已跟踪文件必须通过受审查的 manifest 重建或受审查的内容恢复达到一致；不得修改验证器以接受不一致，也不得把清单检查降为告警。

未满足时，最终 acceptance、安装试验和发布准备均为 `BLOCKED_BASELINE_INTEGRITY`。该恢复不等同于 bundle 版本晋升，版本仍由独立发布评审决定。

## 7. C31：既有 Router 内的 Feature Complexity 派生回执

### 7.1 输入与权威性

`smc-work-router` 继续以受绑定的 Work Facts、仓库内容和分类状态作为权威输入。Feature Scope v1 在存在时作为受校验的作用域证据；它不能覆盖 Work Facts 中的安全事实、风险事实或 provenance。

Router 必须先生成既有 `smc.ges.work-route.v3`，再派生 `smc.ges.feature-complexity.v1`。后者是前端/Consumer/预算策略的稳定消费回执，不得重新计算、覆盖或降级 `work-route.v3`。

### 7.2 `smc.ges.feature-complexity.v1` 最小字段

```yaml
schema: smc.ges.feature-complexity.v1
work_item_id: <non-empty>
repo_identity: <canonical repository identity>
work_facts_digest: sha256:<digest>
work_route_schema: smc.ges.work-route.v3
work_route_digest: sha256:<digest>
feature_scope_digest: sha256:<digest-or-absent>
work_class: SPIKE | BOUNDED | ARCHITECTURAL
governance_profile: NONE | LEAN | FULL
classification_state: PROVISIONAL | FROZEN | ESCALATED
reasons: [<stable reason code>]
generated_at: <UTC RFC3339>
```

回执不得含源文件原文、令牌、凭据、完整提示词或可绕过 Work Facts 的调用方布尔值。

### 7.3 分类与升级规则

| 情形 | 允许结论 | 强制行为 |
| --- | --- | --- |
| 全部为探索、无生产保留物、无受控写入 | `SPIKE/NONE` | 输出 Decision Record；一旦保留生产改动即重新路由。 |
| 已有明确 owner/contract、范围有限、验证确定、无边界/敏感风险 | `BOUNDED/LEAN` | 进入 v3.7 LEAN 上游路径。 |
| 新模块/应用、公开契约、认证授权、数据模型、所有权迁移、跨边界、风险未知或事实陈旧 | `ARCHITECTURAL/FULL` | 完整上游材料与既有交付路径。 |
| 可保留生产文字改动 | `BOUNDED/LEAN` 或 `ARCHITECTURAL/FULL` | 绝不允许 SPIKE；Owner/Scope 不可证明时提升 FULL。 |
| 已产生受治理 PRD、Plan 或交付物 | 原路径或更高路径 | 不得借重新分类离开 canonical pipeline。 |

`NONE → LEAN → FULL` 只能单向升级。仅在生产写入前、证据补全后，才可依据既有 `classification_state` 机制受控纠正；纠正必须保存前后摘要和 reason code。解析错误、路径越界、Work Facts 缺 provenance、路由绑定失败或输入摘要不匹配都必须输出明确失败码（如 `WORK_FACTS_UNVERIFIED`、`ROUTE_BINDING_STALE`、`FEATURE_SCOPE_INVALID`），并不得生成 LEAN 许可。

## 8. C32：v3.7 LEAN 上游路径闭环

所有 BOUNDED 工作继续生成 `smc.plan.v3.7`，以 `governance_profile: LEAN` 表达上游深度；不得引入 `smc.ges.lean-plan.v1` 或任何脱离 v3.7 Validator 的简版计划。

以下内容在 LEAN/FULL 中均为强制且不可 `N/A`：Change Matrix / write ownership、需求覆盖、Todo 与依赖、Verification Ledger、Domain Activation Ledger、Test Asset Ledger、验收策略和提交策略。

在派生回执仍新鲜、所有前置条件可证明且不存在 FULL 触发器时，LEAN 可将 Grounding 限定为授权应用、Surface、owner、相关测试和直接契约；未受影响领域可记录可验证的“不适用依据”，而非复制完整材料；也可复用已验证的新鲜上下文胶囊。

无论 LEAN/FULL，`smc-plan-delivery` 必须执行现有静态/语义校验、工作区/执行检查、whole-diff 独立审查、验证、证据新鲜度、提交门禁和 Roadmap DONE。实现必须修正 `artifact-state-routing.md` 中与 v3.7 LEAN 路径不一致的旧叙述并有回归测试。

## 9. C33：阶段化上下文预算策略

### 9.1 归属与决策记录

在 `engineeing-skills/context-engine/` 内扩展 `token_budget.py`，可新增同域 `policy.py` / `budget_controller.py`。输出为 `smc.ges.context-budget.v1` 决策记录，而非新产品根目录。

```yaml
schema: smc.ges.context-budget.v1
work_item_id: <non-empty>
repo_identity: <canonical identity>
governance_profile: NONE | LEAN | FULL
work_route_digest: sha256:<digest>
feature_scope_digest: sha256:<digest-or-absent>
policy_version: <version>
policy_digest: sha256:<digest>
phases:
  - name: routing | grounding | planning | implementation | review | final_verification
    max_files: <positive integer>
    max_source_capsules: <positive integer>
    max_context_tokens: <positive integer>
    max_model_tier: <policy tier>
    independent_review: <boolean>
```

具体数字必须在受版本控制、可审查的策略数据中；不得由调用方猜测，也不得把模型供应商 token 上限伪装为治理预算。既有定性档位可作为初始策略来源，但必须规范化为可校验记录。

### 9.2 阶段策略与超限

| 阶段 | LEAN 默认范围 | FULL 默认范围 | 不可省略项 |
| --- | --- | --- | --- |
| routing | Work Facts、路由规则、必要 Scope | 加全部风险/边界证据 | 事实绑定与 provenance |
| grounding | 应用/Surface/owner/直接测试 | 跨模块、契约、架构材料 | 来源摘要与新鲜度 |
| planning | v3.7 必填字段最小证据 | 完整架构影响材料 | v3.7 公共必填项 |
| implementation | 授权写入面和相关测试 | 全部受影响写入面 | 所有权 |
| review / final verification | 全量实际 diff、验证证据 | 同左加风险证据 | 独立审查、验证、证据门禁 |

超限时顺序固定为：复用摘要/范围/策略/内容均有效的胶囊；去除作用域外或重复候选；无法容纳强制证据时 `LEAN → FULL` 并重新生成预算；FULL 仍不足则 `CONTEXT_BUDGET_INSUFFICIENT` 阻断阶段。禁止截断必须契约、跳过测试/独立审查、降低验证深度或伪造 `cache_hit`。最终审查永远基于实际 whole diff，绝不因 LEAN 改为局部 diff。

## 10. C34：上下文缓存、新鲜度与隔离

扩展既有 `engineeing-skills/context-engine/context_cache.py`。可保留进程内缓存，并增加受控的工作项级内容胶囊；胶囊是可再生缓存，绝非 PRD、Plan、证据或交付真源。

持久化位置必须位于项目运行目录（如 `.smc/runs/<work-item-id>/context/`），不得写入包安装根目录、Consumer 业务目录或不受管全局目录。安装器不得把运行时缓存作为受管 Consumer 文件交付。

每个胶囊键至少绑定：

```text
repo_identity
+ artifact_kind (SOURCE | PRD_SECTION | PLAN_SECTION | FEATURE_SCOPE | TEST_EVIDENCE)
+ scope_digest
+ canonical path / symbol / section identity
+ content_sha256
+ extractor_version
+ policy_digest
```

复用前必须验证仓库身份、路径 containment、当前内容摘要、作用域摘要、抽取器版本和策略摘要。任一不一致即 cache miss 并重新提取；不得跨仓库、跨工作项未授权范围或跨策略复用。

- 路径必须在解析后的项目根内，拒绝绝对逃逸、`..` 逃逸和符号链接绕界。
- 不缓存密钥、令牌、环境变量值或敏感原文；遥测只记录摘要、计数和大小。
- 写入使用临时文件和原子替换；部分写入、校验失败或并发冲突不得被读作命中。
- 需有可配置 TTL / 容量上限和按工作项清理；清理失败仅告警，不能删除项目外文件或影响交付真源。
- 缓存异常一律 fail-safe 为 miss，随后走预算超限处置。

## 11. C35：Consumer 升级、遥测与兼容性

v5.0.8 Consumer 必须兼容 v5.0.7 实际目录：`.agents/ges/frontend/apps/<app-id>/`、既有 frontend runtime 与 surface/feature scope 文件；不得使用不存在的 `frontend/applications` 作为迁移目标。

安装器必须先校验 Package Manifest、Consumer Profile 和路径 containment；随后在单一事务中安装 Router 回执消费、预算策略/运行时和必要验收资源；将新增/替换受管文件记录到 transaction records 与 `owned_files`；任何后续写入失败时撤销 receipt、兼容指针、锁文件和运行时文件；保留未受管 sibling 应用、Consumer 源码和历史 v5.0.7 Scope。回滚必须继续对 `resolve()` 结果进行 containment 校验，拒绝 manifest 里越出项目根的条目。

Feature Scope 有效时可纳入 route / budget 绑定；没有 Feature Scope 的非前端工作仍由 Work Facts 路由。若工作明确声明应用/Surface，而 Scope 缺失、摘要不符或越界，必须升级 FULL 或阻断。

扩展既有 `runtime_metrics` 的完整性输出，至少记录 work-item 摘要、profile、route/policy 摘要、各阶段预算分配/实际使用、候选数、cache hit/miss/stale、超限、升级和阻断 reason code。不得记录源码、PRD/Plan 原文、提示词、凭据或把“节省 token”作为无实测证据的收益声明。

## 12. 失败语义

| 代码 | 触发 | 强制结果 |
| --- | --- | --- |
| `PACKAGE_MANIFEST_MISMATCH` | 包清单与文件摘要不一致 | 阻断安装、最终验收和发布准备。 |
| `WORK_FACTS_UNVERIFIED` | 缺 provenance、签名/绑定失败或安全事实冲突 | 阻断 LEAN；默认 FULL 或阻断。 |
| `ROUTE_BINDING_STALE` | 仓库、Facts 或路由摘要变更 | 重新路由；不得复用 LEAN 许可。 |
| `FEATURE_SCOPE_INVALID` | Scope 缺失、摘要不符或越界 | 明确声明 Scope 时升级 FULL 或阻断。 |
| `CLASSIFICATION_DOWNGRADE_DENIED` | 已冻结/交付状态试图降低档位 | 保持原档位并输出审计原因。 |
| `CONTEXT_CACHE_STALE` | 任一缓存键项不匹配 | 作为 miss，不得使用内容。 |
| `CONTEXT_BUDGET_INSUFFICIENT` | FULL 仍无法装载强制证据 | 阻断，不得省略关口。 |
| `INSTALL_TRANSACTION_ROLLBACK` | 任一安装步骤失败 | 回滚全部受管写入，不能残留成功 receipt。 |

## 13. 迁移与版本策略

1. `smc.ges.work-route.v3` 继续可读；`feature-complexity.v1` 仅是可重建派生回执。
2. 不迁移已有 v3.3-v3.6 Plan；新建或重新规划工作仍依既有规则使用 v3.7。
3. 不迁移旧缓存；键不完整或版本不符一律安全失效为 miss。
4. v5.0.7 Consumer Profile / Feature Scope 保持兼容；没有新增 runtime capability 的 Consumer 不得被误报为 v5.0.8 已启用。
5. `current_feature_slice`、`current_bundle_version` 与 `accepted_baseline_bundle` 是不同概念，receipt、安装和发布文档必须分别表达；本 PRD 不授权改变它们。

## 14. 文件与验收矩阵

实现计划须在落地前补齐精确文件清单。以下是允许的归属范围，不是预创建文件指令。

| 域 | 预期修改位置 | 验证重点 |
| --- | --- | --- |
| Router | `.agents/skills/smc-work-router/scripts/` 与 references/tests | 单一权威、派生回执、单向升级、fail-closed。 |
| Plan / Delivery | Plan author、validator、`smc-plan-delivery` | v3.7 复用、LEAN 不变量、全量 review。 |
| Context | `context-engine/` 与 source-context 接口 | 策略版本、预算、缓存键、新鲜度、超限。 |
| Consumer | `consumer-bootstrap/`、`install*.py`、`rollback.py`、profile | 事务性、containment、v5.0.7 隔离。 |
| Acceptance | `acceptance/`、`tests/`、skill-local tests | 确定性的正反例，不依赖 Pilot。 |
| Docs | routing / plan / consumer references、CHANGELOG、manifest | 清除旧术语与包身份。 |

每个实现文件必须在计划中映射至需求、所有者、测试与证据；超出矩阵的新顶层产品域须另行 PRD 评审。

## 15. 验收方案

既有 G01-G50 必须持续通过。新增编号从 G51 开始，避免与 v5.0.7 的 G43-G50 冲突；全部测试必须本地、确定性、可复现，不执行 Pilot / Benchmark。

| ID | 场景 | 期望 |
| --- | --- | --- |
| G51 | 同一绑定 Facts + Scope 多次路由 | 仅由 `smc-work-router` 生成一致 route 和派生回执，摘要可验证。 |
| G52 | 缺 provenance、过期绑定或未知风险 | 不能得到 LEAN；明确失败或 `ARCHITECTURAL/FULL`。 |
| G53 | 有 owner 的生产文字改动 | 只能 BOUNDED/LEAN 或提升 FULL，绝不 SPIKE。 |
| G54 | 已有 PRD/Plan/交付物后请求降级 | 拒绝降级并保留 canonical pipeline。 |
| G55 | BOUNDED 计划并交付 | `smc.plan.v3.7`，公共账本完整，whole-diff review/验证/证据门禁仍执行。 |
| G56 | 相同内容、范围和策略的重复上下文请求 | 所有缓存键项一致才命中；命中不省略内容摘要校验。 |
| G57 | 源码、Scope、策略或 repo 身份改变 | stale/miss；不得跨应用、仓库或策略复用。 |
| G58 | LEAN 超过阶段预算 | 先裁剪非必需项，再升 FULL；FULL 仍不足则阻断。 |
| G59 | scoped Consumer 更新与失败回滚 | 只触及受管路径，保留 sibling app，失败后无 receipt/lock/runtime 残留。 |
| G60 | 运行遥测 | 记录预算、命中/失效、升级/阻断摘要，不泄露内容或凭据。 |

强制验证顺序：

1. `python engineeing-skills/build_package_manifest.py --check`；
2. Router、context-engine、Plan Validator、Consumer/rollback 的定向正反测试；
3. `python engineeing-skills/acceptance/run_acceptance.py`，覆盖 G01-G50 和 G51-G60；
4. 安装器临时目标的 install / idempotency / forced-failure rollback 测试；
5. 文档、manifest、whole-diff review 和提交门禁。

任一步失败不得被其他步骤通过而豁免。

## 16. Definition of Done

- [ ] C30 已使 Package Manifest 校验通过，且未改弱完整性门禁。
- [ ] Router 仍只有 `smc-work-router` 一个权威实现，派生回执受绑定且可审计。
- [ ] 未知/陈旧/越界/高风险 fail-closed；生产保留改动永不路由为 SPIKE。
- [ ] BOUNDED 使用 `smc.plan.v3.7` LEAN，不存在平行 plan schema 或绕过公共账本。
- [ ] LEAN 与 FULL 一样完成 whole-diff review、验证、证据新鲜度、提交门禁和 Roadmap DONE。
- [ ] 阶段预算、超限、缓存键、新鲜度、隔离和原子写入都有正反测试。
- [ ] Consumer 升级/回滚事务化，遵守 containment 且保留 v5.0.7 sibling 应用。
- [ ] G01-G50 与 G51-G60 全通过；没有执行 Pilot、Benchmark 或真实项目安装。
- [ ] Spec Kit / Superpowers 状态声明与 provider receipt 一致，未夸大为外部 Runtime 已验证。
- [ ] 文档、CHANGELOG、manifest 和架构索引随实现更新，并通过 `lat check`。

## 17. 最终架构结论

v5.0.8 的正确结构不是在 GES 外侧叠加三个新系统，而是闭合既有边界：Spec Kit 继续提供前半程 UX 适配语义，Superpowers 继续提供中段方法论能力，GES 以 Work Facts 绑定的 Router、v3.7 Plan、Context Engine 和 `smc-plan-delivery` 保留唯一交付真值。复杂度只能决定上游材料与上下文预算，永远不能决定是否跳过可验证交付。

## 18. 评审核验记录（DRAFT 转正前检查）

本 PRD 由 `patchs/GES-v5.0.8-Feature-Complexity-Router-Lean-Governance-Context-Budget-PRD.md` 评审转正，核验于 `source_revision` 锚定提交，未修改任何代码。

| 核验项 | 结果 |
| --- | --- |
| Frontmatter / 章节结构（0–17 + 本记录） | 通过；与 v5.0.7 正式 PRD 体例一致 |
| C30 前置断言可复现 | 通过；`build_package_manifest.py --check` 在锚定提交报告 `PACKAGE_MANIFEST_MISMATCH`（3 个已跟踪文件摘要与清单不一致），P0 前置属实 |
| C31 权威锚点 | 通过；`work_router.py` 已产出 `smc.ges.work-route.v3`，无平行 Router |
| C32 契约锚点 | 通过；`contract_resolver.CURRENT_PLAN_CONTRACT = smc.plan.v3.7`，validator/delivery 已绑定 |
| C33/C34 实现域 | 通过；`context-engine/token_budget.py#budget_for`、`context_cache.py#ContextCache` 存在 |
| C35 事务锚点 | 通过；installer 已有 receipt → lock → rollback 链与 containment 校验 |
| 旧文档修正目标 | 通过；`artifact-state-routing.md` 存在于 `smc-work-router/references/` 与 `using-superpowers/references/` |
| 验收编号 | 通过；G51–G60 与既有 G01–G50 无冲突 |
| 架构索引 | 通过；`lat.md/ges/adaptive-governance-context-v508.md` 已登记且 `lat check` 通过 |
