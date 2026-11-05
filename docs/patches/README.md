# 补丁总览与官方修复核对

本目录覆盖 `patches/` 全部 15 个源码文件（13 个 Python 脚本、2 个运行时辅助文件），每个文件均有独立说明。

审计仅回答：**DeepSeek 官方在所查载荷或源码中，是否已有补丁所解决问题的等价实现。** 补丁的用途与目标单独说明；本地脚本维护、分支叠加和测试成绩不作为官方修复证据。

已核对的发布 ZIP 仍需现有适配。官方 master 已修复 Desktop Cookie 累积。界面定制和旧树迁移不属于官方缺陷修复审计，标为“不适用”；两个代理辅助文件按对应功能核对，不另算两个独立的官方缺陷。

## 核对基线

2026-11-05 复核官方发布 ZIP `0.2.2-rc.1` 和 [官方 master 快照 fcc0ad4](https://github.com/deepseek-ai/deepseek-harness/tree/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159)。ZIP 已按清单核对大小及 SHA512，应用和 runtime 均为 rc.1。该源码快照的 Desktop 版本也标为 rc.1，但 ZIP 内构建提交不同。发布包来源见 [兼容性记录](../COMPATIBILITY.md)。

逐项对照了原始发布包与源码中的适用路径，并在发布包副本验证构建补丁链及主进程和两个 preload 的语法。指纹门禁核对使用发布包所需版本的 Linux x64 npm 原生包。

## 逐文件结论

| 文件 / 独立文档 | 官方修复核对结果 |
|---|---|
| [patch-main.py](patch-main.md) | 未发现等价修复。 |
| [patch-titlebar.py](patch-titlebar.md) | 发布 ZIP 和所查源码均未发现等价实现。 |
| [patch-mac-chrome.py](patch-mac-chrome.md) | 发布 ZIP 和所查源码均未发现等价实现。 |
| [patch-kde-material.py](patch-kde-material.md) | 发布 ZIP 和所查源码均未发现等价实现。 |
| [patch-fullscreen-reveal.py](patch-fullscreen-reveal.md) | 发布 ZIP 和所查源码均未发现等价实现。 |
| [patch-linux-identity.py](patch-linux-identity.md) | 发布 ZIP 和所查源码均未发现等价实现。 |
| [patch-personal-rounded.py](patch-personal-rounded.md) | 不适用：不纳入官方缺陷是否修复的判定。 |
| [patch-fingerprint.py](patch-fingerprint.md) | 所核对的 Linux x64 同版本依赖仍有门禁。 |
| [patch-system-proxy.py](patch-system-proxy.md) | 未发现等价修复。 |
| [patch-mcp-negotiation.py](patch-mcp-negotiation.md) | 未发现等价修复。 |
| [patch-flock-libc.py](patch-flock-libc.md) | 未发现等价修复。 |
| [patch-desktop-auth-cookie.py](patch-desktop-auth-cookie.md) | master 已有等价修复，发布 ZIP 仍需补丁。 |
| [upgrade-mac-chrome.py](upgrade-mac-chrome.md) | 不适用：迁移工具不能按官方缺陷修复判定失效。 |
| [system-proxy/desktop-system-proxy.mjs](system-proxy--desktop-system-proxy.md) | 对应系统代理能力未发现官方等价实现。 |
| [system-proxy/proxy-controller.js](system-proxy--proxy-controller.md) | 对应动态切换能力未发现官方等价实现。 |

## 判断规则

- “未发现等价修复”只针对所查载荷与对应依赖，不是对未来版本的判断。
- 源码已有等价实现，但尚未进入实际桌面载荷时，应分别记录两者状态，不能直接认定已发布修复。
- 锚点匹配失败、重复执行无变化和外观相似，不能独立证明官方已修复。
- 外部原生依赖应核对载荷实际使用的包和版本，不能仅凭桌面源码推断。
- “不适用”不表示已修复或应删除；它表示该文件没有可用于本次判断的官方缺陷对象。

后续若官方提供等价实现，应核对其是否进入实际交付载荷及具体行为，再决定对应补丁是否可以移除。源码审计与实际载荷审计分别记录。
