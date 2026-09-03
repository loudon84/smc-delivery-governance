# gstack Engineering Patterns -> SMC Governed Engineering Adaptation

## Purpose

本文件记录本升级包从 `garrytan/gstack` 工程流水线吸收的模式，以及为什么没有直接照搬。

## 1. Pipeline Skill Orchestration

### gstack pattern

Plan review 与 ship 都不是单条规则，而是有明确入口 Skill 驱动阶段链。

### SMC adaptation

新增 `smc-plan-delivery`，成为 canonical Plan 后唯一 delivery orchestrator：

```text
Static -> Semantic -> Execute -> Completion Audit -> Implementation Review
-> Verification -> Evidence Freshness -> post_review Commit -> Roadmap Update
```

现有专业 Skill 继续拥有各自规则；orchestrator 不复制它们的 domain logic。

## 2. Plan Completion Audit

### gstack pattern

Ship 前使用独立上下文重新读取 Plan 与 diff，分类 done/deferred/unverifiable，避免“实现者说完成了”直接进入 ship。

### SMC adaptation

`completion_audit.py` 提供：

- deterministic precheck；
- content fingerprint binding；
- semantic audit record；
- `FRESH_PASS | STALE | MISSING | FRESH_FAIL`。

语义审计仍由 fresh reviewer context 完成，deterministic script 负责记录和 freshness gate。

## 3. Working-tree Content Fingerprint

### gstack pattern

Review/Test evidence 绑定 working-tree content，不绑定 commit count。相同内容经过 rebase/amend/squash 仍可判断为同一被审内容。

### SMC adaptation

`working_tree_fingerprint.py` 对 Git tracked + untracked(non-ignored) 文件内容计算稳定 hash，并排除 `.smc/` local governance state 与 `docs_agent/evidence/` durable proof metadata；后者必须可提交，但不能因为写入证明摘要而使被证明内容的 fingerprint 自身改变。

它解决 `post_review` 的关键矛盾：Review / Verification 发生时 implementation commit 尚不存在。

## 4. Evidence Freshness

### gstack pattern

测试 evidence 形成 ledger，并按当前工作树判断 FRESH/STALE/MISSING。

### SMC adaptation

`evidence.py`：

```text
run -> exact command + exit + timestamp + fingerprint + raw log
check -> FRESH | STALE | MISSING | FAILED
```

raw log 默认位于 `.smc/evidence/`，不要求进入 Git。Final Gate 额外生成 `docs_agent/evidence/<plan_id>-evidence.json` durable compact Manifest，并与 implementation commit 一起提交。Roadmap 从 implementation commit 中解析该 Manifest。

Plan 只声明 `Evidence Policy`，实际执行结果写 evidence ledger；durable Manifest 负责跨机器审计。

## 5. Review Readiness

### gstack pattern

Router/适用性、实际 review verdict、review freshness 分开。

### SMC adaptation

严格区分：

```text
assess_plan_review: NOT_REQUIRED | REQUIRED
actual plan review: PASS | REVISE | RETURN_PRD
review ledger status: FRESH_PASS | STALE | MISSING | ...
```

`REQUIRED` 永远不能被解释为 PASS。

## 6. Fresh Context

### gstack pattern

关键 Plan completion / review 使用独立 reviewer context，降低实现者确认偏差。

### SMC adaptation

- `subagent-driven-development`: fresh implementer per Todo；
- Completion Audit: fresh reviewer preferred；
- Implementation Review: fresh reviewer preferred；
- script 只绑定结果，不伪装成语义 reviewer。

## 7. Pipeline Tests

### gstack pattern

不仅测试单个 Skill，还测试跨阶段顺序和终止条件。

### SMC adaptation

`smc-plan-delivery/scripts/run_selftest.py` 当前包含 11 项测试，覆盖 Cursor Todo mapping/status、Plan semantic hash、implementation review/evidence/completion freshness、exact verification command、legacy v3.2 migration、untracked scope drift，以及 durable Evidence Manifest 的 fingerprint-neutral/freshness 行为。

`smc-roadmap/scripts/test_roadmap_v11.py` 另有 3 项测试，验证 `smc-evidence:` 必须从 implementation commit 中解析到正确 Manifest，并拒绝 fingerprint mismatch 与 v1.1 非受支持 evidence scheme。

项目集成后应继续增加真实 fixture 的全链 E2E：review fix、verification fail、resume、Roadmap update fail 等。

## Explicitly Not Adopted

### Continuous WIP commits

不采用。SMC 的 frozen invariant 是：

```text
Execute -> Review -> Verification -> Commit Implementation
```

因此 checkpoint 只能写 `.smc/runs/` local state，不能创建中间 Git commit。

### gstack product-role review taxonomy

不直接复制 CEO/Design/DX reviewer。SMC Review Router 应基于 Architecture/Contract/Security/Lifecycle 等企业工程风险选择 reviewer，保持你们现有产品与架构治理边界。
