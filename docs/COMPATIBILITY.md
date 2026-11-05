# DSH 0.2.2-rc.1 Desktop 适配与验证

2026-11-05（Asia/Shanghai），分支 `codex/personal-desktop`，基于 `924b73b`。
构建测试使用隔离环境。会话复查仅使用临时副本。上一版见 [兼容性归档](COMPATIBILITY-PREVIOUS.md)。

## 官方来源

- [官方桌面更新清单](https://download.deepseek.com/dsh-desk/feeds/mac-arm64/nightly-mac.yml)已提供 `0.2.2-rc.1`；发布时间为 2026-11-04 09:24:35.800 UTC，本轮复核时分阶段比例为 100%，ZIP 摘要与首次核对一致。
- 完整 [macOS arm64 ZIP](https://download.deepseek.com/dsh-desk/bin/mac-arm64/deepseek-harness-0.2.2-rc.1-mac-arm64.zip)为 353501474 字节。实际计算 SHA512，与清单的 base64 值一致：`mHn+lwXZd7I3ZvakFhRg0lxrGe0pNSmWhMU65AQiyrjy/yfa0C8Rq6nQ6tLcxnqdFYl+j5BN4ghOToTLiT2qGA==`。
- ZIP SHA256：`7878aaa7e8a82c95b8e92a9dd27df1263d644fa0783438692b236e7477bdc24d`。
- 解包核对应用 `package.json` 和 `runtime/primary-runtime/runtime.json`，均为 `0.2.2-rc.1`；应用记录的构建提交为 `c59d10aff167ad7eefead4b3a9082fb57c8fbfe8`。未将该提交视为已经重新审计的公共源码快照。
- 核对时默认滚动 DMG 尚未提供本版，本轮从上述官方 ZIP 完成全流程。

## 适配范围

- `patch-main.py` 兼容 `DesktopPlatformView` 新增的更新输入守卫参数：仅透传 Linux 平台，完整保留第四个参数及其逻辑。支持旧/新两个完整已知调用；未知、重复或已处理调用拒绝继续，整份主进程补丁失败时不写入部分结果。新增回归覆盖两种调用及守卫保留和拒绝未知状态。
- 官方 Electron Framework 的 Info.plist 为 `44.7.0`，Linux bundled Electron 同步使用 `44.7.0`，更新构建默认值。Electron 与 Node 归档按发行清单 SHA256 校验。
- Node `24.21.0`、Python `3.12.14`、pnpm `11.28.5`、Sharp `0.35.5` 和 13 个 Python 包均沿用新载荷版本。8 个平台包加 node-pty prebuild 共 9 项转换完成，无版本漂移；LibreOffice 沿用同版本 WASM 回退。
- 保留既有窗口策略、图片 worker 隔离、KDE/v2rayN 代理、MCP v2、libc 探测及 Desktop Cookie 修复。对照新版实际模块，代理仍只读环境变量，MCP 仍固定 auto/等待连接，flock 仍调用完整报告，Desktop 仍通过持久 Cookie 重复认证；未发现这几项的官方等价替代。原生依赖的指纹门禁仍存在。官方 master 快照已修复 Desktop Cookie 累积，发布 ZIP 仍需补丁。逐项复核见 [补丁总览](patches/README.md)。

```sh
./auto-build.sh --arch x64 --formats deb --electron bundled --package-jobs 4 \
  --archive /绝对路径/已校验的/deepseek-harness-0.2.2-rc.1-mac-arm64.zip
```

本轮准备/树生成/打包全部完成。为隔离构建附带的可选冒烟流程，构建时设置独立 XDG 配置/缓存/数据和 DSH_HOME；本机缺少 xvfb-run，该附带冒烟未运行，Desktop 实机检查另行记录。

## 成品与自动化验证

- 成品：`dist/deepseek-harness_0.2.2-rc.1_amd64.bundled.deb`，261037952 字节。
- SHA256：`22343671318810dd0d48e57cdf79df865431a5e9fcc2f4dd758bf0be8b70f54a`；在 dist 中执行同名 `.sha256` 校验通过。
- 构建树和成品解包后各运行 81 项回归：79 通过，2 项因缺少 RPM/pacman 工具跳过。包括真实新载荷的 MCP 协商/后台生命周期、HTTP/HTTPS CONNECT、私有 KDE D-Bus、实际跨进程文件锁和 Cookie HTTP/WebSocket/100 次换端口回归。
- 成品元数据、CLI、pnpm、Node/Python、13 个 Python 包版本、Sharp 图片 worker 隔离及 133 个 ELF 架构检查通过。
- 成品 29379 个资源文件与已验证构建树逐文件一致；主进程和两个 preload 语法检查通过。新载荷侧栏 CSS 的 144 种布局组合通过，构建 shell 语法检查通过。
- 首轮尚未转换的 macOS 副本运行测试时，实际文件锁用例因缺少 Linux 模块失败；换入正确的 Linux 同版本模块后，构建树及成品完整回归通过。不将该准备阶段错误算作新版锁兼容性通过证据。

## Desktop 图形测试与边界

- 从最终 deb 解出的原始文件运行，独立 HOME、DSH_HOME、XDG 配置/缓存/数据、user-data-dir、随机 Inspector 与后端端口，一次一个实例，无用户配置、插件或凭据。两后端均等待真实可见的 welcome.html 后跳过，确认主窗口可见且页面加载完成。
- Wayland 启动/重启为 2603/2111 ms，XWayland 为 2568/2068 ms，包含 Inspector 和合成 Cookie 操作，不是用户原配置冷启动基准。各次启动前后 100 个合成旧 Cookie 均保持 100，正常退出码均为 0。
- 两后端的主界面、侧栏切换、原生最大化/还原和真全屏/退出全屏通过；交通灯保持可见，最大化/全屏同步 data-fullscreen，收起后背景宽度为 0。
- 保存了两后端共 8 张整屏截图，实际查看 Wayland 主界面及两后端最大化截图。最大化画面显示正常；普通窗口受当前多显示器放置影响，部分边缘不在截图可见区，不将其视为完整圆角/拖动验收。原始截图已清理。
- 初版驱动把预加载的隐藏主窗口误当作可交互窗口；修正为等待可见欢迎页后完整测试通过。初次截图工具受配置目录写入限制弹出提示，改为独立配置后重拍成功。两者均是测试驱动/隔离问题，没有因此修改生产代码。
- no-sandbox、disable-gpu、Inspector 仅为测试参数，不进入成品；成品文件没有测试注入。未覆盖真实登录、用户插件/模型、原会话、GPU、拖动/顶栏双击或长会话。空 HOME 未建立默认工作区时显示选择文件夹提示，不据此推断现用工作区故障。
- 用户修复本机预设对旧入口的引用后反馈界面恢复。隔离复查确认 5 个自定义预设可加载和新建会话，20 份旧会话可读取，11 个主会话可恢复。测试使用临时工作区，未发送模型请求。
- 按用户要求清理了本轮下载、解包、构建暂存、测试 HOME、原始日志及截图，保留安装包、校验文件和脱敏摘要。测试实例已关闭，无临时 worktree 绑定。
