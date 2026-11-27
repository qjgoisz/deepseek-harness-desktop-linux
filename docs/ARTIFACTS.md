# DeepSeek Harness — Linux 安装包

## Arch Linux x86_64

- 文件 `dist/dsh-desktop-macos-style-1:0.2.2_rc.5-2-x86_64.pkg.tar.zst`
- 大小 124535508 字节
- SHA256 `1e924396445f0fefa902315091989602ee745eca6fc73785cae2eb7d122e89ed`

2026-11-27 使用重新校验的官网 Apple Silicon DMG 构建。应用和运行时均为 `0.2.2-rc.5`，保留 Netlink 退避和图片 worker 重装修复。用户验收后已清理上一版成品。

使用 pacman 管理 Electron 44、Node、Python 和 pnpm。Office 和数据处理所用的 Python 库按需安装，PowerPoint 编辑依赖的 `python-pptx` 可由 Arch Linux CN 提供。安装前核对校验和。

```sh
cd dist
pkg='dsh-desktop-macos-style-1:0.2.2_rc.5-2-x86_64.pkg.tar.zst'
sha256sum -c "$pkg.sha256" && sudo pacman -U "./$pkg"
```

同名旧版本可直接升级。如果 pacman 提示与 `deepseek-harness-desktop` 冲突，确认移除后会在同一次事务中完成迁移。新包沿用原来的启动器和用户数据路径。

系统依赖和旧工作区路径说明见 [Arch 迁移](AUTO_BUILD.md#arch-linux-迁移与系统运行时)。验证范围见 [兼容性记录](COMPATIBILITY.md)。

## Debian amd64

Debian 的 rc.5 构建命令与运行时配置见 [构建说明](AUTO_BUILD.md#自用-deb-使用系统运行时)。本轮交付范围为 Arch x86_64。
