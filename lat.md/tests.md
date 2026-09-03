---
lat:
  require-code-mention: true
---
# Tests

治理控制面的关键测试规格。它们验证身份合同、状态机门禁、Kit 安装与测试隔离，而不是复述实现细节。

## Feature and registry

Feature skeleton、Registry 与合同解析必须在隔离沙箱中保持机器可校验。

### Feature skeleton validates offline

离线 `validate_feature` 必须接受符合 schema 的 Feature 目录，证明中央 SOT 自身可校验。

### Registry catalogs are valid

`validate_registry` 必须枚举已登记的 Project/Repository，拒绝残缺目录进入控制面。

### Contract status reports pinned release

`contract_status` 必须显示 Consumer pin 的 Release version，而不是 Feature 缓存的 current_state。

### Create feature writes strong Source PRD

`create_feature --apply` 必须写入 ArtifactRef v2 的 Source PRD，且不得在 Feature 合同列表里缓存 `current_state`。

## Receipts and artifacts

Receipt 与 ArtifactRef 必须携带强身份字段，路径存在不能代替 hash。

### Receipt schema accepts fixture

标准 Receipt fixture 必须通过 `validate_receipt`，作为项目回报合同的基线。

### ArtifactRef schema requires hashes

ArtifactRef schema 必须把 commit、blob_sha、sha256、source_revision 列为 required。

### Traceability schema requires strong Source PRD

Traceability 中的 ArtifactRef 定义必须要求 commit / blob_sha / sha256，防止弱引用混入交付链。

### Acceptance attestation schema exists

Attestation schema 必须要求 report_sha256 与 manifest_sha256，使中央 Gate 能核对 CI 产物。

### Integration run schema requires real commits

IntegrationRun 的仓库输入 commit 必须是 40 位十六进制 SHA，禁止短 SHA 或占位符。

### Build receipt emits v2 strong identity

本地 `build_receipt` 必须输出 `receipt_version: "2"`，并为 Stage PRD 填 blob_sha 与 sha256。

## Acceptance and gates

中央 Gate 验证证据，不执行项目测试。缺少 Attestation 或消费者未就绪时不得 PASS。

### Acceptance gate passes offline fixture

离线 Acceptance Gate 对合法 Manifest/Report fixture 必须 PASS，证明语言无关验收合同可独立校验。

### Acceptance gate offline mode

不访问 GitHub 时，`--offline` 仍须能完成 fixture 级验收，供 CI 与本地回归使用。

### State machine blocks VERIFIED without attestation

Consumer Work Package 在没有中央 Attestation 时，`transition_state --to VERIFIED` 必须被拒绝。

### Integration gate waits for consumer

消费者未就绪时 Integration Gate 必须以非就绪退出码返回，并报告 WAITING_ 状态。

### Empty integration history is not PASS

`history.yaml` 的 `runs: []` 是等待事实，不得被当成 PASS，也不得在未 READY 时写出 IR 文件。

### Provider role gate allows contract release

Provider Work Package 可用合同 release 证据进入 VERIFIED，而不要求伪造 Stage PRD。

### Contract resolver honors consumer pin

`resolve_contract` 必须按 Consumer 仓库的 pin 返回对应 Release 状态，而不是任意 current_release。

## Sync and onboarding

同步与纳管必须在沙箱中安装 Kit、对齐 Receipt，并且默认不改生产源树。

### Sync repo state reports all SYNCED

用合法 Receipt 同步后，所有活动 Work Package 的 sync_state 应为 SYNCED，且不得改写源仓库 SOT。

### Governance sync bootstraps kit and CI

`governance_sync --apply` 必须写入 binding、Receipt 模板与 CI workflow，`--check` 随后必须通过。

### Governance sync source-tree is explicit

开发态 source-tree 安装必须显式 `--allow-source-tree`，并且 Binding 仍要记录 manifest_sha256。

### Project onboarding dry run

`project_onboard` 默认 dry-run 必须成功描述将要登记的 Project/Repository，且不写入中央 Registry。

## Isolation and audit

测试、dry-run 与审计写入不得污染中央 SOT；环境变量优先级必须稳定。

### Tests do not mutate source SOT

即使测试带 `--apply` 调用状态机，源仓库 Feature YAML 也必须保持不变。

### State invariant tool does not write

`verify_state_invariants` 只检查、不写文件，运行后不得留下 `.tmp`。

### Audit event appends ndjson

`append_transition_event(apply=True)` 必须在隔离根下写出 `audit/transitions/**/events.ndjson`。

### Kit release checksums close over manifest

Kit release 的 SHA256SUMS 必须包含 `manifest.json`，且不得混入 CRLF。

### Transition dry run is non-mutating

没有 `--apply` 的 `transition_state` 不得改写 Roadmap 或其他 materialized YAML。

### Process env wins over dotenv

`.env` 不得覆盖已存在的进程环境变量，只填充尚未设置的键。
