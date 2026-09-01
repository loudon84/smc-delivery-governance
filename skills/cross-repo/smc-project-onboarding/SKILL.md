---
name: smc-project-onboarding
version: 1.0.0
description: 将新 Project/Repository 纳入中央治理 Registry，生成 Binding、治理 Kit 与状态回报约束。
---
# SMC Project Onboarding

## Output

中央：

```text
registry/projects/<project>.yaml
registry/repositories/<repo>.yaml
```

项目：

```text
.agents/governance/binding.yaml
.agents/governance.lock
.agents/governance/receipts/
.agents/governance/acceptance/
```

## Adoption State

```text
REGISTERED → BOOTSTRAPPED → SYNCED → ENFORCED
                    ↘ OUT_OF_SYNC
```

项目状态只通过标准 Delivery Receipt / Governance Sync 更新，禁止人工把本地实现状态直接写成全局 Feature DONE。
