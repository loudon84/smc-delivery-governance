# SMC Delivery Governance

本目录是中央治理仓库的架构意图事实源。它只描述跨仓库交付控制面的 Why、领域模型、边界、状态机和治理决策，不复述项目源码。

当前意图版本：**Closed Loop v1 / Governance Kit v1.2.1**。

- [[architecture/governance]] — 中央治理领域模型与职责边界
- [[architecture/trusted-delivery-loop]] — 可信交付闭环与事实分层
- [[architecture/cross-repo-delivery]] — Cross-Repo Feature → Work Package → Local Delivery
- [[architecture/contract-lifecycle]] — Contract Release Registry / Consume / Conformance
- [[decisions/ADR-001-central-local-boundary]] — 中央/本地职责边界
- [[decisions/ADR-002-state-machines]] — 状态机由中央统一管理
- [[decisions/ADR-003-contract-first]] — Contract Candidate 前置
- [[decisions/ADR-004-repo-work-package]] — Repo Work Package 是中央与项目之间的连接器

- [[architecture/project-onboarding]] — 新项目注册、Bootstrap、Sync/Enforce 状态
- [[architecture/delivery-traceability]] — Source PRD ArtifactRef → Stage PRD → Plan → Commit → Evidence
- [[architecture/acceptance-evidence]] — Stage PRD AC/DOD 的本地测试与中央 Attestation Gate
- [[decisions/ADR-005-delivery-receipt]] — 项目通过 Receipt 回报本地交付事实
- [[decisions/ADR-006-prd-acceptance]] — Acceptance Manifest/Report/Attestation 作为验收证据合同
- [[decisions/ADR-007-artifact-ref-v2]] — ArtifactRef 强身份
- [[decisions/ADR-008-canonical-governance-kit]] — 不可变 Governance Kit Release
- [[decisions/ADR-009-integration-run]] — IntegrationRun 才是跨仓 PASS 证明
- [[decisions/ADR-010-audit-materialized-state]] — Audit Facts 与 Materialized State
- [[decisions/ADR-011-test-isolation]] — 测试不得污染中央 SOT

## Product Mission

```text
Feature SOT
  → Contract SOT
  → Repo Work Package
  → Local PRD/Plan/Execute
  → Verified Evidence
  → IntegrationRun
```

中央治理仓库不是业务系统，不拥有 Work、Backend、Agent、Knowledge、RPA 等产品代码。
