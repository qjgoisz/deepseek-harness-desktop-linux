# DeepSeek Harness — Linux 安装包

## Arch Linux x86_64

- 文件 `dist/deepseek-harness-desktop-macos-style-0.2.2_rc.5+systemruntime1-1-x86_64.pkg.tar.zst`
- 大小 124547553 字节
- SHA256 `b7c23cefd58640e52c15137bcc83a2595396812cb3654d20aff42453b3f28521`

2026-11-25 将 11 月 23 日已验收的 rc.5 成品以新包名重打包。该载荷基于官网 DMG，包含 Netlink 退避和图片 worker 重装修复。用户验收新包后，已清理旧包及本轮暂存。`dist/` 保留新包及 SHA256 校验文件。新包未生成 PGP 签名。

仓库根目录的 `PKGBUILD` 使用新包名构建。使用 pacman 管理 Electron 44、Node、Python、pnpm 和 Office Python 库。本机的 `python-pptx` 由 Arch Linux CN 提供。安装前核对校验和。

```sh
cd dist
pkg=deepseek-harness-desktop-macos-style-0.2.2_rc.5+systemruntime1-1-x86_64.pkg.tar.zst
sha256sum -c "$pkg.sha256" && sudo pacman -U "./$pkg"
```

已安装 `deepseek-harness-desktop` 时，pacman 会询问是否移除冲突的旧包，确认后在同一次事务中完成迁移。新包沿用原来的启动器和用户数据路径。

系统依赖和旧工作区路径说明见 [Arch 迁移](AUTO_BUILD.md#arch-linux-迁移与系统运行时)。验证范围见 [兼容性记录](COMPATIBILITY.md)。

## Debian amd64

Debian 的 rc.5 构建命令与运行时配置见 [构建说明](AUTO_BUILD.md#自用-deb-使用系统运行时)。本轮交付范围为 Arch x86_64。
