# 自用 DSH Desktop 项目交接

更新日期：2026-10-31。分支 codex/personal-desktop，HEAD aa724a5；本轮 libc 探测修复按授权纳入本地提交，暂不推送；具体提交号以 git log 为准。

## 当前交付与待验收

- 已应用局部构建补丁 patch-flock-libc.py，首次会话锁加载的 getReport 仅在调用期间排除网络诊断，finally 恢复设置；不更改锁语义、代理设置、运行时版本或用户插件。
- 新 deb：dist/deepseek-harness_0.2.1-rc.5_amd64.bundled.deb，SHA256 31353beddc7e81f279a8b6f11fbfd048133ff1d2708dcdc9fdcf95301fc880a7。旧 rc.5 SHA 13b0e527... 是历史构建，不是当前成品。
- 新包从当前已安装 rc.5 独立复制树，仅修改 flock.js 后增量生成；未安装或修改现用 DSH。dist/ 本轮开始时没有旧 deb，不声称存在回退安装包。
- 67 项回归 65 通过、2 工具缺失跳过；成品 CLI/pnpm、Node/Python、13 Python 包、Sharp 隔离、133 ELF、26565 资源文件一致性及 SHA256 通过。具体范围见 docs/STARTUP_LIBC.md。
- Wayland/XWayland 隔离空 HOME Desktop 实测：持有外网连接时首次加载锁模块并取得锁约 2ms，设置恢复、正常退出。测试 no-sandbox/disable-gpu 不写入成品；尚待用户安装后用原配置、会话及插件验证启动时快速切换入口，不能把受控空 HOME 测试称为全插件启动耗时。
- Node 24.21.0、Python 3.12.14、pnpm 11.28.5、Sharp 0.35.5、Electron 44.4.5 保持官方载荷/既有构建版本。

## 其他维护边界

- 自用 GUI 实色圆角、交通灯及侧栏位置、KDE/v2rayN 代理、MCP v2 均保持原样。MCP 默认 auto/blocking，显式 background 且非严格服务才释放屏障；安装 deb 不自动修改 MCP 配置。
- 本次诊断已证明代理不是根本修复：真实后台在 flock 的 libc 探测中同步执行完整报告，网络端点反向 DNS 可令整个后台等待数十秒。修复必须保留真实文件锁，不可通过跳过锁规避。
- npm Web 迁移已取消，不恢复。docs/COMPATIBILITY-2026-10-24.md 持续忽略；其他历史记录以当时版本和覆盖边界理解。
- others/ 下诊断和构建材料均为本机忽略文件，禁止提交原始 profile、日志、截图或认证信息。构建缓存按默认保留，测试 HOME 清理不等于删除 dist 成品。
- 每次提交前实质更新 AGENTS.md；只在用户授权后提交、推送或安装，明确实际状态。交付前核对所有 worktree 与分支绑定。
