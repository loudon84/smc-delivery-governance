# ADR-005 — Delivery Receipt

**Status:** APPROVED

项目本地通过标准 `Delivery Receipt` 汇报 Stage PRD、Issues/Bugs、Plan、PR、Commit 与 Acceptance 引用。中央同步 Receipt 后形成 Delivery Ledger，但不直接信任项目声明的全局 DONE。

`receipt_version: "2"` 的受源码控制 ArtifactRef 必须具备完整强身份。Remote Receipt 只能更新 observed facts；Consumer `VERIFIED` 与 Feature `DONE` 只能通过中央 State Machine / Reconcile Gate 推进。
