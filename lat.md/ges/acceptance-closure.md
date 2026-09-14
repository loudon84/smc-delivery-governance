# GES Acceptance Closure Contracts

v5.0.2 Acceptance Closure 冻结跨 Change 共享契约并落地 C07–C13；Architecture Closure 在其上迁移命名并关闭 C01–C07 架构断点。

权威需求见 `docs/prd/PRD-GES-v5.0.2-Acceptance-Closure.md`。命名迁移与后续锚点见 [[governance-architecture-closure]]。`BASELINE.md` 仍只记已接受生产基线。

## Byte Identity and EOL

Package 字节身份要求工作树字节与 git blob 字节一致，并由根 `.gitattributes` 强制 `eol=lf`。

`PACKAGE-MANIFEST.json` / `SHA256SUMS` 登记的是文件 raw bytes digest。Windows `core.autocrlf=true` 不得成为 release identity 的一部分；CI `--check`、`--explain-diff` 与 install release identity 共用同一字节定义。见 [[engineeing-skills/build_package_manifest.py#explain_diff]] 与 [[engineeing-skills/build_package_manifest.py#verify]]。

## Canonical Digests

序列化对象哈希复用 [[engineeing-skills/domain-runtime/domain_runtime.py#canonical_json]] 与 [[engineeing-skills/domain-runtime/domain_runtime.py#sha256_json]]；原始文件身份一律对 bytes 做 SHA256，禁止 loads→reserialize→hash。

Work Facts（及旧 Work Authority）、Domain Intent Binding 属于 derived working-memory，不是第二 SOT；digest 必须可复算。Install lock 的 `package_manifest_sha256` 绑定 PACKAGE-MANIFEST raw bytes；`package_version` 单一来源为 `core/manifest.json` bundle，见 [[install#Install Lock v2]] 与 [[governance-architecture-closure#Delivered Anchors]]。

## Risk Snapshot Tri-State

Risk Facts Snapshot 解析结果必须区分 `ABSENT`、`VALID`、`INVALID`，供 Plan Review 与 legacy Domain fallback 共用。

`ABSENT`（旧 artifact 无 snapshot）对 adaptive review 非阻塞 hard signal；`INVALID`（存在但损坏/篡改）必须 fail-closed 为 hard risk。实现入口见 [[engineeing-skills/domain-runtime/risk_signals.py#parse_risk_snapshot]]；兼容包装仍见 [[engineeing-skills/domain-runtime/risk_signals.py#extract_risk_snapshot]]。

## Structured Domain Triggers

Domain blocking 只读 parsed row prefix token 与共享 Routing Facts；全文 regex 不得在 structured row 完整时产生 blocking FULL。

Core 只提供 [[engineeing-skills/domain-runtime/domain_table.py#validate_enum]] 等 primitives；硬触发集合写在各 Domain validator，守住 FI-16。旧自由文本 → `DOMAIN_SEMANTIC_LEGACY_FULL_REQUIRED`；新 artifact 非法 token → `DOMAIN_SEMANTIC_TOKEN_INVALID`。

## Telemetry Dispatch Correlation

每个 Harness dispatch 必须有 `dispatch_id`；result 必须唯一终态回指同一 id；completeness 与 benchmark 共用该关联契约。

Architecture Closure 起缺配对回 `TELEMETRY_DISPATCH_UNPAIRED`（旧 `TELEMETRY_ORPHAN_*` 只读兼容）、重复 result 回 `TELEMETRY_RESULT_DUPLICATE`；缺 provider/model 回 `TELEMETRY_MODEL_IDENTITY_MISSING`；缺 token 会计回 `TELEMETRY_TOKEN_ACCOUNTING_MISSING` 或显式 `TOKEN_ACCOUNTING_UNAVAILABLE`。仅 cache-hit 不得 `complete=true`。见 [[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/runtime_metrics.py#summarize]]、[[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/runtime_metrics.py#ingest]] 与 [[governance-architecture-closure#Naming Migration Map]]。

## Reused Error Codes

Acceptance Closure 起复用稳定错误码：`PLAN_WRITE_OWNERSHIP_CONFLICT`、`DELIVERY_SCOPE_DRIFT`、`TDD_SCOPE_STALE`、`DEBUG_ARCHITECTURE_ESCALATION`、`LIVE_SUT_MISMATCH`、`PRD_STALE_OR_CONFLICTING`、`INSTALL_STALE_OWNED_FILE_MODIFIED`、`TELEMETRY_INCOMPLETE`。

Architecture Closure 起 canonical 新码见 [[governance-architecture-closure#Naming Migration Map]]（`WORK_FACTS_*`、`PLAN_SOURCE_PRD_*`、`PLAN_REVIEW_CURRENT_RISK_*`、`TELEMETRY_DISPATCH_UNPAIRED`、`BENCHMARK_THRESHOLD_*` 等）；旧名只读兼容一个 release。

## Plan Review Precedence

Plan Review 深度按 Architecture Closure §8.2 九级序；主码为 `PLAN_REVIEW_CURRENT_RISK_FULL_REQUIRED`。

实现顺序（freshness 回归约束）：prior≠PASS → **FRESH_PASS→NONE** → contradiction → hard risk → facts missing where required → STALE PASS+`delta_eligible`→DELTA → acceptance first → legacy low-risk → 兜底 FULL。`INVALID` 为 hard；STALE PASS 下 `ABSENT` 可 DELTA。见 [[engineeing-skills/.agents/skills/smc-plan-review/scripts/assess_plan_review.py#classify]]、[[engineeing-skills/.agents/skills/smc-plan-review/scripts/assess_plan_review.py#delta_eligible]] 与 [[runtime-cost#Adaptive Plan Review]]。

## Work Authority Binding

生产 SPIKE/NONE 必须绑定可验证权威；Architecture Closure 起 canonical 为 `smc.ges.work-facts.v1`。

[[engineeing-skills/.agents/skills/smc-work-router/scripts/work_facts.py#build_envelope]] 写入全量 facts、per-field provenance 与 `facts_digest`（落 `.smc/runs/<id>/routing/work-facts.json`）。[[engineeing-skills/.agents/skills/smc-work-router/scripts/work_router.py#route_bound]] 为 CLI 默认；仅 `--unsafe-raw-facts` 允许裸 facts。旧 [[engineeing-skills/.agents/skills/smc-work-router/scripts/work_authority.py#build_authority]] 为只读兼容 shim，不得单独宣称 bound。见 [[acceptance-hardening#Work Router Research Trust]] 与 [[governance-architecture-closure#Naming Migration Map]]。

## Domain Intent Binding

已批准 PRD 的 Domain Intent 与 Plan Ledger 必须 content-bound，防止执行期静默漂移。

[[engineeing-skills/domain-runtime/domain_intent.py#verify_bindings]] 重算 hash。Architecture Closure 起主码为 `PLAN_SOURCE_PRD_MISSING` / `PLAN_SOURCE_PRD_STALE` / `PLAN_DOMAIN_INTENT_STALE`（见 [[governance-architecture-closure#Naming Migration Map]]）；与 PRD 字节冲突仍回 `PRD_STALE_OR_CONFLICTING`。pack `intent_bindings`（2.2.0）见 [[domain-packs#Intent Binding]]。

## Install Receipt

Architecture Closure 起顺序为 receipt → lock → journal PASS。

[[engineeing-skills/install_v500.py#write_immutable_receipt]] 在 lock 之前落 `.smc/ges-install-receipts/<id>.json`；lock 携带 `install_receipt_path`/`install_receipt_sha256`。见 [[install#Install Receipt]] 与 [[governance-architecture-closure]]。

## Executable Acceptance Evidence

Acceptance harness 必须用真实行为断言 G16–G22，不得用 `callable()` / grep / 错误码顶替。

[[engineeing-skills/acceptance/run_acceptance.py#GoldenCorpus]] 复用 delivery / acceptance governance 夹具触发 `PLAN_WRITE_OWNERSHIP_CONFLICT`、`DELIVERY_SCOPE_DRIFT`、`TDD_SCOPE_STALE`、review/evidence `STALE`、`LIVE_SUT_MISMATCH`、`DEBUG_ARCHITECTURE_ESCALATION`。单写者 FI-04 由 [[engineeing-skills/.agents/skills/smc-plan-validator/scripts/validate_plan_v37.py#ownership_errors]] 实现。测试规格见 [[ges-tests#Acceptance Closure]]。

## Repository Protection Verifier

仓库保护校验器输出 protected / require_pr / required_checks / force_push_blocked / deletion_blocked / direct_update_restricted；token 只从 secret 读。

[[engineeing-skills/acceptance/verify_repository_protection.py#from_api]] 与 [[engineeing-skills/acceptance/verify_repository_protection.py#from_evidence]] 支持 live API 或离线 evidence。Desired-state 见 `governance/github/master-ruleset.json` 与 [[tools/check_repo_governance.py#main]]（`REPO_GOVERNANCE_PASS|DRIFT|UNAVAILABLE`）；C03-AC02 仍 OPEN。

## Benchmark and Pilot Layout

Architecture Closure 起 Benchmark 为 paired A/B（按 `case_id`）计算器；本 slice 只用 synthetic fixture，不跑真实数据。

[[engineeing-skills/acceptance/run_benchmark.py#score]] 产出 `BENCHMARK_READY|BENCHMARK_THRESHOLD_MET|BENCHMARK_THRESHOLD_NOT_MET|TELEMETRY_INCOMPLETE|UNPAIRED_CASES|BENCHMARK_INPUT_INVALID`；阈值 schema 为 `thresholds.v2`。Pilot 规格在 `acceptance/pilot/`（12 slot，状态 `NOT_EXECUTED`），由 [[engineeing-skills/acceptance/pilot/run_pilot.py#validate_matrix]] 校验；旧 [[engineeing-skills/acceptance/verify_pilot_evidence.py#verify]] 仅为兼容 shim。
