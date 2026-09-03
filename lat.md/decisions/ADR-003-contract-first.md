# ADR-003 — Contract Candidate First

跨仓实现必须先有 Contract Candidate，再允许 Provider / Consumer 并行开工。禁止从 Consumer UI 行为反推 Provider 私有接口。

**Status:** APPROVED

```text
Architecture
→ Contract Candidate
→ Parallel Implementation
→ Provider Conformance
→ Immutable Release
→ Consumer Lock
→ Central Acceptance Attestation
→ IntegrationRun
→ E2E PASS
```

合同闸门见 [[architecture/contract-lifecycle]]；交付链见 [[architecture/cross-repo-delivery]]。
