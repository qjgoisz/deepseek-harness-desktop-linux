# 会话管理插件侧栏刷新修复

`dsh-sessions-manager` 3.8.1 的侧栏刷新重复写入会话行的类名和缩进。插件的 MutationObserver 收到这些变更后会再次安排刷新，静置时也可能每帧扫描侧栏。

补丁直接同步子代理和展开标记的目标状态，并只在缩进变化时写入。隔离 Electron 测试使用原版刷新函数和模拟侧栏，对照复现了连续刷新。补丁版在静置窗口内停止刷新，会话选中、子代理缩进及展开收起、未读标记、空白和回收站会话隐藏均通过。

在 DSH Desktop `0.2.2-rc.5` 实测中，页面已加载修补后的代码，且仍启用插件。静置观察未再出现会话行的重复属性写入，性能采样中侧栏刷新回到低频兜底检查。

在仓库根目录运行，需 Python 3、Node.js 和 GNU patch。

```sh
python3 local-fixes/dsh-sessions-manager/apply-fix.py
python3 local-fixes/dsh-sessions-manager/apply-fix.py --apply
```

脚本默认检查 Desktop profile，也可用 `--profile` 指定目录。它核对版本和文件摘要，语法检查通过后才备份并原子替换 `lib/client.js`。重复执行会识别已应用的补丁。插件升级或重装后，先检查当前版本。

已打开的 DSH 窗口需要重新加载客户端代码。撤销时，用脚本打印的同版本备份替换 `lib/client.js`，再重新加载客户端代码。
