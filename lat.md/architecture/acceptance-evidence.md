# PRD Acceptance Evidence

## Principle

中央仓库不远程执行各项目任意测试命令。Stage PRD 的 AC/DOD 在项目本地转换为 `Acceptance Manifest`，由项目 CI 执行并生成 `Acceptance Report` + GitHub Actions `Attestation`。中央验证 attestation、workflow 身份、commit pin 与 digest，不信任 Receipt 里的 `acceptance.status`。

## Chain

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

## VERIFIED Gate

Consumer Repo Work Package 进入 `VERIFIED` 至少要求：

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

`DONE` 仍由中央 Work Package Exit Criteria 与 IntegrationRun 条件裁决。
