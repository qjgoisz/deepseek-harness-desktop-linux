# 自用 DSH Desktop 项目交接

更新日期：2026-10-28（Asia/Shanghai）。本文件描述当前交付与清理状态；历史过程见 `AGENTS.md` 和 `docs/CHANGELOG.md`。

## 当前交付

- 仓库：`/home/debian/Documents/deepseek-harness/default-workspace/deepseek-harness-desktop-linux`。
- 自用分支：`codex/personal-desktop`。功能提交 `0e8dc5c` 为 KDE/v2rayN 系统代理适配，`0577529` 为 rc.3 侧栏收起背景修复。
- 基线：DSH `0.2.1-rc.3`，bundled Electron 44.4.5、Node 24.21.0、Python 3.12.14、pnpm 11.28.5、Sharp 0.35.5。不是对官方滚动下载当前版本的重新检测。
- 产物：`dist/deepseek-harness_0.2.1-rc.3_amd64.bundled.deb`，同目录有 `.sha256`。
- SHA256：`58eed0612283285419b58e0c248cc6db651ce6307bb08df7a809bece89e1b511`。
- 代理修复包以已安装 rc.3 的独立副本增量打包，未重新下载官方 dmg 或重跑 macOS 载荷转换。其他格式、ARM64、非 KDE 桌面未因本次修改获得新的实测结论。

## 验收与验证

2026-10-28 用户反馈代理修复“可以了”，并要求清理缓存、同步文档和推送。此为人工使用反馈，未逐项说明代理开关、端口修改、模型/插件、窗口后端或长会话覆盖范围。

自动化基线为 56 项中 54 通过、2 项因缺少 RPM/pacman 工具跳过；包括真实载荷副本的本机 HTTP/HTTPS CONNECT、代理切换、旧流式响应继续、新 Node 子进程代理继承及私有 KDE D-Bus 通知。独立 HOME 的完整 Desktop Host 启动/优雅退出通过。成品 CLI/pnpm、Node/Python、Sharp worker 隔离、133 个 ELF 架构、GUI/代理文件一致性及 SHA256 检查通过。

代理功能的支持范围、手动环境变量优先级、CLI/worker 边界和不支持的 PAC/SOCKS 等情况见 `docs/SYSTEM_PROXY.md`。自用外观规则见 `PERSONAL.md`；不要改变交通灯始终显示、侧栏按钮坐标、实色圆角及窗口状态策略。

## 缓存与保留材料

本次已按用户授权清理项目 `dl/`、`out-x64/`、空 `tools/`、解包/打包暂存、测试 HOME、诊断用模块副本和 Python 缓存。系统缓存、现用 DSH 配置/凭据/会话未清理。

保留：

- `dist/` 安装包和校验文件；不会提交到 Git。
- `others/system-proxy-20261028/` 的小体积测试/构建日志、结果 JSON、缓存清理清单；其中的应用副本、解包树与打包工作目录已不存在。
- `others/proxy-diagnosis-20261028/` 的诊断报告及结果；复制的运行时代码和模块链接已清理，原探针不能依赖这些已删除副本直接重跑。
- 本机 `docs/COMPATIBILITY-2026-10-24.md` 继续被忽略，不随提交推送；其中路径与截图描述仅代表历史记录。

## 后续工作约定

1. 先读 `AGENTS.md`、核对当前分支、工作区和全部 worktree；每次提交前实质更新 AGENTS.md。
2. 后续构建需要重新准备下载物和应用树，不能假设旧缓存存在。构建方法见 `docs/AUTO_BUILD.md`。
3. 官方 `latest` 下载地址会滚动覆盖，必须核对解包后的应用与 runtime 清单；检测新的上游版本应作为下一轮适配，不能把本次验收扩展到新版。
4. 测试使用独立 HOME/DSH_HOME/XDG/profile 与端口，不修改或重启用户正在使用的安装实例，不复制登录凭据或发真实模型请求。
5. 本轮按用户要求推送自用分支；实际远端同步状态以 `git status` 与 `git ls-remote` 核对为准，不创建或推送其他分支。
