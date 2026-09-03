# Decisions

已批准的架构决策。每条 ADR 冻结一条不可回退的控制面规则，供状态机、Kit 与测试共同遵守。

- [[ADR-001-central-local-boundary]] — 中央到 Interface，本地到 Implementation
- [[ADR-002-state-machines]] — 跨仓状态由中央统一推进
- [[ADR-003-contract-first]] — Contract Candidate 先于并行实现
- [[ADR-004-repo-work-package]] — Repo Work Package 是唯一正式连接器
- [[ADR-005-delivery-receipt]] — Receipt 只回报 observed facts
- [[ADR-006-prd-acceptance]] — Manifest/Report/Attestation 才是验收合同
- [[ADR-007-artifact-ref-v2]] — 受源码控制交付物必须强身份
- [[ADR-008-canonical-governance-kit]] — 生产只安装不可变 Kit Release
- [[ADR-009-integration-run]] — IntegrationRun 才是跨仓 PASS 证明
- [[ADR-010-audit-materialized-state]] — Audit Facts 与 Git YAML 投影分离
- [[ADR-011-test-isolation]] — 测试不得写入中央 SOT
