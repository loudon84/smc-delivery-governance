# GES v5.0.3 Safety and Runtime Integration Closure

v5.0.3 关闭 rollback、Work Facts、仓库保护证据、安装 Receipt 与 v3.7 Intent Binding 的 fail-open，并把 Spec Kit/Superpowers 接入改为可验证 provider；Pilot/Benchmark 保持 NOT_EXECUTED。

权威需求见 `docs/prd/PRD-GES-v5.0.3-Safety-and-Runtime-Integration-Closure.md`。本页记录已交付锚点，不宣称效果验证或基线升格。

## Scope Boundary

本工作项只允许安全修复、Runtime 适配、确定性回归与文档一致性收口。

Consumer Pilot、真实成本 Benchmark、Token 收益结论、`BASELINE.md` promotion 和 release tag 均禁止；两类效果验证固定保持 `NOT_EXECUTED`。

## Delivered Fail-Closed Gates

P0/P1 安全边界已改为显式阻断，不再用默认值或裸路径拼接制造假成功。

- Rollback：[[engineeing-skills/rollback.py#resolve_record_target]] / [[engineeing-skills/rollback.py#validate_manifest]] 在任何写入前校验 containment；见 [[engineeing-skills/tests/test_rollback_security.py]]。
- Work Facts：[[engineeing-skills/.agents/skills/smc-work-router/scripts/work_facts.py#verify_envelope]] 强制全字段 provenance；[[engineeing-skills/.agents/skills/smc-work-router/scripts/work_router.py#route_bound]] 要求 repo 与 true-wins merge。
- Repo evidence：[[engineeing-skills/acceptance/verify_repository_protection.py#parse_evidence]] 三态无正向默认；[[tools/check_repo_governance.py#compare]] 消费严格 parser。
- Install receipt：[[engineeing-skills/install_v500.py#atomic_write_text]] 将 receipt/pointer/lock 纳入同一事务。
- v3.7 binding：[[engineeing-skills/.agents/skills/smc-plan-validator/scripts/validate_plan_v37.py#intent_binding_errors]] 全字段强制；[[engineeing-skills/domain-runtime/domain_intent.py#canonical_empty_binding]] 处理无 Domain。

## Three-Stage Ownership

三段式架构允许外部 provider 增强 UX 和方法，但 Canonical Artifact 与 Delivery Truth 继续由 GES 单一 Owner 持有。

- Spec Kit adapter：`integrations/spec-kit/` — 状态 `ADAPTER_READY`，CLI 缺失时 `NATIVE_ONLY`；[[engineeing-skills/integrations/spec-kit/probe.py#probe]] / [[engineeing-skills/integrations/spec-kit/import_proposal.py#import_proposal]]。
- Superpowers method provider：`integrations/superpowers/` — 状态 `UPSTREAM_PINNED`；[[engineeing-skills/integrations/superpowers/dispatch.py#build_task_packet]] / [[engineeing-skills/integrations/superpowers/verify_result.py#verify_result]]。
- Canonical Work Router：`smc-work-router`；`using-superpowers` 为 deprecated shim。

## Runtime Claim States

集成声明必须区分理念、适配器、固定上游和真实外部调用。

允许：`INSPIRED`、`ADAPTER_READY`、`UPSTREAM_PINNED`、`EXTERNAL_VERIFIED`。本轮 Spec Kit = `ADAPTER_READY`；Superpowers = `UPSTREAM_PINNED`。

## Verification Boundary

验收使用 deterministic、failure-injection、provider conformance 与 Delivery frozen regression，不包含 Pilot/Benchmark 实际执行。

Package Gate 内算法 self-test 不改变 `Pilot/Benchmark = NOT_EXECUTED`。
