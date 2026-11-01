# patch-mcp-negotiation.py：MCP 协商与后台初始化

文档调整：2026-11-01。官方核对日期：2026-10-31。源码：[查看文件](../../patches/patch-mcp-negotiation.py)。

## 用途与目标

给 stdio/HTTP 配置增加 versionNegotiation=auto|legacy、startupMode=blocking|background，默认 auto/blocking；在原连接与清理登记后，仅可选后台服务提前释放启动等待，严格服务继续等待。

目标：`dsh/node_modules/@deepseek-ai/dsh-mcp-client/lib/index.js`。

## 官方是否已有等价修复

**未发现等价修复。**

官方 rc.5 与所查 index.ts 仍等待 connection.ready，没有对应配置字段；所查 SDK 依赖为 @modelcontextprotocol/client 2.2.0。连接 supervisor 原已管理工具同步、通知、重连和生命周期，这些不计为补丁新增或缺失的官方功能。

核对范围：官方桌面载荷 `0.2.1-rc.5`，以及官方源码快照 `ce7073d51254c26cd63b22a60835b8f948deb447`（Desktop package.json 为 `0.2.2-alpha.2`）。源码版本存在不等于桌面载荷已发布；本结论只适用于已核对的版本，不代表后续版本。完整载荷校验信息见 [总览](README.md#核对基线)。

官方源码依据：

- [packages/mcp/mcp-client/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/packages/mcp/mcp-client/src/index.ts)
- [packages/mcp/mcp-client/src/connection.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/packages/mcp/mcp-client/src/connection.ts)
- [packages/mcp/mcp-client/package.json](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/packages/mcp/mcp-client/package.json)

## 后续核对条件

官方同时支持按服务协商与后台启动后，核对严格失败、真实工具就绪、退出取消及重连语义。

返回 [补丁总览](README.md)。
