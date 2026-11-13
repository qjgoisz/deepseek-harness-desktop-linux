# DSH 0.2.2-rc.2 Desktop 适配与验证

2026-11-11（Asia/Shanghai），分支 `codex/personal-desktop`，基于 `776f409`。

## 官方来源

- 核对时开发版清单分阶段比例为 10%，发布时间为 2026-11-11 18:17:26.162（Asia/Shanghai）。[官方桌面更新清单](https://download.deepseek.com/dsh-desk/feeds/mac-arm64/nightly-mac.yml)
- 下载完整 ZIP，确认 362753775 字节，SHA512 与清单一致，为 `SAKrGOp6y3vla/r7QG6hP+y3LfHeRKS3xQ+lxFBuiF7ezSt+dqkCedm9znqKqr7akCkLgag0GnC+yZhkAWL/+Q==`。SHA256 为 `40d59961048840c7681301bb16541b95c7ca953edd526cf0a3c86700608d391b`。[官方 macOS arm64 ZIP](https://download.deepseek.com/dsh-desk/bin/mac-arm64/deepseek-harness-0.2.2-rc.2-mac-arm64.zip)
- 应用 `package.json` 与 `runtime/primary-runtime/runtime.json` 均为 `0.2.2-rc.2`。应用记录的构建提交为 `a6b1b85f44891ee1484bed6a9fc08acaae777d90`。官方源码对照使用发布标签固定提交 `ddac96760b6edf8fa0fe17cbdcf0b512f4c12b2c`。[官方发布说明](https://github.com/deepseek-ai/deepseek-harness/releases/tag/dsh-v0.2.2-rc.2)

## 构建和适配

```sh
./auto-build.sh --arch x64 --formats deb --electron bundled --system-runtime --package-jobs 4 \
  --archive /绝对路径/已校验的/deepseek-harness-0.2.2-rc.2-mac-arm64.zip
```

- 脚本依次执行准备、生成应用树和打包。Electron Framework、运行时与 npm 依赖的版本以实际载荷为准。构建采用 Electron 44.7.0、Node 24.21.0、Python 3.12.14、pnpm 11.28.5、Sharp 0.35.5 和载荷声明的 13 个 Python 包。8 项平台依赖替换及 node-pty prebuild 均沿用对应版本。
- 保留 Windows 主窗口新增的底色选项，并在 Linux 主进程补齐 `screen` 导入。KDE/v2rayN 代理继续使用补丁，同时保留上游新增的 `createRouteDispatcher`。MCP 启动、Linux 文件锁探测和指纹门禁仍需原有补丁。
- 官方桌面载荷已实现内存 Host Cookie，欢迎页 HTTP 与账户 WebSocket 复用该值，并在启动时按名称清理同一主机的遗留认证条目。当前构建直接使用官方实现，已移除本地补丁。逐文件核对见 [补丁总览](patches/README.md)。
- 系统运行时 deb 用 Debian Node/Python，保留内置 pnpm 和私有 python-pptx 1.0.2。rc.2 的 Office 技能在加载时生成 Python 环境说明，默认 PPTX 流程使用返回的私有库路径，显式选择用户 Python 的流程沿用上游说明。LibreOffice 原生可执行文件更名为 `dsoffice`，打包时按适配层声明替换为 WASM 0.2.3。

## 成品

`dist/deepseek-harness_0.2.2-rc.2+systemruntime3_amd64.bundled.deb` 为 184219512 字节。SHA256 为 `ff31934cae39957721e50c008c142f987620c4b2ce68eab5dd969034172b1049`。安装命令见 [产物说明](ARTIFACTS.md)。

## 图片修复成品复验

- 从同一 SHA512 的官方 rc.2 ZIP 完整重建。Debian 包修订号升为 `+systemruntime3`，应用与运行时版本均为 `0.2.2-rc.2`。APT 模拟从 `+systemruntime2` 升级一个包，无新增或移除。
- 打包后的图片 worker 合并同图并发上传，缓存引用失效时携带源字节重试一次。Electron 自检通过旧图重读、20 张图片并发读取与缩放、坏数据拒绝和 libvips 进程隔离。使用成品的附件存储保存 20 张合成图片，连续三轮为全部图片生成模型请求所需版本。
- 成品校验值、内置 CLI、pnpm、主进程与两个 preload 检查通过。成品回归 76 项通过，RPM/pacman 各因缺少工具跳过 1 项。
- 用户桌面验收未复现原 `INVALID_IMAGE` 问题。验收后清理了本轮缓存、打包暂存和旧 deb，`dist/` 仅保留 `+systemruntime3` 与校验文件，清理后再次校验通过。

## rc.2 基线验证（`+systemruntime2`）

- 成品 SHA256、APT 升级模拟、CLI `0.2.2-rc.2`、pnpm `11.28.5`、22 个 ELF 与 Sharp 图片处理隔离通过。移除 Cookie 补丁及其专用测试后，解包成品复测 78 项，76 项通过，RPM/pacman 各因缺少工具跳过 1 项。重新生成应用树后，主进程除打包阶段的系统 Node 路径外与成品逐字节一致。两个 Linux preload 也与成品逐字节一致，主进程和两个 preload 的语法检查通过。
- 实际调用 `load_workspace_dependencies` 得到系统 Node 24.22.2、Python 3.14.10、pnpm 和私有 python-pptx 路径。结果未含占位的 `nodePackages`，没有创建用户运行时缓存。Office 注册的三个编辑技能均可加载，PPTX 指引只在工作区依赖模式提供私有库路径。DOCX、XLSX、PPTX 分别写入再读回通过，WASM 将 DOCX 转换为一页 PDF 通过。
- 从最终 deb 解包运行，Wayland 和 XWayland 各启动、重启一次。独立 KWin 虚拟桌面中约 2.0 至 2.3 秒进入可见主界面，计时包含跳过欢迎页。两后端均通过侧栏切换、原生最大化与还原、真全屏及退出全屏。另以实际载荷的侧栏样式验证了 144 种控件布局组合。
- 两后端分别注入 100 个合成旧 Host Cookie。重启后全部被清理，无关 Cookie 仍在。另通过真实载荷函数完成本地 HTTP、账户 WebSocket 和 100 次换端口测试。
- 虚拟合成器取消了整屏截图请求，窗口结果依据实际界面和尺寸检查。测试使用独立配置、缓存及随机调试和后端端口，关闭了测试实例。真实登录、既有会话、用户插件和 GPU 属于自动化验证范围之外。
- 用户确认 `+systemruntime2` 验收正常。rc.1 源码保留在 `personal-dsh-v0.2.2-rc.1` 标签。
