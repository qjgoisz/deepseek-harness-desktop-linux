# patch-titlebar.py：Linux 标题栏适配

文档调整：2026-11-01。官方核对日期：2026-10-31。源码：[查看文件](../../patches/patch-titlebar.py)。

## 用途与目标

为主窗口和欢迎窗口增加 Linux hidden 标题栏及 Window Controls Overlay。

目标：`lib/main.js`。

## 官方是否已有等价修复

**未发现等价修复。**

rc.5 在基础平台适配后可匹配两个窗口配置；所查官方主窗口与欢迎窗口仍只有 Windows/macOS 的对应标题栏分支。

核对范围：官方桌面载荷 `0.2.1-rc.5`，以及官方源码快照 `ce7073d51254c26cd63b22a60835b8f948deb447`（Desktop package.json 为 `0.2.2-alpha.2`）。源码版本存在不等于桌面载荷已发布；本结论只适用于已核对的版本，不代表后续版本。完整载荷校验信息见 [总览](README.md#核对基线)。

官方源码依据：

- [apps/desktop/src/main.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/apps/desktop/src/main.ts)
- [apps/desktop/src/welcome-window.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/apps/desktop/src/welcome-window.ts)

## 后续核对条件

官方载荷提供 Linux 标题栏、拖动与窗口控制的等价实现后，再核对是否取消相应修改。

返回 [补丁总览](README.md)。
