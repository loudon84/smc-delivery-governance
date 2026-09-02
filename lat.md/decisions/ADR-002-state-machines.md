# ADR-002 — Central State Machines

**Status:** APPROVED

跨仓 Feature、Contract Release、Repo Work Package、Roadmap Item、Integration 状态由中央仓库统一管理。

Reconciler 推进顺序：

```text
Contract release → Work Package → Roadmap Item → Feature → IntegrationRun
```

所有 BLOCKED 必须包含：

```yaml
blocked_by:
  type: contract|work_package|roadmap_item|integration|manual
  id: <stable-id>
  required_state: <state>
  current_state: <state>
```
