# Linux 会话首次打开的同步阻塞修复

## 原因与修改

首次取得会话写锁时，`@deepseek-ai/node-addon-system/lib/flock.js` 的 `loadBinding()` 调用 `process.report.getReport()`，只为通过 `header.glibcVersionRuntime` 选择 glibc/musl 原生模块。完整报告可能对已连接的外网地址进行反向 DNS 查询。

构建补丁 `patches/patch-flock-libc.py` 仅在这一同步调用期间设置 `process.report.excludeNetwork=true`，通过 `finally` 恢复原值。异常继续传播，不把探测失败默认认作 musl；当前运行时若不支持该开关则明确报错。保留延迟加载、binding 缓存、原生包版本和文件锁竞争/释放语义。不依赖全局代理或 NODE_OPTIONS，不安装用户级核心覆盖包，不输出完整报告。

参考：https://nodejs.org/api/report.html （网络报告排除与反向 DNS 行为）。

当前载荷通过报告设置恢复、原生文件锁竞争及正常和异常退出释放回归。musl 路径使用模拟验证。成品检查见 [兼容性记录](COMPATIBILITY.md)。
