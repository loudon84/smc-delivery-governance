---
title: "GES Large Repo Snapshot Optimization PRD"
subtitle: "Business Source Guard v2 + Git-aware Init Hot-path"
prd_id: "PRD-GES-LARGE-REPO-SNAPSHOT-OPTIMIZATION"
version: "1.0"
status: "APPROVED_FOR_PLAN"
product: "GES 6"
repository: "loudon84/smc-delivery-governance"
branch: "feat/ges-v6.1"
owner: "GES"
created_at: "2026-09-17"
updated_at: "2026-09-17"
change_type: ["PERFORMANCE","SAFETY_HARDENING","BROWNFIELD_CHANGE"]
target_release: "GES 6.0.0-alpha.2 Large Repo Performance Closure"
goal: "将 ges init 的 Business Source Guard 从全业务目录双遍逐文件 SHA256 改为 Git-aware Index + Dirty Overlay，并消除 Init Hot-path 中不必要的全树 rglob，同时保持业务源码零修改证明与 fail-closed 安全语义。"
---

# GES Large Repo Snapshot Optimization PRD

> 本 PRD 按《需求PRD工程模板.md》输出。
>
> 本需求不是降低安全门禁，而是重构为 **Business Source Guard v2**：
>
> `Preventive Write Boundary + Git Index Identity + Dirty/Untracked Exact-byte Overlay + Before/After Deterministic Comparison`

# 0. PRD 使用原则

## 0.1 Normative Keywords

`MUST / MUST NOT / SHOULD / SHOULD NOT / MAY`

所有 MUST / MUST NOT 必须映射 Acceptance。

## 0.2 No-Inference Rule

Plan / Coding Agent 不得自行决定：

- 哪些文件属于 Business Source Guard；
- ignored file 是否进入保护集；
- dirty tracked / untracked 是否需要内容 hash；
- Git index identity 如何计算；
- Git unavailable 时是否跳过保护；
- 是否为性能取消 source verification；
- 是否允许 persistent cache 成为正确性 SOT。

无法唯一确定：`SPEC_SEMANTIC_GAP → BLOCK PLAN`。

# 1. 当前实现与问题

当前 `ges init` 主链：

`compose → prepare_apply → apply_plan → ges check → ges doctor`

`apply_plan()` 在 apply 前调用 `snapshot_business_sources(repo)`，在 apply/check 后由 `assert_business_unchanged()` 再做一次快照，因此一次真实 apply 至少双遍业务源码快照。

Business roots：

- `apps/`
- `services/`
- `src/`
- `packages/`
- `contracts/`

当前 `iter_business_files()` 使用 `Path.rglob("*")` 枚举每个物理文件，再逐文件读取并 SHA256，只显式忽略 `.git`。大型项目中 `node_modules/dist/build/cache` 只要位于这些根目录下，也会进入物理扫描。

真实大型 Consumer `E:\git\smc-copilot` 约 8.4 万物理文件，首次 `ges init --yes` 在 SHA256 snapshot 阶段耗时数分钟。该耗时是 CPU + Disk I/O，不是 LLM Token。

另外 Analyzer 仍存在 `repo.rglob("tsconfig*.json")`、`repo.rglob("*.ts")`、`repo.rglob("*.tsx")`、`repo.rglob("package.json")`。即使结果阶段过滤 `node_modules`，遍历本身仍然发生。

# 2. 一句话目标

让 Git 仓库中的 `ges init` 默认使用 **Git Index + Dirty Overlay Business Source Guard v2**：clean tracked 文件只使用 Git index blob identity，不读取工作区内容；只对 dirty tracked、non-ignored untracked 与特殊文件读取必要字节；Analyzer 复用同一 Git-visible file index，从而让性能主要随 Git-visible source 规模变化，而不是随依赖/构建缓存物理文件数变化。

# 3. Scope

## 3.1 In Scope

- Business Source Guard v2
- Git-aware tracked identity
- dirty tracked exact-byte overlay
- non-ignored untracked exact-byte overlay
- deleted / symlink / gitlink identity
- T0/T1 deterministic compare
- Git HEAD / index race detection
- GES write-set ledger
- safe full-SHA fallback
- performance telemetry
- Analyzer GitFileIndex
- non-Git top-down pruning
- 110k synthetic fixture
- `E:\git\smc-copilot` real benchmark
- existing Alpha.1/Alpha.2 behavior regression

## 3.2 Out of Scope

MUST NOT：

- 删除 Business Source Guard；
- 按文件数量自动关闭 Guard；
- 用 LLM 判断“重要文件”；
- 建立全仓 CAS；
- 引入 Watchman/daemon/USN Journal；
- 改变 Composer capability semantics；
- 改变 Governance Backplane Work/Gate semantics；
- 用 persistent cache 作为 correctness SOT。

# 4. Architecture Boundary

| Domain | Owner | Input | Output |
|---|---|---|---|
| Business source policy | GES | roots + Git visibility | Protected Set |
| Git identity | Git | index/worktree | tracked/status |
| Source Guard | GES | T0/T1 | unchanged/changed |
| Write Boundary | Reconciler | target paths | allow/deny ledger |
| Repo Analyzer | GES | GitFileIndex | language/framework evidence |
| Ignore semantics | Git | `.gitignore` | ignored/nonignored |
| Fallback Guard | GES | physical tree | full exact snapshot |

# 5. Terminology

**Physical File**：磁盘中的任意文件，包括 tracked、untracked、ignored dependency/build/cache。

**Git-visible Business Source**：Business root 下的 tracked 文件 + non-ignored untracked 文件。

**Clean Tracked File**：worktree 与 index 一致。身份由 `index mode + blob OID + path` 表达，不再由 GES 重新 SHA256 工作区字节。

**Dirty Tracked File**：相对 index 有 worktree mutation，必须记录 exact content identity。

**Non-ignored Untracked**：Git `??` 且未 ignore，必须 exact hash。

**Ignored Physical File**：不进入 snapshot content identity，但仍受 GES Preventive Write Boundary 保护。

**Dirty Overlay**：对 dirty/untracked/deleted/special path 建立当前工作区 exact identity。

**GitFileIndex**：一次 Git 查询得到的 repo-visible path inventory，供 Guard 和 Analyzer 复用。

# 6. State / SOT

| State | Authority |
|---|---|
| Git HEAD | Git |
| Git index records | Git |
| porcelain-v2 status | Git |
| dirty overlay hash | GES observation |
| untracked overlay hash | GES observation |
| `.gitignore` semantics | Git |
| Business roots | GES |
| Snapshot v2 | Derived |
| persistent cache | NOT SOT |

Invariant：Git index 是 clean tracked identity acceleration，不代表可以忽略 dirty/untracked source。

# 7. State Machine

`UNSNAPSHOTTED → GIT_INDEXED → T0_SNAPSHOTTED → APPLIED → T1_SNAPSHOTTED → UNCHANGED | CHANGED`

- UNCHANGED → commit success
- CHANGED → rollback
- Git provider failure → `SAFE_FALLBACK_FULL`
- Non-Git → `FULL_SHA256_FALLBACK`
- fallback 绝不能变成 skip guard

# 8. Schema

## `ges.business-source-snapshot.v2`

```json
{
  "schema": "ges.business-source-snapshot.v2",
  "strategy": "git-index-overlay",
  "repo_head": "<40-char>",
  "roots": ["apps","packages"],
  "index_digest": "sha256:<hex>",
  "status_digest": "sha256:<hex>",
  "overlay_digest": "sha256:<hex>",
  "snapshot_digest": "sha256:<hex>",
  "counts": {
    "tracked": 0,
    "clean_tracked": 0,
    "dirty_tracked": 0,
    "untracked_nonignored": 0,
    "overlay_content_hashed": 0,
    "symlinks": 0,
    "submodules": 0
  },
  "bytes_hashed": 0,
  "elapsed_ms": 0
}
```

Clean tracked canonical record：

`T<NUL><mode><NUL><blob_oid><NUL><path><LF>`

Dirty/untracked regular：

`F<NUL><path><NUL><size><NUL><sha256><LF>`

Deleted：

`D<NUL><path><LF>`

Symlink：

`L<NUL><path><NUL><sha256(link_target_utf8)><LF>`

Gitlink：

`G<NUL><path><NUL><index_gitlink_oid><NUL><observed_head><NUL><dirty_state><LF>`

Snapshot digest：

`SHA256(repo_head + NUL + index_digest + NUL + status_digest + NUL + overlay_digest)`

# 9. Requirements

## REQ-LR-GIT-001 — Git-aware File Inventory

Git repo MUST use NUL-safe commands equivalent to：

```bash
git ls-files --stage -z -- apps services src packages contracts
git status --porcelain=v2 -z --untracked-files=all --ignore-submodules=none -- apps services src packages contracts
```

MUST NOT 使用 newline path parsing。

Git command failure：

`BUSINESS_GIT_INDEX_UNAVAILABLE → safe full fallback`

Acceptance：`A-LR-GIT-001..002`

---

## REQ-LR-SNAPSHOT-001 — Clean Tracked Files Must Not Be Rehashed

Clean tracked MUST use `mode + blob OID + path`。

MUST NOT open file content / SHA256 worktree bytes。

如果 apply 中 clean file 被修改，T1 status 必须使 snapshot mismatch。

Acceptance：`A-LR-SNAP-001..002`

---

## REQ-LR-SNAPSHOT-002 — Dirty Tracked Exact-byte Overlay

T0 dirty tracked path MUST SHA256 exact bytes；T1 重新计算。

即使 Git status 仍为 `M → M`，内容 `X → Y` 必须 FAIL。

Deleted path 使用 `D` sentinel。

Acceptance：`A-LR-DIRTY-001..003`

---

## REQ-LR-SNAPSHOT-003 — Non-ignored Untracked Overlay

Non-ignored untracked under business roots MUST hash exact bytes。

以下均 FAIL：

- existing → changed
- existing → removed
- absent → new

Ignored untracked MUST NOT content-hash，也不得为 snapshot 专门做 physical full-tree enumeration。

Acceptance：`A-LR-UNTRACKED-001..002`

---

## REQ-LR-SNAPSHOT-004 — Symlink / Submodule

Symlink MUST NOT follow external target；identity 为 link target string。

Gitlink/submodule记录 index gitlink OID + observed HEAD + dirty state。Dirty submodule使用 exact fallback；无法安全解析则：

`SUBMODULE_SOURCE_STATE_UNRESOLVED → BLOCK`

Acceptance：`A-LR-SPECIAL-001..002`

---

## REQ-LR-SNAPSHOT-005 — HEAD / Index / Worktree Consistency

T0/T1 都记录 HEAD / index / status / overlay。

- HEAD change → `BUSINESS_GIT_HEAD_CHANGED_DURING_APPLY`
- index change → `BUSINESS_GIT_INDEX_CHANGED_DURING_APPLY`
- protected bytes change → `BUSINESS_SOURCE_MODIFICATION_FORBIDDEN`

以上均 rollback managed GES state，process exit != 0。

Acceptance：`A-LR-CONSISTENCY-001..003`

---

## REQ-LR-WRITE-001 — Preventive Write Ledger

所有 Composer consumer writes/removes MUST 经过 centralized mutation API：

- normalize
- contain
- record ledger
- assert allowed
- assert not business source

任何目标位于 `apps/services/src/packages/contracts`：

`BUSINESS_SOURCE_MODIFICATION_FORBIDDEN` before mutation。

该规则独立于 Git ignore。即 `apps/work/node_modules/x` 被 ignore，也不是 GES 可写路径。

Acceptance：`A-LR-WRITE-001..002`

---

## REQ-LR-FALLBACK-001 — Safe Full Snapshot Fallback

以下情况自动进入 `full-sha256-fallback`：

- non-Git repo
- Git inventory unavailable
- unsupported Git state

MUST preserve exact-byte verification；MUST NOT silently disable guard。

Acceptance：`A-LR-FALLBACK-001..002`

---

## REQ-LR-ANALYZE-001 — Shared GitFileIndex for Analyzer

Git repo 中以下 detector MUST 从 shared GitFileIndex 得到 path：

- `tsconfig*.json`
- `*.ts/*.tsx`
- `package.json`

MUST NOT 使用 `repo.rglob()` 深入 ignored dependency trees。

输出保持 deterministic：

- TypeScript evidence 最多前 5 个 sorted path
- tsconfig sorted
- package.json sorted

Acceptance：`A-LR-ANALYZE-001..003`

---

## REQ-LR-ANALYZE-002 — Non-Git Traversal Pruning

Non-Git Analyzer 使用 `os.walk(topdown=True)`，进入前 prune：

`.git,node_modules,dist,build,out,coverage,.next,.turbo,.cache,__pycache__,.venv,venv,target`

注意：该 prune list **只用于 Analyzer evidence discovery**，不得替代 Business Guard fallback correctness。

Acceptance：`A-LR-ANALYZE-004`

---

## REQ-LR-PERF-001 — Performance Telemetry

每次 init 至少记录：

- `business_guard_strategy`
- `business_snapshot_t0_ms`
- `business_snapshot_t1_ms`
- `business_tracked_count`
- `business_dirty_hashed_count`
- `business_untracked_hashed_count`
- `business_bytes_hashed`
- `analyzer_file_index_ms`
- `analyzer_index_path_count`

CLI compact summary 示例：

```text
Business Guard: git-index-overlay
Tracked: 12,481
Content-hashed overlay: 37 files / 4.2 MB
Snapshot: T0 1.8s / T1 1.6s
```

MUST NOT打印所有路径或文件内容。

Business Guard LLM call/token：

`0`

Acceptance：`A-LR-PERF-001`

---

## REQ-LR-PERF-002 — Large Repo Performance Gate

Synthetic fixture：

- 10,000 clean tracked
- 100 dirty tracked
- 100 nonignored untracked
- 100,000 ignored generated/dependency files

Required deterministic oracle：

- clean tracked content hash calls = 0
- ignored content hash calls = 0
- overlay content hash calls <= 200

Synthetic two-pass Business Guard target：`<=15s` on standard CI SSD runner；若 CI wall-time 波动，则 operation-count 是硬 Gate，wall-time 转入 Golden Gate。

Real Golden：

`E:\git\smc-copilot`，约 84k physical files：

- strategy = `git-index-overlay`
- ignored/generated content hash calls = 0
- T0 + T1 Business Guard `<=30s`
- business source unchanged
- ges init succeeds

Acceptance：`A-LR-PERF-002..003`

# 10. Side Effects

| Operation | Repo Write | Git Index | Git Ref | Network | LLM |
|---|---:|---:|---:|---:|---:|
| GitFileIndex | NO | NO | NO | NO | NO |
| Snapshot T0/T1 | NO | NO | NO | NO | NO |
| Analyzer index | NO | NO | NO | NO | NO |
| GES apply | managed only | NO | NO | MAY fetch source | NO |
| Telemetry | log only | NO | NO | NO | NO |

# 11. Ownership

- Git index → EXTERNAL/Git-owned
- Business Source → USER_OWNED
- Snapshot v2 → DERIVED/ephemeral
- Mutation ledger → transaction-local
- Metrics → DERIVED
- no new persistent source ownership

# 12. Identity / Hash

- clean tracked → mode + blob OID + path
- dirty regular → SHA256 exact bytes
- nonignored untracked → SHA256 exact bytes
- symlink → SHA256(link target text), no follow
- deleted → ABSENT
- no newline normalization

# 13. Transaction

New apply order：

```text
compose
→ build/reuse GitFileIndex
→ T0 BusinessSnapshotV2
→ stage
→ managed T0
→ commit projection
→ remove obsolete GES paths
→ ges check
→ T1 BusinessSnapshotV2
→ compare
→ success / rollback
```

# 14. Failure Contract

| Failure | Result |
|---|---|
| Git inventory error | safe full fallback |
| fallback error | BLOCK `BUSINESS_SNAPSHOT_FAILED` |
| HEAD changed | rollback/block |
| index changed | rollback/block |
| dirty bytes changed | rollback/block |
| untracked source created/changed/deleted | rollback/block |
| submodule unresolved | BLOCK |
| hash read permission denied | rollback/block |

# 15. Conflict Semantics

Pre-existing dirty worktree MUST be supported。

`dirty X at T0 + dirty X at T1 → PASS`

`dirty X at T0 + dirty Y at T1 → FAIL`

Existing untracked source同理。

Ignored generated tree不做 content hash，但 GES write boundary仍禁止写。

# 16. Compatibility / Migration

Current snapshot is ephemeral，因此无持久状态迁移。

内部 API 建议从：

`snapshot_business_sources()`

升级为 semantic facade：

`capture_business_snapshot()`

MUST NOT change：

- project.yaml
- lock/receipt schema
- capability set
- governance Work/Policy/Gate semantics

# 17. Security

| Threat | Control |
|---|---|
| clean tracked skip read 后漏 mutation | T1 Git status + overlay |
| dirty source漏检 | exact overlay |
| untracked source漏检 | nonignored overlay |
| ignored path被 GES 写 | preventive write ledger |
| symlink escape | no target follow |
| concurrent checkout | HEAD compare |
| concurrent staging | index compare |
| Git error fail-open | full fallback |
| stale persistent cache | no correctness cache |

# 18. Observability

Stages：

`FILE_INDEX / BUSINESS_SNAPSHOT_T0 / COMPOSER_APPLY / BUSINESS_SNAPSHOT_T1 / BUSINESS_COMPARE / ANALYZER_INDEX`

Metrics：

`strategy, elapsed_ms, tracked_count, dirty_count, untracked_count, content_hashed_count, bytes_hashed, fallback_reason`

# 19. Acceptance

### A-LR-GIT-001
10k tracked + 100k ignored → tracked index only contains Git-visible set。

### A-LR-GIT-002
NUL-safe parser支持 space/unicode/newline path。

### A-LR-SNAP-001
10k clean tracked → `clean_tracked_content_hash_calls == 0`。

### A-LR-SNAP-002
clean tracked 在 apply 中被改 → T1 detects → FAIL。

### A-LR-DIRTY-001
pre-existing dirty X unchanged → PASS。

### A-LR-DIRTY-002
status 仍 M，但 bytes X→Y → FAIL。

### A-LR-DIRTY-003
dirty file deleted → FAIL。

### A-LR-UNTRACKED-001
existing nonignored untracked unchanged → PASS。

### A-LR-UNTRACKED-002
untracked new/changed/removed → FAIL。

### A-LR-SPECIAL-001
symlink external target bytes变化但 link string 不变 → snapshot unchanged；link string 变化 → changed。

### A-LR-SPECIAL-002
dirty submodule不能安全解析 → fallback exact or BLOCK，绝不能 silent PASS。

### A-LR-CONSISTENCY-001
HEAD race → rollback/block。

### A-LR-CONSISTENCY-002
index race → rollback/block。

### A-LR-CONSISTENCY-003
protected byte mutation → rollback/block。

### A-LR-WRITE-001
尝试写 ignored `apps/**/node_modules/**` → before-write BLOCK。

### A-LR-WRITE-002
successful transaction ledger 中 `business_root_write_count == 0`。

### A-LR-FALLBACK-001
non-Git fixture → full exact guard。

### A-LR-FALLBACK-002
inject Git failure → fallback active，不允许 skip。

### A-LR-ANALYZE-001
100k ignored fixture → Analyzer ignored-tree traversal count = 0。

### A-LR-ANALYZE-002
新旧 detector 在受控 fixture 的语义结果一致。

### A-LR-ANALYZE-003
重复执行 evidence path/order一致。

### A-LR-ANALYZE-004
Non-Git walker 不进入 node_modules/dist/.cache。

### A-LR-PERF-001
所有 telemetry 字段存在，文件内容未写入日志，LLM calls=0。

### A-LR-PERF-002
110.2k synthetic fixture operation budget PASS。

### A-LR-PERF-003
`E:\git\smc-copilot` T0+T1 <=30s，ignored hash=0，source unchanged。

# 20. Edge Matrix

| Case | Expected |
|---|---|
| clean Git + huge ignored | fast PASS |
| one dirty tracked | only dirty hash |
| one untracked source | only untracked hash |
| dirty changes during apply | FAIL |
| HEAD changes | rollback/block |
| index stages file | rollback/block |
| non-Git | full fallback |
| Git error | fallback, never skip |
| symlink source | link identity |
| dirty submodule | exact fallback/block |
| 100k ignored | 0 ignored hashes |
| 50k nonignored untracked | correct but slower + telemetry |
| staged change before init | allowed baseline |
| staged change during init | FAIL |

# 21. Negative Acceptance

- file count > threshold 时禁用 snapshot → FAIL
- 把所有 untracked 当 ignored → FAIL
- 只用 index 不做 dirty overlay → FAIL
- `M→M` byte change漏检 → FAIL
- Git error直接 PASS → FAIL
- symlink 跟随外部 target → FAIL
- ignored business path可被 GES 写 → FAIL
- Analyzer Git mode仍递归进入 node_modules → FAIL
- persistent cache 未 revalidate 就作为 truth → FAIL

# 22. Failure Injection

- `git ls-files` nonzero → fallback
- porcelain parse error → fallback/block，never silent PASS
- HEAD changes after T0 → rollback
- index changes after T0 → rollback
- dirty bytes change → rollback
- new untracked source → rollback
- submodule unresolved → BLOCK
- content hash permission denied → `BUSINESS_SNAPSHOT_FAILED`

# 23. Evidence Contract

Synthetic Evidence MUST include：

- GES commit
- test command
- fixture counts
- strategy
- content hash call counts
- bytes hashed
- elapsed
- AC results

Golden Evidence MUST include：

- GES commit
- consumer path/HEAD/dirty
- physical file estimate
- Git-visible count
- dirty/untracked count
- T0/T1 ms
- bytes hashed
- init exit
- source compare

Token Evidence：

`llm_call_count = 0`

# 24. Traceability Matrix

| Requirement | Acceptance | Gate |
|---|---|---|
| REQ-LR-GIT-001 | A-LR-GIT-001..002 | REQUIRED |
| REQ-LR-SNAPSHOT-001 | A-LR-SNAP-001..002 | REQUIRED |
| REQ-LR-SNAPSHOT-002 | A-LR-DIRTY-001..003 | REQUIRED |
| REQ-LR-SNAPSHOT-003 | A-LR-UNTRACKED-001..002 | REQUIRED |
| REQ-LR-SNAPSHOT-004 | A-LR-SPECIAL-001..002 | REQUIRED |
| REQ-LR-SNAPSHOT-005 | A-LR-CONSISTENCY-001..003 | REQUIRED |
| REQ-LR-WRITE-001 | A-LR-WRITE-001..002 | REQUIRED |
| REQ-LR-FALLBACK-001 | A-LR-FALLBACK-001..002 | REQUIRED |
| REQ-LR-ANALYZE-001 | A-LR-ANALYZE-001..003 | REQUIRED |
| REQ-LR-ANALYZE-002 | A-LR-ANALYZE-004 | REQUIRED |
| REQ-LR-PERF-001 | A-LR-PERF-001 | REQUIRED |
| REQ-LR-PERF-002 | A-LR-PERF-002..003 | REQUIRED |

# 25. Release Gate

`SKIPPED != PASS`，`BLOCKED != PASS`。

任一 Required AC != PASS：

`LARGE_REPO_OPTIMIZATION_RELEASE_GATE = FAIL`

全部 PASS：

```text
GES Large Repo Snapshot Optimization: PASS
Business Guard v2: PASS
Dirty Overlay: PASS
Untracked Overlay: PASS
Write Boundary: PASS
Analyzer GitFileIndex: PASS
Fallback Safety: PASS
Synthetic 110k Fixture: PASS
Real 84k Consumer: PASS
LARGE_REPO_GUARD_V2_READY
```

# 26. Golden Consumer

Primary performance Golden：

`E:\git\smc-copilot`

Regression Golden：

`E:\git\smc-copilot-desktop`

Primary flow：

`resolve HEAD → record dirty → T0 → ges init → T1 → assert unchanged → record metrics`

# 27. Plan Generation Contract

`status = APPROVED_FOR_PLAN`

Suggested Plan：

- PLAN-LR-01 BusinessSnapshotV2 Model
- PLAN-LR-02 GitFileIndex
- PLAN-LR-03 Dirty / Untracked Overlay
- PLAN-LR-04 Symlink / Submodule
- PLAN-LR-05 Reconciler Integration
- PLAN-LR-06 Mutation Ledger
- PLAN-LR-07 Analyzer Migration
- PLAN-LR-08 Non-Git Fallback
- PLAN-LR-09 Telemetry
- PLAN-LR-10 110k Synthetic Fixture
- PLAN-LR-11 `E:\git\smc-copilot` Golden Benchmark
- PLAN-LR-12 Regression / Release Evidence

Todo schema：

```yaml
id:
requirement_refs:
acceptance_refs:
files_or_symbols:
implementation_goal:
preconditions:
state_transition:
side_effect_scope:
failure_cases:
verification:
status:
evidence:
```

# 28. Code Review Contract

Review顺序：

1. 是否弱化/取消 Business Guard；
2. clean tracked 是否仍逐文件读；
3. dirty tracked 是否 exact protected；
4. untracked nonignored 是否 protected；
5. ignored paths 是否仍被 write boundary deny；
6. Git failure 是否 fail-open；
7. HEAD/index race 是否检测；
8. symlink 是否跟随外部 target；
9. Analyzer 是否仍 rglob ignored tree；
10. perf test 是否有 operation-count oracle；
11. 真实 84k Golden 是否执行；
12. 普通代码质量。

# 29. PRD Quality Gate

- [x] Goal / Scope / Non-goal
- [x] Git-visible Business Source 定义
- [x] ignored semantics
- [x] dirty/untracked semantics
- [x] hash algorithm
- [x] fallback
- [x] race behavior
- [x] side effects
- [x] failure injection
- [x] machine-readable performance oracle
- [x] Synthetic / Golden separation
- [x] no LLM/token contract
- [x] no SPEC_SEMANTIC_GAP
- [x] APPROVED_FOR_PLAN

# 30. Definition of Done

- [ ] BusinessSnapshotV2
- [ ] GitFileIndex
- [ ] clean tracked content hash count = 0
- [ ] dirty exact overlay
- [ ] nonignored untracked overlay
- [ ] deleted detection
- [ ] symlink no-follow
- [ ] submodule fail-closed
- [ ] HEAD/index race detection
- [ ] business mutation rollback preserved
- [ ] ignored generated content hash = 0
- [ ] ignored business paths still deny writes
- [ ] mutation ledger business write count = 0
- [ ] Git failure full fallback
- [ ] no performance path disables guard
- [ ] Analyzer GitFileIndex
- [ ] Git mode no ignored-tree rglob
- [ ] non-Git analyzer prune
- [ ] detector parity
- [ ] telemetry
- [ ] llm_call_count = 0
- [ ] 110k synthetic PASS
- [ ] `E:\git\smc-copilot` T0+T1 <=30s
- [ ] source unchanged
- [ ] `smc-copilot-desktop` regression PASS
- [ ] all Required AC PASS

# 31. Final Engineering Contract

旧模型：

`Business Roots → rglob every physical file → read every file → SHA256 every file → apply → repeat`

新模型：

```text
Git Business Roots
    ↓
GitFileIndex
├─ clean tracked → mode + blob OID → NO worktree content read
├─ dirty tracked → exact SHA256 overlay
├─ nonignored untracked → exact SHA256 overlay
└─ ignored generated/dependency
     → no content scan
     → still protected by GES write deny
    ↓
Snapshot T0
    ↓
GES Apply
    ↓
Snapshot T1
    ↓
compare
```

必须同时满足：

- **Safety**：GES cannot modify business source
- **Correctness**：pre-existing dirty/untracked source preserved exactly
- **Performance**：成本随 Git-visible source + overlay 增长，不随 ignored physical tree增长
- **Tokens**：0 LLM calls

# 32. Product Boundary

本修复属于 `GES Core Infrastructure Hardening`，不是 Governance Backplane 新功能。

完成后继续 Alpha.2：`Work / Artifact / Evidence / Gate B Closure`，不得借性能优化扩大产品范围。
