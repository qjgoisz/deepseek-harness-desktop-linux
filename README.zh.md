# DeepSeek Harness Desktop Linux 构建与安装

本仓库将官方 macOS arm64 应用归档转换为 Linux 桌面安装包。当前适配版本为 **0.2.2-rc.2**，实测范围为 amd64 bundled deb。其他架构与包格式可按构建文档生成。当前产物与测试范围见 [产物说明](docs/ARTIFACTS.md)和[兼容性记录](docs/COMPATIBILITY.md)。

## 准备官方载荷

从兼容性记录中的官方链接下载本版 macOS arm64 ZIP。按更新清单核对大小和 SHA512，再核对归档中应用和 runtime 的版本。构建脚本接收本地 ZIP 或 DMG，当前版本使用已校验的 ZIP。

构建依赖 Bash、Python 3.12+、7z、curl、tar、xz、unzip 和用于打包的系统工具。各包型的依赖见 [自动构建文档](docs/AUTO_BUILD.md)。构建在普通用户权限下运行。

## 构建 amd64 bundled deb

在仓库根目录运行：

```sh
./auto-build.sh --arch x64 --formats deb --electron bundled --system-runtime --package-jobs 4 \
  --archive /绝对路径/已校验的/deepseek-harness-0.2.2-rc.2-mac-arm64.zip
```

脚本依次准备依赖、生成应用树并打包。Electron 默认使用 44.7.0，Node、Python、pnpm 和原生依赖沿用载荷指定版本。包和校验文件保存在 `dist/`。可先加 `--dry-run` 查看步骤，或加 `--clean` 在成功后清除中间产物。

## 使用与排查

- 安装前在产物目录核对 SHA256。安装步骤见 [产物说明](docs/ARTIFACTS.md)。
- 窗口、侧栏和交通灯的当前策略见 [自用外观说明](PERSONAL.md)。
- KDE/v2rayN 的适用范围和环境变量覆盖见 [系统代理说明](docs/SYSTEM_PROXY.md)。
- MCP 协商与后台初始化需要按服务启用，见 [MCP 启动说明](docs/MCP_STARTUP.md)。
- 自定义 Agent 预设若引用独立的 `@deepseek-ai/dsh-tool-subagent-control/list-agents`，移除该条目并保留主模块和原有预设 ID。当前主模块已注册 `list_agents`。更新预设后重启或按本机配置方式重载预设，再检查会话恢复。
- 打包补丁的用途与官方实现核对见 [补丁总览](docs/patches/README.md)。

应用本体版权归 DeepSeek。请遵守原应用的许可条款。
