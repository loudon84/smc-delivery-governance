---
name: smc-integration-gate
version: 1.0.0
description: 对跨仓 Integration Scenario 做机器化入口判断，只有 Provider/Consumer/Contract 达到要求才允许 Live E2E。
---
# SMC Integration Gate

检查 required Contract State、required Repo Work Package State、required Evidence。

输出：WAITING_PROVIDER / WAITING_CONSUMER / READY / RUNNING / PASS / FAIL / BLOCKED。

Integration Gate 不替代项目本地测试。
