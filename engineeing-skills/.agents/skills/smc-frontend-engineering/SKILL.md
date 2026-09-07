---
name: smc-frontend-engineering
description: GES Frontend Domain engineering provider. 为被 Domain Activation 标记为 REQUIRED 的前端变更提供 React composition、state ownership、design-system、accessibility、interaction-state 与 renderer performance 约束；不拥有 Plan/Delivery/Commit 状态。
version: 1.0.0
disable-model-invocation: true
---

# SMC Frontend Engineering v1.0

## Role

本 Skill 是 `frontend` Domain Pack 的 **engineering provider**，不是新的 workflow，也不是 Plan/Delivery owner。

必须由 GES Domain Runtime 判定 `frontend=REQUIRED` 后，由 `smc-plan-delivery` 在 Execution 阶段加载。不得绕过 canonical Plan 自行开工。

## Precedence

```text
GES Frozen Invariants
> Approved Architecture / PRD / Plan
> Consumer project truth (lat.md / existing components / tokens)
> Frontend Domain MUST rules
> SHOULD rules
> ADVISORY design guidance
```

## Required Reads

- `references/react-composition.md`
- `references/state-and-effects.md`
- `references/rendering-performance.md`
- `references/design-system.md`
- `references/accessibility.md`
- `references/interaction-states.md`
- `references/motion.md`
- `references/frontend-testing.md`

## Engineering Contract

1. Prefer composition over boolean-prop proliferation.
2. State has one owner; derive rather than duplicate/synchronize.
3. Effects are for external synchronization, not default state orchestration.
4. Existing semantic design token/component beats raw value/duplicate primitive.
5. Every observable interaction closes applicable loading/error/empty/disabled/focus/keyboard states.
6. Accessibility is implementation correctness, not polish.
7. Performance optimizations require an identifiable cost/identity boundary; do not scatter memoization by default.
8. Renderer code must respect the Consumer's desktop/browser boundary and existing IPC/runtime architecture.
9. Domain guidance cannot change Plan Change IDs, Todo ownership, proof status, commit policy, or Roadmap state.

## Output

Implementation remains owned by `executing-plans` / `subagent-driven-development`. This provider supplies domain constraints and may append normal execution-context notes, but writes no separate frontend status SOT.
