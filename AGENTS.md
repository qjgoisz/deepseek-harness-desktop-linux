# 项目维护约定

## 2026-11-05 当前适配状态

- 官方清单及完整 ZIP 内应用/runtime 均为 `0.2.2-rc.1`，核对时默认滚动 DMG 尚未提供本版。本轮先核对新版 ZIP 大小和 SHA512，再由 auto-build.sh 完成全流程；不要将默认 DMG 或旧缓存视为新版。
- patch-main.py 支持新旧两个完整 PlatformView 调用，透传 Linux 时保留 rc.1 新增的第四参数更新输入守卫；未知/重复调用拒绝且不部分写入。Electron 默认同步官方载荷 44.7.0；Node 24.21.0、Python 3.12.14、pnpm 11.28.5、Sharp 0.35.5 及其他载荷依赖无版本漂移。
- 新 bundled amd64 deb SHA256 为 `22343671318810dd0d48e57cdf79df865431a5e9fcc2f4dd758bf0be8b70f54a`。构建树与成品各 81 项回归：79 通过、2 RPM/pacman 工具缺失跳过；144 侧栏组合、CLI/pnpm、运行时/13 Python 包、图片隔离、133 ELF、29379 资源文件一致性及 SHA256 通过。
- 最终包隔离 Wayland/XWayland 各启动/重启一次，约 2–3 秒进入可见主界面，100 个合成 Cookie 不增长、均退出 0；侧栏切换、原生最大化/还原及全屏切换通过。8 张整屏截图成功，普通窗口部分边缘受多显示器放置影响，不视为完整圆角/拖动验收。no-sandbox/disable-gpu/Inspector 不进入成品，无真实登录、用户插件/模型、GPU 或长会话测试。
- 详见 docs/COMPATIBILITY.md。现用安装和数据未改。当前 dist/ 只含 rc.1 及校验文件。用户反馈修复预设后界面恢复，隔离复查通过。本轮源码交付目标为 origin/codex/personal-desktop。测试实例已关闭，无临时 worktree。按用户要求清理了本轮缓存与测试暂存。

- 交付前对照实际发布包与固定官方源码快照复核全部补丁。官方 master 已修复 Cookie 累积，核对的 rc.1 ZIP 仍需此补丁。后续先确认修复进入发布包，再决定是否移除。

## 分支与范围

- 默认维护用户自用分支 `codex/personal-desktop`。除非用户另有说明，不把自用圆角、实色策略或自动构建工具链混入上游 GUI 分支与 PR。
- 自用外观约定见 `PERSONAL.md`；构建方法见 `docs/AUTO_BUILD.md`；最新适配和验证范围见 `docs/COMPATIBILITY.md`。先核对当前分支与工作区状态，再修改文件。
- 用 `git worktree list` 确认检出位置，不假设旧 `/tmp` 工作树仍然存在。临时目录可能在重启后消失；提交保存在仓库，交付的安装包应放到持久项目目录的 `dist/`。
- 保留用户已有修改。提交、推送及交付时明确说明分支、提交号和是否已推送。
- 每一次 Git 提交前都必须更新 `AGENTS.md`，并将更新随本次改动一起提交；纯文档提交也适用。更新应记录本次改动涉及的维护约定、当前状态或验证结论；若未改变功能或验证基线，也应如实注明本次维护事项，不能仅阅读检查或制造无意义的格式改动来代替更新。

## 自用 GUI 行为

- 欢迎页与主界面都强制实色，不向 KWin 请求毛玻璃。普通窗口为 12px 圆角，最大化及全屏布局取消圆角。
- 保留上游 `syncTilingFullscreen` 和 Linux 最大化视为全屏布局的策略；不要顺手改成另一套最大化/全屏语义。
- 自用分支的交通灯在普通窗口、最大化及全屏时始终显示并可直接点击；侧栏按钮不使用让位位移，展开态贴侧栏右缘（宽度减 40px），折叠态切换按钮为 128px、新建按钮为 88px。相同侧栏状态下，最大化、全屏和顶部悬停不改变按钮坐标。该覆盖放在 `patch-personal-rounded.py`，不改变 GUI 分支的悬停实现，也不改变背景材质。
- 非活动窗口保留交通灯降饱和样式，不自动激活；底层焦点检查与窗口状态同步保留。模拟 macOS 的悬停自动激活尚未采纳，需先与用户讨论。
- 交通灯让位仅限侧栏顶部相关按钮。避免用宽泛的 `_toggle` 选择器误伤插件提供的底部面板按钮。
- 保留 XWayland 的原生拖动和双击还原；原生 Wayland 使用现有 DOM 指针事件和顶栏双击还原。保留正确的 Wayland 应用标识与桌面项关联，避免任务栏退回通用 Wayland 图标。

## DSH 更新适配

- 兼容性检测保留当前和紧邻的上一版。适配新版本时，将原 `docs/COMPATIBILITY.md` 移为 `docs/COMPATIBILITY-PREVIOUS.md`，覆盖更早归档，再写入当前报告。其他文档聚焦当前版本的产物、用法和验证范围。

- 官方滚动下载地址为 `https://download.deepseek.com/desktop/dsh-latest-macos-arm64.dmg`。下载地址和文件名不能证明版本；解包后核对应用 `package.json` 与 `runtime/primary-runtime/runtime.json`。
- Node、Python、Python 包、pnpm 及原生 npm 包使用载荷中的版本；不要独立升级或为了构建成功静默使用其他版本。原生模块默认同版本替换，版本漂移必须明确说明。
- 当前 pnpm 位于 `runtime/primary-runtime/dependencies/pnpm`。资源根覆盖应保留对应载荷的实际布局，并验证 GUI 包管理入口与内置 CLI。
- `patches/patch-main.py` 遇到未知或重复匹配时应失败，且不写入部分补丁。维护其他补丁时也应避免匹配失败后悄悄交付半成品；同时检查主进程与两个 preload。
- 保留 Sharp 的独立 Node worker 隔离方案。facade 的版本信息应读取实际 worker 原包，不能写死旧版版本号。
- 不把插件自身的性能问题或协作桥改动夹带进桌面重打包；发现相关问题可记录诊断，按用户指定范围另行处理。
- `local-fixes/dsh-usage-settings/` 单独保存用户授权纳入自用分支的插件导航修复；仅显式运行 `apply-fix.py --apply` 时修改本机插件，不接入 Desktop 打包流程。

## 构建与产物

自用 x86_64 bundled deb 的常用命令：

```sh
./auto-build.sh --arch x64 --formats deb --electron bundled --package-jobs 4 \
  --archive /绝对路径/已校验的/deepseek-harness-0.2.2-rc.1-mac-arm64.zip
```

- 默认保留下载缓存、解包文件和构建暂存。清理使用显式选项或按用户指定范围执行；不要在构建脚本中加入默认删除行为。
- 更新 dmg 时可下载到独立位置并使用 `--dmg /绝对路径/新版.dmg`，复用其他依赖缓存。`--force` 会忽略已有缓存，不应仅为更换 dmg 而无意重下全部依赖。
- `--electron` 控制本次生成的包型，不会删除 `dist/` 中已有的其他包。不要把旧产物误认为本次新生成；核对版本、修改时间及打包日志。
- 构建无需 sudo。若缺少系统软件包，先告诉用户具体包名和用途，由用户自行安装，不替用户提权或安装。
- `dist/`、下载缓存、应用树与含本机状态的测试文件不提交到 Git。不要重新引入临时调试包后缀或缺少文档说明的构建模式。

## 测试与隔离

代码改动运行相关回归测试；完整适配通常还需要以下检查：

```sh
python3 -m unittest discover -s tests -v
bash -n auto-build.sh
bash -n install-image-worker.sh
for script in scripts/build/*.sh; do bash -n "$script"; done
```

- 使用工作区内构建的 DSH 测试，不启动浏览器版来代替 Desktop，不修改或重启用户正在使用的已安装实例。
- 为测试实例独立设置 `HOME`、`DSH_HOME`、`XDG_CONFIG_HOME`、`XDG_CACHE_HOME`、`--user-data-dir` 和调试端口。确认后端端口与用户实例不冲突，不复制登录凭据。
- 分别用 `--ozone-platform=wayland` 与 `--ozone-platform=x11` 测试原生 Wayland、XWayland。先在正确的 `welcome.html` 页面跳过欢迎流程，再确认主界面已显示；测试最大化问题必须实际最大化，并核对原生窗口状态。
- 窗口圆角和背景穿透问题需结合整屏截图或原生窗口几何检查，单独截取页面内容不足以验证。焦点或自动化限制导致某项未实测时应如实记录，不把合成事件测试当作完整人工验收。
- 验证最终安装包：检查包元数据、解包后运行内置 CLI 与 pnpm 的 `--version`、运行 `image-worker-src/verify-image-worker.cjs`，并在校验文件所在目录执行 `sha256sum -c`。
- 确认打包中的 GUI 文件与已验证的应用树一致。测试后关闭自己创建的实例，清理仅按已授权范围执行；不使用会误杀其他 DSH 实例的宽泛进程匹配。
- 日志可能包含本地认证 token 或用户数据；输出和交付前应筛除，不把凭据或真实会话内容放进文档、Git 或 PR。
