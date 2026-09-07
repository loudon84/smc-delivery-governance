# GES Domain Pack Framework v1

Domain Pack 把专业工程能力挂到既有 GES 流水线上；Core 只认合同，不硬编码具体 domain id。

## Purpose

Domain Pack 是专业工程能力扩展，不是新的 workflow。GES Core 只读取 `smc.ges.domain-pack.v1` / `smc.ges.domain-activation.v1` 合同，不允许在 Core runtime 中硬编码具体 domain id。

## Three Decisions

三条发布决策固定 Domain 与 Core、Profile、Plan 的边界，防止第二套 workflow 出现。

1. Domain Pack 只能提供 `engineering | review | verification` provider，不得拥有 Plan、Delivery、Commit、Roadmap canonical state。
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

`pack.json` MUST declare:

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
