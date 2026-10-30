# DSH rc.5 Desktop 打包与验证

2026-10-30（Asia/Shanghai），自用分支 `codex/personal-desktop`。本次使用官方桌面更新清单中的 macOS arm64 ZIP，而非仍旧的滚动 DMG；未安装、替换或重启用户现用 Desktop，未提交或推送。

## 来源与构建

- 来源：https://download.deepseek.com/dsh-desk/bin/mac-arm64/deepseek-harness-0.2.1-rc.5-mac-arm64.zip
- 下载大小 347767892 字节。下载后计算 SHA512，Base64 值与官方清单一致：`SPXR+TMC5+7v9R544aKgA2CkDrLr2XyNL/35/NuxGBbP5nrSTEGMurNRAi+R1RSlcWZm3KNdySAt0RS8Qizv9g==`。
- 解包核对应用 package.json 和 primary-runtime/runtime.json，均为 0.2.1-rc.5；应用构建提交 d4db512a969fccf0c5cc7ec8fe38e9c1d27af916。
- Node 24.21.0、Python 3.12.14、pnpm 11.28.5、13 项 Python 包均采用该载荷要求；Sharp 0.35.5，bundled Electron 44.4.5。9 项原生转换成功，无版本漂移；LibreOffice 使用既有同版本 WASM 回退策略。
- 现有主进程、标题栏、自用外观、系统代理和 MCP v2 补丁直接匹配，未调整功能补丁。构建入口新增 `--archive`，复用 7z 对 ZIP/DMG 的格式识别与内容哈希缓存，保留 `--dmg` 别名。

```sh
./auto-build.sh --arch x64 --formats deb --electron bundled --package-jobs 4 \
  --archive /绝对路径/已校验的官方.zip
```

## 本机交付

`dist/deepseek-harness_0.2.1-rc.5_amd64.bundled.deb`，259405060 字节，SHA256：

```text
13b0e527bc6d35e96c3d294a8e0b9578344a9094437002532c4d757e027e9c7f
```

附同目录 `.sha256`，已在该目录执行校验通过。原 rc.3 的 deb 在本轮开始前已不存在，仅余校验文件，不能视为可用回退包。本轮未删除用户产物或修改已安装实例。

## 验证结果与边界

- 63 项回归：61 通过，2 项缺少 RPM/pacman 工具跳过；成品解包后重复验证。包括真实 rc.5 MCP 协商、后台初始化、取消、重连、热重载和本机 HTTP/HTTPS CONNECT、私有 KDE D-Bus 代理切换。
- 构建脚本语法与主进程、两个自用 preload 语法通过；真实载荷侧栏 CSS 的 144 种布局组合通过。
- 成品包元数据、内置 CLI、Node/Python/pnpm、13 项 Python 包通过；Sharp 图片链路和独立 worker 隔离通过，133 个 ELF 架构检查通过。
- 成品 26565 个资源文件与已验证应用树逐文件内容一致。
- 从成品解包运行隔离 Wayland/XWayland Desktop：两者欢迎页跳过、主界面显示、最大化/还原及原生全屏切换通过；交通灯持续显示、实色背景和全屏布局标志符合预期，两者退出码均为 0。保存整屏截图，并查看 Wayland 主界面、XWayland 最大化截图；其他截图保存待人工进一步检查。
- 使用独立 HOME、DSH_HOME、XDG 配置/缓存/状态、user-data-dir 与随机调试和后端端口；无登录凭据或真实模型调用。测试参数 no-sandbox/disable-gpu 仅用于隔离验证，不写入成品启动参数。Inspector 直接观察原生 BrowserWindow 状态，未向成品注入观测代码。
- rc.5 主界面使用 `dsh-app://app/`。首次测试驱动仅识别 HTTP 页面、退出前未断开调试器，分别导致等待超时；修正驱动后从成品重新验证通过，不计入产品失败或通过场景。
- 空 HOME 没有用户工作区，界面提示需选择文件夹；本次不以该状态代替登录后真实插件、模型调用、已有会话、拖动/顶栏双击、GPU 或长会话人工验收。MCP 后台模式与 legacy 协商仍需现有显式配置，安装 deb 不自动修改用户配置。

本机测试日志及整屏截图只保存在被忽略的 others/ 下，可能包含其他应用画面，不进入 Git 或公开交付。

2026-10-30 用户反馈本次安装测试正常，未逐项说明覆盖范围，不扩展为完整人工测试矩阵。本机测试/构建日志、结果 JSON、私有截图及临时测试脚本已按用户要求移除；本文保留此前实际验证结论，不能再引用原始本机记录为当前存在的文件。官方 ZIP、依赖下载缓存、安装包与校验文件保留。
