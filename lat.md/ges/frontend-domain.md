# Frontend Domain Pack v1

Frontend is the first production reference implementation of the generic Domain Pack Framework.

## Capabilities

Frontend pack 提供三类 provider skill：engineering、review、verification。

- engineering -> `smc-frontend-engineering`
- review -> `smc-frontend-review`
- verification -> `smc-frontend-visual-verification`

## Activation

激活规则写在 `domain-packs/frontend/activation.json`；Core resolver 无 `frontend` 分支。按 UI 路径与 target-state token 匹配 Change ID，测试与生成物由 pack policy 排除。

## Token Grammar

Preplan Layout / State Ownership / Responsive 以 PRD §11.2 canonical token 为准；旧 token 为 deprecated alias 仍可读。

`TOKEN:<detail>` 由既有 `_token` 前缀解析；FULL 触发含 `NEW_HIERARCHY`、`NEW_OWNER`/`MOVE_OWNER`、`NEW_ARCHITECTURE` 与新 design-system primitive。映射表见 [[governance-architecture-closure#Frontend Token Canonical and Alias]]；实现见 [[engineeing-skills/.agents/skills/smc-frontend-preplan/scripts/validate_prd_intent.py#validate]]。

## Frontend Quality Ledger

For each activated Change ID:

```text
Composition
State Ownership
Design System
Accessibility
Interaction States
Performance
Visual Verification
```

These fields are plan-bound obligations. Visual or live proof still uses existing GES Acceptance/Evidence layers; the pack does not create a second evidence ledger.

## Upstream Skill Sources

External React/Design skills are rule sources only. Blocking production policy is pinned in `policy-lock.json`; runtime network fetches cannot change the rule set for an in-flight Plan.
