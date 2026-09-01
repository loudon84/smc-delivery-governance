---
name: smc-contract-lifecycle
version: 1.0.0
description: 管理跨仓 Contract 从 DRAFT/CANDIDATE 到 RELEASED/CONSUMED/CONFORMANCE_PASS 的状态事实。
---
# SMC Contract Lifecycle

Candidate：schema + fixtures + transport semantics + error semantics + compatibility intent。
Release：immutable version + tag/release + checksum/manifest + provider conformance。
Consume：Consumer Pin/Lock。
Conformance：Provider + Consumer Contract tests。

禁止修改 immutable release。
