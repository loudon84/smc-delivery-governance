# ADR-007 — ArtifactRef v2 Strong Identity

**Status:** APPROVED

Source PRD、Stage PRD、Plan、Verification 等受源码控制的交付物，使用统一 ArtifactRef v2：

```text
repository_id
path
commit          # 完整 40-char SHA
blob_sha
sha256
artifact_type
artifact_id
status
source_revision
```

中央同步时核实 path@commit 存在、blob SHA 与 content SHA-256 匹配、PRD `APPROVED`、Plan `VALIDATED|PASS`。失败标 `DIVERGED`，不得把「路径字符串存在」当成证据。
