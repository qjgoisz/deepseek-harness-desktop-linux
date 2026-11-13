# patch-main.py：Linux 主进程适配

源码：[查看文件](../../patches/patch-main.py)。

## 用途与目标

为 Linux 补充平台准入、客户端平台标识、资源根、打包态、托盘及 CLI/pnpm 路径处理。

目标：`lib/main.js`。

## 官方是否已有等价修复

**官方载荷和所查源码均未发现等价修复。**

Linux 仍不在桌面策略准入列表。账户视图仍将非 Windows 映射为 darwin，并保留更新输入守卫。托盘创建仍限 Windows，系统 Electron 所需的资源根覆盖亦未提供。 [apps/desktop/src/main.ts](https://github.com/deepseek-ai/deepseek-harness/blob/38a6a5c965aa99ab525161efb7cc5cf1fe62fced/apps/desktop/src/main.ts)

核对范围见 [补丁总览](README.md#核对基线)。

## 后续核对条件

官方实际载荷同时提供对应 Linux 平台、资源路径与托盘处理后，逐项核对是否还需补丁。

返回 [补丁总览](README.md)。
