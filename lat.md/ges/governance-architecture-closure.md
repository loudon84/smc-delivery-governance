# GES Governance Architecture Closure

v5.0.2 Governance Architecture Closure 冻结与 Acceptance Closure（8ade941）的命名迁移映射，并关闭 C01–C07 治理架构断点；只完成架构可执行性，不执行真实 Pilot/Benchmark。

权威需求见 `docs/prd/PRD-GES-v5.0.2-Governance-Architecture-Closure.md`。`BASELINE.md` 禁止 promotion。Pilot/Benchmark 状态固定 `NOT_EXECUTED`。

## Naming Migration Map

PRD 名字为准；旧 envelope/code 只读兼容一个 release，不得据旧名宣称已 bound。

| Legacy (Acceptance Closure) | Canonical (Architecture Closure) |
|---|---|
| `smc.ges.work-authority.v1` | `smc.ges.work-facts.v1` |
| pack `intent_binding.fields` | pack `intent_bindings{plan_column,mode}` (2.2.0) |
| `DOMAIN_INTENT_BINDING_MISSING` | `PLAN_SOURCE_PRD_MISSING` |
| `DOMAIN_INTENT_BINDING_STALE` | `PLAN_SOURCE_PRD_STALE` / `PLAN_DOMAIN_INTENT_STALE` |
| `PLAN_REVIEW_HARD_RISK_FULL_REQUIRED` | `PLAN_REVIEW_CURRENT_RISK_FULL_REQUIRED` |
| (none) | `PLAN_REVIEW_DELTA_INELIGIBLE` |
| `TELEMETRY_ORPHAN_DISPATCH` | `TELEMETRY_DISPATCH_UNPAIRED` |
| `thresholds.v1` (+stability) | `thresholds.v2` (PRD §22 keys only) |
| `BENCHMARK_PASS\|COST_GAP\|REJECT\|…` | `BENCHMARK_READY\|THRESHOLD_MET\|THRESHOLD_NOT_MET\|UNPAIRED_CASES\|…` |
| `verify_pilot_evidence.py` | `acceptance/pilot/run_pilot.py` |

`PRD_STALE_OR_CONFLICTING` 保留不变。

## Frontend Token Canonical and Alias

Canonical grammar follows PRD §11.2 (`TOKEN:<detail>` where required). Deprecated aliases remain readable.

| Field | Canonical | Deprecated alias |
|---|---|---|
| Layout | `UNCHANGED` / `MODIFY` / `NEW_HIERARCHY` | `EXTEND_EXISTING`→`MODIFY`, `NAVIGATION_CHANGE`/`MULTI_PANEL`→`NEW_HIERARCHY` |
| State Ownership | `UNCHANGED` / `LOCAL` / `SHARED` / `NEW_OWNER` / `MOVE_OWNER` | `LOCAL_EXISTING`→`LOCAL`, `EXTEND_OWNER`→`SHARED`, `STORE_CHANGE`→`MOVE_OWNER` |
| Responsive | `UNCHANGED` / `MODIFY` / `NEW_ARCHITECTURE` | `EXTEND`→`MODIFY`, `ARCHITECTURE_CHANGE`→`NEW_ARCHITECTURE` |

FULL triggers: `NEW_HIERARCHY`, `NEW_OWNER`/`MOVE_OWNER`, `NEW_ARCHITECTURE`, new design-system primitive.

## Compatibility Policy

旧 `work-authority.v1` 可被 `work_facts` 只读转换，但不得单独产生 production NONE。旧 `intent_binding.fields` 在 pack loader 内升级读入。旧 telemetry orphan code 映射到 unpaired。旧单文件 `ges-install-receipt.json` 在 rollback 时仍可清理。

## Work Facts Authority

`smc.ges.work-facts.v1` 是生产路由权威：全量 facts、per-field provenance、`facts_digest`。

白名单来源 `ROADMAP|FEATURE|PRD|PLAN|ORCHESTRATOR_REQUEST|DERIVED`；`WORKER_ASSERTION|MODEL_GUESS|PROMPT_TEXT_ONLY` 不得单独支撑 `governed=false`。合并策略保守（风险/生产字段 true wins）。实现见 Delivered Anchors 中的 work_facts / route_bound。

## Package Version Single Source

`PACKAGE-MANIFEST.json` 的 `package_version` 必须等于 `core/manifest.json` 的 `bundle`，禁止硬编码漂移。

CI 不自动 regenerate manifest；validate 与 Package Gate 均以 `--check` 失败闭环。

## Repo Governance Desired State

tracked `governance/github/master-ruleset.json`（`smc.repo.ruleset.v1`）是 master 保护期望态；checker 只读。

输出 `REPO_GOVERNANCE_PASS|DRIFT|UNAVAILABLE`。实际启用（C03-AC02）仍为 Admin 手工步骤。

## Out of Scope Markers

本 slice 明确不执行：真实 Consumer Pilot、真实 4.4.1 vs 5.x Benchmark、Token 收益结论、`BASELINE.md` promotion、release tag。C03-AC02（master Ruleset 实际启用）保持 OPEN，待 CI 连续绿后由 Admin 手工启用。

## Delivered Anchors

C01–C07 落地锚点（不含真实执行）：

- Package version：[[engineeing-skills/build_package_manifest.py#package_version]]
- Plan review：[[engineeing-skills/.agents/skills/smc-plan-review/scripts/assess_plan_review.py#classify]]、[[engineeing-skills/.agents/skills/smc-plan-review/scripts/assess_plan_review.py#delta_eligible]]
- Repo governance：[[tools/check_repo_governance.py#main]] + `governance/github/master-ruleset.json`
- Work facts：[[engineeing-skills/.agents/skills/using-superpowers/scripts/work_facts.py#build_envelope]]、[[engineeing-skills/.agents/skills/using-superpowers/scripts/work_router.py#route_bound]]
- Domain：[[engineeing-skills/domain-runtime/domain_intent.py#validate_intent_binding]]、packs `2.2.0` `intent_bindings`
- Install：[[engineeing-skills/install_v500.py#write_immutable_receipt]] → lock → PASS
- Telemetry：[[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/runtime_metrics.py#summarize]]
- Benchmark：[[engineeing-skills/acceptance/run_benchmark.py#score]]（synthetic `--selftest` only）
- Pilot：[[engineeing-skills/acceptance/pilot/run_pilot.py#validate_matrix]]

