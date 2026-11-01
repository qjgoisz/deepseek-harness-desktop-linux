# MCP 启动优化：单次握手、本地入口与后台初始化

实现用户选定的三项优化。后台初始化通过服务配置显式启用，不修改 Electron 提前显示加载窗口的策略。

1. 构建补丁 `patches/patch-mcp-negotiation.py` 为 MCP client 的 stdio、HTTP 配置增加 `versionNegotiation: auto | legacy`，默认保持 `auto`。每次连接和重连读取同一个配置；无效配置在启动进程前拒绝。
2. `runtime/package.json`、`package-lock.json` 固定 `mcp-remote@0.15.1` 及依赖树。配置工具将 OpenAlex、Exa 从 `npx -y mcp-remote@0.15.1 ...` 改为固定 Node + 本地 `dist/proxy.js`；完整保留其余参数、环境、超时及失败策略。Wolfram、OpenAlex、Exa 设置为 `legacy`，OCR 等其他 MCP 不变。
3. v2 核心补丁增加 `startupMode: blocking | background`，默认 `blocking`。配置工具为上述三个可选服务设置 `background`；`failOnStartupError: true` 的服务保留 `blocking`，核心也强制等待严格服务。其他 MCP 可独立配置，工具不会扩大修改范围。

后台模式立即开始连接，主界面无需等其握手或工具同步。连接完成后才向真实工具注册表提供工具，不预注册占位工具；重连、通知同步、退出和热重载仍由同一个连接及原有生命周期管理。刚进入主界面时，尚未连接的 MCP 工具不会出现，应等对应工具可用后再发依赖它的任务。此模式不会缩短远端服务器自身的初始化或登录时间。

不向用户插件目录安装或覆盖 DSH 核心包。核心修改放在应用树现有模块内，构建流程已接入；固定的 mcp-remote 按明确配置的 npm 全局前缀安装，使用独立锁定运行目录。DSH 上游更新若改变补丁锚点，构建应失败，重新评估后再适配。

## 生效步骤

仓库实现与现用安装分开；配置前需确认应用包含 v2 核心标记，工具会拒绝旧核心。当前 Desktop 成品与验证范围见 [交接](../../HANDOFF.md)。

### 安装路径与权限检查

先明确设置 npm 全局前缀，例如：

```bash
npm config set prefix "$HOME/.local"
```

安装工具读取 npm 的有效配置，仅接受来自 user/global/env/cli 的显式 `prefix`，不接受 npm 的内置或默认路径。允许通过 `npm_config_prefix` 环境变量覆盖。未设置、相对路径、系统路径、不可写目录或父路径为文件时，退出并提示，不安装、不自动设置 prefix、不提权。路径尚不存在时检查最近存在的父目录；同时检查 prefix、`prefix/lib` 和已有目标目录的写入与遍历权限，实际安装失败也会退出。

安装目标为 `<prefix>/lib/dsh-mcp-remote-0.15.1`。这是以 npm 全局前缀组织的独立锁定运行目录，**不是 `npm install -g mcp-remote` 的平铺安装**；这样可以继续用仓库的 package-lock 固定全部依赖，避免仅固定顶层版本却重新解析依赖树。不创建全局命令或改 PATH。

```bash
REPO=/home/debian/Documents/deepseek-harness/default-workspace/deepseek-harness-desktop-linux
# 默认只检查路径、权限和既有安装；不写目录。
node "$REPO/local-fixes/mcp-startup/install-runtime.mjs"
# 显式执行安装。
node "$REPO/local-fixes/mcp-startup/install-runtime.mjs" --apply
```

工具在安装父目录下创建临时目录，以 `npm ci --ignore-scripts --no-audit --no-fund` 安装并验证版本和入口后再改名。失败删除本次临时目录；已有目录必须版本/入口/manifest/锁文件匹配，否则退出，不覆盖旧安装。安装和检测时需要 npm；日常 MCP 启动直接执行固定 Node 和入口，不再查询 npm。

在已安装补丁且 Desktop 已正常退出后，先验证，再显式写入：

```bash
node "$REPO/local-fixes/mcp-startup/configure.mjs" \
  --app /usr/lib/deepseek-harness/resources/app \
  --profile "$HOME/.dsh/profiles/desktop" \
  --node /usr/bin/node

node "$REPO/local-fixes/mcp-startup/configure.mjs" \
  --app /usr/lib/deepseek-harness/resources/app \
  --profile "$HOME/.dsh/profiles/desktop" \
  --node /usr/bin/node --apply
```

未指定 `--runtime` 时，配置工具自动使用上述 npm 前缀路径，并执行同样的显式配置及可写性检查。保留 `--runtime /绝对运行目录` 供已有部署显式指定；此选项不会安装软件。

### 从旧目录迁移

先安装新运行目录，再明确给出经验证的旧目录/旧 Node：

```bash
node "$REPO/local-fixes/mcp-startup/configure.mjs" \
  --app /usr/lib/deepseek-harness/resources/app \
  --profile "$HOME/.dsh/profiles/desktop" --node /usr/bin/node \
  --previous-runtime "$HOME/.local/share/dsh-mcp-remote-0.15.1" \
  --previous-node /usr/bin/node
# 验证通过后重复以上命令并加 --apply。
```

两个 previous 参数必须一起提供；只接受配置中精确匹配所给旧 Node/入口的命令，且旧 runtime 也必须是 mcp-remote 0.15.1。未知旧路径拒绝写入，不自动搜索或替换任意 node 命令。迁移保留远端参数、header、env 和其他服务；配置语义仍为本文的 legacy/background 与严格服务 blocking。仅迁移路径时应先检查现有模式没有被改为其他设置。写入前生成原配置备份；保留旧 runtime 供回退，确认不再使用后再自行清理。不会重启 Desktop。

本机验证 Node 为 24.21.0。换用其他 Node 路径时，应确认是持久可执行路径及满足 mcp-remote 的运行要求。工具拒绝旧版/未补丁核心、不匹配的 mcp-remote 版本、缺失/重复服务、未知命令、未知启动模式和未知 YAML 布局；所有目标校验通过才写入。仅替换选中配置字段；注释、`!js` 表达式以及其他服务保持原样。工具不输出配置正文，写入前生成权限 600 的原配置备份，避免泄露认证内容。已经在相同持久路径应用过前两项配置的，可在升级 v2 核心后重新运行同一命令补充后台模式。

只想启用第三步、不调整命令或协商方式时，也可在已安装 v2 核心的相应 MCP 的 `config` 下手动增加：

```yaml
startupMode: background
```

保持原 `failOnStartupError` 设置；为 true 时仍会等待。无需为此重装 mcp-remote。默认 blocking 保持 CLI、worker 和未选择后台模式的服务原有启动行为。

## 回退

退出 Desktop 后，将工具报告的 `cordis.patch.yml.before-mcp-startup-时间` 复制回 `cordis.patch.yml`，再启动。恢复到哪一轮设置取决于所选备份：首次改动前的备份恢复 npx/auto，第三步前的备份则保留前两项。仅关闭后台模式可将 `startupMode` 改为 `blocking`；无该字段时也默认 blocking。恢复后必须保留该备份引用的旧 runtime；确认命令不再引用某目录后才可删除它。不要回退整个用户数据目录或覆盖聊天。

## 验证边界

离线回归覆盖实际 rc.3 MCP client 与 SDK：默认 auto 两个进程、legacy 一个进程、工具同步/本地测试工具调用、重连继续使用 legacy、启动中取消与进程回收、严格启动失败、无效模式，以及 YAML 注释/标签/额外参数保留和重复/未知配置拒绝。

第三步补充后台加载屏障、延迟工具/指令/资源就绪、可选失败、严格等待/失败、探测/握手/工具同步中取消、退避取消、动态工具通知、真实 Cordis 卸载/热重载和 v1→v2 补丁升级。完整 Desktop 使用空 HOME、本地受控 MCP 分别验证 Wayland/XWayland 的就绪、取消与严格等待，不用用户凭据，也不发模型请求。

完整配置的真实 MCP 初始化结果与测试耗时另见 `docs/MCP_STARTUP.md`。减少进程和 npm 查询并不保证每次按固定比例加速；OAuth 登录/刷新、远端响应和 Wolfram 内核仍可造成等待。真实 MCP 仅做初始化和工具列表读取，没有模型请求或任务工具调用。

2026-11-01 配套回归：74 项中 72 通过、2 工具缺失跳过；新增配置来源/缺省拒绝、各级目录权限、非目录、安装失败清理及已有锁文件拒绝覆盖，另验证显式旧路径迁移、幂等、未知旧路径拒绝和 YAML 折行路径。实际 npm 前缀安装与现有两入口迁移通过；未做远端登录、模型或工具调用。
