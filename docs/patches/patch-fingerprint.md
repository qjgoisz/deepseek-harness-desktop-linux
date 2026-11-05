# patch-fingerprint.py：原生模块指纹门禁适配

源码：[查看文件](../../patches/patch-fingerprint.py)。

## 用途与目标

在 Linux node-addon-require-builtin 中按 ELF 符号定位 Matches，将已知指令序列替换为返回 true。

目标：`Linux ELF .node 文件（x86_64 / aarch64）`。

## 官方是否已有等价修复

**本版所用的 Linux x64 依赖仍有门禁。**

已按 npm registry 摘要校验原始 node-addon-require-builtin-linux-x64-gnu@0.1.9。ELF 仍能定位 Matches 且包含预期门禁指令。本次验证范围为该 x64 发布包。 [官方 npm 包](https://www.npmjs.com/package/node-addon-require-builtin-linux-x64-gnu/v/0.1.9)。

核对范围见 [补丁总览](README.md#核对基线)。

## 后续核对条件

重新检查官方载荷所用依赖版本和对应 Linux 原生包。门禁消失或提供匹配 Electron 的模块后，再验证 ABI 与实际加载兼容性。

返回 [补丁总览](README.md)。
