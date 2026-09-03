# Governance Engineering Skills — Maintainer Guide

## 1. 日常职责

Maintainer 负责的是工程治理 contract，不只是 Markdown Skill 文案。

每次审查优先问：

1. 谁拥有 canonical state？
2. 是否出现第二 writer / second owner？
3. static、semantic、execution、proof 是否仍分层？
4. failure 是否 fail-closed？
5. old evidence 是否会在代码变化后错误保持 fresh？
6. consumer-specific 假设是否泄漏进 Core？
7. 版本是否按影响正确提升？
8. 是否有真实 regression test？

## 2. 推荐变更模板

```text
Problem:
Root Cause:
Layer:
Affected Skills:
Affected Contracts:
Frozen Invariant Impact: NONE / YES
Consumer Impact:
Migration:
Rollback:
Tests:
Version Change:
```

## 3. Bug Fix 纪律

Bug fix 不接受“只让当前报错消失”。

必须判断：

```text
local symptom
  -> shared abstraction defect?
  -> same pattern elsewhere?
  -> regression test at abstraction boundary
```

Windows 8.3 path incident 即为参考：正确修复点是共享 filesystem identity abstraction，而不是只在一个 `relative_to()` 调用点 catch exception。

## 4. Consumer 问题分类

收到业务项目安装失败时，先分类：

```text
PACKAGE_INTEGRITY
CORE_RUNTIME
CORE_CONTRACT
CONSUMER_PREFLIGHT
CONSUMER_MIRROR
CONSUMER_VALIDATOR
PROJECT_BASELINE_DRIFT
```

分类后再决定改 Core 还是改 consumer profile，避免把项目特例写进中央 runtime。

## 5. 不允许的维护模式

- 在 consumer 项目直接改 Skill 并长期不回中央；
- 一次 PR 顺便改多个 unrelated Skill；
- validator 报错就默认 skip；
- 为了 tests PASS 降低 gate 强度；
- 把 generated evidence 当 source；
- 修改已发布版本内容但不升版；
- 依赖 Cursor Todo completed 直接写 Roadmap DONE。
