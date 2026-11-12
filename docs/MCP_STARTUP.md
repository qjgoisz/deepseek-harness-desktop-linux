# MCP 启动优化

当前 Desktop 载荷的实现审计见 [逐项说明](patches/patch-mcp-negotiation.md)。

本次维护包含三项：对已知服务选择单次 legacy 协商；固定本地 mcp-remote 入口，去掉启动时的 npx 查询。第三项为可选 MCP 后台初始化。没有实施按需才启动、提前显示加载窗口或其他启动策略。

配套工具要求明确配置且可写的 npm 全局前缀，执行 `npm install -g mcp-remote@0.15.1`。已有配置可迁移到全局包入口。安装、迁移和 CC Switch 同步见 [配套工具](../local-fixes/mcp-startup/README.md)。

## 实现及生效范围

- `patches/patch-mcp-negotiation.py` 已接入应用树构建，stdio/HTTP 均可设置 `versionNegotiation`，默认 `auto`，只允许 `auto`、`legacy`。每次重连继续使用服务配置，其他生命周期保持上游行为。未知、重复或不完整补丁拒绝写入；语法检查通过后原子替换单一模块。
- `local-fixes/mcp-startup/` 提供全局安装及显式配置工具。Wolfram、OpenAlex、Exa 配置 legacy，后两者用固定 Node 直接运行全局包的 `proxy.js`。保留额外命令参数、环境变量、超时、失败策略及其他服务设置。
- 配置工具在核心补丁未安装时拒绝修改配置，并校验安装的 mcp-remote 版本和目标入口。完整验证后备份并替换 YAML，保留非目标内容和 `!js` 标签。
- v2 增加 `startupMode: blocking | background`，默认 blocking，只有显式 background 且非严格服务才释放 Loader 启动屏障。后台连接完成后继续由原有真实工具注册表和通知机制提供工具、指令和资源；退出仍关闭并等待同一连接，不另建失去归属的任务。`failOnStartupError: true` 无论模式如何都保留原来的等待和失败语义。
- 配置工具为三个已知可选服务开启 background，严格服务保持 blocking；v1 核心拒绝新配置。已有前两项设置可在升级后原路重跑配置工具。只需第三步时，也可单独给相应服务设置 `startupMode: background`，无需改远端命令、协商策略或安装新的 npm 包。

具体安装、生效和回退命令见 [本地工具说明](../local-fixes/mcp-startup/README.md)。

## 第三步具体改在哪里

改动点是 `dsh-mcp-client/lib/index.js` 的插件 `apply()`，不是远端 MCP 服务器，也不是另起一个提前显示的窗口。原流程在调用 `startConnection()`、登记服务上下文与退出清理后，一直等待 `connection.ready`；这个 Promise 包括初次连接和工具同步，因此慢服务会占住 Loader 启动屏障。

v2 保留上述顺序，只在最后的等待点分支：

```text
启动原连接 → 登记服务上下文、卸载/退出清理
  ├─ background 且 !failOnStartupError：观察 ready 的成功/失败，然后立即结束 apply
  └─ 其他情况：等待 ready；严格服务失败时抛错，让 Cordis 回滚插件
```

因此“后台”只表示启动阶段不等待可选服务。工具仍由原连接完成发现和同步后注册，没有预先放置不可用的占位工具；已有 supervisor 继续负责通知、重连与工具更新。卸载、退出或热重载会处理同一连接，准备完成前退出也不会遗留另起的无归属连接。后台 ready 的错误被显式观察并记录，避免未处理的 Promise 拒绝；后续重试依然遵守原连接策略。

`startupMode` 默认 `blocking`，必须逐服务显式开启；`failOnStartupError: true` 即使配为 background 也等待并传播错误。安装 deb 不自动修改配置。后台模式不会缩短远端服务自身的连接时间，也不能解除其他同步阻塞，例如后来定位到的 [flock libc 完整报告](STARTUP_LIBC.md)。

## 验证

当前载荷通过本地 MCP 进程回归，覆盖协商方式、工具同步、后台初始化、取消、重连和热重载。完整回归范围见 [兼容性记录](COMPATIBILITY.md)。远程服务的登录与连接时长取决于各自运行环境。
