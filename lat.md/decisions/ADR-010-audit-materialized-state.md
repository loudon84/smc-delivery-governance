# ADR-010 — Audit Facts vs Materialized State

Git YAML 是 Current Materialized State。生命周期事实是 append-only `audit/transitions/` 事件。二者必须同事务写入。

**Status:** APPROVED

每次成功推进必须同时写入：

```text
materialized YAML + transition event
```

写入使用事务辅助：事件失败则回滚 YAML。Invariant checker 核对 audit chain、materialized state 与 sample contamination。无 event 不得 `--apply` 推进状态。

实现：[[tools/state_transaction.py#commit_yaml_transition]]。分层见 [[architecture/trusted-delivery-loop#Fact Layers]]。
