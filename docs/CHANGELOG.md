# Changelog

本项目是 **DeepSeek Harness 桌面端（Electron）的 Linux 移植/重打包**。
格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

---

## 2026-11-18 — 适配 0.2.2-rc.5

- 核对官方开发版清单、ZIP 大小和 SHA512，以及应用与 runtime 版本。Electron 44.7.0、Node 24.21.0、Python 3.12.14、pnpm 11.28.5 构建基线与上一版相同。
- 更新 Arch `PKGBUILD` 和 `.SRCINFO`，构建系统运行时包。复核官方 Cookie 修复和现有补丁，验证双显示协议启动、系统 pnpm、Office Python 库和图片 worker。[兼容性记录](COMPATIBILITY.md)
