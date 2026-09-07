# GES Frozen Invariants

下列规则是 GES Core 的硬约束。兼容、简化或提效都不得静默绕过；改任一条款都是 MAJOR governance change。

它们约束项目仓内的 Agent 工作流，不替代中央 Closed Loop 不变量。中央条款见 [[architecture/governance#Frozen Invariants]]。

## Four State Classes

Plan 规格、Todo 运行时、Proof 与 Roadmap 必须分开。压缩成一个 `status=done` 会使门禁无法重算。

1. **Plan specification** — Markdown Todo、Change Matrix、Evidence Policy。
2. **Todo runtime** — Cursor `todos[].status`，仅 delivery controller 可写。
3. **Proof** — Review / Completion Audit / Verification ledger，绑定 scope fingerprint。
4. **Delivery / Roadmap** — Roadmap Item 状态，且 DONE 必须在 implementation commit 之后。

因此：

```text
Todo completed
  ≠ Plan proven
  ≠ implementation committed
  ≠ Roadmap DONE
```

Semantic Plan hash 忽略 runtime `status` 与 v3.4 `content` 投影，见 [[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/common.py#semantic_plan_sha256]]。

## Invariant List

生产路径不得用 `--skip-*` 当验收策略；诊断逃生口不能变成成功路径。

1. **Single Canonical Plan**：同一 delivery item 只有一个 Plan identity。
2. **Static PASS ≠ Implementation Complete**。
3. **Todo completed ≠ Plan proven ≠ committed ≠ Roadmap DONE**。
4. Semantic Review 独立于 Static Validator。
5. Completion Audit 必须重核 Plan × actual diff。
6. Implementation Review 必须基于当前实现内容。
7. Blocking Verification 必须产生可核验 evidence。
8. Evidence / Review / Audit 具备 FRESH / STALE / MISSING。
9. 实现内容变化后旧 proof 必须失效。
10. **`post_review`**：implementation commit 只能发生在 Audit + Review + Verification 全通过之后。
11. Roadmap DONE 是后续 delivery 更新，不得与实现证明混层。
12. Single Writer / ownership-aware slicing 不得被并行破坏。
13. 不得新增与 `smc-plan-delivery` 并列的 production delivery owner。
14. 不得以 skip 选项作为生产成功路径。
15. **Blocking Failure Integrity**：已知 blocking FAIL 不得降级为 observation 后继续 DONE。
16. **Acceptance Scenario Binding**：LIVE/FAULT/EXTERNAL 必须预绑定 Scenario；Execute 不得做 tool discovery。
17. **Evidence Inheritance**：复用必须显式；blocking 历史 FAIL 禁止 `REUSE_EVIDENCE`。
18. **Live Environment Preflight**：环境缺失是 PRECHECK BLOCKED，不是产品 FAIL。
19. **Verification Candidate Provenance**：live proof 必须对应 Plan-owned candidate，且不得破坏 `post_review`。

15–19 由 acceptance 合同强化，见 [[acceptance]]。Baseline YAML 在 4.1.2 只冻结到第 14 条；树内 `GOVERNANCE.md` 已包含 15–19。
