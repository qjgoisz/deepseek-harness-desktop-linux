# 自用 DSH Desktop 项目交接

## 2026-11-11：0.2.2-rc.2

- 分支 `codex/personal-desktop`。从已校验的官方 macOS arm64 开发版 ZIP 重新构建 `0.2.2-rc.2+systemruntime3` amd64 bundled deb。下载、构建和复验细节见 [兼容性记录](docs/COMPATIBILITY.md)。
- `+systemruntime3` 合并图片 worker 的同图并发上传，并在缓存引用失效时携带原图字节重试一次。成品图片自检、三轮各 20 张附件的请求图片准备、APT 升级模拟和 76 项回归通过，RPM/pacman 检查各跳过 1 项。用户桌面验收未复现原问题。
- 窗口补丁保留 Windows 的新底色设置，在 Linux 补齐 `screen` 导入。代理补丁保留新版 `createRouteDispatcher` 导出。Desktop Host Cookie 累积修复使用官方载荷中的实现。
- 系统运行时适配 rc.2 Office 技能加载逻辑，保留内置 pnpm 和 PPTX 专用的 python-pptx。LibreOffice 原生包改名为 `bin/dsoffice`，Linux 转换脚本据此安装载荷指定的 WASM 0.2.3。
- 移除 Cookie 补丁后复测，成品 76 项回归通过、2 项跳过。两后端隔离启动、重启和旧 Cookie 清理通过。Office 读写及 WASM 导出 PDF 通过。
- 验收后已清理本轮缓存、打包暂存及旧 deb，`dist/` 仅保留 `+systemruntime3` 及校验文件。rc.1 源码由 `personal-dsh-v0.2.2-rc.1` 标记。
