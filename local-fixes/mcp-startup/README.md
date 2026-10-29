# MCP 启动优化：单次握手、本地入口与后台初始化

实现用户选定的三项优化。后台初始化通过服务配置显式启用，不修改 Electron 提前显示加载窗口的策略。

1. 构建补丁 `patches/patch-mcp-negotiation.py` 为 MCP client 的 stdio、HTTP 配置增加 `versionNegotiation: auto | legacy`，默认保持 `auto`。每次连接和重连读取同一个配置；无效配置在启动进程前拒绝。
2. `runtime/package.json`、`package-lock.json` 固定 `mcp-remote@0.15.1` 及依赖树。配置工具将 OpenAlex、Exa 从 `npx -y mcp-remote@0.15.1 ...` 改为固定 Node + 本地 `dist/proxy.js`；完整保留其余参数、环境、超时及失败策略。Wolfram、OpenAlex、Exa 设置为 `legacy`，OCR 等其他 MCP 不变。
3. v2 核心补丁增加 `startupMode: blocking | background`，默认 `blocking`。配置工具为上述三个可选服务设置 `background`；`failOnStartupError: true` 的服务保留 `blocking`，核心也强制等待严格服务。其他 MCP 可独立配置，工具不会扩大修改范围。

后台模式立即开始连接，主界面无需等其握手或工具同步。连接完成后才向真实工具注册表提供工具，不预注册占位工具；重连、通知同步、退出和热重载仍由同一个连接及原有生命周期管理。刚进入主界面时，尚未连接的 MCP 工具不会出现，应等对应工具可用后再发依赖它的任务。此模式不会缩短远端服务器自身的初始化或登录时间。

不向用户插件目录安装或覆盖 DSH 核心包。核心修改放在应用树现有模块内，构建流程已接入；固定的 mcp-remote 则放在独立用户目录。DSH 上游更新若改变补丁锚点，构建应失败，重新评估后再适配。

## 生效步骤

仓库实现与现用安装分开，修改仓库不会自动修改 `/usr/lib/deepseek-harness`。应先安装包含 v2 补丁的新包，再在退出 Desktop 后修改配置。不同自用包都显示 rc.3，不能只凭版本号判断支持情况：配置工具会检查 v2 标记，拒绝向旧核心写入新设置。

现有 `./auto-build.sh --arch x64 --formats deb --electron bundled --package-jobs 4` 在生成新应用树时会应用核心补丁。含后台模式的 rc.3 bundled deb 路径与校验见 `docs/MCP_STARTUP.md`。没有替换正式安装；rc.4 Desktop 更新继续暂停。安装 deb 后仍须执行以下配置步骤，三项优化才会在所选服务生效。

安装固定入口（只在首次安装时需要 npm 网络；选择尚不存在的目标目录）：

如果前两步已经在持久目录安装了 mcp-remote 0.15.1，保留该目录并跳过本安装段，后文 `REMOTE` 设置为原来的路径即可。第三步无需重装 runtime。

```bash
REPO=/home/debian/Documents/deepseek-harness/default-workspace/deepseek-harness-desktop-linux
REMOTE="$HOME/.local/share/dsh-mcp-remote-0.15.1"
test ! -e "$REMOTE" || { echo '目标已存在，请先检查'; exit 1; }
mkdir -p "$REMOTE"
cp "$REPO/local-fixes/mcp-startup/runtime/"package*.json "$REMOTE/"
npm ci --prefix "$REMOTE" --ignore-scripts --no-audit --no-fund
```

使用精确锁文件，安装时不执行依赖脚本。目标入口及依赖必须持续保留，不能指向可清理的 npx 缓存或临时目录。后续启动不再运行 npm；远端协议/OAuth 网络访问仍存在。安装阶段网络失败时应先处理安装命令的代理/网络，不删除锁文件无约束重装。

在已安装补丁且 Desktop 已正常退出后，先验证，再显式写入：

```bash
node "$REPO/local-fixes/mcp-startup/configure.mjs" \
  --app /usr/lib/deepseek-harness/resources/app \
  --profile "$HOME/.dsh/profiles/desktop" \
  --runtime "$REMOTE" --node /usr/bin/node

node "$REPO/local-fixes/mcp-startup/configure.mjs" \
  --app /usr/lib/deepseek-harness/resources/app \
  --profile "$HOME/.dsh/profiles/desktop" \
  --runtime "$REMOTE" --node /usr/bin/node --apply
```

本机验证 Node 为 24.21.0。换用其他 Node 路径时，应确认是持久可执行路径及满足 mcp-remote 的运行要求。工具拒绝旧版/未补丁核心、不匹配的 mcp-remote 版本、缺失/重复服务、未知命令、未知启动模式和未知 YAML 布局；所有目标校验通过才写入。仅替换选中配置字段；注释、`!js` 表达式以及其他服务保持原样。工具不输出配置正文，写入前生成权限 600 的原配置备份，避免泄露认证内容。已经在相同持久路径应用过前两项配置的，可在升级 v2 核心后重新运行同一命令补充后台模式。

只想启用第三步、不调整命令或协商方式时，也可在已安装 v2 核心的相应 MCP 的 `config` 下手动增加：

```yaml
startupMode: background
```

保持原 `failOnStartupError` 设置；为 true 时仍会等待。无需为此重装 mcp-remote。默认 blocking 保持 CLI、worker 和未选择后台模式的服务原有启动行为。

## 回退

退出 Desktop 后，将工具报告的 `cordis.patch.yml.before-mcp-startup-时间` 复制回 `cordis.patch.yml`，再启动。恢复到哪一轮设置取决于所选备份：首次改动前的备份恢复 npx/auto，第三步前的备份则保留前两项。仅关闭后台模式可将 `startupMode` 改为 `blocking`；无该字段时也默认 blocking。恢复了远端命令后才可删除对应独立 mcp-remote 目录。不要回退整个用户数据目录或覆盖聊天。

## 验证边界

离线回归覆盖实际 rc.3 MCP client 与 SDK：默认 auto 两个进程、legacy 一个进程、工具同步/本地测试工具调用、重连继续使用 legacy、启动中取消与进程回收、严格启动失败、无效模式，以及 YAML 注释/标签/额外参数保留和重复/未知配置拒绝。

第三步补充后台加载屏障、延迟工具/指令/资源就绪、可选失败、严格等待/失败、探测/握手/工具同步中取消、退避取消、动态工具通知、真实 Cordis 卸载/热重载和 v1→v2 补丁升级。完整 Desktop 使用空 HOME、本地受控 MCP 分别验证 Wayland/XWayland 的就绪、取消与严格等待，不用用户凭据，也不发模型请求。

完整配置的真实 MCP 初始化结果与测试耗时另见 `docs/MCP_STARTUP.md`。减少进程和 npm 查询并不保证每次按固定比例加速；OAuth 登录/刷新、远端响应和 Wolfram 内核仍可造成等待。真实 MCP 仅做初始化和工具列表读取，没有模型请求或任务工具调用。
