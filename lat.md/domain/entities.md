# Entities

中央治理的对象都有稳定 ID 和单一职责。它们描述跨仓交付边界，不描述某个仓库里的文件或函数。

对象图总览见 [[architecture/governance#中央领域模型]]。

## Feature

Feature 是跨仓变更的中央身份。它 pin 一份 APPROVED Source PRD，并列出参与仓库、Global Change 与 Work Package。

`feature_id` 形如 `FEAT-...`。状态由中央 Feature 状态机管理，禁止在 Feature 文档里缓存 Contract `current_state`。创建入口：[[tools/create_feature.py#main]]。

## Repo Work Package

Repo Work Package 是中央与单个项目仓库之间的唯一正式连接器。它只描述 Outcome、角色、全局变更、合同输入输出、验收与所需证据。

`work_package_id` 形如 `WP-...`，且只属于一个 `repository_id`。禁止写入 exact file、symbol、helper 或本地 Todo slicing。见 [[ADR-004-repo-work-package]]。

## Contract

Contract 是跨仓协作的机器边界。生命周期状态落在某个 Release version 上，而不是落在合同名字上。

Consumer 通过 pin/lock 绑定 `version + tag + peeled commit`。解析时 `current_release` 只是派生指针。见 [[architecture/contract-lifecycle]]。

## Program

Program 是一组相关 Feature 的路线图容器。它不拥有业务代码，只提供全局优先级与下一步建议。

## Global Change ID

Global Change ID 形如 `XR-C01`。项目 Stage PRD 只能继承并映射到本地变更，不能发明同义的全局 ID。

## Integration Scenario

Integration Scenario 描述一次跨仓验收场景及其等待条件。PASS 不能手改 scenario YAML，必须对应不可变 [[facts-and-evidence#IntegrationRun]]。
