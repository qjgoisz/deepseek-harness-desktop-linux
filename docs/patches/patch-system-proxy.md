# patch-system-proxy.py：KDE 动态系统代理接入

文档调整：2026-11-01。官方核对日期：2026-10-31。源码：[查看文件](../../patches/patch-system-proxy.py)。

## 用途与目标

替换 profile-boot 的代理安装入口，在 HTTP 代理模块中接入 KDE 监听、动态控制器及系统策略的 IPv4 CIDR 绕过。

目标：`dsh-http-proxy/lib/index.js、dsh/lib/profile-boot-*.js、新增 desktop-system-proxy.mjs`。

## 官方是否已有等价修复

**未发现等价修复。**

rc.5 的原始入口仍调用 installProxyFromEnvironment；所查 util/http-proxy 源码仍基于环境变量安装代理，没有对应 KDE 文件/通知监听。

核对范围：官方桌面载荷 `0.2.1-rc.5`，以及官方源码快照 `ce7073d51254c26cd63b22a60835b8f948deb447`（Desktop package.json 为 `0.2.2-alpha.2`）。源码版本存在不等于桌面载荷已发布；本结论只适用于已核对的版本，不代表后续版本。完整载荷校验信息见 [总览](README.md#核对基线)。

官方源码依据：

- [packages/util/http-proxy/src/install.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/packages/util/http-proxy/src/install.ts)
- [packages/util/http-proxy/src/policy.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/packages/util/http-proxy/src/policy.ts)

## 后续核对条件

核对官方对 KDE 变更、显式环境覆盖、NO_PROXY、子进程继承和已有流排空的完整语义。

返回 [补丁总览](README.md)。
