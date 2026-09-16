# CHANGES — GES v5.0.7 Frontend Context Scoped Install

基线：v5.0.6。权威 PRD：`docs/prd/PRD-GES-v5.0.7-Frontend-Context-Scoped-Install.md`。

## Change Matrix

| ID | Component | Summary |
|---|---|---|
| C21 | Frontend App Registry | Schema v2：`repository` + `baseline_status`；v1 兼容读 |
| C22 | Shared UI Discovery | `packages/` 下最多 3 层嵌套（如 `packages/shared/ui`） |
| C23 | Scoped Install | `frontend_audit.py --app`：归一、幂等、兄弟保留、fail-closed |
| C24 | Application Boundary | `app-profile.json` v2 `boundary`；扫描受 allowed/forbidden 约束 |
| C25 | Frontend Runtime Delivery | installer 安装 `frontend-runtime/` 与 `frontend-adapters/` |
| C26 | Feature Scope Pipeline | `resolve_feature_scope()` → `smc.ges.feature-scope.v1` |
| C27 | Consumer Validation | 只检 INITIALIZED；取消包路径回退；Boundary/Runtime 检查 |
| C28 | Acceptance | G43–G50；报告 golden=`G01-G50` |
| C29 | Install Identity Probe | 文件系统探针 lock/receipt；区分 bundle vs feature slice；校准门槛 |
| C30 | Baseline Scan Hygiene | 排除 out/dist/references；按 adapter glob 收紧 component-registry；surface 仅 UI 后缀；修复 `unavailable` 误匹配 `nav` |


## Frozen decisions

- 不重命名 `apps-registry.json` / `apps/<app-id>/` / `ui-baseline.json`
- installer 不写入 `.agents/ges/frontend/` 数据目录
- bootstrap 不写入 `frontend-runtime/` / `frontend-adapters/`
- `bundle` 保持 `5.0.0`；5.0.7 为 feature slice，不是 lock.bundle

## Verification

```text
python tests/test_context_engine.py -v
python tests/test_install_identity_probe.py -v
python acceptance/run_acceptance.py          # G01-G50
python build_package_manifest.py
lat check
```
