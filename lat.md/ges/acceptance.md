# GES Acceptance Governance

Acceptance contract 补上「实现证明」与「现场验收证明」之间的缺口。它正交于 `smc.plan.v3.4`：只有 LIVE / FAULT_INJECTION / EXTERNAL 的 Plan 才声明 `acceptance_contract: smc.acceptance.v1`。

该合同强化 [[invariants]] 第 15–19 条，且不得削弱 `post_review`。中央 Attestation 仍是跨仓 VERIFIED 的唯一裁决，见 [[acceptance-evidence]]。

## Five Gates

结构校验是确定性的；fixture 是否真正调用目标能力仍归 semantic Plan review。

1. **Blocking Failure Integrity** — blocking Claim 的真实 FAIL 不得改成 observation/reuse 后继续 DONE。
2. **Acceptance Scenario Binding** — 每个 LIVE/FAULT/EXTERNAL verification 预绑定唯一 Scenario、Subject/Fixture、Stimulus、Oracle。
3. **Evidence Inheritance** — `REUSE_EVIDENCE` 要求 prior PASS + 完整 durable source；prior FAIL 只能 `TARGETED_RERUN` 或 `NEW_EVIDENCE`。
4. **Live Environment Preflight** — 缺 env / fixture / fault driver / candidate 时返回 PRECHECK BLOCKED，不写假产品 FAIL。
5. **Verification Candidate Provenance** — live SUT 必须证明运行的是当前 Plan-owned candidate；否则 `LIVE_SUT_MISMATCH`。

实现入口：[[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/acceptance.py#validate_contract]]。

## Candidate vs Commit

`post_review` 意味着 live verification 发生时最终 implementation commit 还不存在。因此先 capture working-tree candidate，再让环境按 `LOCAL_WORKTREE` / `ENV_TOKEN` / `COMMAND` / `RECEIPT` 证明同一 candidate。

commit guard 随后证明那个 post-review commit 恰好包含已验证的 Plan-owned 内容。禁止「修了 A、测了 B」，也禁止为了现场测试而提前 commit。

Acceptance-enabled Plan 进入 `IMPLEMENTED_AND_PROVEN` 还要求：全部 blocking Claim PASS，且非 reuse 的 live evidence 携带已 capture 的 candidate ID。
