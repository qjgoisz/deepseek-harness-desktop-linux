# Changelog

本项目是 **DeepSeek Harness 桌面端（Electron）的 Linux 移植/重打包**。
格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

---

## 2026-11-05 — 适配 0.2.2-rc.1

- 核对官方更新清单与完整 ZIP 的大小、SHA512、应用/runtime 版本；核对时默认滚动 DMG 尚未提供本版。本轮从新版 ZIP 完成全流程。
- Linux 平台补丁兼容 PlatformView 新增的第四参数，保留上游更新输入守卫，未知/重复调用拒绝；Electron 默认同步官方 44.7.0，Node/Python/pnpm/原生依赖无版本漂移。
- 新 bundled amd64 deb SHA256 为 22343671318810dd0d48e57cdf79df865431a5e9fcc2f4dd758bf0be8b70f54a。81 项回归 79 通过、2 工具缺失跳过；144 侧栏组合、成品 CLI/pnpm、13 Python 包、图片隔离、133 ELF、29379 资源一致性及校验通过。
- 最终包隔离 Wayland/XWayland 启动/重启、侧栏、原生最大化/全屏和 100 合成 Cookie 检查通过，正常退出；保存整屏截图，普通窗口完整视觉、真实登录/插件/模型、GPU 和长会话待验收。用户反馈修复预设后界面恢复。隔离复查通过，本轮缓存已清理。详见 [本轮兼容性记录](COMPATIBILITY.md)。
