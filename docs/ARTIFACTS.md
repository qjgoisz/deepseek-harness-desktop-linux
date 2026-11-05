# DeepSeek Harness — Linux 安装包

当前验证产物为 DSH Desktop `0.2.2-rc.1` 的 amd64 bundled deb，内置 Electron 44.7.0。

- 文件：`dist/deepseek-harness_0.2.2-rc.1_amd64.bundled.deb`
- 大小：261037952 字节
- SHA256：`22343671318810dd0d48e57cdf79df865431a5e9fcc2f4dd758bf0be8b70f54a`

在仓库根目录校验并安装：

```sh
cd dist
sha256sum -c deepseek-harness_0.2.2-rc.1_amd64.bundled.deb.sha256
sudo apt install ./deepseek-harness_0.2.2-rc.1_amd64.bundled.deb
```

安装后可从桌面菜单启动 DeepSeek Harness Desktop。构建工具支持其他架构和包格式，本版实测范围为上述安装包。官方下载来源、会话复查和图形测试范围见 [兼容性记录](COMPATIBILITY.md)。
