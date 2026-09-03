# Governance Engineering Skills — Accepted Baseline v1.0

## 1. Baseline Identity

```text
Governance Baseline : GES-BASELINE-v1.0.0
Accepted Date       : 2026-09-03
Canonical Repository: loudon84/smc-delivery-governance
Canonical Branch    : master
Canonical Path      : engineeing-skills/
Foundation Commit   : 4b0ab08a62c971df4f40faa98480f12f21440aa7
Bundle Release      : 4.1.1
Pipeline Contract   : v4.1
Plan Contract       : smc.plan.v3.3
Commit Policy       : post_review
Status              : ACCEPTED / CORE BASELINE
```

`Foundation Commit` 指建立本治理基线时已经验证并提交的 v4.1.1 技术基线。治理文档合并后的 master SHA 会继续前进；已发布的 v4.1.1 release 内容不得因此被原地重写。

## 2. Accepted Skill Set

| Skill | Baseline Version | Role |
|---|---:|---|
| `smc-architecture-decision` | 1.0.0 | Architecture decision owner |
| `smc-architecture-review` | 1.0.0 | Architecture review owner |
| `smc-roadmap` | 1.1.0 | Roadmap / delivery state owner |
| `smc-prd-grounding` | 4.0.0 | Stage PRD grounding |
| `smc-prd-review` | 4.0.0 | Stage PRD semantic review |
| `smc-prd-converge` | 3.0.0 | Stage PRD converge / approval |
| `smc-plan-from-approved-prd-ponytail` | 3.4.0 | Canonical Plan author |
| `smc-plan-validator` | 1.3.0 | Plan static gate |
| `smc-plan-review` | 1.1.0 | Plan semantic gate |
| `smc-plan-delivery` | 1.0.1 | Delivery orchestrator |
| `executing-plans` | 4.1.0 | Implementation engine |
| `subagent-driven-development` | 4.1.0 | Subagent implementation engine |
| `using-superpowers` | 4.1.0 | Workflow router |
| `verification-before-completion` | inherited | Verification discipline provider |

`verification-before-completion` 在当前基线没有独立 SemVer frontmatter；后续若纳入公司统一版本管理，应在专门 change 中补齐，不得在无关 patch 中顺手修改。

## 3. Accepted Pipeline

```text
Architecture
  -> APPROVED Architecture
  -> Roadmap READY Item
  -> Stage PRD
     -> Grounding
     -> Review
     -> Converge
  -> APPROVED Stage PRD
  -> Canonical Plan
  -> Static Gate
  -> Semantic Gate
  -> Execution
  -> Completion Audit
  -> Implementation Review
  -> Blocking Verification
  -> Evidence Freshness Gate
  -> Durable Evidence Manifest
  -> post_review implementation commit
  -> Roadmap DONE update
```

## 4. Accepted State Model

以下四类状态必须保持独立：

1. **Plan specification state**；
2. **Todo runtime state**；
3. **Proof state**；
4. **Delivery / Roadmap state**。

任何实现不得把四者压缩为一个 `status=done`。

## 5. Accepted Evidence Model

- raw runtime logs：local / CI evidence store；
- implementation fingerprint：content-first；
- review/audit/verification：绑定当前 fingerprint；
- implementation 发生变化：旧 proof => STALE；
- durable summary：进入可提交 evidence manifest；
- Roadmap DONE：引用 implementation commit 可解析的 durable evidence。

## 6. Accepted Installation Safety

当前 v4.1.1 installer 已接受：

- dry-run default；
- package checksum validation；
- transaction backup；
- post-install self-test；
- project validator hook；
- validation failure automatic rollback；
- manual rollback；
- no automatic git commit。

## 7. Windows Compatibility Baseline

v4.1.1 已把 repo-relative path 判断从字符串层级比较提升为 filesystem identity-aware 路径解析，覆盖 Windows 8.3 short path / long path alias 类问题。

后续任何涉及 repo root、Plan path、temp directory、junction/symlink、subst drive 的改动都必须运行 Windows path-alias regression tests，不允许退回裸 `Path.relative_to(repo_root)` 作为唯一身份判断。

## 8. Consumer Integration Status

### Core Status

```text
Delivery self-test : PASS (13 tests)
Roadmap self-test  : PASS (3 tests)
```

### NodeSkClaw Consumer Status

NodeSkClaw 的项目级 validator 会检查整个：

```text
.agents/skills     == .cursor/skills
.agents/references == .cursor/references
```

因此 `SKILL-004 CURSOR_SKILL_MIRROR_DRIFT` 属于 **consumer full-tree acceptance drift**。它可以使安装事务 rollback，但它不是 Delivery 13 项 self-test 的失败。

后续 installer 输出应进一步把 Core validation 与 Consumer validation 分层报告。

## 9. Transitional Technical Debt

v4.1.1 的 `install.py` 仍包含 NodeSkClaw-compatible baseline 假设，例如：

- `.cursor/skills` 必须存在；
- 特定 references / validators 必须存在；
- `tools/agent-skills/validate_agent_skills.py` 作为 project validator；
- project integration overlay 采用固定路径。

这属于当前 **consumer adapter 与 core installer 尚未完全解耦** 的技术债，不得把这些条件提升为公司所有项目的 Core Governance 规则。

建议下一次兼容性能力升级使用 **v4.2.0**，目标是 consumer profile 化，而不是继续向通用 installer 中增加项目名分支。

## 10. Baseline Change Rule

本文件只能在以下情况下更新：

- 新 Bundle release 被接受；
- Pipeline/Contract 版本改变；
- Frozen Invariant 改变；
- Core/Consumer 边界改变；
- 新平台兼容基线被正式验证。

普通文案修正不得伪造新的 accepted runtime baseline。
