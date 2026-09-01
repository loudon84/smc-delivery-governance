# SMC Delivery Governance v1.2.1 — Closed Loop v1 Closure Patch

本包**不是完整仓库**。目录结构与 `loudon84/smc-delivery-governance` 根目录一致，只包含 v1.2.1 Closure 需要新增或替换的文件。

目标：

```text
Engineering Delivery Control Plane
Closed Loop v1
```

对应 P0：

1. Test Isolation，清除 Sample 对中央 SOT 的污染
2. NodeSKClaw / SMC Copilot 真正 Bootstrap + Receipt
3. Governance Kit canonical immutable release
4. ArtifactRef v2 强身份与 semantic verification
5. Source PRD 升级 ArtifactRef
6. Acceptance Artifact + GitHub Actions Attestation
7. Sync exit-code / fail-fast
8. Contract + IntegrationRun Full Reconciler
9. Integration Workflow + immutable IntegrationRun history
10. Audit / Materialized State transaction + invariant check

## 合并顺序

### A. 将本包文件覆盖到仓库根目录

本包没有删除任何业务目录。覆盖前建议创建分支：

```bash
git checkout -b governance/v1.2.1-closure
```

### B. 清除 v1.2 测试 Sample 污染

先 dry-run：

```bash
python tools/cleanup_sample_sot.py FEAT-SKILL-FIRST-001
```

确认后：

```bash
python tools/cleanup_sample_sot.py FEAT-SKILL-FIRST-001 --apply
```

### C. 将 Source PRD 升级为强 ArtifactRef

当前 Skill-first 示例：

```bash
python tools/upgrade_source_prd_artifact.py \
  FEAT-SKILL-FIRST-001 \
  --ref work/prd-v4.0 \
  --apply
```

该工具会从 Registry 找到 Source PRD Repository，解析 Git commit、Git blob SHA 和内容 SHA-256，并移除 Feature 中冗余的 Contract `current_state`。

### D. 测试

```bash
python -m pip install -e . pytest
pytest -q
python tools/validate_registry.py
python tools/validate_feature.py features/FEAT-SKILL-FIRST-001
python tools/verify_state_invariants.py
git diff --exit-code
```

最后一条用于证明测试不会写入中央 SOT。

### E. 提交 Closure 代码并发布 Governance Kit

```bash
git add .
git commit -m "feat(governance): close trusted delivery loop v1.2.1"

git tag -a governance-kit-v1.2.1 -m "SMC Governance Kit v1.2.1"
git push origin HEAD
git push origin governance-kit-v1.2.1
```

`release-governance-kit.yml` 会从 Tag Checkout 构建 canonical Bundle 并发布：

```text
governance-kit-v1.2.1.tar.gz
```

Bundle 内：

```text
manifest.json
SHA256SUMS
skills/
schemas/
tools/
github/
```

`SHA256SUMS` 覆盖 `manifest.json` 和全部 Kit 文件，只排除自身。

### F. Bootstrap 两个真实项目

在中央仓库本地 clone 上先获取 canonical Kit：

```bash
python tools/fetch_governance_kit.py --version 1.2.1
```

然后：

```bash
python tools/governance_sync.py \
  --repo <nodeskclaw-local-clone> \
  --project PROJECT-NODESKCLAW \
  --feature FEAT-SKILL-FIRST-001 \
  --with-ci \
  --apply

python tools/governance_sync.py \
  --repo <smc-copilot-local-clone> \
  --project PROJECT-SMC-COPILOT \
  --feature FEAT-SKILL-FIRST-001 \
  --with-ci \
  --apply
```

提交两个业务仓库的：

```text
.agents/governance/**
.agents/governance.lock
.github/workflows/smc-governance*.yml
```

中央验证：

```bash
python tools/verify_remote_bootstrap.py REPO-NODESKCLAW FEAT-SKILL-FIRST-001
python tools/verify_remote_bootstrap.py REPO-SMC-COPILOT FEAT-SKILL-FIRST-001
```

### G. 配置 Secrets

业务项目：

```text
SMC_GOVERNANCE_DISPATCH_TOKEN
```

中央仓库：

```text
SMC_GOVERNANCE_GITHUB_TOKEN
```

长期仍建议使用 GitHub App 替代共享 PAT。

## IntegrationRun

v1.2.1 不允许“看到一个成功 Workflow 就算 E2E PASS”。

每个 Integration Scenario 必须配置受审查的 runner：

```yaml
runner:
  command: python integration/runners/skill_first.py
  timeout_seconds: 1800
```

中央：

```bash
gh workflow run integration-run.yml \
  -f feature_id=FEAT-SKILL-FIRST-001
```

每次运行都会生成新的：

```text
integration/runs/<SCENARIO_ID>/<INTEGRATION_RUN_ID>.yaml
```

历史不可覆盖。
