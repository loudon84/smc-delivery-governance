# GES Runtime Cost Optimization

GES 4.4 在不改变 `smc.plan.v3.6`、Test Asset 或 Delivery truth ownership 的前提下，减少不必要的上下文重读、重复审查和同型任务调度。

## Complexity Routing

新请求先以 SPIKE、BOUNDED、ARCHITECTURAL 分类，且在同一请求中只能向更高风险等级升级。

只有未引用任何 governed artifact、已有稳定 owner 和可证明 focused verification 的 BOUNDED 工作可走项目轻量流程。已有 Architecture、Roadmap、PRD 或 Plan 的任务仍必须走 [[pipeline#GES Pipeline#Stages]]，不能以成本为由降级。

## Adaptive Plan Review

Plan review 保持 `NOT_REQUIRED | REQUIRED` 的外部协议，并以 NONE、DELTA、FULL 缩小安全的语义读取范围。

首次、acceptance、LIVE/FAULT/EXTERNAL、owner/boundary/security/schema/protocol/concurrency/lifecycle 风险一律 FULL。只有已有 fresh PASS snapshot 且无这些风险的语义变更才能 DELTA；缺 snapshot 必须 fail-closed 升级 FULL。

## Task Context Artifacts

Delivery 为单个 Todo 生成 brief、report path 和 write-scoped review package，作为 worker/reviewer 的派生输入。

这些文件落在 `.smc/runs/<plan_id>/`，仅投影当前 Todo 的约束、写集与 diff。它们不得改写 canonical Plan、Cursor Todo、Review record 或 evidence，且仍受 [[plan-delivery#Plan Delivery#Workspace Scope]] 和 [[test-assets]] 约束。

## Engineering Method Runtime

Engineering Method Runtime 为已清场 Todo 派生 MECHANICAL、BEHAVIOR_CHANGE、BUG_FIX 或 HIGH_RISK 的执行方法，且不新增 artifact owner 或 delivery state。

它将 TDD、systematic debugging、model tier 与 UNIFIED/INDEPENDENT task review 记录在 `.smc/runs/<plan_id>/engineering/`。artifact 必须绑定当前 semantic Plan hash；缺失时可重新分类，损坏或过期则必须阻断并显式重新分类。TDD RED 与 debug records 只是 execution working memory，最终 proof 仍由 [[plan-delivery#Plan Delivery#Evidence Freshness]] 建立。

## Implementation Dispatch

同型且独立的 Todo 可以批处理，模型 tier 与 fix loop 可按风险调整，但不合并 Todo identity、write ownership、状态或最终验证。

任何共享 write hotspot、不同 oracle、依赖关系或独立设计判断都会禁止 batch。最终 Completion Audit、Implementation Review、Verification、Evidence Freshness 和 Roadmap DONE 顺序仍由 [[plan-delivery]] 单独持有。
