# Contract Lifecycle

Contract 是跨仓协作的机器边界，负责 Producer / Transport / Schema / Consumer / Error / Retry / Compatibility / Release Identity。

状态作用在 **某个 Release version**，不是「整个合同只有一个 state」。

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

## Candidate Gate

必须存在 schema、fixtures、transport semantics、error semantics、compatibility intent。

## Release Gate

必须存在 immutable version、tag/release identity、checksum/manifest、provider conformance、release evidence。

## Consume Gate

必须存在 Consumer Pin/Lock，且 pin 的 tag/commit 与 canonical release 一致。

## Conformance Gate

Provider 与 Consumer 均需证明 schema、fixtures、runtime behaviour 与 security boundary 兼容。

Internal Contract 变化不得自动升级 Public Contract。Feature 不得缓存 `current_state`。
