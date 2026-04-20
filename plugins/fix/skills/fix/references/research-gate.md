# Phase 0：研究门控协议（Research Gate）

## 概述

在任何调查开始前，强制执行三级信息源查询。这是区别于"猜测修复"的核心机制。

**铁律：三级查询全部完成且 Evidence Ledger 非空，才能进入 Phase 1。**

## 三级信息源

### Level 1：代码库搜索（必须）

**目标：找到所有关联代码点，不能仅凭报错的那一个文件就下结论。**

执行步骤：
1. 用 Grep 搜索报错信息中的**错误码**或**关键词**
2. 用 Grep 搜索**相关函数名、类名、变量名**
3. 用 Glob 查找**相关配置文件、类型定义文件**
4. 记录每个搜索结果到 Evidence Ledger

示例：
```
报错：TypeError: Cannot read property 'width' of null at Player.ts:42

搜索 1: grep "width" Player.ts → 发现 3 处调用
搜索 2: grep "getComponent" Player.ts → 发现 this.node.getComponent(Sprite) at line 42
搜索 3: grep "getComponent(Sprite)" **/*.ts → 发现 5 个文件有类似调用
搜索 4: glob "**/Sprite.d.ts" → 找到类型定义
```

### Level 2：文档/历史查询（必须）

**目标：了解上下文，排除环境和历史因素。**

执行步骤：
1. 查阅**官方文档**（引擎 API、第三方库文档）
2. 搜索 **GitHub Issues / 社区讨论**（如果有网络访问）
3. 查看项目 **CHANGELOG / README**
4. `git log --oneline -20 -- <相关文件>` 查看近期变更
5. `git blame <报错文件>` 查看报错行附近的变更历史

示例：
```
git log --oneline -10 -- src/game/Player.ts
→ abc1234 refactor: upgrade to Cocos 3.8
→ def5678 feat: add player animation

git blame src/game/Player.ts -L 40,45
→ abc1234 (dev 2026-03-25) this.node.getComponent(Sprite).width
```

### Level 3：API 验证（必须）

**目标：确认你引用的 API 确实存在且行为符合预期。禁止仅凭记忆行动。**

执行步骤：
1. 查阅**官方文档**确认 API 签名、参数、返回值、版本兼容性
2. 读取项目内 **`.d.ts` 类型定义**或**引擎 API 声明文件**
3. 如有不确定，标注 `[待验证]` 并执行进一步验证

示例：
```
问题：Sprite 组件是否有 width 属性？

验证 1: 查阅 CocosCreator 3.8 API 文档
→ Sprite 组件在 3.x 中不再直接包含 width/height，需通过 UITransform 获取

验证 2: grep "class Sprite" 引擎声明文件
→ 确认 Sprite 没有 width 属性
```

## Evidence Ledger 模板

每一级查询完成后，必须填充证据清单：

| # | 级别 | 来源 | 发现 | 结论 |
|---|------|------|------|------|
| 1 | L1 代码搜索 | grep "width" Player.ts | 3处调用 | 所有都依赖 Sprite.width |
| 2 | L1 代码搜索 | grep "getComponent(Sprite)" | 5个文件 | 3个使用了旧API |
| 3 | L2 历史 | git blame Player.ts L42 | commit abc 升级引擎 | 升级后引入 |
| 4 | L2 文档 | Cocos 3.8 CHANGELOG | Sprite API 变更 | 可疑 |
| 5 | L3 验证 | 官方 API 文档 | Sprite 无 width 属性 | **确认根因** |

## 退出条件

- 三级查询全部完成 ✓
- Evidence Ledger 至少有 3 条有效记录 ✓
- 至少有一条结论为"可疑"或"确认" ✓

满足以上条件，进入 Phase 1。

如果三级查询后仍无头绪：
1. 记录已排除的方向
2. 向用户汇报调查进展
3. 请求更多上下文（复现步骤、环境信息、最近操作等）
