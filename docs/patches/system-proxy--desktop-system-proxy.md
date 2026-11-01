# system-proxy/desktop-system-proxy.mjs：KDE 代理读取和通知模块

文档调整：2026-11-01。官方核对日期：2026-10-31。源码：[查看文件](../../patches/system-proxy/desktop-system-proxy.mjs)。

## 用途与目标

读取 KDE 手动 HTTP/HTTPS 代理及绕过项，监听 KIO 通知和 kioslaverc 替换，并每 30 秒补偿检查。

目标：`由 patch-system-proxy.py 复制到 dsh-http-proxy/lib/desktop-system-proxy.mjs`。

## 官方是否已有等价修复

**对应系统代理能力未发现官方等价实现。**

官方 rc.5 和所查代理源码未包含对应 KDE 读取与动态监听。此文件是主补丁的辅助代码，其结论依据同一条代理入口证据。

核对范围：官方桌面载荷 `0.2.1-rc.5`，以及官方源码快照 `ce7073d51254c26cd63b22a60835b8f948deb447`（Desktop package.json 为 `0.2.2-alpha.2`）。源码版本存在不等于桌面载荷已发布；本结论只适用于已核对的版本，不代表后续版本。完整载荷校验信息见 [总览](README.md#核对基线)。

官方源码依据：

- [packages/util/http-proxy/src/install.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/packages/util/http-proxy/src/install.ts)

## 后续核对条件

随官方动态系统代理实现一起核对；不能仅以官方支持 HTTP_PROXY 判断已替代。

返回 [补丁总览](README.md)。
