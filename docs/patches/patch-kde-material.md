# patch-kde-material.py：KDE 材质协商

源码：[查看文件](../../patches/patch-kde-material.py)。

## 用途与目标

对确认属于当前进程的 X11 窗口请求 KWin blur；原生 Wayland、非 KDE、工具缺失或窗口验证失败时回退为实色，preload 按 IPC 结果选择材质。

目标：`lib/main.js 与两个 preload`。

## 官方是否已有等价修复

**官方载荷和所查源码均未发现等价实现。**

可见的原生材质分支是 macOS vibrancy 和 Windows acrylic。Desktop 目标文件未提供 X11 窗口归属验证、KWin blur 请求或 Linux 材质协商。 [apps/desktop/src/main.ts](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/apps/desktop/src/main.ts) [apps/desktop/src/welcome-window.ts](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/apps/desktop/src/welcome-window.ts)

核对范围见 [补丁总览](README.md#核对基线)。

## 后续核对条件

官方载荷提供对应 KDE 能力检测、窗口校验及失败回退后，再比较补丁。

返回 [补丁总览](README.md)。
