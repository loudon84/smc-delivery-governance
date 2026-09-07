# GES Pipeline

标准流水线从 Architecture 决策走到 Roadmap DONE。Plan 创建之后，人类只需进入 `smc-plan-delivery`，不得再手工串执行、审查、验证与提交。

路由表由 `using-superpowers` 持有；后半程顺序由 `smc-plan-delivery` 持有。二者都不得改写其它 Skill 的 canonical state。

## Stages

每个阶段产出下一阶段的输入 artifact，而不是一个总 `status=done`。

```text
Architecture
  → smc-architecture-decision / smc-architecture-review
  → APPROVED Architecture
  → smc-roadmap
  → READY Roadmap Item
  → smc-prd-grounding / smc-prd-review / smc-prd-converge
  → APPROVED Stage PRD
  → smc-plan-from-approved-prd-ponytail
  → Canonical Plan
  → smc-plan-delivery
       Static Gate
       Semantic Gate
       Scoped Execution
       Completion Audit
       Implementation Review
       Blocking Verification
       Evidence Freshness
       post_review scoped Commit
       Roadmap Update
```

`executing-plans` 与 `subagent-driven-development` 只实施 Todo。`post_review` 是 commit policy，不是 workflow executor。`workflow-runner` 不参与本流水线。

## Artifact Routing

当前 artifact 状态决定下一个 owner；禁止 generic planning 绕过治理，也禁止 Plan author 直接把 Plan 交给 implementation engine。

| 当前状态 | 下一 Owner | 硬门禁 |
|---|---|---|
| 无 Architecture Decision | `smc-architecture-decision` | proposal grounded |
| Architecture REVIEW_REQUIRED | `smc-architecture-review` | A1–A8 |
| Architecture Review PASS | `smc-architecture-decision` converge | APPROVED |
| APPROVED Architecture，无 Roadmap | `smc-roadmap` create | roadmap validate |
| Roadmap READY item | `smc-prd-grounding` | 一项 → 一份 Stage PRD |
| PRD REVIEW_REQUIRED | `smc-prd-review` | six gates |
| PRD Review REVISE | `smc-prd-grounding` revision | 关闭 OPEN findings |
| PRD Review PASS | `smc-prd-converge` | APPROVED PRD |
| APPROVED PRD，无 Plan | `smc-plan-from-approved-prd-ponytail` | canonical Plan |
| canonical Plan 已存在 | `smc-plan-delivery` | Static → … → Roadmap |
| Roadmap item DONE | `smc-roadmap` next | 选择下一个 READY |

路由细节由 `using-superpowers` 的 artifact-state-routing 合同持有。Owner 表见 [[skills#Artifact Ownership]]。
