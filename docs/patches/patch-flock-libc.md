# patch-flock-libc.py：libc 探测排除网络诊断

源码：[查看文件](../../patches/patch-flock-libc.py)。

## 用途与目标

在 Linux libc 探测调用 getReport 时暂时设置 excludeNetwork，并在 finally 恢复原值，保留原生 flock、binding 缓存及延迟加载。

目标：`dsh/node_modules/@deepseek-ai/node-addon-system/lib/flock.js`。

## 官方是否已有等价修复

**官方载荷和所查源码均未发现等价修复。**

官方文件锁模块仍调用完整的 process.report.getReport() 来识别 libc，未排除网络诊断。 [native/system/packages/entry/src/flock.ts](https://github.com/deepseek-ai/deepseek-harness/blob/38a6a5c965aa99ab525161efb7cc5cf1fe62fced/native/system/packages/entry/src/flock.ts)

核对范围见 [补丁总览](README.md#核对基线)。

## 后续核对条件

官方实际载荷改用不执行网络诊断的 libc 探测后，核对 libc 分支和真实锁语义。

返回 [补丁总览](README.md)。
