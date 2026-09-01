# Cross-Repo Delivery

## 标准交付链

```text
Cross-Repo Feature Intake
        ↓
System Architecture
        ↓
Global Roadmap
        ↓
Contract Design
        ↓
Contract Candidate
        ↓
┌─────────────────────┬─────────────────────┐
│ Provider Repository │ Consumer Repository │
│ local PRD           │ local PRD           │
│ Plan                │ Plan                │
│ Execute             │ Dark Execute        │
└─────────────────────┴─────────────────────┘
        ↓
Provider Conformance
        ↓
Immutable Contract Release
        ↓
Consumer Lock
        ↓
Cross-Repo Live E2E
        ↓
Feature DONE
```

## Global Change ID

中央使用 `XR-C01...`。项目 PRD 继承该 ID，再映射到本地 Change ID，禁止重新创造同义全局变更。

## External Dependency Maturity

```text
UNDEFINED
DESIGNED
CANDIDATE
APPROVED
RELEASED
CONSUMED
CONFORMANCE_PASS
```

| Local Activity | Required Contract State |
|---|---|
| UI shell / local state | UNDEFINED |
| Parser / DTO / fixture tests | CANDIDATE |
| production tools/call | RELEASED |
| production promotion | CONSUMED + CONFORMANCE_PASS + Integration PASS |

## Local Repository Flow

```text
lat.md
→ Local Roadmap Item
→ smc-prd-grounding
→ smc-prd-review
→ smc-prd-converge
→ smc-plan-from-approved-prd-ponytail
→ Execute
→ Review
→ Verification
```

中央只记录 Evidence 引用和摘要，不复制大规模日志或构建物。
