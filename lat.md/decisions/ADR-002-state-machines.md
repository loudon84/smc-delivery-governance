# ADR-002 — Central State Machines

跨仓 Feature、合同、Work Package、Roadmap 与 Integration 状态由中央统一管理。项目 Receipt 只能提供观察事实，不能直接写全局 DONE。

**Status:** APPROVED

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

转移表与 Gate 见 [[domain/state-machines]]。
