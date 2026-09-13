# GES Acceptance Hardening

Acceptance Hardening 在不改 Frozen Invariants 的前提下加固路由信任、风险判定、Domain 语义、安装 provenance 与可观测性，使 NONE/LEAN/FULL 与安装身份可由工程证据复现。

权威需求见仓库 `docs/prd/PRD-GES-v5.0.1-Acceptance-Hardening.md`。Candidate 变更摘要见 `engineeing-skills/CHANGES-v5.0.1.md`。

## Work Router Research Trust

`research_only` 只是 hint（`research_intent` 别名），不能单独产生 SPIKE/NONE。

[[engineeing-skills/.agents/skills/using-superpowers/scripts/work_router.py#effective_research_only]] 仅在 authority 字段全部显式为 false、且 previous profile 为 None/NONE 时返回有效 research。缺字段、unknown、governed/production 冲突一律 fail-closed 到 FULL，并返回稳定 reason code。路由输出 schema 为 `smc.ges.work-route.v2`，见 [[engineeing-skills/.agents/skills/using-superpowers/scripts/work_router.py#route]]。

## Structured Risk Runtime

PRD、Plan Validator 与 Plan Review 共用同一风险解析模块，禁止第二套风险字段 SOT。

[[engineeing-skills/domain-runtime/risk_signals.py#resolve_risk]] 顺序固定为 Structured Facts → Consistency → Negation-aware Text Hint → Fallback → Escalation。否定句不得当作肯定高风险；contradiction fail-closed。Plan seed 写入 Risk Facts Snapshot 投影，见 [[engineeing-skills/.agents/skills/smc-plan-from-approved-prd-ponytail/scripts/create_plan_seed_v37.py#main]]。

## LEAN First Review Clearance

带 `acceptance_contract` 的 LEAN Plan 首次审查可通过确定性 clearance 进入 DELTA/LIGHT；否则仍 FULL。

[[engineeing-skills/domain-runtime/risk_signals.py#acceptance_structure_clearance]] 要求 structured 无高风险、capability facts 完整、无 LIVE/FAULT/EXTERNAL。

## Domain Semantic Validation

Core 只提供 enum/条件 primitives；Frontend/Backend/Ops validator 持有业务合法值。

[[engineeing-skills/domain-runtime/domain_table.py#validate_enum]] 与条件 helpers 不硬编码 domain id。非法 Framework、Backend breaking+LEAN、Ops irreversible 无 rollback 必须确定性 FAIL/FULL_REQUIRED。

## Install Lock v2

Consumer install lock 证明 package bytes 身份，并安全清理未修改的 stale package-owned 文件。

[[engineeing-skills/install_v500.py#build_install_lock]] 写入 `smc.ges.install-lock.v2`（release_identity + owned_files）。[[engineeing-skills/install_v500.py#reconcile_stale_owned_files]]：v1 skip destructive；v2 未改动 stale 删除并入 rollback；已改动 stale 阻断。

## Runtime Telemetry

Telemetry 记录 tier/token/retry/cache/reviewer 计数，不是 Final Evidence。

[[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/runtime_metrics.py#summarize]] 缺文件时返回 `TELEMETRY_INCOMPLETE`。正常 Delivery 不因缺 telemetry 阻塞；Benchmark 要求完整。

## Package Gate

仓库 CI 提供稳定 status `GES Package Gate / validate-package`，在连续 PASS 后再设为 master required check。

实现于 `.github/workflows/governance-ci.yml` 的 `ges-package-gate` job：manifest `--check`、`validate_package.py`、无未预期 mutation。
