# SMC Delivery Governance

`smc-delivery-governance` 是 SMC 内部多仓库、多团队研发的 **Engineering Delivery Control Plane**。

它不拥有业务代码，也不替代各项目仓库中的 `lat.md → PRD → Plan → Execute → Review → Verification` 单仓治理流程。它只负责跨仓库的全局事实与协作控制：

- Feature / Program
- Cross-Repo Architecture
- Global Roadmap
- Repo Work Package
- Versioned Contract 生命周期
- External Dependency
- Provider / Consumer 成熟度
- Integration Gate
- Verification / Release Evidence
- 通用治理 Skills 的版本与同步

## 核心边界

```text
Central Governance
    负责 Why / System Boundary / Global Outcome / Dependency / Contract / Evidence

Local Repository
    负责 Repo Architecture / Stage PRD / Plan / Code / Test / Release
```

禁止中央仓库成为“超级 PRD 仓库”或业务代码仓库。

## 四层治理

```text
L0  Enterprise Delivery Governance
    smc-delivery-governance

L1  Cross-Repo Feature / Architecture / Contract
    smc-delivery-governance

L2  Repo-local Architecture / PRD / Plan
    each project repository

L3  Code / Test / Release
    each project repository
```

## 快速开始

```bash
python -m pip install -e .
python tools/validate_feature.py features/FEAT-SKILL-FIRST-001
python tools/dependency_status.py features/FEAT-SKILL-FIRST-001
python tools/contract_status.py SKILL-RUN-CONTRACT
python tools/program_next.py programs/agent-platform/roadmap.yaml
python tools/integration_gate.py features/FEAT-SKILL-FIRST-001
```

同步中央治理 Kit 到项目仓库：

```bash
python tools/governance_sync.py   --repo /path/to/project   --project PROJECT-NODESKCLAW   --feature FEAT-SKILL-FIRST-001   --apply
```

同步目标：

```text
<project>/.agents/governance/
<project>/.agents/governance.lock
```

不会覆盖项目原有业务 Skills。

## 中央状态机

```text
Feature
PROPOSED → ARCHITECTURE → PLANNED → IMPLEMENTING → INTEGRATING → VERIFYING → DONE

Contract
DRAFT → CANDIDATE → APPROVED → RELEASED → CONSUMED → CONFORMANCE_PASS

Repo Work Package
BACKLOG → READY → IN_PRD → PLANNED → IMPLEMENTING → REVIEW → VERIFIED → DONE

Integration
WAITING_PROVIDER → WAITING_CONSUMER → READY → RUNNING → PASS
```

`BLOCKED` 必须带结构化 `blocked_by`，不得只写自然语言。

## Repo Work Package

```text
Cross-Repo Feature
      ↓
Repo Work Package
      ↓
Local Roadmap Item
      ↓
Stage PRD
      ↓
Plan
      ↓
Execute
      ↓
Review
      ↓
Verification
      ↓
Evidence 回写中央仓库
```

当前仓库提供 `FEAT-SKILL-FIRST-001` 作为可运行示例。
