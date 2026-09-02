# ADR-011 — Tests Must Not Mutate Central SOT

**Status:** APPROVED

测试针对隔离的 `SMC_GOVERNANCE_ROOT` 运行。中央 Feature / Registry / Ledger / Audit 不是测试夹具。

Sample Receipt 只能存在于 `examples/`。若测试曾把 sample 同步进中央 SOT，必须用 `cleanup_sample_sot.py` 隔离，并要求真实远程 Receipt 重新 bootstrap。CI 在 pytest 后执行 `git diff --exit-code`。
