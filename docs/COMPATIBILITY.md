# DSH 0.2.2-rc.5 Desktop 适配与验证

2026-11-18（Asia/Shanghai），分支 `codex/personal-desktop`，基于 `21f5a7e`。上一适配版见 [rc.3 兼容性归档](COMPATIBILITY-PREVIOUS.md)。

## 官方来源

- macOS arm64 开发版清单标为 rc.5，核对时分发比例为 30%，发布时间为 2026-11-18 19:45:57.670（Asia/Shanghai）。[官方清单](https://download.deepseek.com/dsh-desk/feeds/mac-arm64/nightly-mac.yml)
- ZIP 为 362852032 字节，SHA512 为 `28C1+oaRcSjOwWvzqjXA4Cpic7bvTs++wOu3moAfRQMLhTPZv40G3GQTir0wuyuPGh/PsQH0ykb/qJD4pnWMxA==`，与清单一致。SHA256 为 `c169975831897ee0925dbc23a661893511eff29bf645a7842ae1c2d2b5d5b8a0`。[官方 ZIP](https://download.deepseek.com/dsh-desk/bin/mac-arm64/deepseek-harness-0.2.2-rc.5-mac-arm64.zip)
- `app.asar` 内的应用 `package.json` 与 `runtime/primary-runtime/runtime.json` 均为 `0.2.2-rc.5`。应用记录的构建提交为 `3f85d888b1297107937d9bd5b853f7e733e179a4`，源码对照使用官方标签 `9c2670d3bce5275e0d1610272958121af87787bb`。[官方发布说明](https://github.com/deepseek-ai/deepseek-harness/releases/tag/dsh-v0.2.2-rc.5)

## 构建与补丁

- 从实际载荷确认 Electron 44.7.0、Node 24.21.0、Python 3.12.14、pnpm 11.28.5。保留同版本的 8 项 Linux 平台原生依赖和 node-pty prebuild，包括 Sharp 0.35.5 和 LibreOffice Kit WASM 0.2.3。
- 官方载荷保留内存 Host Cookie 和旧认证条目清理。Linux 窗口、KDE 动态代理、MCP 协商与后台启动、libc 探测、指纹门禁及系统运行时补丁通过原补丁链。官方侧栏说明仍规定插件重新加载时重置取消固定状态。[补丁总览](patches/README.md) [官方侧栏说明](https://github.com/deepseek-ai/deepseek-harness/blob/9c2670d3bce5275e0d1610272958121af87787bb/packages/client/ui-sidebar/README.zh.md#L44)
- Arch `makepkg` 完成源码校验、构建及打包。验证时从签名通过的 Arch 包临时解出 `unzip`，以 `--nodeps` 运行并用 `pacman -T` 单独核对宿主依赖。系统 Electron 44.11.2、Node 26.13.1、Python 3.14.10、pnpm 12.21.0 用于成品测试。

## 成品验证

- `0.2.2_rc.5+systemruntime1-1` 的包信息、SHA256 和 `pacman -U --print` 升级解析均通过。[本轮安装包](ARTIFACTS.md)
- 从最终包解出主进程和两个 preload，语法检查通过。两个 preload 与构建树一致，主进程包含打包阶段的系统 Node 和 pnpm 路径改写。隔离 KWin 的 Wayland 与 XWayland 均从欢迎页进入并渲染主界面。
- CLI 报告 rc.5，系统 pnpm 为 12.21.0。通过 CLI 离线添加、锁文件重放、移除本地测试依赖，并用 pnpm 12 重放由随载荷的 pnpm 11 生成的测试锁文件。
- 实际调用 `load_workspace_dependencies`，返回系统 Node、Python、pnpm 和八项 Office Python 库。系统 Python 读写 DOCX、XLSX、PPTX 通过。图片 worker 通过自检，覆盖同图并发、旧图读取、20 图并发缩放及坏数据拒绝。
- 自动回归 75 项通过，因缺少 deb/RPM 工具跳过 3 项。实际载荷的 Cookie、代理热切换、MCP 和 libc 用例通过。
- 隔离桌面冒烟使用空 profile 和软件渲染。真实账户、会话、第三方插件、GPU、窗口最大化与全屏交互及 Office WASM 导出留待独立验收。

## GitHub HTTPS 诊断

KDE 排除列表中的 IP 通配形式会使适配器拒绝该次读取。排除规则在隔离配置中改用 IPv4 CIDR 后，原 HTTPS 代理字段仍在代理端口的 TLS 握手时失败。将同一地址的代理 URL 改为 `http://` 后，rc.5 Host 的 GitHub HTTPS 请求返回 200，继承该策略的 Git 进程读到了公开仓库 HEAD。用于复测的配置与日常桌面隔离。[配置说明](SYSTEM_PROXY.md#github-https-超时)


## 2026-11-21 主页元数据重打包

- 使用修正主页为 `https://deepseek.com/harness/` 的 `PKGBUILD`，从固定官方 ZIP 重新走 `makepkg` 流程。版本与 pkgrel 仍为 `0.2.2_rc.5+systemruntime1-1`。本次源码校验、构建、依赖解析和包校验通过，宿主 pnpm 为 12.22.0。[产物与新 SHA256](ARTIFACTS.md)
- 新旧包的 25,005 项应用文件、目录和链接逐项一致，包元数据已核对官方主页。最终包解出后验证 CLI、系统 pnpm、主进程和两个 preload 的语法以及图片 worker 自检。相同载荷沿用前轮兼容性检查。
- 构建自带 Xvfb 冒烟遇到宿主 NVIDIA EGL 初始化崩溃。后续在独立 HOME、网络和 PID 命名空间的 Xvfb 中指定 Mesa 软件渲染，最终包成功跳过欢迎页并显示主界面。

## 2026-11-23 官网 DMG 重打包

- 使用[官方下载页](https://deepseek.com/harness/)的 Apple Silicon DMG 通过 `makepkg` 重建同版本 Arch 包。DMG 为 276237948 字节，SHA256 为 `9f0c4406ce97f0cdd3862ba1e70a085b422dbeb1390fdeb8a6e810c38b0a8ffd`。应用与运行时仍为 `0.2.2-rc.5`，Electron 44.7.0、Node 24.21.0、Python 3.12.14、pnpm 11.28.5。[官方 DMG](https://download.deepseek.com/desktop/dsh-latest-macos-arm64.dmg)
- 最终包与 11 月 21 日的 ZIP 构建逐项比较，25,005 项应用文件、目录和链接的类型、权限与内容均一致。包元数据、依赖解析、主进程与两个 preload 的语法、CLI、系统 pnpm 12.22.0、图片 worker 和交付包 SHA256 均通过。[成品与校验和](ARTIFACTS.md)
- 构建内置冒烟报告 X 显示不可用。将包内启动器和应用挂载到独立网络与 PID 命名空间，在 Xvfb 中指定 Mesa 软件渲染，使用空 profile 跳过欢迎页，确认主界面渲染。
