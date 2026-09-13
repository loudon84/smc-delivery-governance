# GES Domain Pack Framework v1

Domain Pack 把专业工程能力挂到既有 GES 流水线上；v5 在保留 v1 兼容性的基础上增加 v2 preplan。Core 只认合同，不硬编码具体 domain id。

## Purpose

Domain Pack 是专业工程能力扩展，不是新的 workflow。GES Core 读取 domain-pack v1/v2 和 domain-activation v1/v2 合同，不允许在 Core runtime 中硬编码具体 domain id。

## Three Decisions

三条发布决策固定 Domain 与 Core、Profile、Plan 的边界，防止第二套 workflow 出现。

1. Domain Pack 提供 `preplan | engineering | review | verification` provider（v1 无 preplan），不得拥有 Plan、Delivery、Commit、Roadmap canonical state。
2. Consumer Profile 决定项目可用 Domain；Canonical Plan 的 Change Matrix 决定当前 delivery 实际激活集合。
3. 新增 Domain 必须能够通过 registry + pack manifest + activation rules + provider skills 接入，不修改 Core routing code。

## Installed Layout

安装后 Domain Runtime、Registry 与各 pack 落在 `.agents/ges/`，与 Core skills 目录分离。

```text
.agents/ges/
├── profile.json
├── domain-runtime/
│   └── domain_runtime.py
└── domain-packs/
    ├── registry.json
    └── <domain>/
        ├── pack.json
        ├── activation.json
        └── policy-lock.json   # optional
```

## Domain Pack Contract

v1 的 `pack.json` 声明以下字段；v2 保留这些字段并增加必需的 preplan provider、preplan_section 和 preplan_validator。

- `schema = smc.ges.domain-pack.v1`
- stable `id` and SemVer `version`
- `activation_rules`
- zero or more capability providers: `engineering`, `review`, `verification`
- optional `plan_extension`
- optional `plan_validator`
- optional `selftest`

Forbidden ownership concepts: `plan_owner`, `delivery_owner`, `commit_owner`, `roadmap_owner`.

## Activation

Resolver input:

```text
Consumer Profile
+ Domain Registry / Pack policy
+ Canonical Plan Change Matrix
```

Resolver output is a set, not a scalar:

```json
{
  "schema": "smc.ges.domain-activation.v1",
  "profile": "consumer@1.0.0",
  "policy_digest": "sha256:...",
  "domains": []
}
```

`policy_digest` binds profile + selected pack manifests + activation policies + pinned policy lock. Policy change makes old Plan domain proof stale.

## Provider Composition

Multiple domains may be active. Provider collision does not change Single Writer. Domain providers advise/validate the same Plan-owned implementation scope and cannot create parallel delivery state machines.

Precedence:

```text
GES Frozen Invariants
> Approved Architecture / PRD / Plan
> Consumer explicit policy
> Domain MUST
> Domain SHOULD
> Domain ADVISORY
```

Conflicting same-level MUST rules require architecture resolution; agents must not pick one silently.

## V2 Preplan and Policy

v2 provider 在 PRD 审查前把领域设计意图写入同一 PRD；已批准后生成 Plan 时再次校验，避免设计在执行中漂移。

[[engineeing-skills/domain-runtime/domain_runtime.py#validate_preplan]] 要求领域行与激活 Change ID 一一对应，并向上传播子 validator JSON errors（不得整块吞为 `DOMAIN_PREPLAN_FAILED`）。[[engineeing-skills/domain-runtime/domain_table.py#validate_table]] 拒绝错列、重复 ID、空值及未决占位符。Frontend 覆盖 React/Vue；Backend 和 Ops 由各自数据包接入。Profile v3 的项目策略文件内容纳入 policy digest，v2/v1 绑定算法保留，以保护在途 Plan。Closure 起 blocking 只读 row prefix token，见 [[acceptance-closure#Structured Domain Triggers]]。

## Intent Binding

pack `2.2.0` 使用 `intent_bindings`（per-field `{plan_column, mode}`）；旧 `intent_binding.fields`（2.1.0）仍可读。

Seed 写 `source_prd`、`source_prd_sha256`、`domain_intent_digest` 与 `## Domain Intent Binding`；validator 主码为 `PLAN_SOURCE_PRD_*` / `PLAN_DOMAIN_INTENT_STALE`。实现见 [[engineeing-skills/domain-runtime/domain_intent.py#build_bindings]]、[[engineeing-skills/domain-runtime/domain_intent.py#verify_bindings]] 与 [[governance-architecture-closure#Naming Migration Map]]。pack 版本变更会改 `policy_digest`，须同步既有 digest 期望。
