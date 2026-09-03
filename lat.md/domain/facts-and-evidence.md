# Facts and Evidence

控制面区分观察、验证与裁决。Receipt 只能上报观察事实；VERIFIED / DONE / PASS 必须由中央 Gate 写入并留下审计。

分层总览见 [[architecture/trusted-delivery-loop#Fact Layers]]。

## Delivery Receipt

每个项目、每个 Work Package 一份机器摘要，记录 source_revision、本地状态、Stage PRD/Plan/PR/Commit 与 Acceptance 引用。

路径：`.agents/governance/receipts/<WORK_PACKAGE_ID>.yaml`。`receipt_version: "2"` 的受源码控制 ArtifactRef 必须带完整强身份。Receipt 自称 PASS 不能写中央 VERIFIED。见 [[ADR-005-delivery-receipt]]。

## Delivery Ledger

Ledger 是中央对 Receipt 的观察投影，位于 Feature 下的 `delivery-ledger/`。`sync_repo_state.py` 只更新 observed facts，不直接改生命周期状态。

## ArtifactRef

ArtifactRef v2 给受源码控制的交付物强身份：仓库、路径、40 位 commit、blob SHA、content SHA-256、类型与 source_revision。

路径字符串存在不算证据。中央同步时核实 path@commit、blob/content hash、PRD `APPROVED`、Plan `VALIDATED|PASS`。失败标 `DIVERGED`。校验：[[tools/artifact_verify.py#verify_artifact_ref]]。见 [[ADR-007-artifact-ref-v2]]。

## Acceptance Attestation

Attestation 把项目 CI 的 Manifest/Report digest 与 workflow 身份钉在一起。中央核对 report/manifest sha256、HEAD SHA、workflow 成功结论与 workflow_sha。

没有中央 Attestation 的 Receipt PASS 不能推进 Consumer VERIFIED。见 [[architecture/acceptance-evidence]]。

## IntegrationRun

每次跨仓集成尝试生成不可变记录 `integration/runs/<SCENARIO_ID>/<INTEGRATION_RUN_ID>.yaml`。必须包含 runner、双方 pin、workflow 证据与输出摘要。

历史不可覆盖。`history.yaml` 在 `runs: []` 时仍是权威等待事实。Feature DONE 要求最新一次结果为 PASS。见 [[ADR-009-integration-run]]。查询：[[tools/state_machine.py#latest_integration_run]]。

## Audit Event

生命周期事实是 append-only `audit/transitions/*.ndjson`。每次成功推进必须同时写 materialized YAML 与 transition event。

事件失败则回滚 YAML。无 event 不得 `--apply`。写入：[[tools/audit_events.py#append_transition_event]]、[[tools/state_transaction.py#commit_yaml_transition]]。见 [[ADR-010-audit-materialized-state]]。

## Governance Kit Release

Governance Kit 是不可变 Release，不是当前 HEAD 的文件拷贝。生产 pin `version / tag / commit / manifest_sha256`。

`SHA256SUMS` 必须覆盖 `manifest.json` 与全部 Kit 文件。开发用 source-tree 必须显式 `--allow-source-tree`。见 [[ADR-008-canonical-governance-kit]]。
