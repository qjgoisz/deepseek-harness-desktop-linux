# KDE/v2rayN 系统代理适配

适用：Linux KDE/Plasma 的 DSH Desktop，HTTP/HTTPS 手动代理。默认从桌面图标启动即可读取系统代理；v2rayN 的 KDE 配置更新通知和 `kioslaverc` 文件变化触发后台刷新，无需为每次启动添加代理环境变量。此功能不修改桌面设置，也不依赖代理服务固定监听某个端口。

## 代理来源与切换

- 仅 Desktop Host 启用；CLI、非 KDE 桌面、工作流/脚本 worker 保留上游代理行为。
- 用户在启动环境或受信任的 DSH home `.env` 中明确设置 `http_proxy`、`https_proxy`、`all_proxy`（或大写形式）时，尊重这份覆盖，不自动跟随 KDE。只有 `no_proxy` 不算手动代理覆盖，它会与系统绕过项合并。
- `DSH_DESKTOP_SYSTEM_PROXY=0` 可禁用适配，恢复上游环境变量行为。普通使用无需设置此变量。
- 通过 `kreadconfig6`/`kreadconfig5` 读取 KDE 代理模式、HTTP/HTTPS 端点、绕过列表等；通过会话总线监听 `/KIO/Scheduler` 的 `org.kde.KIO.Scheduler.reparseSlaveConfiguration`。这正是 v2rayN 官方 Linux 脚本在更新配置后发送的信号。
- 同时监听配置目录以覆盖配置文件的原子替换，并每 30 秒低频检查一次，补偿缺少 D-Bus 工具或漏掉通知的情况。重复通知合并，读取过期结果被丢弃，相同策略不重建连接池。
- 开关或端口变更对新请求生效；旧连接池停止接收新请求，让已有流式响应完成。应用退出时统一释放监听和连接。
- 关闭系统代理时切换直连，并清除适配器发布的旧代理变量；以后新启动的工具继承当前策略。已经启动的外部工具不会因父进程更改变量而自动切换。

## 绕过与支持边界

保留普通域名/子域名、端口和通配 `*` 等上游支持的绕过形式，补充 IPv4 字面地址的 CIDR 匹配。localhost、整个 127.0.0.0/8 和 IPv6 回环仍使用上游强制直连规则。不会为了匹配 CIDR 而解析目标域名。

首版不处理 PAC/自动发现、反向例外、纯 SOCKS、IPv6 CIDR 或 `<local>` 等特殊 KIO 例外语法。配置不支持或读取失败时输出不含端点/凭据的诊断，保留最近一次成功策略；首次启动尚无有效系统策略时沿用初始直连状态。下游工具使用各自的 `NO_PROXY` 语法，不能据此宣称所有外部程序完全支持相同 CIDR/绕过语义。插件自行创建的网络代理和已经运行的外部进程也不保证被全局 dispatcher 覆盖。

`kreadconfig` 属于 KDE 工具；缺失时会给出诊断。`dbus-monitor` 缺失时文件监听和周期检查继续工作，不新增硬性 D-Bus 包依赖。

## 仓库实现

- `patches/patch-system-proxy.py`：构建时检查全部匹配点，再修改 `dsh-http-proxy` 与 `runProfile` 的导入/调用；重复运行验证一致性，未知载荷或已有陌生适配代码失败，不保留部分修改。
- `patches/system-proxy/desktop-system-proxy.mjs`：KDE 读取、范围判断和通知监听，启动时动态加载，保持原代理策略模块在浏览器 worker 中可加载。
- `patches/system-proxy/proxy-controller.js`：追加到原代理模块内部，复用其解析、路由、环境发布和 Undici 依赖；采用单一生命周期管理连接池更新，避免旧 disposer 恢复过期策略。
- `scripts/build/tree.sh`：正常应用树构建自动运行补丁。不向用户 profile 安装核心包，不改变载荷中的版本或插件锁文件。

## 验证

```sh
python3 -m unittest discover -s tests -v
bash -n auto-build.sh
bash -n install-image-worker.sh
for script in scripts/build/*.sh; do bash -n "$script"; done
```

`tests/test_system_proxy.py` 覆盖补丁拒绝/幂等、环境覆盖、KDE 读取、分片通知、读取失败保留策略和生命周期；使用真实载荷副本、Undici 与本机模拟 HTTP 代理和本机 HTTPS CONNECT 隧道（临时测试 CA）验证路由、切换、IPv4 CIDR、域名例外、旧响应继续及子进程环境。可用 `DSH_TEST_APP=/绝对路径/resources/app` 指定真实测试载荷。真实载荷缺失时相关集成用例跳过；`kreadconfig6`/D-Bus 工具缺失时真实桌面通知用例跳过。

真实通知用例在 `dbus-run-session` 的私有总线上发送信号、使用独立 HOME/XDG 配置；另行关闭文件监听/周期回读，断言 D-Bus 本身触发配置读取。不会向正在使用的桌面总线发送测试通知。

2026-10-28 用户反馈本次 KDE/v2rayN 代理修复“可以了”，并授权清理缓存及推送。此为用户人工使用反馈，未逐项说明开关、端口修改、模型/插件、Wayland/XWayland 或长会话覆盖范围；不扩展为完整测试矩阵通过。

本机 HTTP/HTTPS 模拟服务与私有 D-Bus 测试均已通过。后续回归可逐项覆盖普通启动、代理开关、端口修改、流式响应及插件联网；本次用户反馈不替代这些逐项覆盖记录。

参考：
- v2rayN 官方 Linux 脚本：https://github.com/2dust/v2rayN/blob/master/v2rayN/ServiceLib/Sample/proxy_set_linux_sh
- Electron Chromium 与 Node 网络栈区分：https://www.electronjs.org/docs/latest/api/net/
