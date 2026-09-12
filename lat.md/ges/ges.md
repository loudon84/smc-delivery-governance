# Governance Engineering Skills

GES 是项目仓库内的 AI 工程治理工作流，不是跨仓控制面。它把 Architecture → PRD → Plan → Delivery 收成可 fail-closed 的 Skill 流水线。

当前分析快照以工作区 `engineeing-skills/` 为准：已接受基线仍由 `BASELINE.md` 裁决；树内新增 **Bundle 4.3.1 candidate**（`smc.plan.v3.6`、Test Asset Contract v1、Domain Pack Framework v1），并继承 scoped workspace / execution context / acceptance contract。

- [[identity]] — 权威源、路径冻结、与 Governance Kit 的边界
- [[pipeline]] — 流水线阶段与 Artifact 路由
- [[skills]] — Skill 目录、版本与写权限
- [[invariants]] — 冻结不变量与四类状态分离
- [[plan-delivery]] — 唯一交付编排器、workspace、证据与 commit
- [[acceptance]] — LIVE/FAULT 验收合同，正交于 Plan contract
- [[install]] — overlay 安装、回滚、Consumer Profile
- [[ges-tests]] — 交付、workspace、验收与路径身份测试规格
- [[domain-packs]] — Domain Pack Framework、Profile + Change Scope 激活与扩展不变量
- [[frontend-domain]] — Frontend Domain v1 reference implementation
- [[test-assets]] — 跨 Roadmap Item 复用的 test / fixture / driver 资产合同

GES 产出的是项目本地 Architecture / Stage PRD / Plan / evidence；跨仓 Feature / Work Package / Attestation 仍由中央控制面裁决，见 [[architecture]]、[[ADR-001-central-local-boundary]]。
