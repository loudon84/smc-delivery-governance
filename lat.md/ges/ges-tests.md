# GES Tests

GES 交付工具的关键测试规格。它们证明 Plan 投影、scoped workspace、proof freshness、commit guard 与 live acceptance 在隔离沙箱中 fail-closed。

覆盖当前树内 `smc-plan-delivery` 与 Roadmap evidence 合同，而不是复述脚本实现。

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
