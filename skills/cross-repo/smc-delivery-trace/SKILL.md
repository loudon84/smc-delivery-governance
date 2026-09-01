---
name: smc-delivery-trace
version: 1.0.0
description: 汇总 Source PRD → Repo Work Package → Stage PRD → Issue/Bug → Plan → PR/Commit → Verification 的跨仓可追踪链。
---
# SMC Delivery Trace

Traceability 是引用图，不复制项目文档。

每个 Work Package 必须能够回答：

```text
Which source PRD revision?
Which Stage PRD?
Which issues/bugs?
Which plan?
Which implementation commits/PR?
Which acceptance evidence?
```

当状态达到：

- `PLANNED`：至少存在 APPROVED Stage PRD + Plan；
- `IMPLEMENTING`：必须有 Plan + branch/commit/PR 之一；
- `VERIFIED`：必须有 implementation commit + Acceptance PASS；
- `DONE`：必须满足中央 Work Package Exit Criteria。
