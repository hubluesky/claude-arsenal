# Fix-Quick 轻量对齐协议

## Sentinel 格式

**统一引用 `user-language-protocol.md` § 4.1 Light 模板**。

请直接读 `~/.claude/skills/fix-quick/references/user-language-protocol.md` 第 4.1 节，按其格式输出 sentinel：
- 对话框人话区：问题 / 打算怎么改 / 影响
- `<details>` 折叠技术细节

发出前必须跑 protocol § 6 自检清单。

## 什么时候升级到 fix-deep

以下情况立即切到 fix-deep，不要在 fix-quick 里强行 Heavy：

- 修改面超过 3 个文件
- 需要同时改 framework 子模块
- 涉及跨模块时序 / 并发 / 物理
- 用户明确说"我要完整对齐"
- fix-quick L2 升级触发

## 死代码处理

修改过程中**偶遇**被取代的旧代码（如新算法替代老算法后老函数无调用点、新 API 替换后自写实现没人用），把清理动作**加到 sentinel 的 `<details>` 修法描述里**，用户 ok 一起改。

**不要**主动 grep 全工程找 orphan，那是 fix-deep Heavy 对齐的范围。
