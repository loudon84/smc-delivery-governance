# GES Acceptance Closure Contracts

v5.0.2 Acceptance Closure 冻结跨 Change 共享契约并落地 C07–C13，使 CI 字节身份、审查优先级、authority、intent binding、install receipt 与可执行验收共用同一 SOT。

权威需求见 `docs/prd/PRD-GES-v5.0.2-Acceptance-Closure.md`。变更摘要见 `engineeing-skills/CHANGES-v5.0.2.md`；Candidate 见 `BASELINE-CANDIDATE-v5.0.2.md`。`BASELINE.md` 仍只记已接受生产基线。

## Byte Identity and EOL

Package 字节身份要求工作树字节与 git blob 字节一致，并由根 `.gitattributes` 强制 `eol=lf`。

`PACKAGE-MANIFEST.json` / `SHA256SUMS` 登记的是文件 raw bytes digest。Windows `core.autocrlf=true` 不得成为 release identity 的一部分；CI `--check`、`--explain-diff` 与 install release identity 共用同一字节定义。见 [[engineeing-skills/build_package_manifest.py#explain_diff]] 与 [[engineeing-skills/build_package_manifest.py#verify]]。

## Canonical Digests

序列化对象哈希复用 [[engineeing-skills/domain-runtime/domain_runtime.py#canonical_json]] 与 [[engineeing-skills/domain-runtime/domain_runtime.py#sha256_json]]；原始文件身份一律对 bytes 做 SHA256，禁止 loads→reserialize→hash。

Work Authority、Domain Intent Binding 属于 derived working-memory，不是第二 SOT；它们的 digest 必须可复算。Install lock 的 `package_manifest_sha256` 绑定 PACKAGE-MANIFEST raw bytes，见 [[install#Install Lock v2]]。

## Risk Snapshot Tri-State

Risk Facts Snapshot 解析结果必须区分 `ABSENT`、`VALID`、`INVALID`，供 Plan Review 与 legacy Domain fallback 共用。

`ABSENT`（旧 artifact 无 snapshot）对 adaptive review 非阻塞 hard signal；`INVALID`（存在但损坏/篡改）必须 fail-closed 为 hard risk。实现入口见 [[engineeing-skills/domain-runtime/risk_signals.py#parse_risk_snapshot]]；兼容包装仍见 [[engineeing-skills/domain-runtime/risk_signals.py#extract_risk_snapshot]]。

## Structured Domain Triggers

Domain blocking 只读 parsed row prefix token 与共享 Routing Facts；全文 regex 不得在 structured row 完整时产生 blocking FULL。

Core 只提供 [[engineeing-skills/domain-runtime/domain_table.py#validate_enum]] 等 primitives；硬触发集合写在各 Domain validator，守住 FI-16。旧自由文本 → `DOMAIN_SEMANTIC_LEGACY_FULL_REQUIRED`；新 artifact 非法 token → `DOMAIN_SEMANTIC_TOKEN_INVALID`。

## Telemetry Dispatch Correlation

每个 Harness dispatch 必须有 `dispatch_id`；result 必须回指同一 id；completeness 与 benchmark 共用该关联契约。

仅有 cache-hit 事件不得 `complete=true`；usage 缺失必须写 `usage_unavailable_reason`，禁止用 0 伪装。见 [[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/runtime_metrics.py#summarize]] 与 schema `smc.execution.telemetry-completeness.v1`。

## Reused Error Codes

Closure 复用既有稳定错误码，禁止改名：`PLAN_WRITE_OWNERSHIP_CONFLICT`、`DELIVERY_SCOPE_DRIFT`、`TDD_SCOPE_STALE`、`DEBUG_ARCHITECTURE_ESCALATION`、`LIVE_SUT_MISMATCH`、`PRD_STALE_OR_CONFLICTING`、`INSTALL_STALE_OWNED_FILE_MODIFIED`、`TELEMETRY_INCOMPLETE`。

新增码仅覆盖尚无能力：`WORK_AUTHORITY_*`、`DOMAIN_INTENT_BINDING_*`、`INSTALL_RECEIPT_*`、`TELEMETRY_ORPHAN_*`、`BENCHMARK_*`、`PILOT_EVIDENCE_INCOMPLETE`。

## Plan Review Precedence

Plan Review 深度按 R1–R7：当前 hard risk 高于 stale PASS→DELTA，避免把高风险变更误降为增量审查。

顺序为 prior≠PASS → FRESH_PASS → **current hard risk** → STALE PASS→DELTA → acceptance first review → low-risk legacy → 兜底 FULL。`INVALID` snapshot 算 hard signal；`ABSENT` 保持非阻塞。见 [[engineeing-skills/.agents/skills/smc-plan-review/scripts/assess_plan_review.py#classify]] 与 [[runtime-cost#Adaptive Plan Review]]。

## Work Authority Binding

生产 SPIKE/NONE 必须绑定可验证的 `smc.ges.work-authority.v1`，缺来源一律 `UNKNOWN`，不得默认 false。

[[engineeing-skills/.agents/skills/using-superpowers/scripts/work_authority.py#build_authority]] 写入 `.smc/work/<id>/work-authority.json`（`sources[]` + `authority_sha256`）。[[engineeing-skills/.agents/skills/using-superpowers/scripts/work_router.py#route]] 输出 `authority_sha256` / `authority_status`；CLI 强制 `require_authority_for_none`，库接口 `route(facts)` 保持兼容。见 [[acceptance-hardening#Work Router Research Trust]]。

## Domain Intent Binding

已批准 PRD 的 Domain Intent 与 Plan Ledger 必须 content-bound，防止执行期静默漂移。

[[engineeing-skills/domain-runtime/domain_intent.py#verify_bindings]] 重算 hash；缺失/陈旧分别回 `DOMAIN_INTENT_BINDING_MISSING` / `DOMAIN_INTENT_BINDING_STALE`，与 PRD 字节冲突回 `PRD_STALE_OR_CONFLICTING`。pack `intent_binding`（2.1.0）与 seed 表见 [[domain-packs#Intent Binding]]。

## Install Receipt

PASS transaction 之后写入非循环的 `smc.ges.install-receipt.v1`，绑定最终 lock 与 PASS manifest，而不是 PENDING 态。

[[engineeing-skills/install_v500.py#write_install_receipt]] 在 lock 写完且 transaction=`PASS` 后落盘；receipt 自身不入 transaction manifest 哈希。Rollback 在 transaction hash 匹配时显式删除 receipt，见 [[install#Install Receipt]]。

## Executable Acceptance Evidence

Acceptance harness 必须用真实行为断言 G16–G22，不得用 `callable()` / grep / 错误码顶替。

[[engineeing-skills/acceptance/run_acceptance.py#GoldenCorpus]] 复用 delivery / acceptance governance 夹具触发 `PLAN_WRITE_OWNERSHIP_CONFLICT`、`DELIVERY_SCOPE_DRIFT`、`TDD_SCOPE_STALE`、review/evidence `STALE`、`LIVE_SUT_MISMATCH`、`DEBUG_ARCHITECTURE_ESCALATION`。单写者 FI-04 由 [[engineeing-skills/.agents/skills/smc-plan-validator/scripts/validate_plan_v37.py#ownership_errors]] 实现。测试规格见 [[ges-tests#Acceptance Closure]]。

## Repository Protection Verifier

仓库保护校验器输出 protected / require_pr / required_checks / force_push_blocked / deletion_blocked / direct_update_restricted；token 只从 secret 读。

[[engineeing-skills/acceptance/verify_repository_protection.py#from_api]] 与 [[engineeing-skills/acceptance/verify_repository_protection.py#from_evidence]] 支持 live API 或离线 evidence。Ruleset 实际启用以 `RULESET-ACTIVATION.md` 手工步骤为准，CI 连续绿后再执行。

## Benchmark and Pilot Layout

Benchmark 实算 cohort A/B/C median 与 `reduction_pct`，并按全量 Safety/Quality/Efficiency/Stability 阈值裁决。

[[engineeing-skills/acceptance/run_benchmark.py#score]] 产出 `BENCHMARK_PASS|COST_GAP|REJECT|TELEMETRY_INCOMPLETE|BASELINE_NOT_REPRODUCIBLE`；成本降但质量恶化不得 ACCEPT。Pilot 证据布局在 `audit/ges/acceptance/<candidate>/`，缺证据时 [[engineeing-skills/acceptance/verify_pilot_evidence.py#verify]] 确定性返回 `PILOT_EVIDENCE_INCOMPLETE`。
