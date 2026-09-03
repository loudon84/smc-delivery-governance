# Governance Architecture

中央治理仓库的领域模型、职责边界与冻结不变量。它定义 Program 到 Evidence 的对象图，以及中央与项目仓库的能力归属。

详见 [[domain/entities]]、[[ADR-001-central-local-boundary]]。

## 中央领域模型

控制面对象按 Program → Feature → Work Package / Contract / Integration 组织，而不是按代码仓库目录组织。

```text
Program
Project
Repository
Team
Feature
ArchitectureDecision
GlobalRoadmapItem
RepoWorkPackage
Contract
ContractRelease
Dependency
IntegrationScenario
IntegrationRun
Evidence
AuditEvent
GovernanceKitRelease
```

关系：

```text
Program
  └─ Feature
      ├─ Source PRD ArtifactRef
      ├─ Cross-Repo Architecture
      ├─ Global Roadmap
      ├─ Contract Releases + Consumer Pins
      ├─ Repo Work Packages
      ├─ Verified Acceptance Attestation
      └─ IntegrationRun
```

## Production Ownership

中央拥有身份、合同生命周期、Work Package 和证据裁决；项目仓库拥有实现与本地测试执行。

| Capability | Owner |
|---|---|
| Project/Repository Registry | Central Governance |
| Feature identity | Central Governance |
| Global Change ID | Central Governance |
| Cross-repo dependency graph | Central Governance |
| Contract lifecycle metadata | Central Governance |
| Repo Work Package | Central Governance |
| Integration Gate / IntegrationRun | Central Governance |
| Governance Kit Release identity | Central Governance |
| Lifecycle audit facts | Central Governance |
| Local architecture / implementation | Project Repository |
| Stage PRD / Plan / code / tests | Project Repository |
| Provider Contract artifact bytes | Provider Repository |
| Consumer Lock | Consumer Repository |
| Acceptance execution | Project CI |
| Acceptance attestation verification | Central Governance |

## Team Collaboration Roles

角色描述协作职责，不替代 Production Owner。一人可兼多角，但每个 Capability 只能有一个生产归属。

```text
Feature Owner
Architecture Owner
Contract Owner
Repo Work Package Owner
Integration Owner
Evidence Verifier
```

## Frozen Invariants

下列规则是 Closed Loop v1 的硬约束。违反任一条款时，中央不得把实体推进到 VERIFIED / DONE / PASS。

1. 一个 Feature 可包含多个 Repo Work Package。
2. 一个 Repo Work Package 只属于一个 Repository。
3. Work Package 不包含 exact file/symbol。
4. Global Change ID 不允许项目仓库重新定义。
5. Contract RELEASED 前禁止 Consumer 启用真实 production call。
6. Contract CANDIDATE 后允许 Dark Implementation。
7. BLOCKED 必须声明机器可解析 blocker。
8. Feature DONE 必须满足 Repo Evidence 与 immutable IntegrationRun PASS。
9. Git YAML 是 materialized state；`audit/transitions/` 才是生命周期事实。
10. Consumer `VERIFIED` 只认中央 Attestation，不认 Receipt 自称 PASS。
11. 生产 Kit 安装只接受 canonical release。
12. 测试不得写入中央 SOT。
