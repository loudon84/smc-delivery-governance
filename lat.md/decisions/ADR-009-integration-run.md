# ADR-009 — IntegrationRun as PASS Proof

**Status:** APPROVED

跨仓 Integration `PASS` 不是手改 scenario YAML，也不是「看见一次成功 Workflow」。

每次尝试生成不可变记录：

```text
integration/runs/<SCENARIO_ID>/<INTEGRATION_RUN_ID>.yaml
```

必须包含 reviewed runner、provider/consumer pin（repo + commit + contract release）、workflow run 证据和 runner 输出摘要。历史不可覆盖。Feature `DONE` 要求最新 IntegrationRun `PASS`。
