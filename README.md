# SMC Delivery Governance v1.2.1

`smc-delivery-governance` 是 SMC 内部多仓库、多团队研发的 **Engineering Delivery Control Plane**。

Git YAML 保存 **Current Materialized State**；`audit/transitions/` 保存 **Lifecycle Audit Facts**。

## 1. 边界

```text
Central Governance
  Why / Global Boundary / Global Outcome / Contract / Dependency / Evidence / State

Local Repository
  Local LAT / Stage PRD / Plan / Source Code / Unit Tests / Release
```

中央仓库不是业务代码仓库，也不是“超级 PRD 仓库”。

## 2. v1.1 解决的问题

### 2.1 新项目统一纳管

```text
REGISTERED → BOOTSTRAPPED → SYNCED → ENFORCED
                         ↘ OUT_OF_SYNC
```

注册：

```bash
python tools/project_onboard.py \
  --project-id PROJECT-DEMO \
  --project-name "Demo" \
  --repository-id REPO-DEMO \
  --repo loudon84/demo \
  --branch main \
  --team TEAM-WORK-PLATFORM \
  --apply
```

向本地仓库安装治理 Kit：

```bash
python tools/governance_sync.py \
  --repo /path/to/demo \
  --project PROJECT-DEMO \
  --feature FEAT-XXX \
  --with-ci \
  --apply
```

项目获得：

```text
.agents/governance/
├─ binding.yaml
├─ project-status.yaml
├─ skills/
├─ work-packages/
├─ contracts/
├─ receipts/
├─ acceptance/
├─ schemas/
└─ tools/

.agents/governance.lock
.github/workflows/smc-governance.yml
.github/workflows/smc-governance-labels.yml
```

### 2.2 一个 Source PRD 关联多个项目

中央 Feature 显式 pin：

```text
source_prd
source_revision
participants
Global Change IDs
Repo Work Packages
Contract dependencies
```

创建 Feature Skeleton：

```bash
python tools/create_feature.py \
  --feature-id FEAT-EXAMPLE-001 \
  --title "Example Cross Repo Feature" \
  --program-id PROGRAM-AGENT-PLATFORM \
  --source-prd-id PRD-EXAMPLE-v1.0 \
  --source-prd-repo REPO-SMC-COPILOT \
  --source-prd-path docs/example/PRD.md \
  --source-prd-ref main \
  --source-revision PRD-EXAMPLE@1.0 \
  --feature-owner TEAM-AGENT-PLATFORM \
  --integration-owner TEAM-WORK-PLATFORM \
  --participant REPO-NODESKCLAW:provider \
  --participant REPO-SMC-COPILOT:consumer \
  --change XR-C01:PublicContract \
  --change XR-C02:ConsumerIntegration \
  --apply
```

Repo Work Package 用相同 `source_revision`，项目 Receipt 回报同一 revision。若发生漂移，中央标记：

```text
STALE_FEATURE
STALE_CONTRACT
MISSING_RECEIPT
DIVERGED
```

而不是让两个项目继续异步实现。

### 2.3 PRD Acceptance Test

项目本地：

```text
APPROVED Stage PRD
→ Acceptance Manifest
→ unit/contract/static/integration command
→ Acceptance Report
→ Delivery Receipt
```

执行：

```bash
python .agents/governance/skills/smc-prd-acceptance/scripts/run_acceptance.py \
  .agents/governance/acceptance/WP-XXX.yaml \
  --repo . \
  --output .agents/governance/acceptance/WP-XXX.report.json
```

中央验证：

```bash
python tools/acceptance_gate.py \
  --manifest <manifest.yaml> \
  --report <report.json> \
  --work-package WP-XXX
```

中央不执行其他仓库任意测试命令，只验证项目 CI 产生的不可歧义 Evidence。

### 2.4 Stage PRD / Issue / Bug / Plan / Commit Traceability

标准链：

```text
Source PRD
→ Global Change ID
→ Repo Work Package
→ Stage PRD
→ Issue / Bug
→ Plan
→ Pull Request
→ Git Commit
→ Acceptance Report
→ Integration Evidence
```

项目 Commit 推荐：

```text
feat(...): ...

SMC-Feature: FEAT-XXX
SMC-Work-Package: WP-XXX
SMC-PRD: PRD-XXX
SMC-Plan: .cursor/plans/xxx.plan.md
```

GitHub Issue/PR 自动使用：

```text
gov:feature:<FEATURE_ID>
gov:wp:<WORK_PACKAGE_ID>
gov:type:bug|task|feature
```

中央同步：

```bash
python tools/sync_repo_state.py FEAT-XXX \
  --discover-github \
  --apply
```

查看链路：

```bash
python tools/delivery_trace.py FEAT-XXX
```

## 3. Delivery Receipt

每个项目、每个 Work Package 一个机器摘要：

```text
.agents/governance/receipts/<WORK_PACKAGE_ID>.yaml
```

Receipt 记录：

```text
source_revision
local status
Stage PRDs
Issues
Bugs
Plans
PRs
Commits
Acceptance
Evidence refs
```

Remote Receipt **不能直接写中央 DONE**。`sync_repo_state.py` 只更新 observed facts；中央状态必须由 State Machine/Reconciler 推进。

## 4. 中央状态机

### Feature

```text
PROPOSED → ARCHITECTURE → PLANNED → IMPLEMENTING → INTEGRATING → VERIFYING → DONE
```

### Contract

```text
DRAFT → CANDIDATE → APPROVED → RELEASED → CONSUMED → CONFORMANCE_PASS
```

### Work Package

```text
BACKLOG → READY → IN_PRD → PLANNED → IMPLEMENTING → REVIEW → VERIFIED → DONE
```

### Integration

```text
WAITING_PROVIDER → WAITING_CONSUMER → READY → RUNNING → PASS
```

显式状态迁移：

```bash
python tools/transition_state.py \
  --entity work_package \
  --id WP-XXX \
  --to VERIFIED \
  --apply
```

自动 reconciliation：

```bash
python tools/reconcile_states.py FEAT-XXX --apply
python tools/reconcile_project_status.py
```

`VERIFIED` 至少要求：

```text
sync_state == SYNCED
Stage PRD exists
Plan exists
implementation commit exists
Acceptance PASS
```

## 5. GitHub Automation

中央仓库：

```text
.github/workflows/governance-ci.yml
.github/workflows/sync-project-status.yml
```

`sync-project-status.yml` 每小时：

```text
project bootstrap sync
→ Receipt pull
→ Issue/Bug/PR discovery
→ delivery-ledger update
→ state reconciliation
→ registry/feature validation
→ bot commit observed state
```

访问私有内部仓库时，复制 `.env.example` 为 `.env` 并填写：

```text
SMC_GOVERNANCE_GITHUB_TOKEN
SMC_GOVERNANCE_DISPATCH_TOKEN
```

`tools/governance_lib.py` 会在启动时读取仓库根目录 `.env`。已存在的进程环境变量优先，GitHub Actions secrets 仍然是 CI 的权威来源。`.env` 不得提交。

长期建议改用 SMC GitHub App，给中央治理仓库只读业务仓库元数据/Contents 权限，避免共享 PAT。

## 6. 项目状态

```bash
python tools/project_status.py
python tools/program_status.py agent-platform
python tools/contract_status.py
python tools/dependency_status.py FEAT-SKILL-FIRST-001
python tools/integration_gate.py FEAT-SKILL-FIRST-001
```

## 7. 校验

```bash
python -m pip install -e . pytest
python tools/validate_registry.py
python tools/validate_feature.py features/FEAT-SKILL-FIRST-001
pytest -q
```

## 8. 核心目录

```text
registry/          Project / Repository / Team / Contract / Policy
programs/          Program-level roadmap
features/          Cross-repo Feature SOT
contracts/         Lifecycle policy
integration/       Cross-end scenarios/evidence
skills/            Universal + Cross-repo governance skills
tools/             State/sync/onboarding/acceptance/trace automation
schemas/           Machine contracts
.github/workflows/ Central CI + scheduled state synchronization
templates/project/ Project bootstrap GitHub/validation templates
```

## 9. 冻结原则

> Central Governance 到 Interface；Local Repository 到 Implementation。

> Source PRD revision、Contract release、Repo Work Package、Acceptance Evidence 和 Integration Result 必须可机器追踪。

> 项目仓库只能上报 observed facts；全局状态由中央状态机统一裁决。
