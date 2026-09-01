# PRD Acceptance Evidence

## Principle

中央仓库不远程执行各项目任意测试命令。Stage PRD 的 AC/DOD 在项目本地转换为 `Acceptance Manifest`，由项目 CI 执行并生成 `Acceptance Report`，中央只验证报告与 revision/commit pin。

## Chain

```text
APPROVED Stage PRD
  ↓
AC-01 / DOD-01 ...
  ↓
Acceptance Manifest
  ↓
V-01 unit
V-02 contract
V-03 static
V-04 integration
  ↓
Local CI
  ↓
Acceptance Report
  ↓
Delivery Receipt
  ↓
Central Acceptance Gate
```

## VERIFIED Gate

Repo Work Package 进入 `VERIFIED` 至少要求：

```text
sync_state == SYNCED
Stage PRD ref exists
Plan ref exists
Implementation commit exists
Acceptance status == PASS
```

`DONE` 仍由中央 Work Package Exit Criteria 与 Global Integration 条件裁决。
