# GES Enterprise Engineering Governance Platform PRD v6.0.0

## 增强版：加入 GES Context Optimization Engine

版本：v6.0.0\
文档类型：企业级 Agent Coding 工程治理平台 PRD

------------------------------------------------------------------------

# 1. 产品定位

GES（Governance Engineering System）不是代码生成工具，而是面向企业 Agent
Coding 的工程治理平台。

目标：

让 AI Agent
像人工研发团队一样，在明确的架构、项目、模块、组件责任边界内完成软件交付。

核心模型：

    Architecture
          |
    Project
          |
    Module
          |
    Component
          |
    Application

------------------------------------------------------------------------

# 2. 背景问题

企业研发逐渐采用：

-   Monorepo
-   多产品
-   多模块
-   多团队
-   多 Agent 协作

传统 Agent Coding 模式：

    Task
     |
    Agent
     |
    Whole Repository
     |
    Code Change

存在：

-   Context 过载
-   Token 浪费
-   Agent 越界修改
-   Review 无法定位责任
-   多项目协作困难

因此 GES v6 引入：

## GES Context Optimization Engine

作为 Agent 与代码库之间的智能上下文控制层。

------------------------------------------------------------------------

# 3. GES v6 总体架构

                        GES Platform

    +--------------------------------+

    Architecture Governance Layer

    +--------------------------------+

    Project Governance Layer

    +--------------------------------+

    Module Governance Layer

    +--------------------------------+

    Component Governance Layer

    +--------------------------------+

    Context Optimization Engine

    +--------------------------------+

    Agent Workflow Engine

    +--------------------------------+

    Repository

------------------------------------------------------------------------

# 4. 核心组件设计

# 4.1 Architecture Governance

职责：

-   系统架构定义
-   技术约束
-   数据流约束
-   服务依赖关系

资产：

    architecture.yaml

------------------------------------------------------------------------

# 4.2 Project Governance

定义：

-   产品边界
-   生命周期
-   Owner
-   发布策略

示例：

    copilot-work

    copilot-knowledge

    autotask

------------------------------------------------------------------------

# 4.3 Module Governance

Module 是 GES 最核心治理单元。

Module 定义：

-   业务责任
-   代码范围
-   Owner
-   依赖关系
-   Contract

示例：

``` yaml
module:

 id: knowledge

owner:
 team: knowledge-team

boundary:

 include:
   - apps/knowledge/**

 exclude:
   - apps/work/**
```

------------------------------------------------------------------------

# 4.4 Component Governance

组件级管理：

例如：

    Knowledge Module

     |
     +-- DocumentUpload
     |
     +-- SearchPanel
     |
     +-- PreviewComponent

------------------------------------------------------------------------

# 5. GES Context Optimization Engine

## 5.1 产品目标

解决：

> Agent 需要多少上下文，而不是给 Agent 所有上下文。

核心原则：

最小必要上下文（Minimum Required Context）。

------------------------------------------------------------------------

# 5.2 核心职责

## 1. 判断任务范围

输入：

    User Requirement

分析：

-   修改类型
-   影响范围
-   风险等级

输出：

    Component Task

    Module Task

    Project Task

    Architecture Task

------------------------------------------------------------------------

## 2. 选择治理层级

任务分类：

  类型       加载级别
  ---------- --------------
  Bug修复    Component
  小功能     Module
  跨模块     Project
  架构调整   Architecture

------------------------------------------------------------------------

## 3. 控制 Token Budget

根据任务自动控制：

    Task

    ↓

    Risk Assessment

    ↓

    Context Budget

    ↓

    Context Selection

示例：

小修改：

    Component Context

    10k tokens

大型改造：

    Architecture Context

    200k+ tokens

------------------------------------------------------------------------

## 4. 防止过度分析

禁止：

    修改按钮颜色

    ↓

    扫描整个Monorepo

采用：

    Task

    ↓

    Resolver

    ↓

    Relevant Context

    ↓

    Agent

------------------------------------------------------------------------

# 6. Context Resolver 架构

    Task Analyzer

          |

    Scope Resolver

          |

    Module Resolver

          |

    Dependency Graph

          |

    Context Compiler

          |

    LLM Prompt Context

------------------------------------------------------------------------

# 7. Context 数据来源

来源：

    Architecture Spec

    Project Spec

    Module Spec

    Component Spec

    Code Symbol Graph

    Dependency Graph

    Historical Review

------------------------------------------------------------------------

# 8. Dependency Graph Engine

能力：

-   分析模块依赖
-   判断影响范围
-   触发 Review

例如：

修改：

    packages/sdk/auth.ts

分析：

    work

    knowledge

    autotask

全部受影响。

------------------------------------------------------------------------

# 9. Agent Workflow

升级流程：

    Requirement

    ↓

    Context Optimization Engine

    ↓

    Architecture Analysis

    ↓

    Module Resolution

    ↓

    Component Impact Analysis

    ↓

    Plan

    ↓

    Execute

    ↓

    Module Review

    ↓

    Integration Review

    ↓

    Release

------------------------------------------------------------------------

# 10. Agent Role 模型

    Architecture Agent

            |

    Project Agent

            |

    Module Owner Agent

            |

    Developer Agent

            |

    QA Agent

            |

    Release Agent

------------------------------------------------------------------------

# 11. Task Schema

``` yaml
task:

 id:
   KNOW-001

 project:
   copilot

 module:
   knowledge

 component:
   preview

 risk:
   medium

 context_budget:
   50000
```

------------------------------------------------------------------------

# 12. Review Governance

## Module Review

检查：

-   边界
-   Contract
-   代码质量

## Integration Review

检查：

-   公共依赖
-   API变化

## Architecture Review

检查：

-   架构一致性
-   长期影响

------------------------------------------------------------------------

# 13. Skill 体系升级

原：

    smc-prd

    smc-plan

    smc-execute

    smc-review

升级：

    smc-context-analysis

    smc-module-discovery

    smc-plan-v6

    smc-execute-v6

    smc-impact-review

    smc-release-review

------------------------------------------------------------------------

# 14. 成本控制模型

## Token 成本目标

  场景           目标Token
  ------------ -----------
  组件修改          5k-20k
  模块功能         30k-80k
  跨模块修改      80k-200k
  架构调整           200k+

------------------------------------------------------------------------

# 15. 与现有平台集成

    Multica

       |

    GES

       |

    Hermes Agent

       |

    Cursor Agent CLI

       |

    Git Repository

职责：

Multica：

项目状态管理

GES：

工程治理

Hermes：

Agent执行

Cursor：

代码生成

------------------------------------------------------------------------

# 16. 实施路线

## Phase 1

Context Registry

交付：

-   architecture.yaml
-   project.yaml
-   module.yaml

## Phase 2

Context Optimization Engine

交付：

-   Task Analyzer
-   Context Resolver
-   Budget Manager

## Phase 3

Impact Analysis

交付：

-   Dependency Graph
-   Change Analyzer

## Phase 4

Multi Agent Organization

交付：

-   Module Agent
-   Review Agent
-   QA Agent

------------------------------------------------------------------------

# 17. 最终目标

GES v6：

不是：

    AI 自动写代码

而是：

    AI 软件工程组织治理平台

最终实现：

    Human Engineering Team

              ↓

    Agent Engineering Team

核心能力：

-   Architecture Governance
-   Module Isolation
-   Context Optimization
-   Component Contract
-   Agent Workflow
-   Engineering Review

成为企业级 Agent Coding 基础设施。
