---
name: executing-plans
description: Plan implementation engine。v4.3 在现有 Write Ownership/focused-check 边界内接入 Engineering Method Runtime：按 Todo profile 选择直接实现、TDD 或 systematic debugging，不取得 Final Review/Verification/Commit/Roadmap ownership。
version: 4.3.0
---

# Executing Plans v4.3

## Mode Detection

执行任何 `.plan.md` Todo 都按 governed `post_review` 处理；frontmatter 缺 `commit_policy` 时也推断为 `post_review`。

非 Plan 临时任务才是 generic mode。

## Governed Role

在 SMC governed flow 中，本 Skill 是 **implementation engine**，上层唯一 orchestrator 是：

```text
smc-plan-delivery
```

本 Skill 不再拥有：

- Final Plan Completion Audit；
- Final Implementation Review；
- Final Verification；
- implementation commit；
- Roadmap update。

这些必须返回 `smc-plan-delivery` 继续完成。

## Preconditions

上游必须已经满足：

```text
PLAN_STATIC_VALID
PLAN_REVIEW_CLEARED
```

且提供唯一：

```text
PLAN_PATH=<canonical .plan.md>
```

禁止重新搜索另一个 Plan。

## Todo Execution

对每个 Todo：

1. 按 Write Ownership Ledger 与 Depends On 选择可执行 Todo；
2. 先将 canonical Cursor todo status 更新为 `in_progress`：

```bash
python .agents/skills/smc-plan-delivery/scripts/plan_state.py \
  set "$PLAN_PATH" T1 in_progress
```

3. 只读取 Immediate anchors + Ledger Reads + 被真实 trigger 的 Triggered Reads；
4. 只写当前 Todo 的 Ledger Writes；
5. 不实现 Plan 外 cleanup/refactor；
6. 执行 Todo focused check；
7. 对当前 Todo 做局部 spec compliance check；
8. 若通过，将同一 canonical Plan status 更新为 `completed`；
9. 若环境/依赖阻断，更新为 `blocked` 并返回 orchestrator；
10. **不 commit**。

## Ownership Violation

如果实现需要写另一个 Todo 的 production `path#symbol`：

```text
PLAN_WRITE_SCOPE_VIOLATION
```

停止当前 Todo，返回 Plan REVISE；不得“顺手修改”。

## Governed Live Execution Boundary

若 Plan 含 `smc.acceptance.v1`，本 implementation engine 不拥有 Live test subject discovery。

禁止：

```text
search catalog -> try tool A -> try tool B
reuse one convenient tool for semantically different ACs
change prompt repeatedly until desired behaviour appears
replace Plan-bound fixture / fault driver / environment
```

如果 Todo 局部 check 发现绑定 Fixture 不存在或实际能力与 Plan 声明不符：

```text
LIVE_FIXTURE_UNAVAILABLE
LIVE_FIXTURE_CONTRACT_MISMATCH
```

立即返回 orchestrator，进入 `PLAN_REVISE_REQUIRED` / `VERIFICATION_BLOCKED`。不得自行换 Tool。

## Focused Check Semantics

Todo focused check 只证明局部实现可继续，不替代 final Verification evidence。

不得把：

```text
unit check passed
```

报告成：

```text
IMPLEMENTED_AND_PROVEN
```

## Completion

所有 Cursor todos completed 后，本 Skill 只返回：

```text
IMPLEMENTATION_ENGINE_COMPLETE
```

然后控制权交回：

```text
smc-plan-delivery
  -> Plan Completion Audit
  -> Implementation Review
  -> Verification
  -> Evidence Freshness
  -> post_review Commit
  -> Roadmap Update
```

## Generic Mode

非 `.plan.md` 临时任务可以遵循项目自己的 commit cadence；不得把 Generic Mode 规则反向应用到 governed Plan。


## GES 4.2 Plan-Scoped Execution

When invoked by `smc-plan-delivery`:

- write only paths owned by the active Plan/Todo;
- never require repository-wide clean worktree;
- call `workspace.py assert-stable` at Todo boundaries;
- append execution progress/error/local-check events through `execution_context.py`;
- never mutate unrelated ambient dirty;
- never modify governance tooling unless that path is explicitly in the Plan Change Matrix;
- do not commit.

## GES 4.4.1 Engineering Method Runtime

在 Todo status 进入 `in_progress` 后、任何 production write 前：

```bash
python .agents/skills/smc-plan-delivery/scripts/engineering_method.py \
  classify "$PLAN_PATH" --todo T1
```

按 method artifact 执行：

```text
MECHANICAL      -> direct minimal implementation; TDD preferred/not-applicable
BEHAVIOR_CHANGE -> RED -> GREEN -> optional REFACTOR
BUG_FIX         -> systematic debug -> root cause -> regression RED -> GREEN
HIGH_RISK       -> reasoning-tier implementation + required TDD + independent review
```

`BUG_FIX` 在 production fix 前必须：

```bash
python .agents/skills/smc-plan-delivery/scripts/engineering_method.py \
  debug-check "$PLAN_PATH" --todo T1
```

需要 TDD 的 Todo 在 `completed` 前必须：

```bash
python .agents/skills/smc-plan-delivery/scripts/engineering_method.py \
  tdd-check "$PLAN_PATH" --todo T1
```

TDD RED 是预期 execution state，不得写成 final Verification FAIL。Debugging 发现 scope/owner/contract/boundary drift 时，按 SMC governance 返回 Plan revision/PRD，而不是扩大 write set。三次 failed fix 触发 `DEBUG_ARCHITECTURE_ESCALATION`。
