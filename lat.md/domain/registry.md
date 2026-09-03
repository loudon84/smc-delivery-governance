# Registry

Registry 是中央对项目、仓库、团队、合同与策略的权威目录。没有登记的仓库不能被 Feature 引用，也不能安装生产 Kit。

校验入口：[[tools/validate_registry.py#main]]。纳管流程见 [[architecture/project-onboarding]]。

## Project

Project 把一个可交付产品与它的主仓库、所属团队绑定。它不保存 Stage PRD 或源代码路径。

## Repository

Repository 记录 GitHub 身份、默认分支与治理状态。`governance_state` 走仓库状态机，与某个 Feature 的 IMPLEMENTING 无关。

## Team

Team 是 Feature Owner / Integration Owner / Contract Owner 的稳定归属，避免把责任写进个人账号。

## Policy

Policy 描述仓库治理基线，例如必须安装的 Kit 接口与 CI 门禁。策略变化不自动改写已 pin 的 Kit Release。
