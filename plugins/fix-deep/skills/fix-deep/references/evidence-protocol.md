# 证据协议：Pre-Fix 检查表与证据链接

## 概述

每次进入 Phase 4（实现修复）前的强制门控，以及修复过程中的证据链接规则。确保每个修改都有据可依。

## Pre-Fix Checklist

进入 Phase 4 前，以下 5 项**必须全部为 YES**：

- [ ] **报错信息**：已读取并引用了完整报错信息（包括堆栈跟踪、错误码、文件路径、行号）？
- [ ] **代码搜索**：已在代码库中搜索相关代码并引用具体文件和行号？
- [ ] **API 验证**：已验证引用的 API/方法确实存在于当前版本（通过官方文档或类型定义）？
- [ ] **根因陈述**：能用一句话明确陈述根因（非症状）？格式："根因是 [X]，因为 [证据Y]"
- [ ] **修复对应**：修复精确对应根因，而非绕过/掩盖/忽略错误？

**任何一项为 NO → 返回 Phase 0/1/2 继续调查。不允许"先试试看"。**

## Evidence Linking 规则

每个代码修改**必须**关联到具体证据。格式：

```
修改: [文件路径] line [行号] — [具体改动描述]
证据: [来源和具体内容]
根因: [一句话根因陈述]
```

### 示例 1：API 变更导致的错误

```
修改: src/game/Player.ts line 42 — 将 this.node.getComponent(Sprite).width 改为 this.node.getComponent(UITransform).contentSize.width
证据: CocosCreator 3.x Migration Guide 说明 Sprite 不再包含尺寸属性，需通过 UITransform 获取
根因: Cocos 3.x 架构变更将 transform 功能从渲染组件分离到 UITransform
```

### 示例 2：逻辑错误

```
修改: src/utils/parser.ts line 87 — 将 if (result.length > 0) 改为 if (result.length >= 0)
证据: 单元测试 test/parser.test.ts line 23 显示空数组时应返回默认值，但当前条件排除了空数组
根因: 边界条件判断错误，空数组（length === 0）被错误地视为无效结果
```

### 示例 3：配置问题

```
修改: tsconfig.json — 将 "target": "ES5" 改为 "target": "ES2017"
证据: 报错 "async functions are not supported" + git log 显示 commit abc123 降级了 target
根因: target 设置过低导致 async/await 语法无法编译，commit abc123 意外降级
```

## Evidence Ledger 完整模板

在整个调试过程中持续填充此清单：

| # | 阶段 | 来源 | 发现 | 结论 | 信心 |
|---|------|------|------|------|------|
| 1 | Phase 0 L1 | grep "[关键词]" | [具体结果] | [排除/可疑/确认] | [已验证/高度怀疑/假设] |
| 2 | Phase 0 L2 | git log/blame | [具体结果] | [排除/可疑/确认] | [已验证/高度怀疑/假设] |
| 3 | Phase 0 L3 | 官方文档/类型定义 | [具体结果] | [排除/可疑/确认] | [已验证/高度怀疑/假设] |
| 4 | Phase 1 | 堆栈跟踪 | [具体结果] | [入口点/关联] | [已验证] |
| 5 | Phase 2 | [可工作代码] | [差异点] | [关键差异] | [已验证] |

## 使用时机

- **Phase 0**：每完成一级信息源查询，更新 Evidence Ledger
- **Phase 1**：每发现一个线索，记录到 Evidence Ledger
- **Phase 2**：每发现一个差异，记录到 Evidence Ledger
- **Phase 3**：假设形成时，引用 Evidence Ledger 中的证据
- **Phase 4**：修改代码时，使用 Evidence Linking 格式关联证据

---

## Fix-Deep 执行补充（Plan Task 3 Step 5 追加）

### 工具类别（凡归入此类都触发对称义务）

- Chrome DevTools MCP (`mcp__chrome-devtools__*`) 截图/快照/lighthouse
- Playwright MCP 或 `playwright-cli` / `npx playwright`（test --screenshot、codegen、show-trace）
- Puppeteer / Cypress / Selenium / WebdriverIO 脚本
- Pencil MCP (`mcp__pencil__*`) 截图/导出
- Cocos Game Intelligence MCP 场景树/快照
- Vibe-Eyes
- 读取 `.png` / `.jpg` / `.webp` / `.mp4` / `.har` / `playwright-report/**` 作为证据

### Phase 4 执行

1. 记录发现 bug 时使用的工具链
2. 修复后调用同类工具产生"修复后"证据
3. 与"修复前"做显式对比（并排截图、trace diff、日志 diff 等）
4. 命令行验收（build/lint/test）**额外**要做，不能代替可视化收尾

### 命令行验收即足够的场景

- 逻辑纯单元测试（无视觉/交互产物）
- 纯字符串处理 / 纯数据变换
- CLI 工具

这些场景 Phase 4 可以只做 build/lint/test。
