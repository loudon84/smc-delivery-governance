# Delivery Traceability

一个跨仓 Feature 必须存在一条可机器追踪的交付链：

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

- Source PRD：中央 `feature.yaml` 中的 ArtifactRef v2（commit / blob SHA / content SHA-256）。
- Stage PRD / Plan / Commit：项目仓库，由 Receipt v2 回报强身份。
- Issue / Bug / PR：项目 GitHub Repository。
- Delivery Receipt：项目仓库的机器摘要，只能更新 observed facts。
- Delivery Ledger：中央同步后的观察事实。
- Work Package / Feature / Contract / Roadmap lifecycle state：中央状态机 + audit events。

中央只存引用和验证结果，不复制 Stage PRD、Plan 或完整测试日志。

## Drift

Work Package `sync_state`：

```text
UNKNOWN
SYNCED
STALE_FEATURE
STALE_CONTRACT
MISSING_RECEIPT
DIVERGED
```

Source PRD、Contract pin 或 Kit identity 变化后，不允许项目继续使用旧 Receipt 宣布 VERIFIED/DONE。
