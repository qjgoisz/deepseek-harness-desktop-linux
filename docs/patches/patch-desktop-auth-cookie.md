# patch-desktop-auth-cookie.py：Desktop 本地认证 Cookie 累积

源码：[查看文件](../../patches/patch-desktop-auth-cookie.py)。

## 用途与目标

目标：Desktop 载荷中的 `lib/main.js`。

Desktop Host 使用随机端口。浏览器认证 Cookie 的名称包含完整 authority（含端口），有效期默认为 30 天，而浏览器匹配 Cookie 不按端口隔离。不断启动会使同一主机的 Cookie 请求头增长，超过 Node 默认的 16KiB 请求头上限后返回 HTTP 431，发生在应用认证处理之前。

补丁复用 Desktop 已有的 `authenticateWebHost()` 结果，将欢迎页 RPC 和账户 WebSocket 统一为当前 Host 的内存 Cookie；不再通过 Electron `net.fetch` 交换第二次认证，也不再读取持久 Cookie 库。HTTP 适配器校验目标 origin、拒绝 URL 用户信息并禁止重定向。Host 初始认证和 RPC 的错误保留 HTTP 状态码。

保留完整 authority、签名、有效期及浏览器/API 凭据的原有校验；不改变通用 Web 认证协议或放宽请求头上限。旧持久 Cookie 不再用于这些请求，可等待到期，不需要删除整个 Cookie 库。

## 官方是否已有等价修复

**官方 master 源码已有等价修复，已核对的发布 ZIP 尚未包含。**

发布 ZIP 的 lib/main.js 仍在欢迎页使用 net.fetch 和持久 Cookie 库进行认证。master 已将单次 Host 认证得到的内存 Cookie 用于欢迎页 HTTP 与账户 WebSocket，并在 Host 启动后按名称清理同一主机的旧认证 Cookie。当前发布 ZIP 仍需补丁。后续应确认新发布载荷包含修复，再跑 HTTP、WebSocket 与重启回归。 [apps/desktop/src/main.ts](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/apps/desktop/src/main.ts) [apps/desktop/src/welcome-backend.ts](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/apps/desktop/src/welcome-backend.ts) [apps/desktop/src/account-backend.ts](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/apps/desktop/src/account-backend.ts) [apps/desktop/src/web-document.ts](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/apps/desktop/src/web-document.ts)

核对范围见 [补丁总览](README.md#核对基线)。

## 后续核对条件

检查官方 Desktop 是否已停止将随机端口的本地 Host 认证 Cookie 写入持久会话，并确保欢迎页 HTTP、账户 WebSocket、后台重启均不受遗留 Cookie 超限影响。仅提高 HTTP 请求头上限或缩短 Cookie 有效期，不属于等价解决累积机制。

返回 [补丁总览](README.md)。
