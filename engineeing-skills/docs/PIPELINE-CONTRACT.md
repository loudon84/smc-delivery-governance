# SMC Governed Engineering Pipeline Contract v4.1

## Artifact Owners

| Artifact / State | Canonical Owner |
|---|---|
| Architecture Decision | `smc-architecture-decision` |
| Architecture Review | `smc-architecture-review` |
| Delivery/Roadmap state | `smc-roadmap` |
| Stage PRD grounding | `smc-prd-grounding` |
| Stage PRD review | `smc-prd-review` |
| Stage PRD approval/converge | `smc-prd-converge` |
| Canonical Plan author | `smc-plan-from-approved-prd-ponytail` |
| Plan static truth | `smc-plan-validator` |
| Plan semantic truth | `smc-plan-review` |
| Plan delivery sequencing | `smc-plan-delivery` |
| Todo implementation | `executing-plans` / `subagent-driven-development` |
| Implementation semantic review | `code-review-and-quality` |
| Verification truthfulness | `verification-before-completion` + `smc-plan-delivery/evidence.py` |

## State Separation

四类状态不得合并为一个字段：

1. **Plan specification** — Markdown Todo / ledgers；
2. **Todo runtime state** — Cursor `todos[].status`；
3. **Proof state** — Review/Evidence/Completion Audit ledgers；
4. **Delivery state** — Roadmap Item status。

因此：

```text
Todo completed
  != Plan proven
  != implementation committed
  != Roadmap DONE
```

## Content Binding

Final implementation Review、Completion Audit、Verification 必须绑定同一个 current working-tree fingerprint。

任何影响 implementation content 的内容变化都会使 proof stale；`.smc/` 与 `docs_agent/evidence/` 属于 proof metadata，不进入 implementation fingerprint：

```text
previous implementation review -> STALE
previous completion audit -> STALE
previous verification evidence -> STALE
ready-to-commit -> false
```

## Commit Boundary

允许的实施 commit 点只有：

```text
Static PASS
+ Semantic clearance FRESH
+ all Todos completed
+ Completion Audit FRESH PASS
+ Implementation Review FRESH PASS
+ all blocking Verification FRESH PASS
+ durable Evidence Manifest FRESH
= DELIVERY_READY_TO_COMMIT
```

然后才允许 implementation commit。

Roadmap DONE 更新必须是后续独立 commit。
