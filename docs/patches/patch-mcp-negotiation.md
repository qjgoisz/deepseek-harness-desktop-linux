# patch-mcp-negotiation.py：MCP 协商与后台初始化

源码：[查看文件](../../patches/patch-mcp-negotiation.py)。

## 用途与目标

给 stdio/HTTP 配置增加 versionNegotiation=auto|legacy、startupMode=blocking|background，默认 auto/blocking；在原连接与清理登记后，仅可选后台服务提前释放启动等待，严格服务继续等待。

目标：`dsh/node_modules/@deepseek-ai/dsh-mcp-client/lib/index.js`。

## 官方是否已有等价修复

**官方载荷和所查源码均未发现等价修复。**

MCP 客户端固定使用 auto 协商，插件启动时等待 connection.ready，未提供按服务选择协商方式和可选后台连接。 [packages/mcp/mcp-client/src/connection.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ddac96760b6edf8fa0fe17cbdcf0b512f4c12b2c/packages/mcp/mcp-client/src/connection.ts) [packages/mcp/mcp-client/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ddac96760b6edf8fa0fe17cbdcf0b512f4c12b2c/packages/mcp/mcp-client/src/index.ts)

核对范围见 [补丁总览](README.md#核对基线)。

## 后续核对条件

官方同时支持按服务协商与后台启动后，核对严格失败、真实工具就绪、退出取消及重连语义。

返回 [补丁总览](README.md)。
