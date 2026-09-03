# Contributing to Governance Engineering Skills

本文是公司内部工程师修改 `engineeing-skills` 的标准操作流程。

## 1. 修改前先判断变更层级

每个 change 必须先归类：

```text
CORE
CONTRACT
SKILL_IMPLEMENTATION
CONSUMER_PROFILE
RELEASE_TOOLING
DOCUMENTATION
```

如果一个需求同时跨层，PR 中必须分别说明影响。

## 2. 禁止直接从 Consumer 反向覆盖 SOT

发现问题的推荐流程：

```text
Consumer reproducer
  -> central issue/change record
  -> smc-delivery-governance branch
  -> central fix
  -> regression test
  -> package validation
  -> consumer acceptance
  -> review/merge/release
```

业务仓库中的临时修复只能作为 reproducer / patch source，不能作为“最新版 Skill”直接复制回 `master`。

## 3. Branch / PR 规则

推荐分支：

```text
feat/engineering-skills-<topic>
fix/engineering-skills-<topic>
refactor/engineering-skills-<topic>
docs/engineering-skills-<topic>
```

禁止在一个 PR 中混入无关 Skill 清理。

PR 必须回答：

1. Problem / root cause；
2. Change layer；
3. Runtime behavior 是否变化；
4. Contract 是否变化；
5. Frozen Invariant 是否变化；
6. Consumer compatibility；
7. Migration / rollback；
8. Verification evidence；
9. Version impact。

## 4. 修改 Skill 的最低要求

修改 Skill runtime / semantics 时至少同步：

- `SKILL.md`；
- relevant references contract；
- scripts；
- tests；
- individual Skill version；
- bundle CHANGELOG；
- package validation expectation；
- affected consumer profile tests。

如果改变 artifact schema / contract，还必须：

- 提升 contract version；
- 增加 migration/compatibility path；
- 增加旧版本 fixture；
- 验证 fail-closed 行为。

## 5. 修改 installer 的最低要求

Installer 变更属于高风险 write-path change，必须验证：

- dry-run no write；
- package integrity validation；
- transaction manifest；
- backup；
- partial-write failure rollback；
- post-install validation rollback；
- manual rollback；
- Windows/Linux path handling；
- consumer profile mismatch 的明确错误分类。

禁止通过默认 `skip validator` 解决 consumer incompatibility。

## 6. 测试层级

每个 PR 根据影响运行以下层级：

### L1 Static

- Python compile；
- Markdown/frontmatter/schema；
- cross-skill references；
- package checksum/manifest consistency。

### L2 Skill Unit/Self-Test

- changed Skill tests；
- Plan/PRD/Roadmap fixtures；
- state machine / freshness / migration tests。

### L3 Core Pipeline Integration

最少验证：

```text
APPROVED PRD -> Canonical Plan -> Delivery readiness
```

涉及 lifecycle owner 时应覆盖更长链路。

### L4 Consumer Acceptance

在声明支持的 consumer profiles 上执行：

- install dry-run；
- install apply；
- project validator；
- rollback；
- representative workflow smoke。

### L5 Platform Matrix

涉及 filesystem/subprocess/shell/path 时，至少验证 Windows + Linux。

## 7. Review Gate

Core/Contract 变更必须由非作者 reviewer 审查：

- boundary；
- owner；
- state transitions；
- fail-closed；
- migration；
- evidence freshness；
- versioning；
- consumer impact。

“测试通过”不能替代 semantic review。

## 8. Merge 后

Merge 只表示 central source 接受变更，不自动表示 release 已发布。

发布前必须执行 `RELEASE.md` 中的 release gate，并生成不可变 release identity。

## 9. 目录命名规则

物理路径 `engineeing-skills/` 当前被冻结。

如果未来决定更正为 `engineering-skills/`：

- 必须独立迁移 PR；
- 提供兼容窗口/redirect or dual-path strategy；
- 更新 scripts/CI/docs/consumer profiles；
- 属于至少 MINOR，若破坏既有 automation 则按 MAJOR 处理。
