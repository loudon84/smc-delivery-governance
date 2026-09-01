# Contract Lifecycle

Contract 是跨仓协作的机器边界，负责 Producer / Transport / Schema / Consumer / Error / Retry / Compatibility / Release Identity。

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

## Candidate Gate

必须存在 schema、fixtures、transport semantics、error semantics、compatibility intent。

## Release Gate

必须存在 immutable version、tag/release identity、checksum/manifest、provider conformance、release evidence。

## Consume Gate

必须存在 Consumer Pin/Lock。

## Conformance Gate

Provider 与 Consumer 均需证明 schema、fixtures、runtime behaviour 与 security boundary 兼容。

Internal Contract 变化不得自动升级 Public Contract。
