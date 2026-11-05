# 自用 DSH Desktop 项目交接

更新日期：2026-11-05。分支 codex/personal-desktop。用户反馈修复预设后界面恢复。源码交付目标为 origin/codex/personal-desktop。

## 本轮：0.2.2-rc.1 适配

- 官方清单的完整 ZIP 已核对 SHA512/大小，内部应用/runtime 均为 rc.1（11 月 4 日发布、复核时为 100% 分发）。核对时默认 DMG 尚未提供本版，使用官方 ZIP 完成 auto-build.sh 全流程。
- patch-main.py 兼容 PlatformView 新增第四参数，保留更新输入守卫；未知/重复调用拒绝。Electron 默认同步载荷的 44.7.0，Node/Python/pnpm/Sharp 等依赖无版本漂移；逐项官方复核见 docs/patches/README.md。官方 master 已修复 Cookie 累积，当前发布 ZIP 仍需此补丁。
- 新包 dist/deepseek-harness_0.2.2-rc.1_amd64.bundled.deb，261037952 字节，SHA256 22343671318810dd0d48e57cdf79df865431a5e9fcc2f4dd758bf0be8b70f54a。最终复核时 dist/ 只剩 rc.1 安装包及校验文件。成品 81 项回归 79 通过、2 工具缺失跳过；144 侧栏组合、CLI/pnpm、13 Python 包、图片隔离、133 ELF、29379 资源一致性与校验通过。
- 最终包隔离 Wayland/XWayland 各启动/重启一次，约 2–3 秒进入可见主界面，100 个合成 Cookie 不增长、正常退出；侧栏、原生最大化/还原和全屏通过。8 张整屏截图成功，普通窗口部分边缘不在多屏截图可见区，不视为完整圆角/拖动验收。无用户凭据、插件、模型或原会话，GPU 和长会话待人工测试。
- 用户修复本机预设后反馈界面恢复。隔离复查中 5 个自定义预设均能加载和新建会话，20 份旧会话均能读取，11 个主会话均可恢复。按要求已清理本轮下载、应用树、构建和测试暂存，保留安装包、校验文件及脱敏摘要。测试实例已关闭，无临时 worktree。详见 docs/COMPATIBILITY.md。
