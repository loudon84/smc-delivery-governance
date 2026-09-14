# GES Consumer Bootstrap

Consumer Bootstrap 把 GES 从 Skill Package 升级为可审计、可补齐、可验证的 Consumer 接入平台，覆盖 Audit → Gap → Remediation → Apply → Validate。

权威需求见 `docs/prd/PRD-GES-v5.0.5-Consumer-Bootstrap-Platform-Integration.md`。本页记录交付锚点；Pilot / Benchmark / Baseline promotion 仍禁止。

## Pipeline

五段式入口均在 `engineeing-skills/consumer-bootstrap/`，默认只读；唯一 writer 是 apply，且 dry-run 为默认。

1. [[engineeing-skills/consumer-bootstrap/audit_consumer.py#audit]] — 只读探测 GES / Spec Kit / Superpowers
2. [[engineeing-skills/consumer-bootstrap/analyze_gap.py#analyze]] — 分层 `PASS|PARTIAL|MISSING` + claim 词表
3. [[engineeing-skills/consumer-bootstrap/generate_remediation.py#generate]] — 有序 `WRITE_TEMPLATE|RUN_COMMAND|MANUAL`
4. [[engineeing-skills/consumer-bootstrap/apply_remediation.py#apply_plan]] — 只补缺失、事务回滚、receipt
5. [[engineeing-skills/consumer-bootstrap/validate_consumer.py#validate]] — 端到端链路 verdict

报告落点：`.smc/consumer-bootstrap/`；apply receipt：`.smc/ges-bootstrap-receipts/<id>.json`。

## Consumer Audit

Audit 证明 Consumer 是否具备 GES Runtime、Spec Kit 脚手架与方法 skill 面，不修改任何文件（报告写入除外）。

检查 GES：install lock v2、receipt、profile、domain runtime、managed skills、plan validator、delivery、acceptance surface、telemetry。Spec Kit：`.specify/` 脚手架 + 只读 [[engineeing-skills/integrations/spec-kit/probe.py#probe]]。Superpowers：provenance pinned set + PRD shim set。

## Gap Analysis

Gap 把 audit 转成机器可读分层 verdict 与 claim，禁止用模糊的 “integrated”。

允许 claim：`INSPIRED`、`ADAPTER_READY`、`UPSTREAM_PINNED`、`EXTERNAL_VERIFIED`、`GES_NATIVE`、`NATIVE_ONLY`。脚手架 = `ADAPTER_READY`；shim skill = `GES_NATIVE`；缺 CLI = `NATIVE_ONLY`。

## Automated Remediation

Remediation 用 GES 自有模板补齐缺口，不 vendor 上游字节，不覆盖已有文件。

允许写：`.specify/constitution.md`、`templates/`、`scripts/`、`specs/README.md`；`.agents/skills/<shim>/SKILL.md`；`.agents/ges/{spec-kit-binding,superpowers-binding,governance-policy,spec-superpower-ges}.json`。禁止写：`.specify/spec.md`（第二套 requirements SOT）、`.agents/ges/profile.json`（installer 独占）。这是对 v5.0.3「不得创建第二 requirements SOT」不变量的契约收窄，不是推翻 probe/import 禁令。

## Consumer Validation

Validation 输出 `smc.ges.consumer-validation.v1`，逐项判定 Runtime / Spec Kit / Superpowers / handoff / Delivery / Evidence / Release。

失败码：`CONSUMER_VALIDATION_FAILED`；成功：`CONSUMER_VALIDATION_PASS`。

## Scope Boundary

本工作项不执行 Token Benchmark、Consumer Pilot、生产部署或 `BASELINE.md` promotion；Bundle 保持 `5.0.0`。

smc-copilot-desktop 本轮以只读 audit/gap/plan 为验收；`--apply` 需显式确认。ChatBox Artifact Preview 产品验证链记为 OPEN。
