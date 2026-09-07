---
name: smc-frontend-review
description: GES Frontend Domain review provider. 对当前 Plan-owned 前端实现做 React architecture、state/effect、design-system、accessibility、interaction closure、performance/resource hygiene 专业审查；结果由 canonical implementation review owner 汇总，不成为第二 Review SOT。
version: 1.0.0
disable-model-invocation: true
---

# SMC Frontend Review v1.0

## Role

本 Skill 只在 Domain Runtime 返回 `frontend` review provider 时执行。最终 Implementation Review owner 仍是 `code-review-and-quality`；本 Skill 输出结构化 domain findings，不写独立 PASS 状态文件。

## Gates

- F1 Component Architecture
- F2 State Ownership
- F3 Effect / Async Correctness
- F4 Design System Consistency
- F5 Accessibility
- F6 Interaction State Closure
- F7 Performance / Resource Hygiene

Severity: `BLOCKING | MAJOR | MINOR | ADVISORY`。

`BLOCKING` 与未豁免 `MAJOR` 必须令 canonical Implementation Review 返回 REVISE。Domain exception 不能覆盖 GES Frozen Invariant。

## Scope

只审查当前 Plan scope fingerprint 对应的 Plan-owned frontend delta。不要把 ambient preexisting dirty 当作当前 Plan finding。
