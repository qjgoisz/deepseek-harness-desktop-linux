# patch-main.py：Linux 主进程适配

文档调整：2026-11-01。官方核对日期：2026-10-31。源码：[查看文件](../../patches/patch-main.py)。

## 用途与目标

为 Linux 补充平台准入、客户端平台标识、资源根、打包态、托盘及 CLI/pnpm 路径处理。

目标：`lib/main.js`。

## 官方是否已有等价修复

**未发现等价修复。**

rc.5 的预期替换点仍存在；所查 main.ts 仍将平台准入限制为 win32/darwin，PlatformView 将非 Windows 映射为 darwin，托盘创建仍限 Windows。

核对范围：官方桌面载荷 `0.2.1-rc.5`，以及官方源码快照 `ce7073d51254c26cd63b22a60835b8f948deb447`（Desktop package.json 为 `0.2.2-alpha.2`）。源码版本存在不等于桌面载荷已发布；本结论只适用于已核对的版本，不代表后续版本。完整载荷校验信息见 [总览](README.md#核对基线)。

官方源码依据：

- [apps/desktop/src/main.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/apps/desktop/src/main.ts)

## 后续核对条件

官方实际载荷同时提供对应 Linux 平台、资源路径与托盘处理后，逐项核对是否还需补丁。

返回 [补丁总览](README.md)。
