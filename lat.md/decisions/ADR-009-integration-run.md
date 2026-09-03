# ADR-009 — IntegrationRun as PASS Proof

跨仓 Integration PASS 不是手改 scenario YAML，也不是「看见一次成功 Workflow」。每次尝试必须留下不可变 IntegrationRun。

**Status:** APPROVED

记录路径：

```text
integration/runs/<SCENARIO_ID>/<INTEGRATION_RUN_ID>.yaml
```

必须包含 reviewed runner、provider/consumer pin（repo + commit + contract release）、workflow run 证据和 runner 输出摘要。历史不可覆盖。Feature `DONE` 要求最新 IntegrationRun `PASS`。

空 `history.yaml` 仍是权威等待事实。见 [[domain/facts-and-evidence#IntegrationRun]]。
