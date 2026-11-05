# patch-linux-identity.py：Linux 桌面项身份

源码：[查看文件](../../patches/patch-linux-identity.py)。

## 用途与目标

设置应用 package.json 的 desktopName，使 Electron 的 Linux 应用标识与 deepseek-harness.desktop 对应。

目标：`package.json`。

## 官方是否已有等价修复

**官方载荷和所查源码均未发现等价修复。**

发布包 package.json 未声明 desktopName。所查 Desktop 源码没有为 Linux 设置对应标识，也未提供对应的 Linux 桌面项打包配置。 [apps/desktop/package.json](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/apps/desktop/package.json) [apps/desktop/src/main.ts](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/apps/desktop/src/main.ts)

核对范围见 [补丁总览](README.md#核对基线)。

## 后续核对条件

官方 Linux 身份与发行包桌面项一致，并验证任务栏关联后再评估。

返回 [补丁总览](README.md)。
