# PRD Acceptance Evidence

中央仓库不远程执行各项目任意测试命令。Stage PRD 的 AC/DOD 在项目本地变成 Manifest，由项目 CI 执行；中央只验证 attestation 与 digest。

合同细节见 [[ADR-006-prd-acceptance]]；Consumer 关门见 [[domain/state-machines#Work Package]]。

## Principle

中央信任的是 GitHub Actions Attestation 与 digest 对齐，而不是 Receipt 里的 `acceptance.status`。没有中央 Attestation 的自称 PASS 不能把 Consumer Work Package 推到 VERIFIED。

## Chain

验收链从 APPROVED Stage PRD 出发，经本地 CI 产生 Report 与 Attestation，最后由中央 Gate 写入 verified evidence。

```text
APPROVED Stage PRD
  ↓
AC-01 / DOD-01 ...
  ↓
Acceptance Manifest
  ↓
V-01 unit
V-02 contract
V-03 static
V-04 integration
  ↓
Local CI
  ↓
Acceptance Report artifact
  ↓
GitHub Actions Attestation
  ↓
Central Acceptance Gate
  ↓
Work Package VERIFIED
```

实现入口：[[tools/acceptance_gate.py#verify_attestation]]、[[tools/acceptance_gate.py#validate_acceptance]]。

## VERIFIED Gate

Consumer Repo Work Package 进入 `VERIFIED` 至少要求同步、强身份交付物、实现 commit 与中央已验证的 PASS Attestation。

```text
sync_state == SYNCED
strong Stage PRD ArtifactRef
strong Plan ArtifactRef
Implementation commit exists
centrally verified Acceptance Attestation PASS
attestation commit ∈ observed implementation commits
source_revision matches Work Package
```

Provider 合同发布型 Work Package 认 immutable release tag + peeled commit + conformance evidence，不伪造 Stage PRD。

`DONE` 仍由中央 Work Package Exit Criteria 与 IntegrationRun 条件裁决。门禁实现：[[tools/state_machine.py#work_package_gate]]。
