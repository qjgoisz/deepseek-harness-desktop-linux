# patch-mac-chrome.py：Linux 自绘窗口装饰

源码：[查看文件](../../patches/patch-mac-chrome.py)。

## 用途与目标

复用 Windows 自绘顶栏标志并保留 Linux 平台标识，补充交通灯、窗口控制 IPC、侧栏宽度测量、欢迎页表面处理和最大化/全屏事件。

目标：`lib/main.js、lib/preload-app.cjs、lib/preload-welcome.cjs`。

## 官方是否已有等价修复

**官方载荷和所查源码均未发现等价实现。**

左侧原生交通灯与 sidebar vibrancy 位于 macOS 窗口分支。Linux 未实现相应的自绘控件、窗口操作 IPC 和窗口布局处理。 [apps/desktop/src/main.ts](https://github.com/deepseek-ai/deepseek-harness/blob/38a6a5c965aa99ab525161efb7cc5cf1fe62fced/apps/desktop/src/main.ts) [apps/desktop/src/welcome-window.ts](https://github.com/deepseek-ai/deepseek-harness/blob/38a6a5c965aa99ab525161efb7cc5cf1fe62fced/apps/desktop/src/welcome-window.ts)

核对范围见 [补丁总览](README.md#核对基线)。

## 后续核对条件

官方 Linux 窗口控制、拖动和状态事件进入实际桌面载荷后，按功能逐项比较。

返回 [补丁总览](README.md)。
