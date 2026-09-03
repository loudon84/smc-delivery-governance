# State Machines

跨仓 Feature、合同 Release、Work Package、Roadmap、Integration 与仓库治理状态由中央统一管理。项目 Receipt 不能直接写 DONE。

合法转移表在 `contracts/lifecycle/states.yaml`。推进入口：[[tools/transition_state.py#main]]、[[tools/reconcile_states.py#tx]]。决策见 [[ADR-002-state-machines]]。

## Feature

Feature 从提案走到完成，中间被架构、实现与集成闸门卡住。DONE 要求全部 Work Package 已 VERIFIED/DONE，且 IntegrationRun PASS。

```text
PROPOSED → ARCHITECTURE → PLANNED → IMPLEMENTING → INTEGRATING → VERIFYING → DONE
```

`BLOCKED` / `CANCELLED` 是显式退出，不是默认成功。门禁：[[tools/state_machine.py#feature_gate]]。

## Work Package

Work Package 描述单个仓库的本地交付进度。Consumer 的 VERIFIED 只认中央 Acceptance Attestation；Provider 认合同 release 证据。

```text
BACKLOG → READY → IN_PRD → PLANNED → IMPLEMENTING → REVIEW → VERIFIED → DONE
```

进入 PLANNED 及之后要求 `sync_state == SYNCED`。门禁：[[tools/state_machine.py#work_package_gate]]。

## Contract

合同状态作用在某个 Release version。CANDIDATE 允许 Dark Implementation；RELEASED 之后才允许生产调用。

```text
DRAFT → CANDIDATE → APPROVED → RELEASED → CONSUMED → CONFORMANCE_PASS → DEPRECATED → RETIRED
```

Reconciler 按 Provider VERIFIED → RELEASED、Consumer pin → CONSUMED、双方 VERIFIED → CONFORMANCE_PASS 派生。门禁：[[tools/state_machine.py#contract_gate]]。

## Integration

跨仓集成状态表示「能不能跑」以及「跑的结果」。PASS 是终态，只能由不可变 IntegrationRun 证明。

```text
WAITING_PROVIDER → WAITING_CONSUMER → READY → RUNNING → PASS
```

`FAIL` 可回到 READY/RUNNING；空 `history.yaml` 保持等待事实，不等于 PASS。

## Roadmap Item

全局路线图项把 Feature 拆成可退出的里程碑。DONE 必须满足机器可解析的 exit 条件（合同/WP/集成）。

```text
PLANNED → ACTIVE → DONE
```

门禁：[[tools/state_machine.py#roadmap_item_gate]]。

## Repository

仓库治理状态描述纳管深度，而不是某个 Feature 的进度。OUT_OF_SYNC 表示 pin 或 Receipt 漂移。

```text
REGISTERED → BOOTSTRAPPED → SYNCED → ENFORCED
                         ↘ OUT_OF_SYNC
```

见 [[architecture/project-onboarding]]。

## Reconcile Order

自动推进必须按依赖方向进行，避免 Feature 先 DONE、合同仍是 APPROVED。

```text
Contract release → Work Package → Roadmap Item → Feature → IntegrationRun
```

所有 BLOCKED 必须包含机器可解析的 `blocked_by`（type / id / required_state / current_state）。
