# patch-flock-libc.py：libc 探测排除网络诊断

文档调整：2026-11-01。官方核对日期：2026-10-31。源码：[查看文件](../../patches/patch-flock-libc.py)。

## 用途与目标

在 Linux libc 探测调用 getReport 时暂时设置 excludeNetwork，并在 finally 恢复原值，保留原生 flock、binding 缓存及延迟加载。

目标：`dsh/node_modules/@deepseek-ai/node-addon-system/lib/flock.js`。

## 官方是否已有等价修复

**未发现等价修复。**

官方 rc.5 原始调用仍存在；所查 native/system/packages/entry/src/flock.ts 仍直接执行 process.report.getReport()，没有排除网络诊断。

核对范围：官方桌面载荷 `0.2.1-rc.5`，以及官方源码快照 `ce7073d51254c26cd63b22a60835b8f948deb447`（Desktop package.json 为 `0.2.2-alpha.2`）。源码版本存在不等于桌面载荷已发布；本结论只适用于已核对的版本，不代表后续版本。完整载荷校验信息见 [总览](README.md#核对基线)。

官方源码依据：

- [native/system/packages/entry/src/flock.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/native/system/packages/entry/src/flock.ts)

## 后续核对条件

官方实际载荷改用不执行网络诊断的 libc 探测后，核对 libc 分支和真实锁语义。

返回 [补丁总览](README.md)。
