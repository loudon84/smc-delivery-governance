---
status: DRAFT
title: GES Consumer Bootstrap Platform Integration PRD
version: v5.0.5
---

# GES Consumer Bootstrap Platform Integration PRD v5.0.5

## 1. 背景

GES v5 已完成治理能力建设：

-   Plan Validation
-   Delivery State
-   Evidence Governance
-   Acceptance Runtime
-   Install Provenance
-   Rollback Control

但当前 GES 更接近工程治理 Skill Package。

本版本目标：

> 让 GES 具备类似 GitHub Actions / Terraform Provider 的平台级 Consumer
> 接入能力，而不是单纯工程 Skill 包。

------------------------------------------------------------------------

# 2. 目标架构

    Consumer Project

            |
            v

    GES Consumer Bootstrap

            |
            +----------------+
            |                |
            v                v

        Spec Kit        Superpowers

        需求治理          执行治理

            \             /

                 GES

            交付真值治理

职责：

  层            职责
  ------------- ---------------------------------------------------
  Spec Kit      PRD、Spec、Acceptance、Plan Input
  Superpowers   Planning、Implementation、Debugging、Verification
  GES           Validation、Evidence、Release、Rollback

------------------------------------------------------------------------

# 3. 核心能力

新增：

    consumer-bootstrap/

    ├── audit_consumer.py
    ├── analyze_gap.py
    ├── generate_remediation.py
    ├── apply_remediation.py
    ├── validate_consumer.py
    ├── schemas/
    └── templates/

------------------------------------------------------------------------

# 4. Consumer Installation Audit

命令：

``` bash
python consumer-bootstrap/audit_consumer.py <project>
```

输出：

-   consumer-audit-report.json
-   consumer-audit-report.md

检查：

## GES

验证：

-   Runtime
-   Plan Validator
-   Delivery Runtime
-   Domain Runtime
-   Acceptance Runtime
-   Telemetry
-   Install Receipt

## Spec Kit

检查：

    .specify/

    constitution.md
    templates/
    specs/
    scripts/

## Superpowers

检查：

    .agents/skills/

    brainstorming
    writing-plans
    executing-plans
    systematic-debugging
    verification
    finishing-branch

------------------------------------------------------------------------

# 5. Gap Analysis

自动生成：

    consumer-gap-analysis.md

示例：

    GES:
    PASS

    Spec Kit:
    MISSING

    Superpowers:
    PARTIAL

同时生成：

    Remediation Plan

------------------------------------------------------------------------

# 6. Automated Remediation

## Spec Kit Bootstrap

生成：

    .specify/

    constitution.md
    templates/
    specs/
    scripts/

## Superpowers Bootstrap

生成：

    .agents/skills/

    brainstorming
    writing-plans
    executing-plans
    systematic-debugging
    verification

## GES Integration Contract

生成：

    .ges/

    consumer-profile.yaml
    spec-kit-binding.yaml
    superpowers-binding.yaml
    governance-policy.yaml

------------------------------------------------------------------------

# 7. Spec Kit + Superpowers + GES Bridge

新增：

    .ges/spec-superpower-ges.yaml

定义：

``` yaml
spec_kit:
  output:
    prd

handoff:
  spec_to_superpower:
    enabled: true
  plan_to_ges:
    enabled: true

ges:
  validation:
    required: true
  release_gate:
    required: true
```

------------------------------------------------------------------------

# 8. Consumer Validation

命令：

``` bash
python consumer-bootstrap/validate_consumer.py
```

验证：

    PASS GES Runtime
    PASS Spec Kit
    PASS Superpowers
    PASS Spec -> Plan handoff
    PASS Plan -> Delivery
    PASS Evidence
    PASS Release Governance

------------------------------------------------------------------------

# 9. smc-copilot-desktop 落地流程

目标：

    smc-copilot-desktop

流程：

    GES install
        |
    Consumer Audit
        |
    Gap Analysis
        |
    Remediation Plan
        |
    Bootstrap Apply
        |
    Full Validation

------------------------------------------------------------------------

# 10. 第一阶段验证功能

选择：

    ChatBox Artifact Preview

覆盖：

-   Vue/React UI
-   Backend API
-   File System
-   Agent
-   MCP
-   Release

验证链：

    Spec Kit
        |
    Superpowers
        |
    GES
        |
    Evidence
        |
    Release

------------------------------------------------------------------------

# 11. 非目标

本版本不包含：

-   Token Benchmark
-   Consumer Pilot
-   Production Deployment
-   Baseline Promotion

------------------------------------------------------------------------

# 12. DoD

    [ ] Consumer Audit 可执行

    [ ] GES 能力自动识别

    [ ] Spec Kit 缺口识别

    [ ] Superpowers 缺口识别

    [ ] Gap Report 自动生成

    [ ] Remediation Plan 自动生成

    [ ] Bootstrap 自动补齐

    [ ] Bridge Contract 自动生成

    [ ] Consumer Validation 可执行

    [ ] smc-copilot-desktop 完成完整链路

------------------------------------------------------------------------

# 13. 最终状态

GES v5.0.5：

从：

    Engineering Skill Package

升级为：

    AI Software Delivery Platform

具备：

    Install
    Audit
    Bootstrap
    Validate
    Govern
    Release

完整 Consumer 生命周期能力。

------------------------------------------------------------------------

# 14. 契约收窄记录（相对 v5.0.3）

本版本 **不推翻** v5.0.3 硬不变量「外部 provider 不得创建第二套 requirements SOT / Plan / Ledger」。落地时做如下收窄：

1. **允许** Consumer Bootstrap `--apply` 在文件缺失时写入非 SOT 脚手架：`.specify/constitution.md`、`templates/`、`scripts/`、`specs/README.md`。
2. **禁止** 写入 `.specify/spec.md` 或任何第二套 requirements SOT；`integrations/spec-kit/probe.py` 与 `import_proposal.py` 仍不得 `init` / 写 Consumer-root SOT。
3. **Bridge Contract** 落在 `.agents/ges/*.json`（复用既有 config root），**不**新增 `.ges/*.yaml`，**不**引入 PyYAML。
4. 缺失方法 skill 使用 GES 自有模板，claim 为 `GES_NATIVE`；不得在无 provenance 字节时宣称 `UPSTREAM_PINNED`。
5. `.agents/ges/profile.json` 仍由 `install.py` 独占；bootstrap 不得覆盖。
