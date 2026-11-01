# patch-kde-material.py：KDE 材质协商

文档调整：2026-11-01。官方核对日期：2026-10-31。源码：[查看文件](../../patches/patch-kde-material.py)。

## 用途与目标

对确认属于当前进程的 X11 窗口请求 KWin blur；原生 Wayland、非 KDE、工具缺失或窗口验证失败时回退为实色，preload 按 IPC 结果选择材质。

目标：`lib/main.js 与两个 preload`。

## 官方是否已有等价修复

**未发现等价实现。**

官方 rc.5 未包含此 KDE 窗口验证与材质协商；所查桌面源码未提供对应 KWin 协商机制。macOS vibrancy 或 Windows acrylic 不能视为 KDE 等价实现。

核对范围：官方桌面载荷 `0.2.1-rc.5`，以及官方源码快照 `ce7073d51254c26cd63b22a60835b8f948deb447`（Desktop package.json 为 `0.2.2-alpha.2`）。源码版本存在不等于桌面载荷已发布；本结论只适用于已核对的版本，不代表后续版本。完整载荷校验信息见 [总览](README.md#核对基线)。

官方源码依据：

- [apps/desktop/src/main.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/apps/desktop/src/main.ts)

## 后续核对条件

官方载荷提供对应 KDE 能力检测、窗口校验及失败回退后，再比较补丁。

返回 [补丁总览](README.md)。
