# DeepSeek Harness — Linux 安装包

## Arch Linux x86_64

- 文件 `dist/dsh-desktop-macos-style-0.2.2_rc.5+systemruntime1-1-x86_64.pkg.tar.zst`
- 大小 124547549 字节
- SHA256 `8068df555eb82fbd344dcd4d60299a68e33afc31c41874dc0a62ecaf5fc46309`

2026-11-25 将已验收的 rc.5 应用载荷以短包名重打包。该载荷基于官网 DMG，包含 Netlink 退避和图片 worker 重装修复。旧名成品已清理。

仓库根目录的 `PKGBUILD` 使用新包名构建。使用 pacman 管理 Electron 44、Node、Python、pnpm 和 Office Python 库。本机的 `python-pptx` 由 Arch Linux CN 提供。安装前核对校验和。

```sh
cd dist
pkg=dsh-desktop-macos-style-0.2.2_rc.5+systemruntime1-1-x86_64.pkg.tar.zst
sha256sum -c "$pkg.sha256" && sudo pacman -U "./$pkg"
```

已安装旧包时，pacman 会询问是否移除冲突的旧包，确认后在同一次事务中完成迁移。新包沿用原来的启动器和用户数据路径。

系统依赖和旧工作区路径说明见 [Arch 迁移](AUTO_BUILD.md#arch-linux-迁移与系统运行时)。验证范围见 [兼容性记录](COMPATIBILITY.md)。

## Debian amd64

Debian 的 rc.5 构建命令与运行时配置见 [构建说明](AUTO_BUILD.md#自用-deb-使用系统运行时)。本轮交付范围为 Arch x86_64。
