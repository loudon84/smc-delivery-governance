---
name: smc-program-roadmap
version: 1.0.0
description: 管理跨 Feature / Repository 的 Global Roadmap DAG，并把 Repo Work Package 作为叶子交付单元。
---
# SMC Program Roadmap

Global Roadmap 只保存 Outcome、Depends On、Required Contract State、Required Work Package State、Integration Exit，不保存 local Todo。

Global Item DONE 必须证明 required Work Packages >= VERIFIED、required Contracts 达到成熟度，必要时 Integration Gate PASS。
