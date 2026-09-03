# Governance Engineering Skills — Consumer Integration Contract v1.0

## 1. 目的

Consumer Integration 负责把公司统一 GES Core 安装/映射到某个具体项目，但不得改变 Core Governance semantics。

## 2. Consumer Profile 必须声明

建议每个 profile 至少包含：

```yaml
schema: smc.ges.consumer-profile.v1
id: nodeskclaw
version: 1.0.0
skill_roots:
  canonical: .agents/skills
  mirrors:
    - .cursor/skills
reference_roots:
  canonical: .agents/references
  mirrors:
    - .cursor/references
project_validator:
  command: python tools/agent-skills/validate_agent_skills.py
required_baseline: []
managed_skills: []
local_skills_policy: preserve
evidence:
  transient_root: .smc/evidence
  durable_root: docs_agent/evidence
```

未来 generic installer 应读取 profile，而不是在 `install.py` 中继续增加 `if project == ...`。

## 3. Core Managed Set 与 Local Set

Consumer 中的 Skill 必须区分：

```text
Managed by GES Core
Managed by Consumer Profile
Project-local / unmanaged
```

Core installer 不应要求整个 `.agents/skills` 都与某个 IDE mirror 完全一致，除非 consumer profile 明确声明 **full-tree mirror**。

这能避免公司统一 Skill 升级错误地接管项目自有 Skill。

## 4. Mirror Policy

允许 profile 选择：

- `none`：没有镜像；
- `managed-set`：仅 GES managed paths 镜像；
- `full-tree`：整个 canonical/mirror tree 必须字节级一致。

NodeSkClaw 当前属于 `full-tree` 语义：它的项目 validator 会比较 `.agents/skills` 与 `.cursor/skills` 整棵树，也会比较两套 references。

因此：

```text
SKILL-004 CURSOR_SKILL_MIRROR_DRIFT
```

表示 consumer repository 没有满足其自己的 full-tree mirror contract。

它不代表：

```text
smc-plan-delivery self-test failed
```

但生产 installer 仍应 rollback，因为 consumer acceptance 未通过。

## 5. Consumer Acceptance Report

后续安装器 SHOULD 分层输出：

```text
CORE_PACKAGE_INTEGRITY       PASS/FAIL
CORE_SKILL_SELFTEST          PASS/FAIL
CORE_PIPELINE_VALIDATION     PASS/FAIL
CONSUMER_PROFILE_PREFLIGHT   PASS/FAIL
CONSUMER_PROJECT_VALIDATOR   PASS/FAIL
INSTALL_TRANSACTION          PASS/ROLLED_BACK
```

不要把所有失败统一打印成“Skill package failed”。

## 6. Project-Specific Dependencies

以下内容只能进入 profile，不得进入 Core Governance invariant：

- 某个项目固定文件必须存在；
- 某个项目的 `tools/...` 路径；
- IDE-specific mirror；
- monorepo tool；
- framework-specific test command；
- project-specific deprecated Skill list。

Core 可以定义接口，但不能硬编码业务仓库名称或目录结构。

## 7. Consumer Onboarding

新项目接入流程：

```text
1. 选择/创建 consumer profile
2. 运行 profile preflight
3. 安装 GES managed skills
4. 同步 declared mirrors（v4.1.2 NodeSkClaw installer 已对 full-tree mirrors 执行 canonical `.agents` → `.cursor` 同步）
5. 运行 Core self-tests
6. 运行 consumer validator
7. 跑最小 workflow smoke
8. 记录 installed bundle/profile version
9. 项目提交升级 commit
```

新项目禁止为了“先跑起来”删除 Static/Semantic/Audit/Review/Verification gates。

## 8. Upgrade Compatibility

Consumer 项目应记录：

```text
GES bundle version
Consumer profile version
Installed source/release identity
```

升级前比较 compatibility matrix；升级失败时事务 rollback，不能把半更新 Skill 留在项目中。

## 9. Current v4.1.2 Transitional Rule

当前 v4.1.2 `install.py` 仍是 NodeSkClaw-compatible overlay installer。它可继续用于 NodeSkClaw 类基线，但不应被当成所有公司项目的 universal installer contract。

v4.1.2 补上了 NodeSkClaw full-tree mirror 同步，避免 overlay 未覆盖的既有 `.agents` / `.cursor` drift 把生产安装卡在 `SKILL-004`。泛化 profile 选择（`none` / `managed-set` / `full-tree`）仍留待 v4.2.0。

推荐 v4.2.0 实施：

```text
Core package
  + Generic installer
  + consumers/nodeskclaw.yaml
  + consumers/<project>.yaml
```

并保持 v4.1.x NodeSkClaw profile 行为向后兼容。
