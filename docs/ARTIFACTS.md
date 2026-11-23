# DeepSeek Harness — Linux 安装包

## Arch Linux x86_64

- 文件 `dist/deepseek-harness-desktop-0.2.2_rc.5+systemruntime1-1-x86_64.pkg.tar.zst`
- 大小 124543566 字节
- SHA256 `41d1969268d71e015f2d2349c338768fc79e6f1430b90898b138168a4a5aebbb`

2026-11-23 从官方下载页的 Apple Silicon DMG 按原版本号重新构建。构建源码见 `personal-dsh-v0.2.2-rc.5`。

由仓库根目录的 `PKGBUILD` 经 `makepkg` 构建，可升级同包名的 rc.3。使用 pacman 管理 Electron 44、Node、Python、pnpm 和 Office Python 库。本机的 `python-pptx` 由 Arch Linux CN 提供。安装前核对校验和。

```sh
cd dist
sha256sum -c deepseek-harness-desktop-0.2.2_rc.5+systemruntime1-1-x86_64.pkg.tar.zst.sha256
sudo pacman -U ./deepseek-harness-desktop-0.2.2_rc.5+systemruntime1-1-x86_64.pkg.tar.zst
```

系统依赖和旧工作区路径说明见 [Arch 迁移](AUTO_BUILD.md#arch-linux-迁移与系统运行时)。验证范围见 [兼容性记录](COMPATIBILITY.md)。

## Debian amd64

Debian 的 rc.5 构建命令与运行时配置见 [构建说明](AUTO_BUILD.md#自用-deb-使用系统运行时)。本轮交付范围为 Arch x86_64。
