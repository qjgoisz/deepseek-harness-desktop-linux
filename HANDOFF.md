# 自用 DSH Desktop 项目交接

## 2026-11-25 · Arch 包名迁移

- `codex/personal-desktop` 的 Arch 包名为 `deepseek-harness-desktop-macos-style`，版本为 `0.2.2_rc.5+systemruntime1-1`。用户已验收，宿主已安装新包。旧包和本轮暂存已清理，`dist/` 保留新包与复核过的 SHA256。[成品和用法](docs/ARTIFACTS.md)

## 2026-11-23 · 0.2.2-rc.5

- 交接时检出 `codex/personal-desktop`，本地 `dee4c95` 比远端跟踪分支 `9d07eaa` 多一个提交。该提交移除了旧 MCP 运行时的忽略规则，npm 全局安装流程继续使用。构建及验收基线为下述 rc.5 成品。
- `codex/personal-desktop` 上的 `PKGBUILD` 和 `.SRCINFO` 固定了官网 rc.5 Apple Silicon DMG 的 SHA256。构建基线为 Electron 44.7.0、Node 24.21.0、Python 3.12.14、pnpm 11.28.5。
- Arch x86_64 宿主已安装 `0.2.2_rc.5+systemruntime1-1`。系统运行时、包校验、升级解析、隔离 Wayland/XWayland 启动及回归测试已核对。交付后 `dist/` 保留 rc.5 安装包和 SHA256 校验文件。[成品和用法](docs/ARTIFACTS.md)
- 官方载荷保留 Host Cookie 修复，Linux 补丁链应用成功。GitHub HTTPS 的隔离测试复现了两项配置问题，分别是 KDE 绕过通配符拒绝和 HTTP 代理端口的 URL 协议误设，见 [系统代理](docs/SYSTEM_PROXY.md)。
- 2026-11-21 修正包元数据主页并用 `makepkg` 按相同版本号重打包。25,005 项应用文件、目录和链接与之前的 rc.5 包一致，产物记录和 SHA256 已更新。交付后已按用户要求清理本轮构建和测试暂存，保留新成品及校验文件。
- 2026-11-23 用官网 DMG 构建同版本 Arch 成品。包内载荷与此前已验收的 ZIP 成品逐项一致，成品通过包校验、CLI、图片 worker 和隔离桌面启动检查。
- 官网 DMG 构建已通过用户验收。本轮下载、构建和隔离测试暂存已清理，保留 `dist/` 内的成品和校验文件。
- rc.5 官网 DMG 构建基线见 `personal-dsh-v0.2.2-rc.5`（`e089bd3`），上一适配版见 `personal-dsh-v0.2.2-rc.3`（`21f5a7e`）。对应报告见 [rc.5](docs/COMPATIBILITY.md) 和 [rc.3](docs/COMPATIBILITY-PREVIOUS.md)。
- 当前构建加入 Agent 预设依赖检查、Sharp 隔离重装、Netlink 收包退避和最终包验证。Arch x86_64 成品通过 Xvfb、Wayland 与 XWayland 主界面检查，三条路径均确认桌面进程加载了包内守卫。用户验收通过后已清理暂存，`dist/` 保留本次成品及复核过的 SHA256。[验证用法](docs/AUTO_BUILD.md#验证最终安装包)
