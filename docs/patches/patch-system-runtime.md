# patch-system-runtime.py

[补丁源码](../../patches/patch-system-runtime.py)

`load_workspace_dependencies` 返回系统 Python、系统 Node、pnpm 路径及实际 Python 库版本。
Debian 使用内置 pnpm，并在默认 PPTX 命令中加入私有 `python-pptx`。Arch 直接使用
`/usr/bin/pnpm` 和系统 `python-pptx`。项目显式指定的环境优先。

补丁处理工作区依赖工具、主运行时清单、Office 编辑技能的 Python 环境说明、Desktop Host 启动路径和 CLI 启动器。
保留指向系统 Node 的兼容链接供命令管理和图片 worker 使用。构建和依赖声明见[系统运行时打包](../AUTO_BUILD.md#自用-deb-使用系统运行时)。

## 官方修复核对

不适用。系统解释器的选择属于发行包策略。核对的官方 `0.2.2-rc.5` 载荷由 `load_workspace_dependencies` 选择随附的解释器，Office 编辑技能默认使用该工具返回的路径。
