---
name: fix-deep
description: >
  重量深修。仅手动 /fix-deep、/fix 命令用户在 AskUserQuestion 中明确选择 fix-deep、或 fix-quick L2 用户选择升级时触发，不自动匹配用户自由表述，也不再被 fix-quick L2 自动切入。
  单 Agent 跑完 Phase 0-5 + L0-L4 阶梯 + Heavy 对齐（sentinel 含变更范围/根因/修法/死代码清单）+
  证据对称强制（用什么工具发现 bug 必须用什么工具收尾）+ 最小修改（含死代码清理）。
  适用：时序/并发/跨模块/架构层 bug、fix-quick 多轮失败后用户选择升级、用户明确"深度修"。
  Sentinel / 完成报告 / 升级声明 严格按 ~/.claude/skills/fix-quick/references/user-language-protocol.md 输出（人话三字段 + 折叠技术细节）。
---

# Fix-Deep：重量深修协议

## 触发条件（严格限定）

本 skill **不自动触发**。仅在以下情况激活：
1. 用户显式输入 `/fix-deep`
2. `/fix` 命令路由分发后，**用户在 AskUserQuestion 中明确选了 fix-deep**
3. fix-quick 达到 L2（2 次失败后），**用户在 AskUserQuestion 中明确选了"升级 fix-deep"**
4. 用户明确说"深度修"/"彻查"/"根因分析"

**不适用**：用户随口说"修一下"/"帮我改"——那是 quick-fix 的场景。
**注意**：fix-quick L2 不再自动切入本 skill；必须由用户通过 AskUserQuestion 显式选择。

---

## 核心原则（六条，按优先级）

1. **对齐先行** — sentinel 发出后立即停手等用户放行，任何写操作都在放行后执行
2. **证据先行** — 每个结论必须有可引用的证据（文件行号 / 运行时输出 / 日志），禁止凭记忆假设
3. **根因先行** — 修复必须指向根因而非症状，禁止在报错处加 if/try-catch 绕过
4. **验证先行** — Pre-Fix Checklist 5 项全 YES 才能进入执行
5. **证据对称** — 用什么工具发现 bug，就用什么工具验收修复（详见 references/evidence-protocol.md）
6. **最小修改含死代码清理** — 不做无关扩展；但被本次修复直接取代的旧代码必须一并清理

---

## Phase 0：多轮升级检测（L0-L4 阶梯）

每次响应开头必须声明当前 Level：`[FIX-DEEP Level: L{n}]`

> **L1-L4 升级声明对话框输出严格按 `~/.claude/skills/fix-quick/references/user-language-protocol.md` 模板**：
> - L1（fix-quick 内升级）走 § 5.2 模板
> - L2（升级到 fix-deep）走 § 5.3 模板
> - L3 / L4 比照 § 5.2 模板，加深"换思路"的措辞强度
> - 人话区：上一轮假设（人话） / 本轮新假设（人话） / 打算怎么改 / 影响
> - `<details>` 块：内部 L0-L{n-1} 假设清单 + 失败原因 + 已排除根因方向

### L0（首次，或用户描述了不相关的新 bug）
标准流程，进入 Phase 1。

### L1（1 次失败：用户报告上轮修复无效）
- 从零重读所有涉及文件（不依赖对话早期的文件记忆）
- 列出 ≥2 个替代根因假设（每个标注信心等级：[已验证] / [高度怀疑] / [假设]）
- 明确哪个假设被上轮修复排除了，为什么

### L2（2 次失败）
- 搜索半径扩大：从报错文件扩展到所有调用方、被调用方、同类实现
- 至少执行 ≥1 次运行时埋点（console.log / 断言 / playwright-cli eval）
- 书面声明："bug 不在 [之前检查的层/文件/逻辑]，因为 [具体排除证据]"
- 进入 Phase 2 前，更新 Evidence Ledger（见 references/evidence-protocol.md）

### L3（3 次失败）
- 列出 3 个竞争假设，每个标注：根因描述 / 验证成本（低/中/高）/ 所需工具
- **拒绝写任何代码**，把 3 个假设交给用户选择
- 格式：
  ```
  [FIX-DEEP Level: L3]
  假设 A：[描述] — 验证成本：低 — 工具：grep/Read
  假设 B：[描述] — 验证成本：中 — 工具：运行时埋点
  假设 C：[描述] — 验证成本：高 — 工具：架构级 diff
  请选择一个方向，或提供更多上下文。
  ```

### L4（4 次失败——硬停）
- 停止尝试修复
- 产出失败尝试日志：列出 L0-L3 的每次假设 + 排除证据
- 提出升级建议：
  - 架构重构（如果问题在设计层）
  - 引入单元测试覆盖边界（如果问题在隐式假设）
  - 用户提供最小复现用例再重新开始
- 不再自主推进，等待用户决策

---

## Phase 1：Ground Truth（地基建立）

**目标**：读完所有涉及文件，不依赖记忆。

步骤：
1. Read 报错文件 + 调用栈涉及的每个文件（使用 Read 工具，非记忆）
2. Grep 相关函数名 / 类名 / 变量名，确认实际代码位置
3. 查阅 git log / git blame（如适用）定位变更时间线
4. 产出项目上下文摘要：
   - 文件清单（已读）
   - 相关接口签名
   - 依赖关系图（文字描述）

**L2+ 额外要求**：
- 调用 LSP goToDefinition / findReferences 确认实际调用链
- 不仅读报错文件，还读其上下游

---

## Phase 1.5：Heavy 对齐门控（必须）

> **对话框 sentinel 输出严格按 `~/.claude/skills/fix-quick/references/user-language-protocol.md` 各档模板**：
> - Light 走 § 4.1
> - Medium 走 § 4.2
> - Heavy 走 § 4.3（spec 文件首节强制人话摘要）
>
> 详细对齐机制见 `references/alignment-protocol.md`，但**模板字段定义和对话框露出格式以 user-language-protocol 为准**。
> 不再在对话框输出 `[ALIGN-LEVEL: ...]` `[ALIGN-LIGHT]` `[ALIGN-MEDIUM]` `[ALIGN-GATE-OPEN]` 等内部标签。

**这是 fix-deep 的硬性门控。无逃生阀。**

产出 Heavy Sentinel，包含以下 5 项（缺一不可）：

```markdown
[FIX-DEEP SENTINEL]
**Level**：L{n}
**根因**：[一句话，格式："根因是 [X]，因为 [具体证据Y]"]
**变更范围**：
  - 修改：[文件路径:函数名/字段名 清单，不用量词"所有/全部"，逐条列]
  - 不动：[显式列出]
**修法**：[具体改动说明，引用 Phase 1 读到的代码行]
**死代码清单**：[被本次修复直接取代的旧函数/字段/import；无则写"无取代关系，不清理"]

等待放行：**Plan Mode 优先**（`EnterPlanMode` + `ExitPlanMode`，approve = 放行 / reject = 改方向）；
spec 文件兜底场景（无 Plan Mode 工具时），写完 spec 后**立即调用 `AskUserQuestion`** 弹三选一（确认 / 改方向 / 取消）。
**不再接受"显式回 ok / go / 继续"作为放行替代**；用户必须通过 Plan Mode UI 或 AskUserQuestion 显式选择。
用户放行前不执行任何写操作。详见 `~/.claude/skills/fix-quick/references/user-language-protocol.md` § 6。
```

关于 Heavy Sentinel 的详细规则，见 `references/alignment-protocol.md`。

---

## Phase 2：根因调查

**目标**：将 [假设] 级别的结论升级为 [已验证]。

### 标准工具链（按顺序尝试）
1. Grep / LSP findReferences — 定位所有引用点
2. Read 相关文件最新版本 — 核实接口签名
3. git log -S / git blame — 定位变更引入点
4. 运行时埋点（playwright-cli eval / console 日志）— 确认运行时行为

### L2+ 强制：运行时埋点
- 在关键路径插入 console.log / 断言
- 用 playwright-cli eval 读取运行时值
- 把埋点结果记入 Evidence Ledger

### 根因分析框架
根据 bug 类型选择对应框架（详见 `references/advanced-rca.md`）：
- 回归 bug → Change Analysis（git bisect）
- 偶发 bug → Fault Tree Analysis
- 防御加固需求 → Barrier Analysis

### LLM 反模式自检
Phase 2 结束前，过一遍反模式清单（详见 `references/llm-anti-patterns.md`）：
- 每个结论有信心等级标注吗？
- 引用了当前文件的具体行号吗？
- 是在修根因而非症状吗？

---

## Phase 3：修复计划 + 执行

### Pre-Fix Checklist（5 项全 YES 才能写代码）

- [ ] **报错信息**：已引用完整报错（堆栈 / 错误码 / 文件路径 / 行号）？
- [ ] **代码搜索**：已在代码库中搜索相关代码并引用具体文件和行号？
- [ ] **API 验证**：已确认引用的 API/方法在当前版本存在（Grep / 类型定义）？
- [ ] **根因陈述**：能一句话陈述根因（非症状），格式"根因是 [X]，因为 [证据Y]"？
- [ ] **修复对应**：修复指向根因，而非绕过/掩盖/忽略错误？

任何一项 NO → 返回 Phase 2 继续调查，不允许"先试试看"。

### 执行原则
- 每个代码修改必须关联到具体证据（Evidence Linking 格式，见 references/evidence-protocol.md）
- 只改 Sentinel 变更范围里列出的文件
- 同步清理 Sentinel 死代码清单里的条目（每条都要在最终 diff 里真删）
- 修改后立即检查 import 去重

---

## Phase 4：证据对称验证

**核心规则**：用发现 bug 的工具做"修复后"对比，不得用其他工具替代。

### 工具对称矩阵

| 发现 bug 时用了 | 验收时必须用 |
|---------------|------------|
| playwright-cli screenshot / snapshot | 修复后再截图，并排对比 |
| playwright-cli eval | 修复后再 eval，对比输出值 |
| Chrome DevTools MCP 截图 | 修复后再截图对比 |
| Vibe-Eyes SVG | 修复后再获取 SVG 对比 |
| console 日志 / network 请求 | 修复后再检查日志/请求 |
| Cocos MCP 场景树 | 修复后再读场景树对比 |

详细工具类别和 Phase 4 执行步骤见 `references/evidence-protocol.md`。

### 命令行验收（必须额外执行）
```bash
# 按项目情况选择：
bash .vscode/cocos-compile.sh   # Cocos 项目
npm run build / npm test        # 通用 JS/TS
```

### 命令行即足够的场景
仅当 bug 是"纯逻辑/纯数据/无视觉产物"时，Phase 4 可只做命令行验收（无需视觉对比）：
- 纯单元测试（无视觉/交互产物）
- 纯字符串处理 / 纯数据变换
- CLI 工具

### 验收结论格式

> **完成报告对话框输出严格按 `~/.claude/skills/fix-quick/references/user-language-protocol.md` § 5.1 完成报告模板**：
> - 人话区：现在玩家会看到 X / 之前那个问题已经不会发生 / 顺手清理了 Y（可选）
> - `<details>` 块：编译记录 / 截图对比 / 运行时检查 / 证据对称结果
> - 人话区只描述玩家可见行为，禁止写"修了 X 函数"或"改了 X.ts"

```
[Phase 4 验收]
发现工具：playwright-cli snapshot（见 [截图路径/描述]）
修复后验证：playwright-cli snapshot → [结果描述]
对比结论：[修复前 vs 修复后的显式对比]
命令行：bash .vscode/cocos-compile.sh → [编译结果]
```

---

## Phase 5：防御加固

**目标**：确保同类 bug 不再出现。

### Barrier Analysis（屏障分析）
对照以下屏障层，找出"不存在"或"不完善"的层，在本 Phase 加固：

| 屏障层 | 状态 | 加固方案 |
|--------|------|---------|
| TypeScript 类型系统 | ? | 收窄类型 / 去掉 any |
| 运行时断言/守卫 | ? | 加入口参数检查 |
| 单元测试 | ? | 补边界用例 |
| Lint / 静态分析 | ? | 新增规则 |

详细框架见 `references/advanced-rca.md` 的 Barrier Analysis 节。

### 加固优先级
1. **Layer 1（入口验证）**：函数入口加参数断言
2. **Layer 2（业务规则）**：关键路径加不变式检查
3. **Layer 3（边界防护）**：空值 / 越界 / 并发等边界场景

### 死代码最终核查
Sentinel 列出的"拟清理旧代码"每一条是否都在最终 diff 里真删了？
任何漏删 = 违反 Sentinel 承诺 = 当轮未闭环，必须补删。

---

## 明确排除

- **不派发 researcher / dev / tester 多 Agent**（旧 fix 的模式废弃）
- **不用多模型分派**（haiku / opus / sonnet）
- **不自动触发**（fix-deep 是重量工具，需明确调用）
- **不允许 Fast-Track**（Heavy sentinel 无逃生阀）

---

## References 索引

| 文件 | 内容 | 何时读 |
|------|------|--------|
| `references/alignment-protocol.md` | Heavy Sentinel 完整规则 + 死代码清理协议 + 反合理化对照表 | Phase 1.5 前 |
| `references/advanced-rca.md` | Change Analysis / Barrier Analysis / Fault Tree Analysis | Phase 2，L2+ |
| `references/evidence-protocol.md` | Pre-Fix Checklist + Evidence Linking + 证据对称工具类别 | Phase 3-4 |
| `references/llm-anti-patterns.md` | 幻觉 API / 虚假记忆修复 / 信心三级标注 | Phase 2 自检 |
| `references/research-gate.md` | 三级信息源协议（代码搜索 / 文档历史 / API 验证）| Phase 1，L0 起始 |

---

## 快速自检清单（每轮响应前过一遍）

- [ ] 我声明了 `[FIX-DEEP Level: L{n}]` 吗？
- [ ] 我是否从零 Read 了涉及文件（不是凭记忆）？
- [ ] Heavy Sentinel 发出了吗？5 项齐全吗？
- [ ] 用户放行了吗？（放行前禁止任何写操作）
- [ ] Pre-Fix Checklist 5 项全 YES 了吗？
- [ ] 修完后，发现 bug 的工具用来验收了吗（证据对称）？
- [ ] Sentinel 死代码清单里的条目都在 diff 里真删了吗？
- [ ] Phase 5 加固了至少一个屏障层吗？

任何一项 NO → 停下来，补完再继续。
