# patch-system-proxy.py：KDE 动态系统代理接入

源码：[查看文件](../../patches/patch-system-proxy.py)。

## 用途与目标

替换 profile-boot 的代理安装入口，在 HTTP 代理模块中接入 KDE 监听、动态控制器及系统策略的 IPv4 CIDR 绕过。

目标：`dsh-http-proxy/lib/index.js、dsh/lib/profile-boot-*.js、新增 desktop-system-proxy.mjs`。

## 官方是否已有等价修复

**官方载荷和所查源码均未发现等价修复。**

启动路径调用 installProxyFromEnvironment。已核对的 Desktop Host 和代理实现未提供 KDE 配置读取或动态刷新。 [apps/cli/src/profile-boot.ts](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/apps/cli/src/profile-boot.ts) [packages/util/http-proxy/src/install.ts](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/packages/util/http-proxy/src/install.ts)

核对范围见 [补丁总览](README.md#核对基线)。

## 后续核对条件

核对官方对 KDE 变更、显式环境覆盖、NO_PROXY、子进程继承和已有流排空的完整语义。

返回 [补丁总览](README.md)。
