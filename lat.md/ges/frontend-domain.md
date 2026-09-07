# Frontend Domain Pack v1

Frontend is the first production reference implementation of the generic Domain Pack Framework.

## Capabilities

Frontend pack 提供三类 provider skill：engineering、review、verification。

- engineering -> `smc-frontend-engineering`
- review -> `smc-frontend-review`
- verification -> `smc-frontend-visual-verification`

## Activation

激活规则写在 `domain-packs/frontend/activation.json`；Core resolver 无 `frontend` 分支。按 UI 路径与 target-state token 匹配 Change ID，测试与生成物由 pack policy 排除。

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
