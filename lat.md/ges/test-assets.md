# GES Test Assets

GES 将可复用的 test、fixture、driver 与 harness 建模为项目级资产，使后续 Roadmap Item 能引用和扩展已有能力而非重新创建同类 live test。

Test Asset Contract 是 `smc.plan.v3.6` 的候选能力；它不改变 [[invariants#GES Frozen Invariants]] 中 Plan、Todo、Proof 与 Roadmap 的 canonical ownership，也不把测试资产变成第二个 Delivery owner。

## Project Catalog

每个 ACTIVE Test Asset 在 Consumer Profile `test_asset_root`（默认 `docs_agent/test-assets/`）有单独 manifest，绑定稳定 ID、kind、path、capabilities 和当前内容 digest。

manifest 是 Git-tracked 的长期工程资产，区别于 `docs_agent/evidence/` 中按 Plan fingerprint 保存的一次 proof。资产路径或能力变化必须更新 manifest digest，避免后续 Plan 把已变化的脚本误当可复用基线。

## Plan Binding

Plan 的 Test Asset Ledger 为 live verification 声明唯一 asset ID 与 `REUSE`、`EXTEND` 或 `NEW` 决策，并把受影响资产放入 Change Matrix。

`REUSE` 只允许引用 ACTIVE 且 digest-current 的资产，当前 Plan 不得修改它。`EXTEND` / `NEW` 必须拥有 test file 和 manifest 写集，且关联验证必须产生新的 proof；这使 [[acceptance#GES Acceptance Governance#Five Gates]] 的 Evidence Inheritance 与测试实现复用保持正交。

## Delivery Synchronization

Delivery 在 implementation 完成后、Completion Audit 前同步 NEW/EXTEND asset manifest，并把最终 asset ID 和 digest 写入 durable Evidence Manifest。

同步发生在 Plan scope 内，所以改变测试资产会使既有 audit/review/evidence 按 [[plan-delivery#Plan Delivery#Evidence Freshness]] 规则失效；它不会通过复用历史 PASS 绕过当前验证。
