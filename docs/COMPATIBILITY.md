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

## 2026-11-23 构建检查与 Netlink 退避

- 同版本 Arch x86_64 包通过最终归档校验。从包内启动器分别在隔离的 Xvfb、Wayland 和 XWayland 中跳过欢迎页并渲染主界面，三条路径均确认加载包内 Netlink 守卫。模拟 Netlink 收包拒绝时测到 1、2、4、8、8 毫秒的封顶退避，原始错误码不变。
- 包内 CLI、pnpm、20 个 Agent 预设相关静态导入和图片 worker 自检通过。移除 ACL 依赖的临时副本触发检查失败。Sharp 脚本重跑两次仍保留原生 worker 依赖，大图、双帧 GIF、并发缓存及截断 JPEG 均通过测试。自动回归 75 项通过、4 项跳过。
- 用户已验收，清理本轮构建与隔离测试暂存。最新成品和 SHA256 见[产物说明](ARTIFACTS.md)。

## 2026-11-25 Arch 包名迁移

- 第一次改名时重打包了 11 月 23 日的成品，版本仍为 `0.2.2_rc.5+systemruntime1-1`。许可证移到新包名对应目录。两份包的 25,008 项安装文件、目录和链接经清单对照，类型、权限、属主、内容摘要和链接目标一致。
- 使用宿主包数据库的隔离副本，确认 `pacman -U` 在同一次事务中移除旧包并安装新包。安装后文件完整性和旧包名依赖解析均通过。
- 新包的 SHA256、CLI、pnpm、Agent 预设依赖和图片 worker 通过检查。隔离 Xvfb、原生 Wayland 和 XWayland 均显示主界面并加载 Netlink 守卫。自动回归 75 项通过、4 项跳过。[新包与迁移命令](ARTIFACTS.md)
- 用户已验收并在宿主安装新包。旧包和重打包暂存已清理，交付包 SHA256 已复核。
- 包名随后缩短为 `dsh-desktop-macos-style`。同版本的 25,008 项载荷清单复核通过，许可证位于短包名目录。隔离的 pacman 事务成功从上一包名迁移，新包通过 SHA256、CLI、pnpm、图片 worker 和三种显示模式的启动检查。使用包内载荷运行回归，76 项通过，3 项因缺少 deb/RPM 工具跳过。

## 2026-11-27 Arch 打包规范化

- 重新下载官网 Apple Silicon DMG，大小为 276235917 字节，SHA256 为 `a257ded3fbcb9211d5ea0329cec68a07bbd05a5caaa73fd46693c02aa02c52e9`。包内应用和运行时均为 `0.2.2-rc.5`，应用构建提交为 `3f85d888b1297107937d9bd5b853f7e733e179a4`，Node 和 Python 版本与此前载荷一致。[官方 DMG](https://download.deepseek.com/desktop/dsh-latest-macos-arm64.dmg)
- Arch 包采用上游版本 `0.2.2_rc.5`、`pkgrel=2` 和 `epoch=1`。资源移入 `/usr/lib/dsh-desktop-macos-style/`，保留启动器和桌面项。补齐直接依赖，将 Office 和数据处理的 Python 库移至 `optdepends`。跨发行版脚本生成的 pacman 包也使用标准许可证路径和系统安装钩子。
- 隔离 pacman 事务从 `0.2.2_rc.5+systemruntime1-1` 升级成功，25,008 个条目无缺失。成品通过 CLI、pnpm、图片 worker、Netlink 守卫以及 Xvfb、原生 Wayland 和 XWayland 启动检查。隔离遮蔽系统 Python 第三方库后，原生 Wayland 主界面仍正常启动。自动回归 76 项通过，3 项因缺少 deb/RPM 工具跳过。
- 在同一 Arch 宿主上复用已准备的依赖缓存，以相同构建输入和固定 `SOURCE_DATE_EPOCH` 完整运行两次 `makepkg`，成品逐字节一致。空缓存构建需要下载运行时和原生依赖。独立 chroot 的 `repro` 验证尚未运行。
- 用户已验收，复核宿主已安装 `1:0.2.2_rc.5-2`。上一版成品及本轮构建和测试暂存已清理，当前成品 SHA256 已复核。[产物说明](ARTIFACTS.md)
