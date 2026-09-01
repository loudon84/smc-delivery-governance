---
name: smc-delivery-receipt
version: 1.0.0
description: 将本地 Stage PRD、issue/bug、Plan、PR、commit 与 verification 生成标准 Delivery Receipt，供中央仓库同步。
---
# SMC Delivery Receipt

每个 Work Package 一个 Receipt：

```text
.agents/governance/receipts/<WORK_PACKAGE_ID>.yaml
```

Receipt 是本地交付事实的机器摘要，不替代本地 PRD/Plan/Evidence。

必须记录：

```text
feature_id
work_package_id
repository_id
source_revision
status
stage_prds
issues
bugs
plans
pull_requests
commits
acceptance
reported_at
```

Git commit 推荐加入 trailers：

```text
SMC-Feature: FEAT-...
SMC-Work-Package: WP-...
SMC-PRD: PRD-...
SMC-Plan: .cursor/plans/...
```

Issue/PR 推荐 labels：

```text
gov:feature:<FEATURE_ID>
gov:wp:<WORK_PACKAGE_ID>
gov:type:feature|bug|task
```
