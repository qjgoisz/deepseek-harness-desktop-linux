# Changelog

本项目是 **DeepSeek Harness 桌面端（Electron）的 Linux 移植/重打包**。
格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

---

## 2026-11-11 — 适配 0.2.2-rc.2

- 核对官方更新清单、ZIP 大小与 SHA512，确认应用与 runtime 版本。Electron 44.7.0、Node 24.21.0、Python 3.12.14、pnpm 11.28.5 沿用官方基线。
- 适配主窗口标题栏和代理模块导出，保留每服务 MCP 设置和 Linux 文件锁探测补丁。官方 Cookie 修复已进入桌面载荷。
- 更新系统运行时模式下 Office 技能的 Python 指引。识别新命名的 LibreOffice 原生可执行文件，打包时替换为载荷指定的 WASM 0.2.3。详见 [兼容性记录](COMPATIBILITY.md)。
