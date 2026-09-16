# GES Install

GES 以 checksummed overlay 安装到已有 SMC skills baseline。默认 dry-run；`--apply` 才写入；失败自动回滚；永不自动 git commit。

生产安装必须校验发布包完整性。`install.py` 是稳定入口；当前工作树优先派发到 5.0.0 repaired candidate，已接受生产发布仍由 `BASELINE.md` 裁决。

## Stable Entrypoint

`install.py` 优先在未设置 `GES_V500_NO_DISPATCH` 时派发到 `install_v500.py`；v5 复用既有事务安装器，并增加完整清单校验及 Profile v2/v3 兼容逻辑。

Windows 上禁止用 `os.execv` 派发：它不会覆盖当前控制台进程，PowerShell 会提前回到提示符，安装看起来像卡住。实现必须 `subprocess.call` 并返回子进程退出码。

## Transactional Overlay

安装事务先备份再覆盖，post-install gate 失败则恢复升级前字节。

顺序：

1. 校验 `SHA256SUMS` / `PACKAGE-MANIFEST`；
2. 确认目标已有 SMC skills baseline（或显式 `--seed-consumer-skills`）；
3. overlay `.agents/skills`，并按 consumer 声明同步 mirrors；
4. 写入 gitignore（`.smc/evidence|reviews|runs|backups`）；
5. 跑 delivery self-test、Roadmap tests、可选项目 validator；
6. 任一 gate 失败 → [[engineeing-skills/install_v430.py#restore]]。

实现入口：[[engineeing-skills/install_v500.py#main]]、[[engineeing-skills/install_v500.py#preflight]]、[[engineeing-skills/install_v500.py#install_metadata]]。省略 `--profile` 时保留已安装 profile；但若 `profile.json` 或 `domain-packs/registry.json` 缺失，安装器必须修复完整元数据（不可只刷新 domain-runtime）。显式迁移 profile 需要重新绑定受影响 Plan。Managed skill 路径（如 `smc-plan-validator`）由 overlay 写入，不得作为 preflight 硬依赖。

## Consumer Baseline Seed

Greenfield 仓库可缺少 consumer-owned skills；默认仍 fail-closed，避免静默 stub 污染已有项目。

`--seed-consumer-skills` 仅复制**缺失**的 `consumer_required_skills`：优先包内 `.agents/skills/<name>`，否则 `consumer-baseline/<name>`；已存在文件永不覆盖。实现：[[engineeing-skills/install_v500.py#seed_consumer_skills]]、[[engineeing-skills/install_v430.py#preflight]]。

## Consumer Bootstrap

Install 之后用 [[consumer-bootstrap]] 做平台级 Audit / Gap / Remediation / Validate；apply 默认 dry-run，只补缺失脚手架与 bridge JSON。

禁止写入 `.specify/spec.md` 与 `.agents/ges/profile.json`。详见 [[consumer-bootstrap#Automated Remediation]]。

## Frontend Context Root

v5.0.6 起 Consumer UX Baseline 落在 `.agents/ges/frontend/`（JSON only），由 `consumer-bootstrap/frontend_audit.py` 与 [[frontend-context]] 维护，不由 installer overlay 强制覆盖。

路径约定：`apps-registry.json`、`apps/<app-id>/` baseline 文件集、`shared/shared-ui-registry.json`。默认 Adoption Mode 为 OBSERVE。v5.0.7 起 installer 另将运行时安装到 `.agents/ges/frontend-runtime/` 与 `.agents/ges/frontend-adapters/`（与数据目录分离），见 [[frontend-context#Frontend Runtime Delivery]]。

## Install Lock v2

Hardening 后的 install lock 证明 package bytes 身份，并安全清理未修改的 stale package-owned 文件。

见 [[acceptance-hardening#Install Lock v2]]：`smc.ges.install-lock.v2` 含 `release_identity` 与 `owned_files`；v1 lock 跳过破坏性清理。Closure 起 `package_manifest_sha256` 必须是 PACKAGE-MANIFEST **raw bytes** digest，lock 不再绑定 PENDING `transaction_manifest_sha256`（改由 receipt 绑定最终 PASS），见 [[acceptance-closure#Canonical Digests]]。

## Install Receipt

Architecture Closure 将顺序改为 receipt → lock → journal PASS（PRD §16）。

[[engineeing-skills/install_v500.py#write_immutable_receipt]] 在 [[engineeing-skills/install_v500.py#build_install_lock]] 内先落 `.smc/ges-install-receipts/<install_id>.json`（§15 全字段）；lock 引用 `install_receipt_path` + `install_receipt_sha256`。兼容指针 `.smc/ges-install-receipt.json` 仍可写。dirty source → `release_eligible=false`。契约见 [[acceptance-closure#Install Receipt]] 与 [[governance-architecture-closure]]。

## Rollback

手工回滚默认 dry-run，且在升级后又有人工修改时 fail-closed。

只有复核后的 `--force` 允许覆盖安装后的新改动。实现入口：[[engineeing-skills/rollback.py#main]]。Rollback 清理 `.smc/ges-install-receipts/` 中匹配本次事务的条目，并兼容删除旧单文件 `.smc/ges-install-receipt.json`。

## Consumer Integration

项目 validator 是 Consumer Acceptance Gate，不是 Core Package Self-Test。报告必须分层：`CORE_VALIDATION` 与 `CONSUMER_INTEGRATION_VALIDATION`。

v4.1.2 installer 仍把 NodeSkClaw 假设（`.cursor` 必须存在、固定 baseline 文件、full-tree 镜像）编进 Core 入口。v4.2.0 不再制造 `.cursor`；若 consumer 已声明 `.cursor/skills` 或 `.cursor/references`，则保留 full-tree 修复语义。

Profile 应声明 canonical/mirror roots、project validator、managed vs local skills、evidence 落点。Core installer 不应要求全树 Skill 都与 IDE mirror 一致，除非 profile 明确 `full-tree`。

## Version Axes

改版本时必须说清改的是哪一层，禁止只改一个数字掩盖 contract 变化。

| 轴 | 已接受基线 | 当前工作区 |
|---|---|---|
| Governance Baseline | `GES-BASELINE-v1.0.0` | 尚未升基线 |
| Bundle | 4.1.2 | 6.0.0 candidate |
| Pipeline contract | 4.1 | 保持 Delivery 状态机；新增 Context Package freshness 与 COE |
| Plan contract | `smc.plan.v3.3` | 新 Plan 为 `smc.plan.v4.0`；v6 运行时拒绝在途 v3.6/v3.7 |
| Plan author / validator / delivery | 3.4.0 / 1.3.0 / 1.0.1 | 扩展既有 owner；不新增 `*-v6` 并列流水线 |

PATCH 修 bug 与路径兼容；MINOR 加向后兼容能力；MAJOR 改 Frozen Invariant 或替换 canonical owner。单个 Skill 变更必须提升该 Skill SemVer，Bundle 至少 PATCH，未改动 Skill 不得机械升版。

v3.4 把 Cursor `todos[].content` 定为 Plan author 拥有的 UI 投影，`status` 仍只由 controller 写。Markdown Todo 仍是规格 SOT；缺 `content` 在 v3.3 是兼容警告，在 v3.4 是硬错误。
