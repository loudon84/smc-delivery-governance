# Delivery Traceability

一个跨仓 Feature 必须存在一条可机器追踪的交付链：

```text
Source PRD Revision
  ↓
Feature / Global Change ID
  ↓
Repo Work Package
  ↓
Local Stage PRD
  ↓
Issue / Bug
  ↓
Plan
  ↓
Branch / Pull Request
  ↓
Implementation Commit
  ↓
Acceptance Report
  ↓
Integration Evidence
```

## Source of Truth

- Source PRD/Feature Revision：中央 `feature.yaml`。
- Stage PRD / Plan / Commit：项目仓库。
- Issue / Bug / PR：项目 GitHub Repository。
- Delivery Receipt：项目仓库的机器摘要。
- Delivery Ledger：中央同步后的观察事实。
- Work Package lifecycle state：中央状态机。

中央只存引用，不复制 Stage PRD、Plan 或完整测试日志。

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

Source PRD 或 Contract Revision 变化后，不允许项目继续使用旧 Receipt 宣布 VERIFIED/DONE。
