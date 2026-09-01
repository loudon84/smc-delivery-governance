# FEAT-SKILL-FIRST-001 Architecture

## Goal

普通员工从 Work 选择 Published Skill，通过 NoDeskClaw Backend 调用 Skill Run，并在同一 Chat 中消费 Event、Result 与 Artifact。

```text
smc-copilot/apps/work
        │ SKILL-RUN-CONTRACT
        ▼
nodeskclaw-backend
        ▼
nodeskclaw-agent
```

### NoDeskClaw Owns
Provider Contract、MCP Gateway、Run projection、Agent execution、Event/Result/Artifact production。

### SMC Copilot Owns
Contract Consumer、Layout/Chat UX、Main-process lifecycle、Renderer projection、File Platform integration。

**Frozen:** Work 不直接访问 `nodeskclaw-agent`；NodeSKClaw 不根据 Work 私有 UI 定义 Public API。
