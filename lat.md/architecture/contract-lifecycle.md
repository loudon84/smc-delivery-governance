# Contract Lifecycle

Contract 是跨仓协作的机器边界，负责 Producer / Transport / Schema / Consumer / Error / Retry / Compatibility / Release Identity。

状态作用在 **某个 Release version**，不是「整个合同只有一个 state」。解析入口是 [[tools/governance_lib.py#resolve_contract]]。

```text
DRAFT
 ↓
CANDIDATE
 ↓
APPROVED
 ↓
RELEASED
 ↓
CONSUMED
 ↓
CONFORMANCE_PASS
 ↓
DEPRECATED
 ↓
RETIRED
```

Gate 通过 `resolve(contract_id, required_version, consumer_repository)` 读取：

- `releases[]`：不可变 version / tag / peeled commit / state
- `consumers`：Consumer pin
- `current_release`：派生指针，不是第二事实源

完整转移表见 [[domain/state-machines#Contract]]。

## Candidate Gate

进入 CANDIDATE 后才允许 Dark Implementation。必须存在 schema、fixtures、transport semantics、error semantics、compatibility intent。

## Release Gate

进入 RELEASED 后 Consumer 才可启用真实 production call。必须存在 immutable version、tag、peeled commit、checksum/manifest、provider conformance。

## Consume Gate

CONSUMED 表示 Consumer 已把 pin/lock 钉在 canonical release 上。pin 的 tag/commit 必须与 registry release 一致。

## Conformance Gate

Provider 与 Consumer 均需证明 schema、fixtures、runtime behaviour 与 security boundary 兼容。Internal Contract 变化不得自动升级 Public Contract。Feature 不得缓存 `current_state`。
