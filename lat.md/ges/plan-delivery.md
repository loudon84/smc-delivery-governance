# Plan Delivery

`smc-plan-delivery` 是 canonical Plan 后半程的唯一编排器。它只拥有门禁顺序，把 static / semantic / implement / review / verify / roadmap 委托给各自 owner。

v1.1 把交付所有权从「整仓 dirty」收成 Plan-scoped workspace，并持久化 execution context。状态转移是必要证据，但从来不是充分证据；每个 gate 必须按当前 fingerprint 重算。

## Delivery State Machine

合法前进一次一格；禁止跳步与回退。Blocked 记住 `last_valid_state`，resume 看当前 evidence readiness。

```text
PLAN_CREATED
  → PLAN_STATIC_VALID
  → PLAN_REVIEW_CLEARED
  → IMPLEMENTING
  → IMPLEMENTATION_COMPLETE
  → COMPLETION_AUDIT_PASS
  → IMPLEMENTATION_REVIEW_PASS
  → VERIFICATION_PASS
  → IMPLEMENTED_AND_PROVEN
  → IMPLEMENTATION_COMMITTED
  → ROADMAP_DONE
```

`IMPLEMENTING` 之前必须已冻结 workspace baseline。实现入口：[[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/delivery_state.py#transition]]。

运行时落点：

```text
.smc/runs/<plan_id>.json
.smc/runs/<plan_id>/workspace-baseline.json
.smc/runs/<plan_id>/resume.json
.smc/runs/<plan_id>/ledger-*.jsonl
```

## Workspace Scope

一个指定 Plan 是 mutation / audit / review / verification / commit 的唯一 scope owner。启动前已存在的无关 dirty 作为 ambient 被保护，而不是被要求清仓。

| Class | 含义 | 动作 |
|---|---|---|
| `PLAN_OWNED` | Plan、Change Matrix 路径、durable manifest | 允许变更 |
| `AMBIENT_PREEXISTING` | 启动前已 dirty 且非本 Plan | 允许且必须保持原状 |
| `TARGET_CONFLICT` | Plan 写集在 baseline 前已 dirty | fail-closed |
| `TOOLING_BLOCKED` | 无关治理工具在 baseline 前 dirty | fail-closed |
| `AMBIENT_MUTATED` / `SCOPE_DRIFT` / `TOOLING_MUTATION` | 交付中破坏 ambient 或越界 | fail-closed |

`scope_fingerprint` 绑定 semantic Plan hash + 每个 planned path 的内容状态。Cursor `status` / `content` 与 `.smc/`、durable manifest 不进入 implementation scope。实现入口：[[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/workspace.py#init]]。

`init --refresh` 只允许在尚未产生 implementation delta 时重绑；否则 `DELIVERY_WORKSPACE_REFRESH_AFTER_MUTATION`。

## Evidence Freshness

Review、Audit、Verification 必须绑定同一对 `scope_fingerprint` + `ambient_fingerprint`。内容变化使旧 proof 变为 STALE；命令与 Plan Verification Ledger 不一致则不得记为 PASS。

raw log 留在 `.smc/evidence/`，默认不进 Git。blocking evidence 全 FRESH 后生成 `docs_agent/evidence/<plan_id>-evidence.json`。Roadmap 引用 `smc-evidence:<plan_id>@sha256:<fingerprint>`，从 implementation commit 解析 manifest。

实现入口：[[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/evidence.py#current_status]]。

## Test Asset Synchronization

`smc.plan.v3.6` 把可复用 test、fixture、driver 与 harness 放到项目级 Test Asset Catalog，而不再让每个 Roadmap Item 临时复制 live test。

Plan 的 `REUSE` 资产必须拥有当前 digest；`EXTEND` / `NEW` 资产与其 `docs_agent/test-assets/<asset_id>.json` manifest 必须是 Plan-owned Change Matrix 路径。Delivery 在 Completion Audit 前同步 manifest，Evidence Manifest 记录最终 asset ref/digest，详见 [[test-assets]]。

## Plan Contract Resolution

运行时按 Plan frontmatter 声明的 contract 选择校验器，明确支持 v3.3 到 v3.6，且不静默回退到旧规则。

这让历史 Plan 仍可读取，同时确保 v3.6 Plan 必经 v3.6 的验收与测试资产规则。

## Execution Context

Resume capsule 在上下文丢失后恢复当前 Todo、下一步、指纹与最近错误。Continuation gate 只判断 Agent 是否该继续，不能产出 `IMPLEMENTED_AND_PROVEN`。

Workers 只追加自己的 ledger；canonical Todo `status` 仍由 controller 通过 [[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/plan_state.py#set_status]] 写入。

v4.4 的 task brief、worker report 与 write-scoped review package 都是 `.smc/runs/<plan_id>/` 下的派生产物：它们把单个 Todo 的必要输入交给 worker/reviewer，不能成为第二 Plan、Review 或 Evidence SOT，详见 [[runtime-cost#Task Context Artifacts]]。

## post_review Commit

允许 implementation commit 的充要条件是全部当前 proof FRESH，而不是 Todo 全 completed。

```text
Static PASS
+ Semantic clearance FRESH
+ all Todos completed
+ Completion Audit FRESH PASS
+ Implementation Review FRESH PASS
+ all blocking Verification FRESH PASS
+ durable Evidence Manifest FRESH
= DELIVERY_READY_TO_COMMIT
```

commit 只含 Plan-owned delta + canonical Plan + durable manifest。仓库不必干净；ambient dirty 可保留但必须匹配 baseline。HEAD 在 commit 前必须等于冻结 `base_commit`。实现入口：[[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/commit_guard.py#capture]]。

Roadmap DONE 必须是后续独立 commit。
