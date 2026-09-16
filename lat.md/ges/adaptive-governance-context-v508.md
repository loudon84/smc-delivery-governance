# v5.0.8 可自适应治理与上下文预算

本设计记录 v5.0.8 如何复用既有 Router、Plan 和 Delivery 真源，以可验证的预算控制减少重复上下文，而不降低交付门禁。

## 单一权威边界

工作复杂度由 [[engineeing-skills/.agents/skills/smc-work-router/scripts/work_router.py#route_bound]] 绑定 Work Facts 与仓库内容后裁决，v5.0.8 只能产生供 Consumer 使用的派生回执，不能创建平行 Router 或覆盖原路由。

`smc.plan.v3.7` 是 LEAN 和 FULL 共用的唯一计划契约。LEAN 可缩减上游材料深度，但 [[plan-delivery]] 的 whole-diff review、验证、证据新鲜度、提交门禁和 Roadmap DONE 仍为所有档位的交付不变量。

派生回执由 [[engineeing-skills/.agents/skills/smc-work-router/scripts/work_router.py#derive_feature_complexity]] 在已有 `smc.ges.work-route.v3` 上生成 `smc.ges.feature-complexity.v1`。Feature Scope 只提供 `feature_scope_digest`；声称受 app/Surface 约束但 Scope 缺失或无效时标记 `FEATURE_SCOPE_INVALID` 并拒绝 LEAN 许可。

## 分类与升级

SPIKE 仅限无生产保留物的探索；任何生产修改至少为 BOUNDED，并在事实不完整、边界变化或风险未知时升级为 ARCHITECTURAL/FULL。治理档位只能从 NONE 到 LEAN 再到 FULL 单向升级，生产写入前的受控纠正必须留下审计原因。

现有 [[engineeing-skills/.agents/skills/smc-work-router/scripts/classification_state.py#apply_profile]] 负责承载分类状态的冻结和升级规则；冻结后降档失败码为 `CLASSIFICATION_DOWNGRADE_DENIED`（`CLASSIFICATION_DOWNGRADE_FORBIDDEN` 作一期别名）。Feature Scope 不能覆盖 Work Facts 的 provenance 或安全事实。

## 上下文预算与缓存

阶段预算由 [[engineeing-skills/context-engine/budget_controller.py#decide_budget]] 读取版本化策略 `context-engine/policies/context-budget.v1.json` 生成 `smc.ges.context-budget.v1`，并与路由、作用域、仓库身份和策略摘要绑定。`token_budget.budget_for` 保持向后兼容；work-scope 可附带 `context_budget` 决策但不替代旧 `token_budget` 字段。

预算超限顺序：裁剪越界/重复候选 → LEAN 升 FULL 重生预算 → 仍不足则 `CONTEXT_BUDGET_INSUFFICIENT` 阻断；不得跳过测试、审查或验证。审查与 final_verification 相位在新策略中要求独立审查，而不改写旧 LEAN `independent_review=False` 定性字段。

[[engineeing-skills/context-engine/context_cache.py#ContextCache]] 保留 `app_id|path|sha` API。[[engineeing-skills/context-engine/context_cache.py#CapsuleStore]] 使用 `repo_identity + artifact_kind + scope_digest + identity + content_sha256 + extractor_version + policy_digest` 键，可选落盘 `.smc/runs/<work-item-id>/context/`（项目根 containment、原子替换、TTL/容量）。缓存只减少重复模型注入，是可再生数据，绝不替代 PRD、Plan、证据或交付真源，也不缓存密钥原文。

## 安装与验证前置

任何 v5.0.8 验收或 Consumer 安装前，Package Manifest 必须验证通过并输出 `PACKAGE_MANIFEST_VALID`；清单不一致会阻断安装和发布准备。安装事务必须记录新增受管文件并在失败时连同 receipt、锁和兼容指针一并回滚，同时保留 v5.0.7 Consumer 的应用隔离。遥测 summarize 只汇总 digest、相位配额/实际、cache hit/miss/stale 与升级/阻断原因，禁止源码/提示词/凭据。

## Acceptance G51–G60

扩展既有 golden 语料，覆盖 Router 派生回执、生产改动不进 SPIKE、v3.7 LEAN 闭环、缓存新鲜度、预算超限、Consumer 回滚和脱敏遥测；报告 `golden: G01-G60`。v5.0.8 不执行 Pilot、Benchmark、真实项目安装或基线晋升。

### G51 Deterministic Complexity Receipt

同一绑定 Facts + Scope 两次派生回执的 route/scope digest 必须一致。

### G52 Missing Provenance Not Lean

缺 provenance 或未验证 Work Facts 不得得到 LEAN；路由或派生回执升 FULL / ARCHITECTURAL。

### G53 Production Text Never Spike

有 owner 的生产保留文字改动绝不能路由为 SPIKE/NONE。

### G54 Downgrade Denied

分类状态 FROZEN 后请求降档必须失败并返回 `CLASSIFICATION_DOWNGRADE_DENIED`。

### G55 Lean Plan Delivery Gates

BOUNDED 使用 `smc.plan.v3.7` + LEAN；公共账本不可 `N/A`；delivery 仍绑定当前契约。

### G56 Cache Hit

相同胶囊键字段全部一致时命中，并校验内容摘要绑定。

### G57 Cache Stale

策略/范围/身份变化不得跨键复用；过期绑定记为 stale。

### G58 Budget Escalate Or Block

LEAN 超限先升 FULL；FULL 仍不足则 `CONTEXT_BUDGET_INSUFFICIENT`。

### G59 Install Rollback Sibling

临时仓 install 失败回滚后无 receipt/lock/runtime 残留，且 sibling app baseline 保留。

### G60 Telemetry Redacted

遥测拒绝敏感原文字段，摘要只含 digest 与计数类预算/缓存指标。
