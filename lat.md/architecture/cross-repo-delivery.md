# Cross-Repo Delivery

一个 Source PRD 可以驱动多个仓库并行交付，但全局变更身份、合同版本和完成证明必须由中央统一。

连接器是 [[domain/entities#Repo Work Package]]；合同前置见 [[ADR-003-contract-first]]。

## 标准交付链

跨仓 Feature 先定架构与合同候选，再让 Provider / Consumer 并行实现，最后用不可变 IntegrationRun 关门。

```text
Cross-Repo Feature Intake
        ↓
System Architecture
        ↓
Global Roadmap
        ↓
Contract Design
        ↓
Contract Candidate
        ↓
┌─────────────────────┬─────────────────────┐
│ Provider Repository │ Consumer Repository │
│ contract release    │ local PRD           │
│ conformance         │ Plan                │
│                     │ Dark Execute        │
└─────────────────────┴─────────────────────┘
        ↓
Provider Conformance
        ↓
Immutable Contract Release
        ↓
Consumer Lock
        ↓
Central Acceptance Attestation
        ↓
Immutable IntegrationRun
        ↓
Feature DONE
```

## Global Change ID

中央使用 `XR-C01...` 作为全局变更身份。项目 PRD 只能继承并映射到本地 Change ID，禁止重新创造同义全局变更。

## External Dependency Maturity

外部依赖成熟度跟随合同 Release 状态。本地活动必须停在对应成熟度之前，不能靠 UI 完成度提前调用生产接口。

```text
UNDEFINED
DESIGNED
CANDIDATE
APPROVED
RELEASED
CONSUMED
CONFORMANCE_PASS
```

| Local Activity | Required Contract State |
|---|---|
| UI shell / local state | UNDEFINED |
| Parser / DTO / fixture tests | CANDIDATE |
| production tools/call | RELEASED |
| production promotion | CONSUMED + CONFORMANCE_PASS + IntegrationRun PASS |

## Local Repository Flow

项目仓库走本地 LAT / PRD / Plan / Execute / Review，中央只记录 Evidence 引用，不复制实现源码或大规模日志。

```text
lat.md
→ Local Roadmap Item
→ smc-prd-grounding
→ smc-prd-review
→ smc-prd-converge
→ smc-plan-from-approved-prd-ponytail
→ Execute
→ Review
→ Verification
```
