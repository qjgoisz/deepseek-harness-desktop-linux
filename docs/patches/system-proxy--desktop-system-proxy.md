# system-proxy/desktop-system-proxy.mjs：KDE 代理读取和通知模块

源码：[查看文件](../../patches/system-proxy/desktop-system-proxy.mjs)。

## 用途与目标

读取 KDE 手动 HTTP/HTTPS 代理及绕过项，监听 KIO 通知和 kioslaverc 替换，并每 30 秒补偿检查。

目标：`由 patch-system-proxy.py 复制到 dsh-http-proxy/lib/desktop-system-proxy.mjs`。

## 官方是否已有等价修复

**官方载荷和所查源码均未发现等价修复。**

官方启动路径从环境读取代理，未提供 kioslaverc 读取与 KDE 会话总线通知监听。 [apps/cli/src/profile-boot.ts](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/apps/cli/src/profile-boot.ts) [packages/util/http-proxy/src/install.ts](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/packages/util/http-proxy/src/install.ts)

核对范围见 [补丁总览](README.md#核对基线)。

## 后续核对条件

随官方动态系统代理实现一起核对；不能仅以官方支持 HTTP_PROXY 判断已替代。

返回 [补丁总览](README.md)。
