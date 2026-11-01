# 补丁总览与官方修复核对

文档调整：2026-11-01。官方核对日期：2026-10-31。本目录覆盖 `patches/` 全部 14 个源码文件（12 个 Python 脚本、2 个运行时辅助文件），每个文件均有独立说明。

审计仅回答：**DeepSeek 官方在所查载荷或源码中，是否已有补丁所解决问题的等价实现。** 补丁的用途与目标单独说明；本地脚本维护、分支叠加和测试成绩不作为官方修复证据。

在适用的功能项中，尚未确认有整份补丁已被官方等价实现替代。界面定制和旧树迁移不属于官方缺陷修复审计，标为“不适用”；两个代理辅助文件按对应功能核对，不另算两个独立的官方缺陷。

## 核对基线

- [官方桌面更新清单](https://download.deepseek.com/dsh-desk/feeds/mac-arm64/nightly-mac.yml)在核对时为 `0.2.1-rc.5`。使用清单对应的完整 macOS arm64 ZIP，实际校验 SHA512，并展开核对应用 `package.json` 与 `runtime/primary-runtime/runtime.json`，两者均为 rc.5；没有仅凭文件名判断版本。
- 归档 SHA512（base64）：`SPXR+TMC5+7v9R544aKgA2CkDrLr2XyNL/35/NuxGBbP5nrSTEGMurNRAi+R1RSlcWZm3KNdySAt0RS8Qizv9g==`。
- 另检查官方仓库 master 的固定快照 [`ce7073d51254c26cd63b22a60835b8f948deb447`](https://github.com/deepseek-ai/deepseek-harness/tree/ce7073d51254c26cd63b22a60835b8f948deb447)，提交时间为 2026-10-29 16:13:15 UTC；其中 [Desktop package.json](https://github.com/deepseek-ai/deepseek-harness/blob/ce7073d51254c26cd63b22a60835b8f948deb447/apps/desktop/package.json) 标为 `0.2.2-alpha.2`。源码版本不等于已发布桌面载荷。
- 对照的是各补丁实际修改的行为和锚点。指纹门禁位于外部原生依赖，本次用 rc.5 对应的 Linux x64 同版本 npm 包实测，不把 GUI 仓库没有相关代码当作外部包已修复的证据。

## 逐文件结论

| 文件 / 独立文档 | 官方修复核对结果 |
|---|---|
| [patch-main.py](patch-main.md) | 未发现等价修复。 |
| [patch-titlebar.py](patch-titlebar.md) | 未发现等价修复。 |
| [patch-mac-chrome.py](patch-mac-chrome.md) | 未发现等价实现。 |
| [patch-kde-material.py](patch-kde-material.md) | 未发现等价实现。 |
| [patch-fullscreen-reveal.py](patch-fullscreen-reveal.md) | 未发现等价实现。 |
| [patch-linux-identity.py](patch-linux-identity.md) | 未发现等价修复。 |
| [patch-personal-rounded.py](patch-personal-rounded.md) | 不适用：不纳入官方缺陷是否修复的判定。 |
| [patch-fingerprint.py](patch-fingerprint.md) | 所核对的 Linux x64 同版本依赖仍有门禁。 |
| [patch-system-proxy.py](patch-system-proxy.md) | 未发现等价修复。 |
| [patch-mcp-negotiation.py](patch-mcp-negotiation.md) | 未发现等价修复。 |
| [patch-flock-libc.py](patch-flock-libc.md) | 未发现等价修复。 |
| [upgrade-mac-chrome.py](upgrade-mac-chrome.md) | 不适用：迁移工具不能按官方缺陷修复判定失效。 |
| [system-proxy/desktop-system-proxy.mjs](system-proxy--desktop-system-proxy.md) | 对应系统代理能力未发现官方等价实现。 |
| [system-proxy/proxy-controller.js](system-proxy--proxy-controller.md) | 对应动态切换能力未发现官方等价实现。 |

## 判断规则

- “未发现等价修复”只针对上述载荷和固定源码快照，不是对未来版本的判断。
- 源码已有等价实现，但尚未进入实际桌面载荷时，应分别记录两者状态，不能直接认定已发布修复。
- 锚点匹配失败、重复执行无变化和外观相似，不能独立证明官方已修复。
- 外部原生依赖应核对载荷实际使用的包和版本，不能仅凭桌面源码推断。
- “不适用”不表示已修复或应删除；它表示该文件没有可用于本次判断的官方缺陷对象。

后续若官方提供等价实现，应核对其是否进入实际交付载荷及具体行为，再决定对应补丁是否可以移除。本次文档调整未重新查询官方发布状态。
