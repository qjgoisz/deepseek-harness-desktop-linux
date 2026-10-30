# Linux 会话首次打开的同步阻塞修复

2026-10-31，DSH 0.2.1-rc.5 自用分支。

## 原因与修改

首次取得会话写锁时，`@deepseek-ai/node-addon-system/lib/flock.js` 的 `loadBinding()` 调用 `process.report.getReport()`，只为通过 `header.glibcVersionRuntime` 选择 glibc/musl 原生模块。完整报告可能对已连接的外网地址进行反向 DNS 查询。实际 Desktop Host 的 51.8 秒采样中，50.0 秒停留在该调用；独立 Electron/Node 实验中，持有外网 TCP 连接时默认报告约 10010ms，排除网络后约 1ms，glibc 检测结果相同；连接本地代理时默认报告约 1ms。这也解释了代理环境与启动时切换会话会影响表现。

构建补丁 `patches/patch-flock-libc.py` 仅在这一同步调用期间设置 `process.report.excludeNetwork=true`，通过 `finally` 恢复原值。异常继续传播，不把探测失败默认认作 musl；当前运行时若不支持该开关则明确报错。保留延迟加载、binding 缓存、原生包版本和文件锁竞争/释放语义。不依赖全局代理或 NODE_OPTIONS，不安装用户级核心覆盖包，不输出完整报告。

参考：https://nodejs.org/api/report.html （网络报告排除与反向 DNS 行为）。

## 回归与成品

- 67 项回归：65 通过、2 缺少 RPM/pacman 工具跳过；成品解包后同样通过。
- 验证原设置为 true/false、报告抛错后的恢复，glibc/musl 路径选择、缓存、Darwin 原路径和不支持运行时的明确失败。
- glibc 主机上实际跨进程竞争临时文件锁：冲突拒绝，正常释放和异常退出后均可重新获取。musl 分支为模拟验证，未进行 musl 实机验证。
- 严格匹配、幂等、未知/部分补丁拒绝，以及语法失败不替换目标文件均通过。
- 成品解包运行隔离 Wayland/XWayland Desktop，主界面分别约 2.205/2.217 秒显示。各自在真实 Desktop Host 中持有外网 TCP 连接并首次加载同内容的新 flock 模块，取得锁均约 2ms，设置恢复，正常退出码 0。
- Desktop 测试使用空 HOME、独立 DSH_HOME/XDG 配置/缓存/状态/user-data-dir、独立主进程调试端口与临时后台调试端口；环境代理清除、KDE 适配禁用、Chromium 系统代理禁用，未改系统代理。no-sandbox/disable-gpu 仅为测试参数，没有写入成品启动器。
- 该受控测试不等于带用户凭据、原会话与全插件的一轮人工验收，也不扩展既有 GUI 外观或 GPU 测试矩阵。
- CLI、Node/Python/pnpm、13 项 Python 包、图片 worker 隔离、133 个 ELF、26565 个资源文件与应用树一致性、主进程/两个 preload/补丁模块语法及 SHA256 通过。

本轮从本机已安装的 rc.5 独立复制应用树，仅修改 flock.js 后增量打包；未修改已安装文件，没有重新下载官方载荷或转换 macOS 原生包。包中 GUI、代理、MCP 与运行时均与复制来源一致。后续从官方 ZIP/DMG 全新构建也会自动应用此补丁。

当前产物：`dist/deepseek-harness_0.2.1-rc.5_amd64.bundled.deb`，SHA256：

```text
31353beddc7e81f279a8b6f11fbfd048133ff1d2708dcdc9fdcf95301fc880a7
```

版本号仍是官方 rc.5，应用补丁标记 `dsh-linux-flock-libc:v1` 和成品 SHA256 区分本轮。构建开始时 dist/ 没有旧 deb，不能声称已保留可直接安装的旧包。本轮未安装，源码按用户授权纳入本地提交、暂不推送；用户安装后请在直连状态下立即切换会话、打开插件页，验收之前的加载卡顿。
