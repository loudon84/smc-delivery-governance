---
name: smc-frontend-visual-verification
description: GES Frontend Domain verification provider. 把前端 UI/interaction 的 component/browser/live-visual 验证映射到 Consumer Profile 声明的命令与现有 smc.acceptance/evidence 机制；不创建第二 Evidence SOT。
version: 1.0.0
disable-model-invocation: true
---

# SMC Frontend Visual Verification v1.0

## Role

本 Skill 是 Verification provider。它只负责确定当前前端 Claim 应使用的项目级验证入口与 oracle；真正命令执行、scope fingerprint、candidate provenance、freshness 与 durable manifest 仍由 `smc-plan-delivery` evidence/acceptance layer 持有。

## Levels

```text
STATIC -> lint / typecheck
COMPONENT -> unit / DOM behavior
INTERACTION -> browser/renderer automation
LIVE_VISUAL -> real application + DOM/screenshot/console oracle
```

使用 `scripts/preflight.py` 检查 Consumer Profile 是否提供 Plan 所需的 quality command。缺失是 PRECHECK BLOCKED，不得伪造产品 FAIL。
