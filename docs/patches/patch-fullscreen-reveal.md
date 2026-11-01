# patch-fullscreen-reveal.py：全屏顶部交互适配

文档调整：2026-11-01。官方核对日期：2026-10-31。源码：[查看文件](../../patches/patch-fullscreen-reveal.py)。

## 用途与目标

补充全屏顶部悬停显隐、DOM 指针桥、X11 原生光标轮询、焦点检查、窗口状态同步及 Wayland 顶栏双击还原。

目标：`lib/main.js 与两个 preload`。

## 官方是否已有等价修复

**未发现等价实现。**

官方 rc.5 可应用该补丁；所查桌面源码没有本补丁的 Linux 顶部指针桥与对应交互组合。官方已有的窗口机制不自动证明这些 Linux 路径已覆盖。

核对范围：官方桌面载荷 `0.2.1-rc.5`，以及官方源码快照 `ce7073d51254c26cd63b22a60835b8f948deb447`（Desktop package.json 为 `0.2.2-alpha.2`）。源码版本存在不等于桌面载荷已发布；本结论只适用于已核对的版本，不代表后续版本。完整载荷校验信息见 [总览](README.md#核对基线)。

官方源码依据：

- [apps/desktop/src/main.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/apps/desktop/src/main.ts)
- [apps/desktop/src/preload-windows.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/apps/desktop/src/preload-windows.ts)

## 后续核对条件

分别核对官方实际载荷中的顶部交互、失焦处理、最大化/全屏同步及 Wayland 双击路径。

返回 [补丁总览](README.md)。
