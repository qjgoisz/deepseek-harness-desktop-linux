# 自用 DSH Desktop 项目交接

更新日期：2026-10-29（Asia/Shanghai）。当前维护分支为 `codex/personal-desktop`；本次维护提交包含 MCP 启动优化及必要测试、文档。历史细节见 AGENTS.md 与 docs/CHANGELOG.md。

## 当前功能与边界

- 基线为 DSH 0.2.1-rc.3，Electron 44.4.5、Node 24.21.0、Python 3.12.14、pnpm 11.28.5、Sharp 0.35.5；自用实色圆角、固定侧栏按钮和 KDE/v2rayN 代理适配保持原状。
- MCP 构建补丁 v2 支持按服务 auto/legacy 协商与 blocking/background 启动，默认 auto/blocking；严格服务始终等待。后台连接完成后注册真实工具，不预注册占位工具，重连、通知、退出和热重载由原连接管理。
- local-fixes/mcp-startup/ 提供固定 mcp-remote 0.15.1 的公共锁文件和显式配置工具，检查 v2 核心并备份配置，只修改 Wolfram/OpenAlex/Exa 的指定字段，不安装用户级核心覆盖包。
- 安装 deb 不会自动启用这些配置；可以按 docs/MCP_STARTUP.md 单独启用后台模式，或显式运行工具应用三项优化。配置工具与打包流程分离，不修改现用实例。
- 官方 rc.4 Desktop 更新仍暂停；最近一次快速查询清单仍指向 rc.3，不将 npm rc.4 发布当作桌面载荷已可用。
- 用户已取消 npm Web 迁移，相关脚本、文档、工具包和数据副本已清理；今后继续维护 Desktop，不恢复迁移流程。

## 当前本机产物

- 当前 deb：dist/deepseek-harness_0.2.1-rc.3_amd64.bundled.deb，同目录附 .sha256。
- SHA256：42ccb7170636f94bf0423eed0f53dc5345299ae64b62bf723c4cad206ddcfcae。
- 前两步 v1 包位于 dist/previous-mcp-step12-20261029/，SHA256 为 f38c1204e8c32cfff149833ee56c35bcc9c990baa079cdca1f8cd33f77417460；更早代理修复包位于 dist/previous-20261028/，SHA256 为 58eed0612283285419b58e0c248cc6db651ce6307bb08df7a809bece89e1b511。
- 当前包从上一版 rc.3 deb 独立解包升级 MCP client 后增量生成；未重新下载/转换官方 dmg。主进程中的临时窗口观测和退出注入在打包前已还原，GUI、代理及运行时与上一版一致。
- dist 成品仅本机交付，不进入 Git，也未创建远端 release；没有安装或重启用户的现用 Desktop。实际源码提交和远端同步状态以 git log、git status 及推送结果为准。

## 已验证

- 完整回归 62 项：60 通过、2 缺少 RPM/pacman 工具跳过；包括原载荷/v1 升级/v2 幂等、未知补丁拒绝、配置工具旧核心保护及 12 个后台生命周期场景。
- Wayland/XWayland 各通过受控慢 MCP 下主界面先显示、后注册工具、退出取消和严格等待，共六项完整 Desktop 检查。使用空 HOME、独立配置与端口、本地假 MCP，无用户凭据、真实任务工具或模型调用。
- 受控测试使用 no-sandbox/disable-gpu，不写入成品参数，不代表 GPU 或窗口外观全矩阵验收。以原生 BrowserWindow 显示状态和整屏截图核对，不能用 DOM visibility 代替原生窗口显示。
- 成品重新解包后的 62 项回归、CLI/pnpm、13 项 Python 包、Sharp worker 隔离、133 个 ELF、9 个 GUI/代理/MCP 文件一致性与 SHA256 通过。
- 原真实配置测试中 OpenAlex/OCR 成功，但 Exa 要求登录、Wolfram 隔离初始化未通过；完整 Host 当时约 66–67 秒包含失败/超时，不能称为全部就绪。本轮后台模式验收不能替代真实服务及用户全插件启动验收。

## 清理与继续维护

- 工作区曾约 55G，下载物、解包/应用树、测试 HOME、凭据副本、node_modules 和原始日志已清理。当前约 767M，主要保留三个 Desktop deb 及少量本机验收记录。
- others/mcp-background-20261029/ 保留小日志、脱敏 verification.json、结果 JSON 和私有整屏截图；截图包含其他应用窗口，不得公开上传。其他 others/ 中的报告是历史证据，不能假设其中旧私有测试目录仍存在。
- docs/COMPATIBILITY-2026-10-24.md 继续忽略，不随提交交付。后续构建/集成重测需重新准备独立载荷，不能恢复或依赖已取消的 Web 迁移副本。
- 先读 AGENTS.md，核对当前分支与所有 worktree，保留用户修改。每次提交前实质更新 AGENTS.md；提交和推送只针对用户授权的自用分支，交付时报告提交号和推送结果。
