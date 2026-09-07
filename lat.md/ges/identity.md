# GES Identity

GES 的唯一权威源是中央仓库 `engineeing-skills/`。业务仓里的 Skill 副本、ZIP 和 patch 都是 consumer artifact，不得反向覆盖中央 SOT。

产品全称 **SMC Governance Engineering Skills**。目录名 `engineeing-skills` 是历史拼写，已冻结为稳定路径；重命名必须走显式迁移。

## Canonical Source

权威坐标固定为仓库、分支与目录三元组，而不是某个 consumer 的当前 HEAD。

```text
Repository : loudon84/smc-delivery-governance
Branch     : master
Directory  : engineeing-skills/
```

NodeSkClaw 是第一个 Consumer Profile，不是 Core 定义者。语义冲突按 `GOVERNANCE.md` → `governance/baseline.yaml` → `BASELINE.md` → pipeline contract → Skill 合同 → consumer 文档解释。

## GES vs Governance Kit

GES 治理的是 Agent 如何在项目仓内写 Architecture/PRD/Plan；Kit 治理的是项目如何向中央回报 Receipt 与 Acceptance。

| 产品 | 装入项目后的职责 | 权威 ADR / 合同 |
|---|---|---|
| Governance Kit | Binding、Receipt、CI 门禁、Attestation 输入 | [[ADR-008-canonical-governance-kit]]、[[project-onboarding]] |
| GES | Architecture → Roadmap → Stage PRD → Canonical Plan → Plan Delivery | 本文档、[[pipeline]] |

二者都是中央发布的不可变 overlay，但对象图不同。Kit pin 不能替代 GES Bundle pin；GES PASS 也不能把 Work Package 推到中央 `VERIFIED`。

## Core vs Consumer

Core 拥有治理语义；Consumer Profile 只映射路径、镜像、项目 validator 与 evidence 落点。

Core 必须统一：生命周期、四类状态分离、门禁顺序、evidence freshness、`post_review`、单一 canonical Plan、单一 delivery owner。

Consumer 可以不同：`.agents` / `.cursor` 镜像策略、项目级 baseline 文件、build/test 命令、durable evidence 目录、保留的本地 Skill。NodeSkClaw 当前是 `full-tree` 镜像；镜像漂移属于 consumer acceptance 失败，不证明 `smc-plan-delivery` self-test 失败。详见 [[install#Consumer Integration]]。
