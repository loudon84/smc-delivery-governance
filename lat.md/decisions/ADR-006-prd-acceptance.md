# ADR-006 — PRD Acceptance Contract

**Status:** APPROVED

Stage PRD 的验收采用语言无关的 Acceptance Manifest/Report：每个 AC/DOD 必须映射至少一个 Verification ID。测试命令在项目自身 CI 执行；中央只验证报告结构、source_revision、repository_commit 和 blocking verification 结果。
