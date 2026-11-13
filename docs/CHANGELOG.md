# Changelog

本项目是 **DeepSeek Harness 桌面端（Electron）的 Linux 移植/重打包**。
格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

---

## 2026-11-13 — 适配 0.2.2-rc.3

- 核对官方更新清单、ZIP 大小与 SHA512，以及应用与 runtime 版本。构建沿用官方 Electron 44.7.0、Node 24.21.0、Python 3.12.14、pnpm 11.28.5 基线。
- 从 rc.3 桌面 ZIP 生成系统运行时 amd64 deb。复核官方 Cookie 修复与 Linux 补丁的适用性，验证代理、MCP、文件锁、图片和 Office 链路。详见 [兼容性记录](COMPATIBILITY.md)。
