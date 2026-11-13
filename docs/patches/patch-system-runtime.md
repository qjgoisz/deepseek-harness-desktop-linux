# patch-system-runtime.py

[补丁源码](../../patches/patch-system-runtime.py)

`load_workspace_dependencies` 返回系统 Python、系统 Node、内置 pnpm 及实际 Python 库版本。
PPTX 技能只在执行 PPTX 脚本时将私有的 `python-pptx` 加入搜索路径。项目显式指定的环境优先。

补丁处理工作区依赖工具、主运行时清单、Office 编辑技能的 Python 环境说明、Desktop Host 启动路径和 CLI 启动器。
保留指向系统 Node 的兼容链接供命令管理和图片 worker 使用。构建和依赖声明见[系统运行时打包](../AUTO_BUILD.md#自用-deb-使用系统运行时)。

## 官方修复核对

不适用。系统解释器的选择属于 Debian 打包策略。核对的官方 `0.2.2-rc.3` 载荷由 `load_workspace_dependencies` 选择随附的解释器，Office 编辑技能默认使用该工具返回的路径。
