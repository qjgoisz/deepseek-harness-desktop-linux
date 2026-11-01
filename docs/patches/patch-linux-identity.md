# patch-linux-identity.py：Linux 桌面项身份

文档调整：2026-11-01。官方核对日期：2026-10-31。源码：[查看文件](../../patches/patch-linux-identity.py)。

## 用途与目标

设置应用 package.json 的 desktopName，使 Electron 的 Linux 应用标识与 deepseek-harness.desktop 对应。

目标：`package.json`。

## 官方是否已有等价修复

**未发现等价修复。**

官方 rc.5 缺少该 desktopName；所查 package.json 的 macOS appId 不等同于 Linux desktopName。

核对范围：官方桌面载荷 `0.2.1-rc.5`，以及官方源码快照 `ce7073d51254c26cd63b22a60835b8f948deb447`（Desktop package.json 为 `0.2.2-alpha.2`）。源码版本存在不等于桌面载荷已发布；本结论只适用于已核对的版本，不代表后续版本。完整载荷校验信息见 [总览](README.md#核对基线)。

官方源码依据：

- [apps/desktop/package.json](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/apps/desktop/package.json)

## 后续核对条件

官方 Linux 身份与发行包桌面项一致，并验证任务栏关联后再评估。

返回 [补丁总览](README.md)。
