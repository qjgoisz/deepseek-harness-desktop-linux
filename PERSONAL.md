# 个人使用分支

`codex/personal-desktop` 在 GUI 修复与自动构建工具链之上加入实色圆角窗口。

普通窗口使用 12px 圆角；最大化和全屏布局取消圆角。交通灯在普通窗口、最大化和全屏时始终显示，可直接点击。侧栏顶部按钮取消让位位移，统一使用普通窗口的位置：展开态切换按钮贴侧栏右缘，折叠态切换按钮为 128px、新建按钮为 88px；最大化、全屏和鼠标进出顶部都不改变同一侧栏状态下的位置。保留原有的最大化和全屏策略，非活动窗口不自动激活。欢迎页和主界面都强制实色，不向 KWin 请求毛玻璃。

侧栏收起动画结束后，顶栏的侧栏底色宽度同步为 0，避免在新会话按钮附近残留底色分界。

圆角层由 `patches/patch-personal-rounded.py` 应用，包含在全新构建和已有应用树的升级流程中。它仅用于个人分支，不包含在上游 GUI PR 中。

构建 bundled x64 deb：

```sh
./auto-build.sh --arch x64 --formats deb --electron bundled --system-runtime --package-jobs 4
```

默认保留构建缓存；如需在成功后删除解包、打包暂存和应用树，增加 `--clean`。下载缓存仍保留，可在确认成品可用后删除构建存储目录。


当前适配基线为 DSH `0.2.2-rc.1`，保留 KDE/v2rayN 系统代理、MCP v2 启动优化、libc 探测及 Desktop Cookie 修复，窗口策略不变。2026-11-05 从已校验的官方更新 ZIP 构建 x86_64 bundled deb，Electron 同步至载荷的 44.7.0；用户反馈修复本机预设后界面恢复。具体测试范围见 [兼容性记录](docs/COMPATIBILITY.md)。
