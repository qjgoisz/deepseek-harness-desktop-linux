# system-proxy/proxy-controller.js：动态代理连接池控制器

文档调整：2026-11-01。官方核对日期：2026-10-31。源码：[查看文件](../../patches/system-proxy/proxy-controller.js)。

## 用途与目标

复用上游策略解析与 Undici，切换 dispatcher、路由策略和新子进程环境，排空旧池，退出时恢复先前状态。

目标：`由 patch-system-proxy.py 追加到 dsh-http-proxy/lib/index.js 的模块作用域`。

## 官方是否已有等价修复

**对应动态切换能力未发现官方等价实现。**

官方 rc.5 与所查 install.ts 仍提供环境安装生命周期，未提供此 Desktop 动态控制器。对环境代理的既有支持不等于运行中读取 KDE 变化。

核对范围：官方桌面载荷 `0.2.1-rc.5`，以及官方源码快照 `ce7073d51254c26cd63b22a60835b8f948deb447`（Desktop package.json 为 `0.2.2-alpha.2`）。源码版本存在不等于桌面载荷已发布；本结论只适用于已核对的版本，不代表后续版本。完整载荷校验信息见 [总览](README.md#核对基线)。

官方源码依据：

- [packages/util/http-proxy/src/install.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/packages/util/http-proxy/src/install.ts)

## 后续核对条件

核对官方实现的新请求切换、旧流排空、退出恢复及子进程继承后，再评估整体替代。

返回 [补丁总览](README.md)。
