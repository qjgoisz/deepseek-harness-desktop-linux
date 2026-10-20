# 项目维护约定

## 分支与范围

- 默认维护用户自用分支 `codex/personal-desktop`。除非用户另有说明，不把自用圆角、实色策略或自动构建工具链混入上游 GUI 分支与 PR。
- 自用外观约定见 `PERSONAL.md`；构建方法见 `docs/AUTO_BUILD.md`；历史适配和验证范围见 `docs/CHANGELOG.md`。先核对当前分支与工作区状态，再修改文件。
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

- 官方滚动下载地址为 `https://download.deepseek.com/desktop/dsh-latest-macos-arm64.dmg`。下载地址和文件名不能证明版本；解包后核对应用 `package.json` 与 `runtime/primary-runtime/runtime.json`。
- Node、Python、Python 包、pnpm 及原生 npm 包使用载荷中的版本；不要独立升级或为了构建成功静默使用其他版本。原生模块默认同版本替换，版本漂移必须明确说明。
- pnpm 在旧版位于 `runtime/pnpm`，在 `0.2.1-rc.2` 位于 `runtime/primary-runtime/dependencies/pnpm`。资源根覆盖应保留对应载荷的实际布局，并验证 GUI 包管理入口与内置 CLI。
- `patches/patch-main.py` 遇到未知或重复匹配时应失败，且不写入部分补丁。维护其他补丁时也应避免匹配失败后悄悄交付半成品；同时检查主进程与两个 preload。
- 保留 Sharp 的独立 Node worker 隔离方案。facade 的版本信息应读取实际 worker 原包，不能写死旧版版本号。
- 不把插件自身的性能问题或协作桥改动夹带进桌面重打包；发现相关问题可记录诊断，按用户指定范围另行处理。
- `local-fixes/dsh-usage-settings/` 单独保存用户授权纳入自用分支的插件导航修复；仅显式运行 `apply-fix.py --apply` 时修改本机插件，不接入 Desktop 打包流程。2026-10-18 纳入版本管理时 Python 与 JavaScript 语法检查通过；DOM 回归测试因缺少 `chromium` 未运行成功，未应用到已安装实例，桌面构建与 GUI 验证基线不变。

## 构建与产物

自用 x86_64 bundled deb 的常用命令：

```sh
./auto-build.sh --arch x64 --formats deb --electron bundled --package-jobs 4
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

## 最近验证基线

截至 2026-10-18，自用分支已适配 DSH `0.2.1-rc.2`：Node 24.21.0、Python 3.12.14、pnpm 11.28.5、Sharp 0.35.5，bundled Electron 44.4.5。

- 已构建并验证 x86_64 bundled deb；离线测试 44 项通过，2 项因缺少 RPM/pacman 工具跳过。
- KDE KWin 6.7.4 下已验证 Wayland/XWayland 的欢迎页、主界面、实色圆角、最大化/还原和合成器全屏布局同步，以及 Wayland 顶栏双击还原。
- 新版其他包格式、ARM64、其他桌面环境和带用户插件的长会话未重新验证。旧版多格式验证记录不代表新版已通过这些检查；后续更新应刷新本节与变更记录。

2026-10-20 自用交通灯改为始终显示：48 项离线测试中 46 项通过，2 项因缺少 RPM/pacman 工具跳过；构建脚本语法检查通过。隔离无头 Chrome 验证主界面/欢迎页注入样式的 16 种全屏、悬停、失焦组合，交通灯可见且命中测试通过、侧栏按钮无重叠、插件按钮未位移。已覆盖旧版自用样式升级及未知样式不部分写入；未重新构建安装包，未进行本次改动后的 Desktop Wayland/XWayland 实机窗口验收，以上历史 GUI 记录不代表本次验收。

同日后续修正侧栏按钮位置：移除 76px 让位位移，统一普通、最大化及全屏的定位；`tests/personal-sidebar-layout.py` 使用真实载荷侧栏 CSS 验证 144 种组合坐标，并确认旧版会在最大化状态下失败。48 项离线测试仍为 46 项通过、2 项跳过；已重新生成 `0.2.1-rc.2` x86_64 bundled deb，最终包的主进程和两个 preload 与应用树一致，CLI、pnpm、Node/Python 版本、图片隔离和 SHA256 检查均通过。尚未重新进行 Desktop Wayland/XWayland 原生窗口与整屏视觉验收，不将浏览器坐标检查视为完整 GUI 验收。

2026-10-20 用户确认交付的侧栏按钮位置修正版视觉验收通过，并授权推送自用分支。该结论为用户实测反馈，未分别标注 Wayland/XWayland、页面及窗口状态的覆盖范围；本次仅补充验收记录，不改变代码或自动化验证基线。
