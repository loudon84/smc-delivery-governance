# Governance Engineering Skills

GES 是项目仓库内的 AI 工程治理工作流，不是跨仓控制面。它把 Architecture → PRD → Plan → Delivery 收成可 fail-closed 的 Skill 流水线。

当前工作区为 **Bundle 5.0.0 repaired candidate**：新工作采用 `smc.plan.v3.7`、Domain Pack v2 与命令绑定的 Engineering Method v2；在途 v3.6 保留兼容路径。已接受生产基线仍由 `BASELINE.md` 裁决，安装 candidate 不等于升格生产基线。

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
- [[runtime-cost]] — 复杂度路由、增量审查与任务级上下文的成本优化边界
- [[ges-v5]] — v5 升级边界、兼容链、证据新鲜度与清单验收
- [[acceptance-hardening]] — 路由信任、结构化风险、Domain 语义、install-lock.v2、telemetry 与 package gate
- [[acceptance-closure]] — v5.0.2 闭环：字节身份、审查优先级、authority→work-facts、intent binding、install receipt、可执行验收与保护校验
- [[governance-architecture-closure]] — v5.0.2 架构闭环命名迁移与 C01–C07 治理断点关闭（效果验证禁入）
- [[safety-runtime-closure-v503]] — v5.0.3 安全 fail-closed 与 Spec Kit/Superpowers provider 接入方案（Pilot/Benchmark 禁入）

GES 产出的是项目本地 Architecture / Stage PRD / Plan / evidence；跨仓 Feature / Work Package / Attestation 仍由中央控制面裁决，见 [[architecture]]、[[ADR-001-central-local-boundary]]。
