# deepseek-harness-desktop-linux

把 **DeepSeek Harness 桌面端**（官方仅发布 macOS / Windows 包）移植到 Linux 的
**重新打包工具链**：官方 macOS ZIP 或 DMG 载荷 + 若干公开下载物 → AppImage / deb / pacman / rpm。

工具链支持 **x86_64** 与 **aarch64** 的多种包型；当前实测范围见下文。

自用分支当前适配基线：`@deepseek-ai/dsh-desktop 0.2.2-rc.2`。
本分支使用实色背景与普通窗口圆角，保留全屏交通灯及窗口控件修复。
当前验证范围为 x86_64 bundled deb。
已加入 KDE/v2rayN 系统代理自动读取和动态切换。
支持范围和手动环境覆盖规则见 [系统代理说明](docs/SYSTEM_PROXY.md)。

自用分支另提供按服务选择 MCP 协商方式和后台初始化的补丁。默认仍等待连接；
显式配置 `startupMode: background` 的可选服务可在主界面显示后继续连接，严格服务仍等待。
固定 mcp-remote 本地入口和配置工具须单独启用，安装 deb 不会自动改用户配置。
启用、回退与验证边界见 [MCP 启动说明](docs/MCP_STARTUP.md)。

全部补丁的用途、目标文件及官方载荷/源码对照见 [补丁总览与逐项文档](docs/patches/README.md)。
2026-11-11 从官方 rc.2 ZIP 构建系统运行时 deb。Electron 44.7.0 与载荷一致，Cookie 修复沿用官方实现。来源、成品和验证边界见 [本轮兼容性记录](docs/COMPATIBILITY.md)。

> 本仓库只包含**移植补丁与打包脚本**，不含任何官方二进制载荷（体积与授权原因）。
> 详细的中文使用教程见 **[README.zh.md](README.zh.md)**。

---

## 这个移植在解决什么

官方代码里 Linux 分支基本是空实现，因此移植 = **补齐那些空分支**。逐项：

| # | 问题 | 处理 |
|---|---|---|
| 1 | `main.js` 平台白名单只有 `win32` / `darwin`，Linux 启动即 `unsupported platform` | 加入 `linux`，并上报 `x-client-platform: desktop-linux` |
| 2 | 原生模块只带 macOS / Windows 预编译产物 | 换成 `@img/sharp-linux-*`、`@koromix/koffi-linux-*`、`node-pty` prebuilds 等 9 类 |
| 3 | 运行时载荷是 macOS 构建 | 换 Linux 版 Node 24.21.0 + Python 3.12.14（13 个科学计算包）+ pnpm |
| 4 | 原实现依赖 `process.resourcesPath`，系统 Electron 下指错目录 | `DSH_DESKTOP_RESOURCES_DIR` 覆盖 |
| 5 | 系统 Electron 下 `app.isPackaged` 为 false，被误判为开发模式 | `DSH_DESKTOP_FORCE_PACKAGED=1` |
| 6 | 原生插件限制 Electron/V8 指纹 | 二进制放宽匹配（**不降级 Electron**） |
| 7 | **libvips 在 Electron 内段错误，JS 无法捕获，整个应用崩溃** | 进程隔离：Sharp 调用转发到独立 Node worker |
| 8 | Linux 无窗口装饰规则，且托盘代码被 `win32` 门禁挡住 | 复用应用自身的 `data-windows-titlebar` 模式并补充 Linux 托盘 |

---

## 目录结构

```
├── patches/
│   ├── patch-main.py            平台准入 / resources 根 / 打包态 / 托盘 / CLI 路径
│   ├── patch-system-proxy.py    KDE/v2rayN Desktop 后台代理适配
│   ├── system-proxy/           系统代理适配模块及连接池控制器
│   ├── patch-mcp-negotiation.py MCP 协商方式与可选后台初始化（默认行为不变）
│   ├── patch-flock-libc.py      会话锁 libc 探测排除网络诊断
│   ├── patch-mac-chrome.py      左置交通灯、窗口控制及 GUI 补丁组合入口
│   ├── patch-kde-material.py    KDE 材质基础层（自用层禁用 blur）
│   ├── patch-fullscreen-reveal.py 全屏指针桥、焦点、状态及 Wayland 双击
│   ├── patch-linux-identity.py  Linux 桌面项身份关联
│   ├── patch-personal-rounded.py 自用实色、圆角、交通灯及固定侧栏按钮
│   ├── patch-fingerprint.py     按 ELF 符号定位并放宽 V8 指纹白名单（x64 / arm64）
│   ├── patch-titlebar.py        Linux 标题栏中间配置（chrome 的顺序依赖）
│   └── upgrade-mac-chrome.py    旧 chrome 树的手工迁移工具（非自动构建入口）
├── image-worker-src/
│   ├── client.cjs               Sharp API 兼容层（Electron 内，只记录并转发）
│   ├── worker.cjs               真正执行 libvips 的独立 Node 进程
│   └── verify-image-worker.cjs  隔离效果自检
├── icons/                       桌面项 + 16→512 全套 hicolor 图标
├── build-packages.sh            打全部格式（deb×2 / pkg.tar.zst / rpm / AppImage）
├── install-image-worker.sh      把 Sharp 替身包装入某棵应用树
├── verify-launch-x64.sh         五种格式逐个解包并实测启动
└── docs/
    ├── patches/                全部补丁的独立文档与上游审计
    ├── ARTIFACTS.md             产物说明：安装方式、依赖策略、验证记录
    ├── CHANGELOG.md             当前版本变更
    └── COMPATIBILITY.md         当前兼容性报告
```

---

## 自动构建工具链

```bash
./auto-build.sh --dry-run
./auto-build.sh --arch x64 --formats deb --electron bundled --system-runtime --package-jobs 4 \
  --archive /绝对路径/已校验的/deepseek-harness-0.2.2-rc.2-mac-arm64.zip
```

默认保留缓存、解包文件、构建目录和历史产物；`--clean` 显式清理中间文件。
支持 AppImage、deb、RPM 与 pacman，`--electron` 选择 bundled/system 包型，
`--package-jobs` 调整打包压缩线程数。ARM64 尚未在真实设备上完成运行验证。

依赖、分阶段执行、网络配置与验证边界见 [自动构建文档](docs/AUTO_BUILD.md)。
窗口外观使用本仓库现有补丁；本工具链不更改其默认材质或窗口行为。

## 安装与校验

构建输入、安装命令和校验方式见 [产物说明](docs/ARTIFACTS.md)和[中文构建教程](README.zh.md)。

## 两个值得说明的实现

### Sharp / libvips 进程隔离

SIGSEGV 是进程级信号，JS 层无法捕获，因此**只能真正隔离进程**：

```
resources/
├── app/dsh/node_modules/sharp/     替身包：只转发调用，不含原生库
└── image-worker/
    ├── client.cjs                  记录链式调用 → 转发给 worker
    ├── worker.cjs                  在独立 Node 中重放并执行 libvips
    └── worker-modules/node_modules/ 私有依赖闭包（standalone Node 读不了 asar）
```

worker 崩溃只影响当次图片操作：客户端自动重启，连续 3 次失败后熔断，桌面端不受影响。

### 窗口装饰

Linux 窗口复用应用内置的自绘标题栏布局。左侧交通灯通过 IPC 操作窗口，Linux 平台标识保留 Ctrl 快捷键语义。当前窗口材质、全屏和侧栏位置见 [自用外观说明](PERSONAL.md)。

## 许可

应用本体版权归 **DeepSeek**。请遵守原应用许可条款。
