# Project Onboarding

任何内部项目都可以通过统一 Registry + Governance Binding 纳入中央治理。不要求同一技术栈，但必须提供稳定仓库身份、治理路径与 Delivery Receipt。

生命周期与 Kit 安装见 [[ADR-008-canonical-governance-kit]]；注册对象见 [[domain/registry]]。

## Goal

把新仓库从「知道它存在」推进到「CI 强制治理门禁」，并始终能检测 pin 漂移。

## Lifecycle

项目治理状态独立于 Feature 状态机。OUT_OF_SYNC 是可修复的漂移，不是业务失败。

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
- `BOOTSTRAPPED`：项目已安装 canonical Governance Kit 与 Binding pin。
- `SYNCED`：所有活动 Work Package Receipt 与中央 source_revision/contract/kit pin 一致。
- `ENFORCED`：项目 CI 已把治理校验设为合并门禁。
- `OUT_OF_SYNC`：缺 Receipt、Feature revision 漂移、Contract/Kit pin 漂移、Sample 污染或 Receipt 无法验证。

## Kit Install

生产安装必须来自已验证的 canonical Kit Bundle。source-tree / unsigned HEAD 仅用于开发，且必须显式允许。Binding 与 lock 必须 pin `version / tag / commit / manifest_sha256`。

## Required Local Interface

中央不读取项目私有实现源码来推断状态。项目通过标准 Receipt 汇报事实，通过 CI artifact 提供可验证 Acceptance。

```text
.agents/governance/binding.yaml
.agents/governance.lock
.agents/governance/work-packages/
.agents/governance/contracts/
.agents/governance/receipts/
.agents/governance/acceptance/
```
