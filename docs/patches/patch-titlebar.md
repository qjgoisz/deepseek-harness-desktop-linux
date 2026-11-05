# patch-titlebar.py：Linux 标题栏适配

源码：[查看文件](../../patches/patch-titlebar.py)。

## 用途与目标

为主窗口和欢迎窗口增加 Linux hidden 标题栏及 Window Controls Overlay。

目标：`lib/main.js`。

## 官方是否已有等价修复

**官方载荷和所查源码均未发现等价修复。**

主窗口和欢迎窗口的 hidden/overlay 样式仍限定在 Windows 或 macOS 分支，没有 Linux 窗口配置。 [apps/desktop/src/main.ts](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/apps/desktop/src/main.ts) [apps/desktop/src/welcome-window.ts](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/apps/desktop/src/welcome-window.ts)

核对范围见 [补丁总览](README.md#核对基线)。

## 后续核对条件

官方载荷提供 Linux 标题栏、拖动与窗口控制的等价实现后，再核对是否取消相应修改。

返回 [补丁总览](README.md)。
