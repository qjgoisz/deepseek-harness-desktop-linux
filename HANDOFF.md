# 自用 DSH Desktop 项目交接

更新日期：2026-11-02。分支 codex/personal-desktop；本轮 Cookie 修复基于 c63219c（npm 前缀适配）。用户反馈验收可用并授权清理、提交与推送 origin/codex/personal-desktop；实际提交号和远端同步结果以 git log/status 为准。

## 本轮：Desktop Cookie 累积修复

- 新增 patches/patch-desktop-auth-cookie.py，接入 scripts/build/tree.sh。欢迎页 HTTP 与账户 WebSocket 复用 authenticateWebHost 的当前内存 Cookie，不再以 Electron Cookie 库重复认证。请求限定在当前 Host origin，拒绝 URL 用户信息及重定向；错误带 HTTP 状态码，不输出 token 或 Cookie。
- 保留通用 Web 的签名、authority 和有效期校验；旧 Cookie 不再被这些请求读取或发送，等待自然过期。不修改现用 Cookie 库、配置、登录凭据或会话。
- 80 项回归 78 通过、2 RPM/pacman 工具缺失跳过，构建 shell 与新增 JS/Python 语法检查通过。测试用真实载荷函数和合成凭据复现 HTTP 431，并覆盖 HTTP、账户 WebSocket、100 次换端口/密钥、并存 Host、过期/签名及取消/重定向。
- 从已安装 rc.5 复制独立完整应用树，仅应用新补丁后进行 Desktop 测试。Wayland/XWayland 各启动、重启一次，预置 100 个合成旧 Cookie，均进入可见主界面且 Cookie 数不增长，正常退出。独立 HOME/DSH_HOME/XDG/user-data，无用户插件或凭据。no-sandbox/disable-gpu、Inspector 与播种/观测仅限临时测试树，不进入补丁；不是全 GUI 或真实登录/长会话验收。
- 用户随后要求打包，并明确指定从默认 DMG 下载开始运行原始 auto-build.sh。已完成 `./auto-build.sh --arch x64 --formats deb --electron bundled --package-jobs 4` 的 prepare/tree/package 全流程，没有用上一份 deb 或 ZIP 生成最终成品。官方 DMG 应用/runtime 均为 rc.5，SHA256 7f387a78a7800de26af98a796c833295ebe57ee72f1f36a0810f296c871c2baf。
- 当前 dist/deepseek-harness_0.2.1-rc.5_amd64.bundled.deb 已包含 Cookie 修复，SHA256 32d34addc782227b49d0c251ccaf253aa14d10be13cbd40da2d18c87ae970af6，260349116 字节。旧包（900bc502...）及校验文件移至 dist/previous-20261102-before-cookie/，不假设更早的回退目录仍存在。成品 CLI/pnpm、Node/Python、13 Python 包、图片隔离、133 ELF、26565 资源一致性和 SHA256 通过；最终包的 80 项回归为 78 通过、2 跳过。测试夹具支持从已打补丁成品恢复已知原始状态，以继续验证首次写入失败保护。
- 从最终 deb 解包的原始应用文件完成 Wayland/XWayland 各启动和重启一次：在独立测试会话经 Inspector 预置 100 个合成旧 Cookie，均进入可见主页面、数量不增长并正常退出；没有在成品文件中加入播种/观测代码。no-sandbox/disable-gpu 和 Inspector 仅为测试启动参数，不扩展为用户原配置/登录/长会话验收。用户随后反馈“好了”，视为使用验收反馈，未逐项说明覆盖范围；本代理未替换安装或修改现用数据。
- 按用户后续清理要求，确认无进程占用后删除下载物、DMG/ZIP 解包、out-x64、打包暂存、测试 HOME/原始日志、废弃增量包和 Python 缓存；保留 dist 成品/回退包及校验文件、源码和 others/ 内的小体积脱敏摘要。两份 deb 校验再次通过，后续完整构建需重新准备下载和应用树。新补丁用途及官方固定源码核对见 docs/patches/patch-desktop-auth-cookie.md；本次构建时另读取官方更新清单，仍为 rc.5，最终输入为默认 DMG。

## 历史交付与待验收（2026-10-31，后续状态以上节为准）

- 已应用局部构建补丁 patch-flock-libc.py，首次会话锁加载的 getReport 仅在调用期间排除网络诊断，finally 恢复设置；不更改锁语义、代理设置、运行时版本或用户插件。
- 新 deb：dist/deepseek-harness_0.2.1-rc.5_amd64.bundled.deb，SHA256 31353beddc7e81f279a8b6f11fbfd048133ff1d2708dcdc9fdcf95301fc880a7。旧 rc.5 SHA 13b0e527... 是历史构建，不是当前成品。
- 新包从当前已安装 rc.5 独立复制树，仅修改 flock.js 后增量生成；未安装或修改现用 DSH。dist/ 本轮开始时没有旧 deb，不声称存在回退安装包。
- 67 项回归 65 通过、2 工具缺失跳过；成品 CLI/pnpm、Node/Python、13 Python 包、Sharp 隔离、133 ELF、26565 资源文件一致性及 SHA256 通过。具体范围见 docs/STARTUP_LIBC.md。
- Wayland/XWayland 隔离空 HOME Desktop 实测：持有外网连接时首次加载锁模块并取得锁约 2ms，设置恢复、正常退出。测试 no-sandbox/disable-gpu 不写入成品；尚待用户安装后用原配置、会话及插件验证启动时快速切换入口，不能把受控空 HOME 测试称为全插件启动耗时。
- Node 24.21.0、Python 3.12.14、pnpm 11.28.5、Sharp 0.35.5、Electron 44.4.5 保持官方载荷/既有构建版本。

## 其他维护边界

- 全部 15 个补丁源码/辅助文件已逐项说明，入口见 [补丁审计](docs/patches/README.md)。既有核对基线为官方 rc.5 原始 ZIP 和 master 固定快照 ce7073d51254c26cd63b22a60835b8f948deb447（源码 Desktop 为 0.2.2-alpha.2）；Cookie 项追加核对相同固定源码。未确认整份补丁已被官方等价吸收；没有改用 alpha 构建。
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
