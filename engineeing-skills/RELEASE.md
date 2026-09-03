# Governance Engineering Skills — Release Standard v1.0

## 1. Release Identity

每个正式发布必须产生：

```text
bundle_version
source_commit
package_manifest_sha256
release_date
pipeline_contract
changed_skill_versions
consumer_profiles_tested
validation_summary
```

同一 bundle version 对应的 bytes 必须不可变。

## 2. Release Gate

### Gate A — Source Cleanliness

- release branch 基于最新 approved central source；
- 无 `__pycache__` / `.pyc` / 临时 evidence；
- 无未声明本地 patch；
- package source 与 generated artifact 可追溯。

### Gate B — Contract Validation

- Pipeline Contract；
- changed Skill contracts；
- Plan/PRD/Roadmap contract compatibility；
- migration fixtures。

### Gate C — Core Tests

- compile/static checks；
- package validator；
- changed Skill self-tests；
- pipeline integration tests。

### Gate D — Platform Tests

涉及 filesystem / shell / subprocess 的 release 至少：

- Linux supported Python；
- Windows supported Python；
- Windows long/short path alias regression where applicable。

### Gate E — Consumer Acceptance

至少测试所有标记 `supported` 的 profiles：

- dry-run；
- apply；
- consumer validator；
- rollback；
- representative workflow smoke。

### Gate F — Review

Release 结果由非作者复核：

- version classification；
- invariant impact；
- evidence；
- migration；
- package hash。

## 3. Release Artifact

推荐命名：

```text
SMC-Governance-Engineering-Skills-v<version>.zip
SMC-Governance-Engineering-Skills-v<version>.zip.sha256
```

历史已有命名可保留；改名不应影响目录 SOT。

## 4. Git Tag

建议 tag：

```text
engineering-skills-v4.1.1
engineering-skills-v4.2.0
```

Tag 必须指向已经通过 release gate 的 source commit。

## 5. Release Notes 必须包含

- Summary；
- changed Skills；
- contract changes；
- migration；
- consumer impact；
- known limitations；
- validation matrix；
- source commit；
- SHA256。

## 6. Release 与 Master 的关系

`master` 可以包含下一版本开发中的 approved changes；Release 则必须是冻结的、可重复验证的 snapshot。

因此：

```text
master HEAD != latest immutable release
```

是允许的，但 BASELINE / CHANGELOG 必须明确当前 accepted release。
