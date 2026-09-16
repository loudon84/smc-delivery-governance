# SMC Delivery Governance

本目录是中央治理仓库的架构意图事实源。它只描述跨仓库交付控制面的 Why、领域模型、边界、状态机和治理决策，不复述项目源码。

当前意图版本：**Closed Loop v1 / Governance Kit v1.2.1**；本地工程工作流见 **GES Bundle 5.0.0 冻结** 与 **GES 6.0-alpha.1 Composer Bootstrap**。

- [[architecture]] — 中央控制面领域模型、交付闭环、合同生命周期与证据链
- [[ges]] — 项目仓内 Architecture → Plan Delivery 的 GES v5 工作流（已冻结，不进入 v6 core）
- [[ges6]] — GES 6 Composer + Governance Backplane；Alpha.1 只交付 Composer Bootstrap
- [[decisions]] — 已批准的架构决策（中央/本地边界、状态机、证据合同）
- [[domain]] — Feature、Work Package、Contract、Receipt 与状态机等核心概念
- [[tests]] — 治理工具、证据合同与测试隔离的规格

## Product Mission

中央仓库把跨仓交付收成一条可机器裁决的控制链，而不是一份文档仓库。

```text
Feature SOT
  → Contract SOT
  → Repo Work Package
  → Local PRD/Plan/Execute
  → Verified Evidence
  → IntegrationRun
```

中央治理仓库不是业务系统，不拥有 Work、Backend、Agent、Knowledge、RPA 等产品代码。边界见 [[ADR-001-central-local-boundary]]。
