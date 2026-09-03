# Trusted Delivery Control Loop

v1.2.1 把控制面从「Git YAML 自动化」收成 **Closed Loop v1**。中央仍然不执行项目测试、不拥有业务代码；它只验证身份、证据和状态推进。

分层定义见 [[domain/facts-and-evidence]]；事务写入见 [[ADR-010-audit-materialized-state]]。

## Fact Layers

控制面把「看见」「证明」「裁决」分成五层，禁止用下层自称覆盖上层。

```text
Lifecycle Audit Facts     audit/transitions/*.ndjson     append-only
Materialized State        Git YAML                       current projection
Observed Facts            Delivery Ledger                synced from Receipt
Verified Evidence         Acceptance Attestation         central-acceptance-gate
Proven Integration        immutable IntegrationRun       runner + workflow
```

Remote Receipt 只能更新 Observed Facts。`VERIFIED` / `DONE` / Integration `PASS` 只能由中央 Gate + Reconciler 写入 Materialized State，并同时留下 Audit Event。

## Control Loop

每次跨仓交付按同一循环推进：先钉住 Kit 与身份，再同步观察事实，最后由 Gate 与 IntegrationRun 关门。

```text
Canonical Kit Release
  → Project Bootstrap / Binding pin
  → Delivery Receipt v2 (ArtifactRef)
  → Event-driven Sync (hourly = repair)
  → Semantic + Provenance Verify
  → Central Acceptance Attestation
  → Reconcile: Contract → WP → Roadmap → Feature
  → IntegrationRun attempt
  → Feature DONE
```

Reconciler 顺序见 [[ADR-002-state-machines]]。

## Closed Loop v1 Enforcement

以下条款把循环收成可执行门禁，而不是文档约定。空 Integration 历史不得被读成 PASS。

1. 生产 Kit 安装只接受 canonical immutable release；source-tree 必须显式 `--allow-source-tree`。
2. `receipt_version: "2"` 的受源码控制 ArtifactRef 必须具备 commit / blob SHA / content SHA-256。
3. Feature `source_prd` 必须是 APPROVED Source PRD ArtifactRef，禁止 Feature 缓存 Contract `current_state`。
4. Consumer Work Package `VERIFIED` 只认中央已验证的 Acceptance Attestation，不认 Receipt 自称 `PASS`。
5. Integration `PASS` 与 Feature `DONE` 只认不可变 IntegrationRun 尝试及其 runner/workflow 证据。
6. 测试必须在隔离 `SMC_GOVERNANCE_ROOT` 中运行，禁止污染中央 SOT。
7. IntegrationRun `history.yaml` 在 `runs: []` 时仍是权威等待事实；空历史不等于 PASS。Consumer 在中央 Attestation 之前保持 IMPLEMENTING，Scenario 保持 WAITING_CONSUMER。
