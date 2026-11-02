# patch-desktop-auth-cookie.py：Desktop 本地认证 Cookie 累积

文档及官方固定源码核对日期：2026-11-02。源码：[查看文件](../../patches/patch-desktop-auth-cookie.py)。

## 用途与目标

目标：Desktop 载荷中的 `lib/main.js`。

Desktop Host 使用随机端口。浏览器认证 Cookie 的名称包含完整 authority（含端口），有效期默认为 30 天，而浏览器匹配 Cookie 不按端口隔离。不断启动会使同一主机的 Cookie 请求头增长，超过 Node 默认的 16KiB 请求头上限后返回 HTTP 431，发生在应用认证处理之前。

补丁复用 Desktop 已有的 `authenticateWebHost()` 结果，将欢迎页 RPC 和账户 WebSocket 统一为当前 Host 的内存 Cookie；不再通过 Electron `net.fetch` 交换第二次认证，也不再读取持久 Cookie 库。HTTP 适配器校验目标 origin、拒绝 URL 用户信息并禁止重定向。Host 初始认证和 RPC 的错误保留 HTTP 状态码。

保留完整 authority、签名、有效期及浏览器/API 凭据的原有校验；不改变通用 Web 认证协议或放宽请求头上限。旧持久 Cookie 不再用于这些请求，可等待到期，不需要删除整个 Cookie 库。

## 官方是否已有等价修复

**所查官方固定源码仍存在该路径，未发现等价修复。**

核对固定快照 `ce7073d51254c26cd63b22a60835b8f948deb447`：

- [apps/desktop/src/main.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/apps/desktop/src/main.ts) 已先取得 `hostCookie`，随后仍以 `net.fetch` 和默认会话 Cookie 读取器调用欢迎页连接。
- [apps/desktop/src/welcome-backend.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/apps/desktop/src/welcome-backend.ts) 再次以 `credentials: include` 访问启动 URL；请求失败仅抛出通用认证错误。
- [apps/desktop/src/web-document.ts](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/apps/desktop/src/web-document.ts) 已提供不依赖 Chromium Cookie 库的 Host Cookie 获取和主页面转发路径，但未统一欢迎页连接。

结论只针对上述快照，不代表最新 master 或后续桌面载荷；本项源码审计未检查最新 master。既有官方 rc.5 载荷来源与校验记录见 [核对基线](README.md#核对基线)。

## 后续核对条件

检查官方 Desktop 是否已停止将随机端口的本地 Host 认证 Cookie 写入持久会话，并确保欢迎页 HTTP、账户 WebSocket、后台重启均不受遗留 Cookie 超限影响。仅提高 HTTP 请求头上限或缩短 Cookie 有效期，不属于等价解决累积机制。

返回 [补丁总览](README.md)。
