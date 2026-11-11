# DeepSeek Harness — Linux 安装包

当前自用安装包为 DSH Desktop `0.2.2-rc.2+systemruntime2` amd64 bundled deb，内置 Electron 44.7.0，使用 Debian 的 Node 和 Python。

- 文件 `dist/deepseek-harness_0.2.2-rc.2+systemruntime2_amd64.bundled.deb`
- 大小 184213760 字节
- SHA256 `3e020287d75aa7ddf6b4ce6a32ed7332058cc960fa940bd22fca9792ad1ad1c7`

在仓库根目录校验并安装。

```sh
cd dist
sha256sum -c deepseek-harness_0.2.2-rc.2+systemruntime2_amd64.bundled.deb.sha256
sudo apt install ./deepseek-harness_0.2.2-rc.2+systemruntime2_amd64.bundled.deb
```

安装后可从桌面菜单启动 DeepSeek Harness。当前验证范围见 [兼容性记录](COMPATIBILITY.md)。
