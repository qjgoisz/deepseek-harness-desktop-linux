# DSH 0.2.2-rc.3 Desktop 适配与验证

2026-11-13（Asia/Shanghai），分支 `codex/personal-desktop`，基于 `6646115`。上一版见 [rc.2 兼容性归档](COMPATIBILITY-PREVIOUS.md)。

## 官方来源

- 核对时开发版清单分阶段比例为 10%，发布时间为 2026-11-13 15:40:14.455（Asia/Shanghai）。[官方桌面更新清单](https://download.deepseek.com/dsh-desk/feeds/mac-arm64/nightly-mac.yml)
- ZIP 为 362840431 字节，SHA512 为 `UThWXKCqiiUnjFgij655+Gc1MgiSl+Ybl71jkQi48BhcBCN0XSDNT4GGmGJY3nvEqnkLT3LtWbL6wy6t/kRxIw==`，与清单一致。SHA256 为 `1648a29609710d852f04fb3c50602ff37b1ed0def1d2aff65ce813daa5a4f4a4`。[官方 macOS arm64 ZIP](https://download.deepseek.com/dsh-desk/bin/mac-arm64/deepseek-harness-0.2.2-rc.3-mac-arm64.zip)
- 应用 `package.json` 和 `runtime/primary-runtime/runtime.json` 均为 `0.2.2-rc.3`。载荷记录的构建提交为 `6b729fedde0c8fd03af7afdf5a711aa64fe87c3b`。官方源码对照使用标签快照 `38a6a5c965aa99ab525161efb7cc5cf1fe62fced`。[官方发布说明](https://github.com/deepseek-ai/deepseek-harness/releases/tag/dsh-v0.2.2-rc.3)
- 官方发布说明列出了实验性「DeepSeek 会话导入」插件及 Windows 更新修复。已在桌面 ZIP 确认实验性插件随载荷提供。[官方发布说明](https://github.com/deepseek-ai/deepseek-harness/releases/tag/dsh-v0.2.2-rc.3)

## 构建与补丁

```sh
./auto-build.sh --arch x64 --formats deb --electron bundled --system-runtime --package-jobs 4 \
  --archive /绝对路径/已校验的/deepseek-harness-0.2.2-rc.3-mac-arm64.zip
```

- Electron Framework 为 44.7.0，载荷声明 Node 24.21.0、Python 3.12.14、pnpm 11.28.5 和 13 个 Python 包。Linux 构建沿用这些版本，8 项平台依赖和 node-pty prebuild 均同版本替换，包括 Sharp 0.35.5 和 LibreOffice WASM 0.2.3。
- 官方 ZIP 保留内存 Host Cookie 及旧认证条目清理。KDE 动态代理、MCP 协商与后台启动、libc 探测和指纹门禁仍有对应缺口，现有补丁可应用。Linux 窗口和系统运行时适配通过原补丁链。逐项核对见 [补丁总览](patches/README.md)。
- 成品使用 Debian Node/Python，内置 pnpm、PPTX 专用的 python-pptx 1.0.2 和 LibreOffice WASM。图片 worker 保留并发上传合并与缓存引用失效时的重试。

## 成品验证

- `dist/deepseek-harness_0.2.2-rc.3+systemruntime3_amd64.bundled.deb` 为 184274592 字节，SHA256 为 `b8d119061fc210a2b570415eae408a1b79c0276152c4c401f943df666cff26a8`。校验通过。APT 模拟由 rc.2 升级，升级 1 个包，新增和移除均为 0。[安装说明](ARTIFACTS.md)
- 从 deb 解包验证 CLI `0.2.2-rc.3`、pnpm `11.28.5` 和 22 个 ELF 文件。主进程仅有打包阶段的系统 Node 路径改写，两个 preload 与已验证的应用树一致，三者语法检查通过。
- 成品回归 76 项通过，RPM/pacman 因缺少工具各跳过 1 项。覆盖本地 HTTP 与账户 WebSocket 的 Host Cookie、100 次换端口、KDE 代理、MCP 及原生锁行为。
- 图片 worker 自检通过，包括同图并发、旧图读取、20 张图并发缩放、坏数据拒绝和 libvips 隔离。使用成品附件存储为三轮各 20 张合成图生成请求图片。
- 实际调用 `load_workspace_dependencies` 返回系统 Node 24.22.2、Python 3.14.10、内置 pnpm 和私有 PPTX 路径。没有创建用户运行时缓存。加载三种 Office 编辑技能的默认和用户 Python 指引，完成 DOCX、XLSX、PPTX 读写和 WASM 导出一页 PDF。
- 从最终 deb 在隔离的 KWin 虚拟桌面启动原生 Wayland 和 XWayland，约 3.2 秒和 3.1 秒进入主界面，含跳过欢迎页。两后端的欢迎页和主界面实色与普通窗口 12px 圆角通过检查，折叠侧栏按钮位于 128px 和 88px。点击交通灯后窗口尺寸由 1280×820 变为 1600×1000 并成功还原，DOM 真全屏及退出也通过。最大化和全屏时交通灯保持可见，圆角消失，侧栏按钮位置不变。
- 桌面测试使用窗口几何和计算样式，XWayland 使用 Mesa 软件渲染。自动化测试未覆盖真实账户、现有会话、用户插件、GPU 和会话导入流程。


## 用户验收与清理

- 用户完成桌面验收，除侧边栏应用入口取消固定后重启会恢复外，未报告其他问题。官方 rc.2 与 rc.3 均只在内存中保存未固定列表，侧边栏插件重新加载时会重置。rc.3 官方 ZIP 与自用 deb 的侧边栏模块逐字节一致，本次暂保留该行为。[官方侧边栏说明](https://github.com/deepseek-ai/deepseek-harness/blob/38a6a5c965aa99ab525161efb7cc5cf1fe62fced/packages/client/ui-sidebar/README.zh.md#L44)
- 清理本轮下载、解包、构建及测试暂存和 rc.2 安装包。`dist/` 保留已验收的 rc.3 deb 及校验文件。
