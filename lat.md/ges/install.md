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
2. 确认目标已有 SMC skills baseline；
3. overlay `.agents/skills`，并按 consumer 声明同步 mirrors；
4. 写入 gitignore（`.smc/evidence|reviews|runs|backups`）；
5. 跑 delivery self-test、Roadmap tests、可选项目 validator；
6. 任一 gate 失败 → [[engineeing-skills/install_v430.py#restore]]。

实现入口：[[engineeing-skills/install_v500.py#main]]、[[engineeing-skills/install_v500.py#preflight]]。省略 profile 选择时保留已安装元数据；显式迁移 profile 需要重新绑定受影响 Plan。

## Install Lock v2

Hardening 后的 install lock 证明 package bytes 身份，并安全清理未修改的 stale package-owned 文件。

见 [[acceptance-hardening#Install Lock v2]]：`smc.ges.install-lock.v2` 含 `release_identity` 与 `owned_files`；v1 lock 跳过破坏性清理。Closure 起 `package_manifest_sha256` 必须是 PACKAGE-MANIFEST **raw bytes** digest，lock 不再绑定 PENDING `transaction_manifest_sha256`（改由 receipt 绑定最终 PASS），见 [[acceptance-closure#Canonical Digests]]。

## Install Receipt

PASS 之后写入 `smc.ges.install-receipt.v1`，把最终 lock 与 PASS transaction 钉死，且不进入 transaction manifest 哈希以免循环。

[[engineeing-skills/install_v500.py#write_install_receipt]] 仅在 transaction status=`PASS` 后落 `.smc/ges-install-receipt.json`。契约见 [[acceptance-closure#Install Receipt]]。

## Rollback

手工回滚默认 dry-run，且在升级后又有人工修改时 fail-closed。

只有复核后的 `--force` 允许覆盖安装后的新改动。实现入口：[[engineeing-skills/rollback.py#main]]。当 transaction hash 与 receipt 匹配时，rollback 必须显式删除 `.smc/ges-install-receipt.json`，避免 receipt 残留冒充仍已安装。

## Consumer Integration

项目 validator 是 Consumer Acceptance Gate，不是 Core Package Self-Test。报告必须分层：`CORE_VALIDATION` 与 `CONSUMER_INTEGRATION_VALIDATION`。

v4.1.2 installer 仍把 NodeSkClaw 假设（`.cursor` 必须存在、固定 baseline 文件、full-tree 镜像）编进 Core 入口。v4.2.0 不再制造 `.cursor`；若 consumer 已声明 `.cursor/skills` 或 `.cursor/references`，则保留 full-tree 修复语义。

Profile 应声明 canonical/mirror roots、project validator、managed vs local skills、evidence 落点。Core installer 不应要求全树 Skill 都与 IDE mirror 一致，除非 profile 明确 `full-tree`。

## Version Axes

改版本时必须说清改的是哪一层，禁止只改一个数字掩盖 contract 变化。

| 轴 | 已接受基线 | 当前工作区 |
|---|---|---|
| Governance Baseline | `GES-BASELINE-v1.0.0` | 尚未升基线 |
| Bundle | 4.1.2 | 5.0.0 repaired candidate |
| Pipeline contract | 4.1 | 保持 Delivery 状态机，新增 Domain preplan 与 Engineering Method v2 门禁 |
| Plan contract | `smc.plan.v3.3` | 新 Plan 为 `smc.plan.v3.7`；在途 v3.6 保持原合同，旧 validator 仍可调用 |
| Plan author / validator / delivery | 3.4.0 / 1.3.0 / 1.0.1 | 4.0.0 / 2.0.0 / 1.5.0 |

PATCH 修 bug 与路径兼容；MINOR 加向后兼容能力；MAJOR 改 Frozen Invariant 或替换 canonical owner。单个 Skill 变更必须提升该 Skill SemVer，Bundle 至少 PATCH，未改动 Skill 不得机械升版。

v3.4 把 Cursor `todos[].content` 定为 Plan author 拥有的 UI 投影，`status` 仍只由 controller 写。Markdown Todo 仍是规格 SOT；缺 `content` 在 v3.3 是兼容警告，在 v3.4 是硬错误。
