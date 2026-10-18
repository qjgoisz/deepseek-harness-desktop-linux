# 本机 dsh-usage 导航兼容修复

`@linxin666/dsh-usage@0.4.4` 的今日用量卡片使用侧栏 `settingsArea` 内第一个按钮进入设置。在当前 DSH 中，这个按钮打开头像菜单，因此只留下账号菜单，无法进入使用统计。

此修复适用于本机 Desktop profile 的 `dsh-usage` 和聚合包 `dsh-web-all` 的客户端文件，不属于 Desktop 打包补丁，不会自动进入社区项目 PR。

新逻辑保留旧版直接打开设置的路径；当前版本先选择账号菜单中的“设置”，再选择“使用统计”。箭头仍只展开/收起卡片。已有设置窗口不会被关闭，无关对话框不会被误当作设置；未知菜单结构会停止操作并关闭本次打开的菜单。

预览与应用（无需 sudo）：

```bash
python3 local-fixes/dsh-usage-settings/test-fix.py
python3 local-fixes/dsh-usage-settings/apply-fix.py
python3 local-fixes/dsh-usage-settings/apply-fix.py --apply
```

应用后完整退出并重开 Desktop。原文件保存在各插件的 `lib/client.js.before-usage-settings-fix`；恢复时复制回同目录 `client.js`。插件更新/重装可能覆盖修复。脚本检查旧逻辑及 JS 语法，遇到未知新版会停止，需重新核对。
