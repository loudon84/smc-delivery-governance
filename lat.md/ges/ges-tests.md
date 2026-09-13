# GES Tests

GES 交付工具的关键测试规格。它们证明 Plan 投影、scoped workspace、proof freshness、commit guard 与 live acceptance 在隔离沙箱中 fail-closed。

覆盖当前树内 `smc-plan-delivery` 与 Roadmap evidence 合同，而不是复述脚本实现。

v5 补充回归覆盖 v3.7 Test Asset 复用与陈旧阻断、命令绑定 RED/GREEN、epoch 不复活、显式 v1 迁移、根因与 VERIFIED 顺序、Todo 完成门禁、STALE REVISE 和快照篡改。包集成验证 Profile v2 策略保留、v3 项目策略摘要、领域激活、seed/wrapper 兼容及事务回滚，见 [[ges-v5#Verification Boundary]]。v5.0.2 Closure 真行为规格见下方 Acceptance Closure。

## Plan contract

`smc.plan.v3.4` 把 Cursor `content` 当成校验过的 UI 投影；Markdown Todo 仍是规格 SOT。v3.3 缺 content 只警告。

### Cursor projection is valid

合法 v3.4 Plan 的 `todos[].content` 必须等于 Markdown Todo 标题加 Owns Changes 投影。

### Missing content fails v3.4

v3.4 Plan 缺少 Cursor `content` 时，静态校验必须硬失败，不得当成兼容警告。

### Content drift fails v3.4

`content` 与 Markdown Todo 投影不一致时必须报 `PLAN_CURSOR_TODO_CONTENT_DRIFT`，防止 UI 文案脱离规格。

### Status update preserves content

controller 更新 `status` 时必须原样保留 `content`，避免把运行时状态写进规格投影。

### Semantic hash ignores runtime fields

semantic Plan hash 必须忽略 `status` 与 `content`，只对 Markdown 规格变化敏感。

### v3.3 missing content is warning

遗留 v3.3 Plan 缺 `content` 不得判静态 FAIL；只允许兼容警告，以便显式迁移。

### sync-content backfills without status change

`sync-content` 必须回填投影并保留 runtime `status` 与未知 Cursor 字段，且不改变 semantic hash。

## Workspace

Plan-scoped workspace 保护 ambient dirty，同时拒绝目标冲突、工具污染、越界变更与 HEAD 漂移。

### Requires explicit init

未冻结 baseline 时 `inspect` 必须失败，禁止用「当前脏工作区」假装已隔离。

### Allows ambient preexisting

启动前已存在的无关 dirty 必须记入 `AMBIENT_PREEXISTING`，且 inspect 仍可通过。

### Target conflict blocks

Change Matrix 目标在 baseline 前已 dirty 时必须 `DELIVERY_TARGET_CONFLICT`。

### Tooling conflict blocks

无关治理工具在 baseline 前 dirty 时必须 `DELIVERY_TOOLING_BLOCKED`。

### Ambient mutation blocks

交付过程中改写 ambient 路径必须 `DELIVERY_AMBIENT_MUTATED`。

### Scope drift blocks

交付后新出现的非 Plan dirty 必须 `DELIVERY_SCOPE_DRIFT`。

### HEAD drift blocks

无关 commit/rebase 移动 HEAD 必须 `DELIVERY_HEAD_DRIFT`，不能当成 ambient。

### Plan semantic drift blocks

冻结后改 Plan 规格必须 `DELIVERY_PLAN_SEMANTIC_DRIFT`。

### Refresh cannot hide implementation delta

已有 implementation delta 时 `init --refresh` 必须 `DELIVERY_WORKSPACE_REFRESH_AFTER_MUTATION`。

### Completion precheck allows ambient dirty

Completion Audit precheck 在稳定 ambient dirty 下仍可通过，且只把 Plan-owned 路径算作 changed。

### Completion precheck rejects unplanned files

未在 Change Matrix 中的新文件必须让 Completion Audit precheck 失败。

## Proof freshness

Audit、Review、Verification 与 durable manifest 必须绑定当前 scope；命令或内容变化要使旧 proof stale。

### Plan review survives runtime status

Todo `status` 变化不得使已绑定 semantic hash 的 Plan review 变成 STALE。

### Completion audit is scope-bound

Plan-owned 内容变化后 Completion Audit 必须从 FRESH_PASS 变为 STALE。

### Implementation review is scope-bound

Plan-owned 内容变化后 implementation review 必须变为 STALE。

### Evidence command must match plan

Verification 命令与 Plan Ledger 不一致时不得记 PASS，状态应为 MISSING。

### Evidence freshness is scope-bound

曾经 FRESH 的 blocking evidence 在实现内容变化后必须变为 STALE。

### Durable manifest is scope-neutral

生成 durable manifest 不得改写 `scope_fingerprint`，且 manifest 自身必须 FRESH。

## Execution context

Resume 与 continuation gate 只服务恢复与停机判断，不能代替 Completion Gate。

### Resume tracks attempts

同一 ERROR 摘要必须累计 attempt，resume 仍指向当前 active Todo。

### Continuation gate is not completion

无进度重复询问时 continuation gate 可 `ALLOW_STOP`，但不得产出 `IMPLEMENTED_AND_PROVEN`。

## Commit

post_review commit 只收录 Plan-owned 路径；Windows 路径别名不得破坏 repo-relative identity。

### Commit guard allows stable ambient dirty

稳定 ambient dirty 下，commit guard 必须允许只提交 Plan-owned 路径，且 commit 后 ambient 仍在。

### Path identity accepts filesystem alias

repo-relative 路径必须按文件系统身份识别别名根，而不是裸字符串 `relative_to`。

## Acceptance

LIVE 验收必须在执行前做合同与环境预检；blocking FAIL 不得被 reuse 成 PASS。

### Contract accepts targeted rerun

声明 `TARGETED_RERUN` 且带 invalidation reason 的 blocking Claim 必须通过结构校验。

### Blocking prior failure cannot be reused

blocking Claim 的 Prior Result=FAIL 使用 `REUSE_EVIDENCE` 时必须 `PLAN_BLOCKING_FAILURE_REUSE_FORBIDDEN`。

### Missing environment is precheck blocked

缺必需环境变量时 preflight 必须 `LIVE_ENV_NOT_READY`，且不得当成产品 FAIL。

### Candidate mismatch is LIVE_SUT_MISMATCH

部署 candidate 与当前 capture 不一致时必须 `LIVE_SUT_MISMATCH`。

### Matching candidate passes preflight

环境就绪且 candidate 一致时，live preflight 必须通过。

## Test Asset Catalog

Test Asset Catalog 的回归测试保证跨 Roadmap Item 可复用测试实现，同时不把已变更的脚本伪装成可复用或历史 PASS。

### Resolves the v3.6 contract

Delivery readiness and completion 必须将 v3.6 Plan 分派给 v3.6 validator，不得回退到 v3.3 或把候选合同误判为非当前版本。

### Reuses an unchanged live asset

后续 Plan 引用 ACTIVE 且 digest-current 的 live asset 时，验证允许 `REUSE` 并保持资产文件不属于当前 Plan 写集。

### Rejects stale reuse

资产文件内容与 manifest digest 不一致时，Plan 不能声明 `REUSE`，以防 RM-20 错把已变更的 RM-10 live test 当作可靠基线。

### Synchronizes an extended asset

`EXTEND` asset 的测试文件和 manifest 都被 Plan 所有时，Delivery sync 必须刷新 digest，使后续 Plan 能确定性发现该资产的新版本。

## Runtime Cost Optimization

运行时成本优化必须缩小重复上下文而非削弱 Plan、Review、Evidence 或 Delivery 的唯一事实源。

### Creates a todo-scoped brief

派生 brief 必须只包含当前 Todo 及全局约束，不能意外携带其它 Todo 的写权限。

### Creates a plan-scoped report path

worker report 必须位于当前 Plan 的 `.smc/runs/<plan_id>/reports/`，避免跨 Plan 状态混用。

### Scopes task review to declared writes

task review package 只能包含当前 Todo 声明的写路径差异，不能泄露或重审其它 Todo 的未完成变更。

### Skips semantic review for low risk

无确定性语义风险的首次 Plan review 可以路由为 `NOT_REQUIRED/NONE`，但仍需要记录当前 hash 的 clearance。

### Escalates acceptance review to full

声明 acceptance contract 且无法通过确定性结构 clearance（或缺 structured risk snapshot）的 Plan 必须路由到 `REQUIRED/FULL`，不得因成本优化跳过真实语义审查。

### Allows lean light first review

LEAN + structured 无高风险且 acceptance 结构 clearance 通过时，首次审查可路由为 `REQUIRED/DELTA`（LIGHT_FIRST_REVIEW），仍保留 blocking acceptance 检查。

### Routes a reviewed semantic delta

已有 PASS snapshot 且 Plan 语义变化时必须路由为 `REQUIRED/DELTA`，并只提供可审计的语义 diff。

### Fails closed without a semantic snapshot

请求 DELTA 但没有先前 snapshot 时必须升级为 FULL，不能把未知差异误作轻量审查。

### Requires a fresh pass before snapshot

semantic snapshot 只能在当前 Plan hash 对应的 PASS review record 之后保存。

## Work Router Research Trust

Work Router 测试验证 research 自报不能绕过 governed/production 工作，且纯研究仍可低成本 NONE。

### Research only alone cannot none

仅设置 `research_only=true` 而缺少 authority 字段时不得路由 NONE，必须 fail-closed。

### Governed research forces full

`research_intent` 与 `governed=true` 冲突时必须 FULL，并返回 `RESEARCH_ONLY_CONTRADICTS_GOVERNED_WORK`。

### Pure research may spike none

authority 字段全部显式 false 的纯研究请求可路由 SPIKE/NONE。

## Structured Risk Runtime

风险解析测试验证否定句不假 FULL，以及 structured/text contradiction fail-closed。

### Negated schema migration is not high risk

文本 “No schema migration” 在 structured `schema_migration=false` 时不得单独升级 FULL。

### Affirmative contradiction fails closed

structured false 但文本肯定高风险时必须返回 `RISK_FACT_CONTRADICTION` 并 fail-closed。

## Engineering Method Runtime

Engineering Method Runtime 的测试验证它只约束 Todo 的执行方法，既不放宽 delivery gate，也不以过期 working memory 替代当前 Plan。

### Classifies profiles and risk tiers

Todo 的语义信号必须确定性映射到 mechanical、behavior、bug 或 high-risk profile，并给出相应的 model tier 与 review depth。

### Requires a RED-GREEN cycle

TDD_REQUIRED Todo 缺少确认 RED 或其后的 GREEN PASS 时必须阻断完成，防止测试记录被伪装成最终验证。

### Requires root cause before a bug fix

BUG_FIX Todo 在没有确认 ROOT_CAUSE 前必须阻断 debug gate，避免在没有解释失败机制时盲目修改生产代码。

### Escalates three failed fixes

同一 Todo 的第三次 failed FIX_ATTEMPT 必须触发 architecture escalation，禁止第四次盲修。

### Persists explicit controller overrides

controller 的 profile 与 model override 必须写入 method artifact，使执行策略可审计而非隐式继承。

### Rejects a stale method artifact

Plan 语义变化后，旧 method artifact 不得继续决定 TDD、debug 或审查策略，必须显式重新分类。

### Rejects a malformed method artifact

损坏或 schema 不匹配的 method artifact 必须 fail-closed，不能静默回退到更弱的 heuristic profile。

## Acceptance Closure

Acceptance Closure 测试证明 Remaining Findings 以真实行为关闭，而不是文档或 grep 断言。

### Hard risk beats stale pass

当前 hard risk（如 schema migration）必须把审查深度升为 FULL，即使 prior PASS 已因语义变更变为 STALE 且本可走 DELTA。

### Invalid snapshot forces full

存在但被篡改的 Risk Facts Snapshot（`INVALID`）必须 fail-closed 为 FULL；旧 Plan 完全缺 snapshot（`ABSENT`）仍可走低风险 NONE。

### Authority required for production none

生产 CLI 在无 verified work-authority 时不得路由 NONE；绑定后的纯研究 authority 仍可 SPIKE/NONE。

### No fulltext blocking on negation

Domain Preplan 在 structured row 完整且否定高风险时，不得因全文 regex 误触发 blocking FULL。

### Duplicate write owner is blocked

两个 Todo 争同一 `path#symbol` WRITE_OWNER 必须回 `PLAN_WRITE_OWNERSHIP_CONFLICT`（FI-04）。

### Worker out of scope drifts

Delivery workspace 在写集外修改 production 路径时必须回 `DELIVERY_SCOPE_DRIFT`。

### TDD scope becomes stale

真实 RED/GREEN receipt 之后改绑定源码必须回 `TDD_SCOPE_STALE`。

### Review becomes stale after semantic change

Implementation review PASS 后改 semantic Plan 必须使 review 状态变为 `STALE`。

### Evidence becomes stale after production change

Blocking evidence 绑定后改 production 内容必须使 evidence 变为 `STALE`。

### Live candidate mismatch

Live acceptance candidate 与声明 SUT 不一致时必须回 `LIVE_SUT_MISMATCH`。

### Debug escalates after three failed fixes

REPRODUCTION + ROOT_CAUSE 后连续三次 FIX_ATTEMPT FAIL 必须回 `DEBUG_ARCHITECTURE_ESCALATION`。
