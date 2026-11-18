# 自用 DSH Desktop 项目交接

## 2026-11-18 · 0.2.2-rc.5

- `codex/personal-desktop` 上的 `PKGBUILD` 和 `.SRCINFO` 已更新到官方 rc.5 桌面 ZIP。Electron 44.7.0、Node 24.21.0、Python 3.12.14、pnpm 11.28.5 构建基线与上一版相同。
- Arch x86_64 宿主已安装 `0.2.2_rc.5+systemruntime1-1`。系统运行时、包校验、升级解析、隔离 Wayland/XWayland 启动及回归测试已核对。交付后 `dist/` 保留 rc.5 安装包和 SHA256 校验文件。[成品和用法](docs/ARTIFACTS.md)
- 官方载荷保留 Host Cookie 修复，Linux 补丁链应用成功。GitHub HTTPS 的隔离测试复现了两项配置问题，分别是 KDE 绕过通配符拒绝和 HTTP 代理端口的 URL 协议误设，见 [系统代理](docs/SYSTEM_PROXY.md)。
- 当前和上一适配版的验证记录见 [rc.5](docs/COMPATIBILITY.md) 和 [rc.3](docs/COMPATIBILITY-PREVIOUS.md)。
