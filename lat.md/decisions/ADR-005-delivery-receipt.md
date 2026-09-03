# ADR-005 — Delivery Receipt

项目通过标准 Delivery Receipt 回报本地交付事实。中央同步后形成 Ledger，但不信任项目自称的全局 DONE。

**Status:** APPROVED

项目本地汇报 Stage PRD、Issues/Bugs、Plan、PR、Commit 与 Acceptance 引用。`receipt_version: "2"` 的受源码控制 ArtifactRef 必须具备完整强身份。

Remote Receipt 只能更新 observed facts；Consumer `VERIFIED` 与 Feature `DONE` 只能通过中央 State Machine / Reconcile Gate 推进。

证据分层见 [[domain/facts-and-evidence#Delivery Receipt]]。
