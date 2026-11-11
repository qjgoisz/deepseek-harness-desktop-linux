# DeepSeek Harness — Linux 安装包

当前自用安装包为 DSH Desktop `0.2.2-rc.2+systemruntime3` amd64 bundled deb，内置 Electron 44.7.0，使用 Debian 的 Node 和 Python。本次修订修复图片并发处理时的 `INVALID_IMAGE` 误报。

- 文件 `dist/deepseek-harness_0.2.2-rc.2+systemruntime3_amd64.bundled.deb`
- 大小 184219512 字节
- SHA256 `ff31934cae39957721e50c008c142f987620c4b2ce68eab5dd969034172b1049`

在仓库根目录校验并安装。

```sh
cd dist
sha256sum -c deepseek-harness_0.2.2-rc.2+systemruntime3_amd64.bundled.deb.sha256
sudo apt install ./deepseek-harness_0.2.2-rc.2+systemruntime3_amd64.bundled.deb
```

安装后可从桌面菜单启动 DeepSeek Harness。当前验证范围见 [兼容性记录](COMPATIBILITY.md)。
