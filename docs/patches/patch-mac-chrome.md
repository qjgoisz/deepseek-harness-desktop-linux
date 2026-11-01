# patch-mac-chrome.py：Linux 自绘窗口装饰

文档调整：2026-11-01。官方核对日期：2026-10-31。源码：[查看文件](../../patches/patch-mac-chrome.py)。

## 用途与目标

复用 Windows 自绘顶栏标志并保留 Linux 平台标识，补充交通灯、窗口控制 IPC、侧栏宽度测量、欢迎页表面处理和最大化/全屏事件。

目标：`lib/main.js、lib/preload-app.cjs、lib/preload-welcome.cjs`。

## 官方是否已有等价修复

**未发现等价实现。**

rc.5 可以应用对应注入；所查官方源码没有 installLinuxChrome 或对应 Linux 窗口控制 IPC。这里核对功能是否等价，不以外观相似作为已修复证据。

核对范围：官方桌面载荷 `0.2.1-rc.5`，以及官方源码快照 `ce7073d51254c26cd63b22a60835b8f948deb447`（Desktop package.json 为 `0.2.2-alpha.2`）。源码版本存在不等于桌面载荷已发布；本结论只适用于已核对的版本，不代表后续版本。完整载荷校验信息见 [总览](README.md#核对基线)。

官方源码依据：

- [apps/desktop/src/main.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/apps/desktop/src/main.ts)
- [apps/desktop/src/preload-app.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/apps/desktop/src/preload-app.ts)
- [apps/desktop/src/preload-welcome.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/apps/desktop/src/preload-welcome.ts)

## 后续核对条件

官方 Linux 窗口控制、拖动和状态事件进入实际桌面载荷后，按功能逐项比较。

返回 [补丁总览](README.md)。
