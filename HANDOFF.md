# 自用 DSH Desktop 项目交接

## 2026-11-11：0.2.2-rc.2

- 分支 `codex/personal-desktop`。从已校验的官方 macOS arm64 开发版 ZIP 构建 `0.2.2-rc.2+systemruntime2` amd64 bundled deb。下载、构建和复验细节见 [兼容性记录](docs/COMPATIBILITY.md)。
- 窗口补丁保留 Windows 的新底色设置，在 Linux 补齐 `screen` 导入。代理补丁保留新版 `createRouteDispatcher` 导出。Desktop Host Cookie 累积修复使用官方载荷中的实现。
- 系统运行时适配 rc.2 Office 技能加载逻辑，保留内置 pnpm 和 PPTX 专用的 python-pptx。LibreOffice 原生包改名为 `bin/dsoffice`，Linux 转换脚本据此安装载荷指定的 WASM 0.2.3。
- 移除 Cookie 补丁后复测，成品 76 项回归通过、2 项跳过。两后端隔离启动、重启和旧 Cookie 清理通过。Office 读写及 WASM 导出 PDF 通过。
- 用户已确认新版验收正常。清理后 `dist/` 仅保留新版成品和校验文件。上版源码由 `personal-dsh-v0.2.2-rc.1` 标记。
