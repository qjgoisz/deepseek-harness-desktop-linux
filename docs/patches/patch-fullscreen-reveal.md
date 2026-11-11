# patch-fullscreen-reveal.py：全屏顶部交互适配

源码：[查看文件](../../patches/patch-fullscreen-reveal.py)。

## 用途与目标

补充全屏顶部悬停显隐、DOM 指针桥、X11 原生光标轮询、焦点检查、窗口状态同步及 Wayland 顶栏双击还原。

目标：`lib/main.js 与两个 preload`。

## 官方是否已有等价修复

**官方载荷和所查源码均未发现等价实现。**

官方主进程只在 macOS/Windows 分支发布全屏事件。Linux 尚无配套的最大化、焦点同步或 Wayland 指针和双击还原路径。 [apps/desktop/src/main.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ddac96760b6edf8fa0fe17cbdcf0b512f4c12b2c/apps/desktop/src/main.ts)

核对范围见 [补丁总览](README.md#核对基线)。

## 后续核对条件

分别核对官方实际载荷中的顶部交互、失焦处理、最大化/全屏同步及 Wayland 双击路径。

返回 [补丁总览](README.md)。
