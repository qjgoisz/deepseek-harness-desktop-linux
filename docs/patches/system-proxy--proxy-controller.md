# system-proxy/proxy-controller.js：动态代理连接池控制器

源码：[查看文件](../../patches/system-proxy/proxy-controller.js)。

## 用途与目标

复用上游策略解析与 Undici，切换 dispatcher、路由策略和新子进程环境，排空旧池，退出时恢复先前状态。

目标：`由 patch-system-proxy.py 追加到 dsh-http-proxy/lib/index.js 的模块作用域`。

## 官方是否已有等价修复

**官方载荷和所查源码均未发现等价修复。**

官方环境代理安装器未提供由 KDE 代理配置变化触发的连接池切换和旧流排空。 [packages/util/http-proxy/src/install.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ddac96760b6edf8fa0fe17cbdcf0b512f4c12b2c/packages/util/http-proxy/src/install.ts)

核对范围见 [补丁总览](README.md#核对基线)。

## 后续核对条件

核对官方实现的新请求切换、旧流排空、退出恢复及子进程继承后，再评估整体替代。

返回 [补丁总览](README.md)。
