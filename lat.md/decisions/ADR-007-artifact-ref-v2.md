# ADR-007 — ArtifactRef v2 Strong Identity

受源码控制的交付物使用统一 ArtifactRef v2。路径字符串存在不算证据，必须同时钉住 commit、blob SHA 与 content SHA-256。

**Status:** APPROVED

Source PRD、Stage PRD、Plan、Verification 等字段：

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

中央同步时核实 path@commit 存在、blob SHA 与 content SHA-256 匹配、PRD `APPROVED`、Plan `VALIDATED|PASS`。失败标 `DIVERGED`。校验：[[tools/artifact_verify.py#verify_artifact_ref]]。
