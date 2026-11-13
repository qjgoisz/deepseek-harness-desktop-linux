# 自用 DSH Desktop 项目交接

## 2026-11-13 · 0.2.2-rc.3

- 分支 `codex/personal-desktop`。使用已核对的官方 macOS arm64 开发版 ZIP 构建 `0.2.2-rc.3+systemruntime3` amd64 bundled deb。来源、SHA512、构建步骤和安装包校验见 [兼容性记录](docs/COMPATIBILITY.md)。
- 保持 Electron 44.7.0、Node 24.21.0、Python 3.12.14、pnpm 11.28.5 的官方构建基线。成品沿用 Debian Node/Python、内置 pnpm、私有 python-pptx 和 LibreOffice WASM 0.2.3。
- 官方载荷保留 Host Cookie 修复。现有 Linux 补丁链应用成功，复核见 [补丁总览](docs/patches/README.md)。
- 成品通过 APT 升级模拟、图片并发与 Office 回归，76 项自动回归通过、2 项因缺少 RPM/pacman 工具跳过。隔离 Wayland/XWayland 桌面通过启动、侧栏、最大化和全屏检查。
- 用户已完成桌面验收。侧边栏入口的取消固定状态会在重启后重置，按上游实现暂予保留。验收未报告其他问题。
- 验收后清理本轮下载、解包、打包和测试暂存及 rc.2 安装包。`dist/` 保留 rc.3 deb 与校验文件。
