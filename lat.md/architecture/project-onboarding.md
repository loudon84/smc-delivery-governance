# Project Onboarding

## Goal

任何内部项目都可以通过统一 Registry + Governance Binding 纳入中央治理，不要求使用同一技术栈，但必须提供稳定的仓库身份、治理路径与 Delivery Receipt。

## Lifecycle

```text
REGISTERED
  ↓
BOOTSTRAPPED
  ↓
SYNCED
  ↓
ENFORCED
  ↘
OUT_OF_SYNC
```

- `REGISTERED`：中央 Registry 已有 Project/Repository。
- `BOOTSTRAPPED`：项目已安装 Governance Kit/Binding。
- `SYNCED`：所有活动 Work Package Receipt 与中央 source_revision/contract pin 一致。
- `ENFORCED`：项目 CI 已把治理校验设为合并门禁。
- `OUT_OF_SYNC`：缺 Receipt、Feature revision 漂移、Contract pin 漂移或 Receipt 无法验证。

## Required Local Interface

```text
.agents/governance/binding.yaml
.agents/governance.lock
.agents/governance/work-packages/
.agents/governance/contracts/
.agents/governance/receipts/
.agents/governance/acceptance/
```

中央不读取项目私有实现源码来推断状态；项目通过标准 Receipt 汇报事实。
