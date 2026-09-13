# GES Install

GES 以 checksummed overlay 安装到已有 SMC skills baseline。默认 dry-run；`--apply` 才写入；失败自动回滚；永不自动 git commit。

生产安装必须校验发布包完整性。`install.py` 是稳定入口；当前工作树存在 `install_v440.py` 时派发到 4.4.0 candidate 实现，已接受生产发布仍由 `BASELINE.md` 裁决。

## Stable Entrypoint

`install.py` 保持 v4.1.2 兼容路径，优先在未设置 `GES_V440_NO_DISPATCH` 时派发到 `install_v440.py`；4.4.0 再复用 4.3.1 的事务安装器与 Consumer Profile 语义。

Windows 上禁止用 `os.execv` 派发：它不会覆盖当前控制台进程，PowerShell 会提前回到提示符，安装看起来像卡住。实现必须 `subprocess.call` 并返回子进程退出码。

## Transactional Overlay

安装事务先备份再覆盖，post-install gate 失败则恢复升级前字节。

顺序：

1. 校验 `SHA256SUMS` / `PACKAGE-MANIFEST`；
2. 确认目标已有 SMC skills baseline；
3. overlay `.agents/skills`，并按 consumer 声明同步 mirrors；
4. 写入 gitignore（`.smc/evidence|reviews|runs|backups`）；
5. 跑 delivery self-test、Roadmap tests、可选项目 validator；
6. 任一 gate 失败 → [[engineeing-skills/install_v420.py#restore]]。

实现入口：[[engineeing-skills/install_v420.py#main]]、[[engineeing-skills/install_v420.py#preflight]]。

## Rollback

手工回滚默认 dry-run，且在升级后又有人工修改时 fail-closed。

只有复核后的 `--force` 允许覆盖安装后的新改动。实现入口：[[engineeing-skills/rollback.py#main]]。

## Consumer Integration

项目 validator 是 Consumer Acceptance Gate，不是 Core Package Self-Test。报告必须分层：`CORE_VALIDATION` 与 `CONSUMER_INTEGRATION_VALIDATION`。

v4.1.2 installer 仍把 NodeSkClaw 假设（`.cursor` 必须存在、固定 baseline 文件、full-tree 镜像）编进 Core 入口。v4.2.0 不再制造 `.cursor`；若 consumer 已声明 `.cursor/skills` 或 `.cursor/references`，则保留 full-tree 修复语义。

Profile 应声明 canonical/mirror roots、project validator、managed vs local skills、evidence 落点。Core installer 不应要求全树 Skill 都与 IDE mirror 一致，除非 profile 明确 `full-tree`。

## Version Axes

改版本时必须说清改的是哪一层，禁止只改一个数字掩盖 contract 变化。

| 轴 | 已接受基线 | 当前工作区 |
|---|---|---|
| Governance Baseline | `GES-BASELINE-v1.0.0` | 尚未升基线 |
| Bundle | 4.1.2 | 4.4.0 candidate |
| Pipeline contract | 4.1 | 4.3.1 + scoped workspace / acceptance / Test Asset Contract；4.4 增加成本优化运行时 |
| Plan contract | `smc.plan.v3.3` | 新 Plan 为 `smc.plan.v3.6`；v3.3–v3.5 可读 |
| Plan author / validator / delivery | 3.4.0 / 1.3.0 / 1.0.1 | 3.7.0 / 1.6.0 / 1.3.0 |

PATCH 修 bug 与路径兼容；MINOR 加向后兼容能力；MAJOR 改 Frozen Invariant 或替换 canonical owner。单个 Skill 变更必须提升该 Skill SemVer，Bundle 至少 PATCH，未改动 Skill 不得机械升版。

v3.4 把 Cursor `todos[].content` 定为 Plan author 拥有的 UI 投影，`status` 仍只由 controller 写。Markdown Todo 仍是规格 SOT；缺 `content` 在 v3.3 是兼容警告，在 v3.4 是硬错误。
