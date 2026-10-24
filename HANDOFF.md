# 自用 DSH Desktop 项目交接

交接日期：2026-10-24（Asia/Shanghai）。本文件记录交接时的本机状态，不表示已经检测官方最新版本。

## 当前请求与下一步范围

用户最初要求“dsh 已更新，请先检测一下是否适配”，随后改为先准备交接，在另一个会话继续。
本次仅核对仓库状态并整理交接，尚未查询或下载 2026-10-24 的最新官方载荷，没有运行新版兼容性检查，也没有进行新一轮适配或 GUI 测试。

接手后先检测最新官方载荷与自用分支的兼容性，报告实际版本、补丁匹配结果和验证边界。是否继续修复、构建与发布，按后续用户指示执行。

## 仓库位置与分支

- 实际项目目录：`/home/debian/Documents/deepseek-harness/default-workspace/deepseek-harness-desktop-linux`。
- 当前分支：`codex/personal-desktop`，默认只维护此自用分支。
- 交接编写前 HEAD：`abfcf81`；本地分支与 `origin/codex/personal-desktop` 跟踪引用一致，工作区干净。此处未另行查询远端；接手时重新核对状态。
- `origin`：`git@github:qjgoisz/deepseek-harness-desktop-linux.git`。
- `upstream`：`git@github:macOS-Terminal/deepseek-harness-desktop-linux.git`。
- 聊天中的旧工作目录 `/home/debian/Documents/deepseek-harness/dsh-test/deepseek-harness-desktop-linux` 已不存在。旧 `/tmp/dsh-personal-desktop` 和 `/tmp/dsh-update-store` 也已不存在，不要使用这些旧路径继续工作。

先阅读根目录 `AGENTS.md`、`PERSONAL.md`、`docs/AUTO_BUILD.md`、`docs/CHANGELOG.md`。每一次 Git 提交前都必须实质更新 `AGENTS.md` 并随同提交，纯文档提交同样适用。

## 必须保留的当前自用行为

- 欢迎页和主界面强制实色；普通窗口 12px 圆角，最大化/全屏布局取消圆角，不请求 KWin 毛玻璃。
- **交通灯现在始终显示**，包括普通窗口、最大化和全屏，可直接点击。这是 2026-10-20 的后续决策；不要恢复早期自用版“顶部悬停才显示”的行为。
- 侧栏顶部按钮位置固定，不再有让位动画。展开态切换按钮为侧栏宽度减 40px；折叠态切换按钮为 128px，新建按钮为 88px。同一侧栏状态下，最大化、全屏和顶部悬停不改变按钮坐标。
- 自用覆盖由 `patches/patch-personal-rounded.py` 实现；上游 GUI 分支仍保持自己的悬停实现，不把自用覆盖混入该分支。
- 非活动窗口不自动激活，交通灯保留失焦降饱和效果；保留底层焦点检查和状态同步。
- 保留上游 `syncTilingFullscreen` 和“Linux 最大化使用全屏布局”的策略，以及既有拖动、双击还原、Wayland 应用图标关联等修复。

## 关键提交与已知适配点

| 提交 | 内容 |
|---|---|
| `c44440e` | 适配 DSH `0.2.1-rc.2`：兼容新版 pnpm 路径，Sharp facade 元信息随原包读取，主进程补丁失败时不写入半成品 |
| `2fdfa57`、`020da79` | 新增维护约定，并要求每次提交前更新 `AGENTS.md` |
| `372eb62` | 将 `local-fixes/dsh-usage-settings/` 插件导航修复独立纳入自用分支，未接入 Desktop 构建 |
| `fb73750` | 自用交通灯改为始终显示 |
| `02ecb01` | 固定侧栏按钮位置，移除随窗口状态变化的位移 |
| `abfcf81` | 记录用户对侧栏按钮修正版的视觉验收反馈 |

已知载荷基线为 DSH `0.2.1-rc.2`，Node 24.21.0、Python 3.12.14、pnpm 11.28.5、Sharp 0.35.5；bundled Electron 使用 44.4.5。这些是旧基线，不能假定最新 DSH 仍使用相同版本。

pnpm 在旧版为 `runtime/pnpm`，在 `0.2.1-rc.2` 为 `runtime/primary-runtime/dependencies/pnpm`。`patch-main.py` 支持两种布局且要求唯一匹配；检测失败时保持主文件原样。Sharp 必须继续通过独立 Node worker 隔离 libvips，不能为升级方便改回 Electron 进程内加载。

## 已有验证及其边界

- 2026-10-18 的 `0.2.1-rc.2` 适配完成 x86_64 bundled deb、CLI、pnpm、图片 worker 和校验验证，并实测 KDE KWin 6.7.4 的 Wayland/XWayland 基础窗口行为。
- 2026-10-20 后续 GUI 修改的离线测试记录为 48 项中 46 项通过、2 项因缺少 RPM/pacman 工具跳过；另外用无头浏览器覆盖交通灯样式和真实侧栏 CSS 的 144 种坐标组合。
- `02ecb01` 后已重新构建 `0.2.1-rc.2` x86_64 bundled deb，验证包内主进程和两个 preload 与应用树一致，CLI、pnpm、Node/Python、图片隔离和 SHA256 通过。
- 用户随后确认侧栏按钮修正版视觉验收通过，记录于 `abfcf81`。用户反馈未逐项注明后端、页面和窗口状态覆盖范围；不能把它扩展为全部 Wayland/XWayland 实机用例通过。
- 新版 DSH、其他桌面环境、其他包格式、ARM64 和带用户插件的长会话均不能据此宣称已验证。本次交接没有重跑这些测试。

## 当前缓存、产物与工具

- `dist/` 只有 `deepseek-harness_0.2.1-rc.2_amd64.bundled.deb.sha256`，对应 deb 已不存在。校验文件不能证明当前存在可安装产物。
- 没有 `out-x64/` 或 `out-arm64/` 应用树，`others/` 中没有 dmg 或 dmg 解包目录；`.app-version`、`.dmg-head` 只是历史记录。
- `dl/` 尚有 Electron 44.4.5 x64、Node 24.21.0 x64、Python 3.12.14 x64 归档和 npm 缓存。是否能复用取决于新载荷的实际版本。
- 本次确认存在 `rg`、`7z`、`node`、`python3`；未找到 `rpmbuild`、`bsdtar`。环境可能变化，接手时再做所需工具检查。
- 默认保留缓存、解包和构建暂存；清理按用户要求或显式选项执行。需要系统软件包时，先告诉用户包名和用途，由用户安装，不提权代装。

## 建议的检测顺序

1. 核对当前分支、工作区修改及 `AGENTS.md`。用户可能在其他会话继续修改，不能直接按本文件覆盖代码。
2. 检查官方 `https://download.deepseek.com/desktop/dsh-latest-macos-arm64.dmg`，将新载荷放入独立缓存位置。按解包后的应用 `package.json` 与 `runtime/primary-runtime/runtime.json` 确认版本，不能只凭 `latest` 文件名或 HTTP 日期。
3. 在独立应用树副本上检查 Linux 原生包替换、主进程、标题栏、两个 preload、个人圆角层、CLI、pnpm、图片 worker 与原生指纹补丁。检查退出码及输出，防止部分补丁失败后继续打包；保留原始载荷以便重试。
4. 运行相关离线回归和脚本语法检查，按实际检测结果列出不兼容点。需要构建验证时，常用命令为 `./auto-build.sh --arch x64 --formats deb --electron bundled --package-jobs 4`，新版 dmg 可通过 `--dmg /绝对路径/新版.dmg` 指定。
5. GUI 只使用工作区构建的独立 Desktop 实例，隔离 `HOME`、`DSH_HOME`、XDG 配置/缓存、`--user-data-dir` 和调试端口；不重启用户正在使用的安装版，不复制真实登录状态。
6. 如需 GUI 验证，分别覆盖 `--ozone-platform=wayland` 与 `--ozone-platform=x11`；在正确的 `welcome.html` 跳过欢迎页后再检查主界面，最大化问题必须实际最大化。圆角应结合整屏或原生几何验证，不能只截页面。测试后仅关闭自己创建的实例。

关于旧插件诊断：用户曾通过禁用 `dsh-genui` 明显缓解长会话卡顿，`billion-context` 可能间接增加会话长度；这是独立问题，不应自动夹带进本次桌面兼容性检查。`local-fixes/dsh-usage-settings/` 也只在明确运行其应用脚本时修改本机插件。
