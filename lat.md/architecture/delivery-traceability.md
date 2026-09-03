# Delivery Traceability

一个跨仓 Feature 必须存在一条可机器追踪的交付链：从 Source PRD ArtifactRef 到 IntegrationRun，中间每个节点都有稳定身份。

强身份规则见 [[ADR-007-artifact-ref-v2]]；观察事实见 [[ADR-005-delivery-receipt]]。

```text
Source PRD ArtifactRef
  ↓
Feature / Global Change ID
  ↓
Repo Work Package
  ↓
Local Stage PRD ArtifactRef
  ↓
Issue / Bug
  ↓
Plan ArtifactRef
  ↓
Branch / Pull Request
  ↓
Implementation Commit
  ↓
Acceptance Attestation
  ↓
IntegrationRun
```

## Source of Truth

中央只存引用和验证结果，不复制 Stage PRD、Plan 或完整测试日志。各层事实源不可互相冒充。

- Source PRD：中央 `feature.yaml` 中的 ArtifactRef v2（commit / blob SHA / content SHA-256）。
- Stage PRD / Plan / Commit：项目仓库，由 Receipt v2 回报强身份。
- Issue / Bug / PR：项目 GitHub Repository。
- Delivery Receipt：项目仓库的机器摘要，只能更新 observed facts。
- Delivery Ledger：中央同步后的观察事实。
- Work Package / Feature / Contract / Roadmap lifecycle state：中央状态机 + audit events。

## Drift

Work Package `sync_state` 记录观察事实与中央 pin 是否一致。漂移后不得用旧 Receipt 宣布 VERIFIED/DONE。

```text
UNKNOWN
SYNCED
STALE_FEATURE
STALE_CONTRACT
MISSING_RECEIPT
DIVERGED
```

Source PRD、Contract pin 或 Kit identity 变化后，必须重新同步并验证，而不是让两个项目继续异步实现。
