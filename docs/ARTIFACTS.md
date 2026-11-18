# DeepSeek Harness — Linux 安装包

## Arch Linux x86_64

- 文件 `dist/deepseek-harness-desktop-0.2.2_rc.3+systemruntime1-2-x86_64.pkg.tar.zst`
- 大小 124505862 字节
- SHA256 `d19fe3b45d7b80780e267875339c51b74da4c85fb6cc70f5bc84f00533b7ca5c`

由仓库根目录的 `PKGBUILD` 经 `makepkg` 构建，可升级相同包名的 `pkgrel=1`。
使用 pacman 管理 Electron 44、Node、Python、pnpm 和 Office Python 库。当前 `python-pptx`
由 Arch Linux CN 提供。安装步骤和旧工作区路径说明见 [Arch 迁移](AUTO_BUILD.md#arch-linux-迁移与系统运行时)。

## Debian amd64

自用安装包为 DSH Desktop `0.2.2-rc.3+systemruntime3` amd64 bundled deb，内置 Electron 44.7.0，使用 Debian 的 Node 和 Python。包含图片并发处理时的 `INVALID_IMAGE` 修复。

- 文件 `dist/deepseek-harness_0.2.2-rc.3+systemruntime3_amd64.bundled.deb`
- 大小 184274592 字节
- SHA256 `b8d119061fc210a2b570415eae408a1b79c0276152c4c401f943df666cff26a8`

在仓库根目录校验并安装。

```sh
cd dist
sha256sum -c deepseek-harness_0.2.2-rc.3+systemruntime3_amd64.bundled.deb.sha256
sudo apt install ./deepseek-harness_0.2.2-rc.3+systemruntime3_amd64.bundled.deb
```

安装后可从桌面菜单启动 DeepSeek Harness。当前验证范围见 [兼容性记录](COMPATIBILITY.md)。
