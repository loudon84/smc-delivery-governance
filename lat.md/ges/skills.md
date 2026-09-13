# GES Skills

每个治理 artifact 只有一个 canonical owner。其它 Skill 可以调用该 owner，但不得夺取其状态写权限。

下表记录**当前工作区**版本。已接受基线仍 pin Bundle 4.1.2（Plan `3.4.0` / Delivery `1.0.1` / Plan contract `smc.plan.v3.3`），见 [[install#Version Axes]]。

## Artifact Ownership

写权限按 artifact 切分，避免第二个 delivery owner 或 Plan author 兼执行器。

| Artifact / State | Canonical Owner | 当前树版本 |
|---|---|---|
| Architecture Decision | `smc-architecture-decision` | 1.0.0 |
| Architecture Review | `smc-architecture-review` | 1.0.0 |
| Roadmap / Delivery state | `smc-roadmap` | 1.2.0 |
| Stage PRD grounding | `smc-prd-grounding` | 4.0.0 |
| Stage PRD review | `smc-prd-review` | 4.0.0 |
| Stage PRD converge | `smc-prd-converge` | 3.0.0 |
| Canonical Plan author | `smc-plan-from-approved-prd-ponytail` | 3.7.0 |
| Plan static truth | `smc-plan-validator` | 1.6.0 |
| Plan semantic truth | `smc-plan-review` | 1.2.0 |
| Plan delivery sequencing | `smc-plan-delivery` | 1.3.0 |
| Todo implementation | `executing-plans` / `subagent-driven-development` | 4.3.0 |
| Workflow router | `using-superpowers` | 4.4.0 |
| Implementation semantic review | `code-review-and-quality` | consumer baseline |
| Verification truthfulness | `verification-before-completion` + delivery evidence | inherited |
| Frontend engineering provider | `smc-frontend-engineering` | 1.0.0 |
| Frontend review provider | `smc-frontend-review` -> canonical review owner | 1.0.0 |
| Frontend verification provider | `smc-frontend-visual-verification` -> delivery evidence | 1.0.0 |

`code-review-and-quality` 属于 consumer required baseline，不在 GES overlay 包内发布。`verification-before-completion` 当前无独立 SemVer frontmatter，不得在无关 patch 中顺手改版本。

## Plan Review Split

静态 PASS 与语义 clearance 必须分开。`assess_plan_review` 继续只输出 `NOT_REQUIRED | REQUIRED`，但可在 packet 中声明 `NONE | DELTA | FULL` 深度；实际审查输出仍为 `PASS | REVISE | RETURN_PRD`。

无论路由结果是 `NOT_REQUIRED` 还是实际 `PASS`，都必须留下绑定当前 semantic Plan hash 的 clearance。运行时 Todo `status` 变化不得使 Plan review stale。

`DELTA` 仅可在已有 fresh PASS semantic snapshot 且风险未升级时缩小读取范围；缺 snapshot 或涉及 acceptance、owner、boundary、安全、schema、protocol、并发或生命周期时必须 `FULL`，详见 [[runtime-cost#Adaptive Plan Review]]。

## Domain Provider Ownership

Domain Skill 是专业 provider，不是 artifact owner。Consumer Profile 决定可用 pack，Plan Change Matrix 决定当前 activation；最终 implementation review / verification evidence 仍写入既有 canonical owner。

Core runtime 不得按具体 domain id 分支；新增 Domain 的 release test 必须证明 registry/profile/pack data 足以接入。
