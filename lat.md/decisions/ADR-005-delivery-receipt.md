# ADR-005 — Delivery Receipt

**Status:** APPROVED

项目本地通过标准 `Delivery Receipt` 汇报 Stage PRD、Issues/Bugs、Plan、PR、Commit 与 Acceptance Evidence。中央同步 Receipt 后形成 Delivery Ledger，但不直接信任项目声明的全局 DONE。

Remote Receipt 只能更新 observed facts；中央生命周期状态只能通过中央 State Machine / Reconcile Gate 推进。
