# Qoder 侧栏布局修复

`dsh-qoder-connect` 的共享底栏样式会让「会话与工作区」入口被裁切，即使额度卡已经关闭。脚本仅在磁盘上找到已验证的规则时替换它。新的规则在额度卡或折叠态额度按钮显示时启用纵向单列布局。已在 DSH Desktop `0.2.2-rc.3` 与 `dsh-qoder-connect 0.2.16` 上验收。

在仓库根目录运行，需 Python 3 和 PATH 上的 Node.js。

```sh
python3 local-fixes/dsh-qoder-sidebar/apply-fix.py         # 只检查
python3 local-fixes/dsh-qoder-sidebar/apply-fix.py --apply # 备份并应用
```

默认使用 Desktop profile。脚本沿用已配置的 `DSH_HOME`，也支持用 `--profile /绝对路径/到/profile` 指定目录。

每次插件更新或重装后可先检查。已修复时重复运行不会写入。新版规则变化或出现重复时，脚本会退出并提示复核。应用后完全退出并重开 DSH。若要撤销，可在 DSH 退出后把脚本本次打印的备份复制回同目录下的 `client.js`。请选用当前安装版本对应的备份。
