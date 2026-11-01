# 自用 DSH Desktop 项目交接

更新日期：2026-11-01。分支 codex/personal-desktop；libc 修复提交 e744487、标题栏修复提交 fd6702e。用户授权随后单独提交补丁文档，并将三个本地提交一并推送 origin/codex/personal-desktop；最终提交号与远端结果以 git log 和推送结果为准。

## 当前交付与待验收

- 已应用局部构建补丁 patch-flock-libc.py，首次会话锁加载的 getReport 仅在调用期间排除网络诊断，finally 恢复设置；不更改锁语义、代理设置、运行时版本或用户插件。
- 新 deb：dist/deepseek-harness_0.2.1-rc.5_amd64.bundled.deb，SHA256 31353beddc7e81f279a8b6f11fbfd048133ff1d2708dcdc9fdcf95301fc880a7。旧 rc.5 SHA 13b0e527... 是历史构建，不是当前成品。
- 新包从当前已安装 rc.5 独立复制树，仅修改 flock.js 后增量生成；未安装或修改现用 DSH。dist/ 本轮开始时没有旧 deb，不声称存在回退安装包。
- 67 项回归 65 通过、2 工具缺失跳过；成品 CLI/pnpm、Node/Python、13 Python 包、Sharp 隔离、133 ELF、26565 资源文件一致性及 SHA256 通过。具体范围见 docs/STARTUP_LIBC.md。
- Wayland/XWayland 隔离空 HOME Desktop 实测：持有外网连接时首次加载锁模块并取得锁约 2ms，设置恢复、正常退出。测试 no-sandbox/disable-gpu 不写入成品；尚待用户安装后用原配置、会话及插件验证启动时快速切换入口，不能把受控空 HOME 测试称为全插件启动耗时。
- Node 24.21.0、Python 3.12.14、pnpm 11.28.5、Sharp 0.35.5、Electron 44.4.5 保持官方载荷/既有构建版本。

## 其他维护边界

- 全部 14 个补丁源码/辅助文件已逐项说明，入口见 [补丁审计](docs/patches/README.md)。核对官方 rc.5 原始 ZIP 和 master 固定快照 ce7073d51254c26cd63b22a60835b8f948deb447（源码 Desktop 为 0.2.2-alpha.2），未确认整份补丁已被官方等价吸收；没有改用 alpha 构建。
- KDE blur 和全屏悬停视觉被自用层覆盖，但基础层仍有结构和交互依赖。titlebar 是 chrome 的构建中间步骤，旧版完成树重跑会重复插入，2026-11-01 已修复为完整状态跳过、部分/未知状态拒绝写入；upgrade 仅为历史手工迁移。其他旧 GUI 脚本的部分写入/弱校验风险仍保留记录，没有删除补丁。
- 本轮审计在独立官方副本逐项应用、重跑和语法核对，并重跑 67 项回归（65 通过、2 跳过）与 144 种侧栏组合；文档改动不改变现有 deb 的内容、SHA256 或原生 GUI 验证范围。
- 自用 GUI 实色圆角、交通灯及侧栏位置、KDE/v2rayN 代理、MCP v2 均保持原样。MCP 默认 auto/blocking，显式 background 且非严格服务才释放屏障；安装 deb 不自动修改 MCP 配置。
- 本次诊断已证明代理不是根本修复：真实后台在 flock 的 libc 探测中同步执行完整报告，网络端点反向 DNS 可令整个后台等待数十秒。修复必须保留真实文件锁，不可通过跳过锁规避。
- npm Web 迁移已取消，不恢复。docs/COMPATIBILITY-2026-10-24.md 持续忽略；其他历史记录以当时版本和覆盖边界理解。
- others/ 下诊断和构建材料均为本机忽略文件，禁止提交原始 profile、日志、截图或认证信息。构建缓存按默认保留，测试 HOME 清理不等于删除 dist 成品。
- 每次提交前实质更新 AGENTS.md；只在用户授权后提交、推送或安装，明确实际状态。交付前核对所有 worktree 与分支绑定。

## 2026-11-01 titlebar 修复收尾

- 标题栏修复与测试已单独提交为 fd6702e；补丁文档按用户要求在下一提交交付。
- 完整原始树才插入；完整 overlay/chrome 树跳过；部分、重复或未知布局拒绝写入。原子替换保留权限，失败清理临时文件。
- 完整回归 73 项：71 通过、2 工具缺失跳过；官方 rc.5 首次输出与旧版一致，独立 GUI 组合链和三个 JS 语法检查通过。既有安装包内容与窗口外观不变，本次未重打包或运行原生 GUI。详见 docs/patches/patch-titlebar.md。

2026-11-01 文档范围按用户要求收敛：docs/patches/ 删除自用分支行为及本地维护审计内容，只保留补丁用途/目标、官方等价修复证据和后续核对条件。界面定制与旧树迁移记为不适用。官方核对仍截至 2026-10-31，未重新查询；本轮仅文档调整；用户现已授权分两次提交并推送。

## 2026-11-01 MCP runtime 路径迁移

当前 npm 用户前缀为 /home/debian/.local。local-fixes/mcp-startup/install-runtime.mjs 要求明确设置且可写的前缀，锁定运行目录为 <prefix>/lib/dsh-mcp-remote-0.15.1；不会使用 npm 缺省路径或修改 npm 设置。配置工具可显式迁移旧目录，流程见 local-fixes/mcp-startup/README.md。现用 OpenAlex/Exa 已备份后迁移到新入口；旧 share/dsh-mcp-remote-0.15.1 保留供回退，本轮不重启 Desktop。74 项回归 72 通过、2 跳过，未重打包。用户已授权将配套工具、回归与说明提交并推送 origin/codex/personal-desktop；具体提交及远端状态以 Git 结果为准。
