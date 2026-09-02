# Integration Evidence

Immutable IntegrationRun history lives at:

```text
integration/runs/<SCENARIO_ID>/history.yaml
integration/runs/<SCENARIO_ID>/<INTEGRATION_RUN_ID>.yaml
```

`history.yaml` is required even when `runs: []`. Empty history is the waiting
state. Feature DONE / scenario PASS require a real attempt with runner and
workflow evidence. Synthetic PASS is forbidden.

推荐辅助目录：

```text
<feature-id>/
  provider.json
  consumer.json
  contract.json
  e2e.json
```

禁止提交 Secret、JWT、Prompt 全文、Artifact bytes、内部 Endpoint。
