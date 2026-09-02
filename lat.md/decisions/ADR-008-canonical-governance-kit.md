# ADR-008 — Canonical Governance Kit Release

**Status:** APPROVED

Governance Kit 是不可变 Release，不是当前 HEAD 的文件拷贝。生产 pin：

```text
version
tag                 # governance-kit-vX.Y.Z
commit              # peeled commit
manifest_sha256
```

`SHA256SUMS` 覆盖 `manifest.json` 与全部 Kit 文件。生产 `governance_sync` 只安装已验证 Bundle；开发用 source-tree 必须显式 `--allow-source-tree`。
