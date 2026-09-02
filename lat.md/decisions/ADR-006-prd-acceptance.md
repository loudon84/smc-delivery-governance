# ADR-006 — PRD Acceptance Contract

**Status:** APPROVED

Stage PRD 的验收采用语言无关的 Acceptance Manifest/Report，并附带 GitHub Actions Attestation：每个 AC/DOD 必须映射至少一个 Verification ID。测试命令在项目自身 CI 执行。

中央验证：

- report/manifest digest
- workflow run 存在且 conclusion=success
- HEAD SHA == report commit
- workflow 身份与 workflow_sha
- blocking verification 结果

没有中央 Attestation 的 Receipt `PASS` 不能把 Consumer Work Package 推进到 `VERIFIED`。
