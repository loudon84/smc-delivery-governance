# Governance Engineering Skills — Versioning Policy v1.0

GES 同时存在多个版本轴。工程师必须明确“改的是哪一层”，禁止只改一个数字掩盖 contract/runtime 变化。

## 1. Bundle Version

格式：`MAJOR.MINOR.PATCH`，例如 `4.1.1`。

### PATCH

适用于：

- bug fix；
- OS/path compatibility fix；
- validator false positive/false negative 修正，但不改变已声明 contract；
- rollback/reliability hardening；
- 文档修正且不改变治理语义。

示例：v4.1.0 -> v4.1.1 的 Windows path identity 修复。

### MINOR

适用于向后兼容的新能力：

- 新 Skill；
- 新可选 gate；
- generic consumer profile framework；
- 新 evidence backend；
- 新 adapter，但旧 consumer 不需要迁移即可继续工作。

预计把 NodeSkClaw-specific installer 假设外置为 consumer profiles，若保持旧 profile 可兼容，属于 `4.2.0` 类变更。

### MAJOR

适用于：

- Frozen Invariant 改变；
- 删除/替换 canonical artifact owner；
- Plan/PRD/Roadmap contract 不兼容升级；
- `post_review` 等核心 commit boundary 被改变；
- consumer 必须做不兼容迁移才能继续运行。

## 2. Individual Skill Version

每个公司维护的 Skill SHOULD 在 `SKILL.md` frontmatter 中维护独立 SemVer。

只修改一个 Skill 时：

- 必须提升该 Skill version；
- Bundle version 同时至少 PATCH；
- CHANGELOG 必须指出 skill old -> new；
- 相关 self-test / contract test 必须更新。

不得因为 Bundle 升级就机械地提升所有未改动 Skill 版本。

## 3. Contract Version

Contract 与实现版本分离。

示例：

```text
Bundle       : 4.1.1
Plan Skill   : 3.4.0
Plan Contract: smc.plan.v3.3
```

Contract 版本变化必须声明 migration policy：

- compatible read；
- compatible write；
- explicit migrate；
- unsupported/blocked。

不允许“脚本已经能读”就默认认为 contract 兼容。

## 4. Governance Baseline Version

`GES-BASELINE-vX.Y.Z` 版本只用于描述公司接受的工程治理标准。

它不等于 Bundle version。

- Bundle 可以发布候选版本但未被 Governance Baseline 接受；
- Governance 文档可以更新维护规则而不修改 runtime bundle；
- 新 baseline 必须指向明确的 accepted bundle/contract matrix。

## 5. Consumer Profile Version

每个 Consumer Profile 独立版本：

```text
nodeskclaw-profile: 1.x
smc-copilot-profile: 1.x
<future-project-family>: 1.x
```

Consumer profile 版本升级不能擅自改变 Core Pipeline Contract。

## 6. Immutable Release Rule

一旦发布：

```text
Bundle version + source commit + package manifest SHA256
```

三者组成不可变 release identity。

禁止：

- 修改 v4.1.1 文件后仍称 v4.1.1；
- 替换同名 ZIP 但不提升版本；
- 重写历史 `SHA256SUMS` 让旧版本指向新内容。

## 7. Required Version Matrix

每次 release 必须记录：

| Layer | Required |
|---|---|
| Bundle version | yes |
| Governance baseline compatibility | yes |
| Changed Skill versions | yes |
| Pipeline contract | yes |
| Plan/PRD/Roadmap contract versions | yes |
| Consumer profiles tested | yes |
| Source commit | yes |
| Package manifest SHA256 | yes |
