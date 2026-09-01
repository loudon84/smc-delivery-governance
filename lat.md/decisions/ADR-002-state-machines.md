# ADR-002 — Central State Machines

**Status:** APPROVED

跨仓 Feature、Contract、Repo Work Package、Integration 状态由中央仓库统一管理。

所有 BLOCKED 必须包含：

```yaml
blocked_by:
  type: contract|work_package|roadmap_item|integration|manual
  id: <stable-id>
  required_state: <state>
  current_state: <state>
```
