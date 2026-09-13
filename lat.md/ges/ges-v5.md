# GES 5 Upgrade

v5 repaired candidate 在唯一 PRD、Plan 和 Delivery 状态机内增加治理深度与执行证据门禁，不改变已接受生产基线或替用户完成业务验收。

## Complete Package Inventory

升级包清单必须覆盖实际 payload 全集及原始清单全部路径；丢失文件的重建不能冒充历史字节恢复。

升级包保留 ORIGINAL-MANIFEST.json 作为来源记录；新 manifest 与 SHA256SUMS 绑定修复后字节。合并后的完整包由 [[engineeing-skills/build_package_manifest.py#inventory]] 建立闭合集合，拒绝缺失、额外或被修改文件。仓库升级锁定基线并备份所有触及文件，验证失败自动恢复；与 Consumer 安装回滚分开。

## Compatibility Chain

新 v3.7 串通 seed、项目 wrapper、静态校验、Test Asset、Cursor 投影及最终完成门禁；在途 v3.6 不被批量改写。

[[engineeing-skills/.agents/skills/smc-plan-validator/scripts/validate_plan_v33.py#transform_to_v32]] 为受支持合同适配 Consumer 自有 legacy validator，不能绕过该 validator。[[engineeing-skills/install_v500.py#resolve_profile]] 和 [[engineeing-skills/install_v500.py#pack_context]] 保留隐式更新时已安装的 v2/v1 策略。v3.7 seed 要求显式采用 Profile v3；尚未迁移的消费者可以继续调用 v3.6 seed。

## Engineering Freshness

v3.7 TDD 按实际命令、Plan 语义、不可复活的 method epoch 与当前写入范围判定新鲜度；声明性 PASS 不能替代执行证据。

[[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/engineering_method.py#tdd_check]] 要求同命令 RED/GREEN、有命令 receipt，最新通过的范围指纹必须匹配当前源码及测试。debug 根因关联较早的失败复现，根因前修复或缺少新鲜 VERIFIED 均阻断。[[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/plan_state.py#set_status]] 和 [[engineeing-skills/.agents/skills/smc-plan-delivery/scripts/validate_delivery_completion.py#validate]] 同时接入门禁。receipt 是本地审计数据，不是密码学远端证明；预期失败原因仍需审查确认。

## Review Closure

非 PASS 审查结论即使因 Plan 修改变旧也保持阻断；增量审查只能引用确实属于上次 PASS 的快照。

[[engineeing-skills/.agents/skills/smc-plan-review/scripts/build_review_packet.py#accept]] 记录 snapshot 字节摘要、Plan 摘要及 review record 摘要。[[engineeing-skills/.agents/skills/smc-plan-review/scripts/build_review_packet.py#build]] 拒绝借空 diff 或伪造快照把 DELTA 降为 NONE；缺绑定升级 FULL。

## Verification Boundary

包测试证明治理运行时和安装事务，不证明具体 Consumer 的业务正确性、线上部署或 LIVE 验收。

[[engineeing-skills/validate_package_v500.py#main]] 运行继承回归、v5 方法及领域校验、fixture 安装和回滚。包集成中的 legacy validator 替身只验证适配协议；真实 Consumer 仍保留并执行其自有 validator。测试资产复用与证据复用严格区分，源码变更后不得复用旧 PASS。

## Acceptance Hardening Slice

v5.0.1 Hardening lands routing trust, structured risk, domain semantics, install-lock.v2, telemetry hooks, CI package gate, and acceptance tooling.

See [[acceptance-hardening]] and `engineeing-skills/CHANGES-v5.0.1.md`. Bundle SemVer and Baseline promotion remain Release Review decisions; Candidate evidence must not claim cost optimization until Benchmark thresholds pass.
