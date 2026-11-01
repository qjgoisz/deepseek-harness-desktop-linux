# patch-fingerprint.py：原生模块指纹门禁适配

文档调整：2026-11-01。官方核对日期：2026-10-31。源码：[查看文件](../../patches/patch-fingerprint.py)。

## 用途与目标

在 Linux node-addon-require-builtin 中按 ELF 符号定位 Matches，将已知指令序列替换为返回 true。

目标：`Linux ELF .node 文件（x86_64 / aarch64）`。

## 官方是否已有等价修复

**所核对的 Linux x64 同版本依赖仍有门禁。**

使用 rc.5 对应的 node-addon-require-builtin-linux-x64-gnu@0.1.9 原始 npm 包实测，仍需改变目标函数。该依赖位于外部原生包，桌面/core 仓库源码不足以证明其最新版本状态；本次未据此推断其他版本或真实 ARM64 二进制。

核对范围：官方桌面载荷 `0.2.1-rc.5`，以及官方源码快照 `ce7073d51254c26cd63b22a60835b8f948deb447`（Desktop package.json 为 `0.2.2-alpha.2`）。源码版本存在不等于桌面载荷已发布；本结论只适用于已核对的版本，不代表后续版本。完整载荷校验信息见 [总览](README.md#核对基线)。

## 后续核对条件

重新检查官方载荷所用依赖版本和对应 Linux 原生包。门禁消失或提供匹配 Electron 的模块后，再验证 ABI 与实际加载兼容性。

返回 [补丁总览](README.md)。
