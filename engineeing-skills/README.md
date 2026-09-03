# SMC Governed Engineering Skills v4.1.2

> **Canonical source:** `loudon84/smc-delivery-governance` branch `master`, directory `engineeing-skills/`. Future governed engineering Skill iterations must originate there; generated ZIP files are release artifacts, not an independent source of truth.

面向 `loudon84/nodeskclaw` 当前 `.agents/skills` 治理链的 **overlay 升级包**。

本包不替换你们已冻结的 Architecture / Roadmap / Stage PRD 治理模型，而是在其后补齐一个真正可执行的 Plan Delivery Orchestrator，并把 gstack 中高价值的工程机制吸收到现有 SMC 约束中。

## 1. 目标工程流水线

```text
Architecture
  -> smc-architecture-decision
  -> smc-architecture-review
  -> APPROVED Architecture
  -> smc-roadmap
  -> READY Roadmap Item
  -> smc-prd-grounding
  -> smc-prd-review
  -> smc-prd-converge
  -> APPROVED Stage PRD
  -> smc-plan-from-approved-prd-ponytail
  -> Canonical Plan (smc.plan.v3.3)
  -> smc-plan-delivery
       1. Plan Static Gate
       2. Plan Semantic Gate
       3. Execution Engine
       4. Plan Completion Audit
       5. Implementation Review
       6. Verification
       7. Evidence Freshness Gate
       8. post_review Implementation Commit
       9. Roadmap Update
```

Plan 创建完成后，唯一推荐的人类入口是：

```text
smc-plan-delivery
```

`post_review` 只保留为 commit policy；不再被误认为 workflow executor。

## 2. 本包新增 / 升级的核心能力

### NEW: `smc-plan-delivery v1.0.1`

独立 Skill 包，包含：

- Delivery state machine；
- single canonical Plan identity；
- Cursor Todo runtime state；
- working-tree content fingerprint；
- plan / implementation review ledger；
- Verification evidence ledger；
- FRESH / STALE / MISSING 判定；
- Plan Completion Audit；
- resume / recovery；
- ready-to-commit deterministic gate；
- post_review commit guard；
- legacy Plan v3.2 -> v3.3 migration。

### `smc-plan-from-approved-prd-ponytail v3.4.0`

- Plan contract 升级到 `smc.plan.v3.3`；
- canonical Plan 同时承载 Cursor metadata + SMC body；
- `plan_id` 唯一；
- Cursor `todos[].status` 为 Todo runtime status SOT；
- Verification Ledger 从 `Evidence Output` 改成 `Evidence Policy`；
- 增加 `DIAGNOSE_PLAN` read-only 模式；
- Plan exit 统一进入 `smc-plan-delivery`。

### `smc-plan-validator v1.3.0`

新增 v3.3 wrapper：

```bash
python .agents/skills/smc-plan-validator/scripts/validate_plan_v33.py <plan>
```

它先验证 v3.3 canonical/Cursor/evidence-policy，再复用现有 v3.2 validator 的 AC/DoD、Lifecycle、Change Matrix、Single Writer、DAG、Ponytail 等强门禁。

### `smc-plan-review v1.1.0`

明确区分：

```text
Router: NOT_REQUIRED | REQUIRED
Actual Review: PASS | REVISE | RETURN_PRD
```

无论 `NOT_REQUIRED` 还是实际 `PASS`，都形成绑定当前 semantic Plan hash 的 clearance record。

### Execution Engines v4.1.0

`executing-plans` 与 `subagent-driven-development` 收敛为 **implementation engine**：

- 只实现 Todo；
- 不做最终 commit；
- 不把 focused checks 当 Final Verification；
- Todo 完成由 controller 更新 canonical Plan；
- final Audit / Review / Verification / Commit / Roadmap 统一由 `smc-plan-delivery` 管理。

### `smc-roadmap v1.1.0`

`DONE` 仍要求真实 implementation commit，但 Verification Evidence 支持 logical evidence ref：

```text
smc-evidence:<plan_id>@<working-tree-fingerprint>
```

raw XML/TXT/stdout 不再默认进入 Git。Final Verification 后生成 `docs_agent/evidence/<plan_id>-evidence.json` 紧凑 Manifest，并与 implementation 一起提交；Roadmap 引用从 implementation commit 中解析该 Manifest。

## 3. 从 gstack 吸收但按 SMC 约束重构的能力

本包吸收的是工程模式，不复制 gstack 代码：

1. **Pipeline Skill orchestration**：一个后半程入口驱动多个专业 Skill；
2. **Plan Completion Audit**：实现完成后重新核对 Plan × Diff，而非相信 Todo 自报；
3. **working-tree fingerprint**：Review/Verification 绑定实际内容，而非 commit 数量；
4. **FRESH / STALE / MISSING evidence**：代码变化自动使旧 proof 失效；
5. **Review Readiness / Delivery Readiness**：路由结果与实际 Verdict 分离；
6. **fresh-context audit/review**：实现者与最终审计尽量使用独立上下文；
7. **pipeline E2E/self-test**：验证状态、freshness、Todo mapping，而不只验证 Markdown schema。

不引入 gstack 的 continuous WIP commit，因为它会破坏 SMC `post_review`。

## 4. 安装

### 4.1 预检（不修改项目）

在解压目录运行：

```bash
python install.py /path/to/nodeskclaw
```

### 4.2 应用升级

```bash
python install.py /path/to/nodeskclaw --apply
```

安装器行为：

1. 校验本发布包 `SHA256SUMS`；
2. 验证目标是现有 SMC skills baseline；
3. 对每个将被覆盖/新增的文件建立 transaction manifest，并备份旧文件到 `.smc/skill-upgrade-backups/<timestamp>/`；
4. overlay copy 本包 `.agents/skills/*`，同时写入 `.cursor/skills`；
5. 以 `.agents` 为 canonical，同步 declared full-tree mirrors（skills + references），修复 overlay 未覆盖的既有 drift；
6. 确保 `.smc/evidence/`、`.smc/reviews/`、`.smc/runs/` 被 gitignore；
7. 执行 `smc-plan-delivery` 13 项 self-test 与 `smc-roadmap v1.1` 3 项 evidence/commit 测试；
8. 若存在 `tools/agent-skills/validate_agent_skills.py`，执行项目级 Skill 校验；
9. 任一 post-install gate 失败则**自动回滚到升级前文件状态**；
10. **不会自动 git commit**。

## 4.3 手工回滚

安装成功后如果需要撤销升级，先预览：

```bash
python rollback.py /path/to/nodeskclaw
```

确认后：

```bash
python rollback.py /path/to/nodeskclaw --apply
```

`rollback.py` 会检查当前文件是否仍与安装后的 SHA256 一致；若升级后又有人工修改，会 fail-closed，避免静默覆盖新修改。只有人工复核后才能使用 `--force`。

## 5. 新 Plan 使用

APPROVED PRD 后创建 Plan seed：

```bash
python .agents/skills/smc-plan-from-approved-prd-ponytail/scripts/create_plan_seed.py \
  docs_agent/.../RM-07.md \
  .cursor/plans/rm-07-edge-control.plan.md \
  --plan-id RM-07
```

完成 grounding / slicing / verification design 后：

```bash
python .agents/skills/smc-plan-validator/scripts/validate_plan_v33.py \
  .cursor/plans/rm-07-edge-control.plan.md
```

然后让 Agent 使用：

```text
smc-plan-delivery 执行 .cursor/plans/rm-07-edge-control.plan.md
```

不需要用户手工再串：validator -> plan review -> execute -> review -> verification -> commit -> roadmap。

## 6. Legacy v3.2 Plan

默认不批量迁移历史 Plan。历史 in-flight Plan 可维持原流程；准备继续实施或 REVISE 时再迁移：

```bash
python .agents/skills/smc-plan-delivery/scripts/migrate_legacy_plan.py \
  .cursor/plans/<legacy>.plan.md --in-place
```

迁移规则：

- `smc.plan.v3.2 -> smc.plan.v3.3`；
- 保留既有 Plan body；
- 补 `plan_id`；
- 保留未知 Cursor metadata；
- 若缺 Cursor todos，则由 Markdown `Todo Tn` 建立映射；
- `Evidence Output -> Evidence Policy`；
- 默认 policy=`LOCAL_TRANSIENT`；
- 不重新规划 implementation。

历史 `artifacts/*` 不批量删除，也不使历史 Roadmap evidence 失效；它们视为 legacy retained evidence。

## 7. Evidence 使用

Final Verification 必须通过 wrapper 执行：

```bash
python .agents/skills/smc-plan-delivery/scripts/evidence.py run \
  --plan "$PLAN_PATH" --verification V01 -- <exact test command>
```

检查：

```bash
python .agents/skills/smc-plan-delivery/scripts/evidence.py check \
  --plan "$PLAN_PATH" --all-blocking
```

raw log 保存在 `.smc/evidence/...`，默认不进 Git。所有 blocking evidence FRESH 后生成 durable Manifest：

```bash
python .agents/skills/smc-plan-delivery/scripts/evidence.py manifest \
  --plan "$PLAN_PATH"
```

输出 `docs_agent/evidence/<plan_id>-evidence.json`，该文件进入 implementation commit。Roadmap 保存 `smc-evidence:<plan_id>@sha256:<fingerprint>`，v1.1 validator 从 implementation commit 中读取并校验该 Manifest。

## 8. 重要边界

- 本包只改开发治理 Skills，不修改 NodeSkClaw/Hermes production runtime；
- 不新增第二个 production owner；
- `workflow-runner` 仍是 agency-orchestrator YAML runner，不参与 SMC Plan Delivery；
- 静态 Plan PASS 不等于 implementation complete；
- Cursor Todo 全 completed 不等于 `IMPLEMENTED_AND_PROVEN`；
- code 变化后旧 implementation review / verification 必须自动 stale；
- Roadmap status commit 与 implementation commit 分离。

## 9. 验证本升级包

```bash
python validate_package.py
```

该命令执行 Python compile、13 个流水线 Skill 版本/结构检查、11 项 delivery tests、3 项 Roadmap durable-evidence tests、installer + rollback smoke。发布 ZIP 另带 `SHA256SUMS` 与 `PACKAGE-MANIFEST.json`。
