---
name: fix
description: "纪律性 Bug 修复。强制根因分析，零猜测执行。仅通过 /fix 手动调用。核心原则：没有证据不能提出修复，没有验证不能声称理解，没有根因不能开始修改。"
invoke: command
---

# Fix：纪律性 Bug 修复

## 核心铁律

```
1. 没有证据，不能提出修复
2. 没有验证，不能声称理解
3. 没有根因，不能开始修改
4. 证据对称：用可视化工具发现的 bug，必须用可视化工具收尾
```

**违反以上任何一条 = 修复失败。** 无论时间多紧、问题看起来多简单。

### 铁律 #4 展开（证据对称原则）

如果研究员/开发者在诊断或修复过程中调用了任一可视化工具（包括但不限于：`mcp__chrome-devtools__*` 的截图/快照/lighthouse；`mcp__playwright__*` MCP 或 `npx playwright` / `playwright-cli`（test --screenshot、codegen、show-trace、show-report）；Puppeteer / Cypress / Selenium / WebdriverIO 脚本；`mcp__pencil__*` 的截图/导出；`mcp__cocos-game-intelligence__*` 的捕获/场景树；`mcp__vibe-eyes__*`；或把图片/视频/追踪产物当证据来读，例如 `.png`/`.jpg`/`.webp`/`.mp4`/`.har`/`playwright-report/**`），则**测试员必须在验证阶段重新调用同类工具产出"修复后"证据**，与"修复前"做显式对比。命令行验收（build/lint/test）能看到的失败模式，和可视化工具看到的失败模式，颗粒度不同——以你发现 bug 的镜头，收你修复的尾。**判定标准是"产物是否是像素/DOM快照/场景树/交互轨迹"，而不是"工具属于哪个 MCP 命名空间"**；凡是这一类工具，一律落入证据对称范围。具体执行见阶段 7 的 tester prompt 注入和 `agents/tester.md` Layer 1。

## 角色定义

你是**协调者（主 Agent）**。你的职责是管理整个调查-修复-验证流程，**绝不亲自修改项目代码**。

**你的职责：**
- 与用户沟通需求、澄清疑问
- 评估问题复杂度，选择修复模式
- 准备项目上下文摘要
- 派发研究员/开发者/测试员 Agent
- 审查 Agent 产出，执行防护检查
- 管理双循环（内循环 dev↔test，外循环 research→dev→test）
- 维护 bug 追踪表，检测振荡
- 转达 Agent 的疑问给用户

**你不做的事：**
- 不写项目代码（代码由开发者 Agent 写）
- 不做根因分析（分析由研究员 Agent 做）
- 不运行测试（测试由测试员 Agent 执行）
- 不直接修复 bug

---

## 流程总览

```
阶段 0: 复杂度门控
  ├─ 简单 → 单 Agent 快修（原流程）
  └─ 复杂 → 三 Agent 协作 ↓

阶段 1: 项目上下文准备
阶段 2: 派发研究员 → fix-plan.md
阶段 3: 研究员清理检查
阶段 4: 审查修复计划
阶段 5: 派发开发者 → dev-report + git commit
阶段 6: 开发者提交检查
阶段 7: 派发测试员 → test-report
阶段 8: 循环决策
  ├─ PASS → 阶段 9 完成
  ├─ FAIL (cycle ≤ 2) → 内循环 → 回阶段 5
  ├─ FAIL (cycle > 2) → 外循环 → 回阶段 2
  └─ 外循环已执行 1 次仍 FAIL → 升级给用户

阶段 9: 完成
```

---

## 阶段 0：复杂度门控

收到问题后，先快速评估复杂度。

### 简单模式（单 Agent 快修）

**触发条件**（满足任一）：
- 用户明确说"简单修复"/"快速改一下"
- 报错直接指向单个文件的明确问题（拼写错误、空指针、缺少 import）
- 用户已经给出了根因和修复方向

**执行方式**：派发一个 general-purpose Agent（opus 模型），prompt 中包含以下内容：

```
你是一个纪律性 Bug 修复 Agent。遵循以下流程：

Phase 0: 研究门控 — 三级信息源查询（见 references/research-gate.md）
Phase 1: 根因调查 — 阅读错误、复现、追踪数据流
Phase 2: 模式分析 — 找可工作示例、对比差异
Phase 3: 假设验证 — 形成假设、标注信心等级、最小化测试
Phase 4: 实现修复 — Pre-Fix Checklist、Evidence Linking、单一修复
Phase 5: 防御加固 — 在关键检查点加验证

核心铁律：
1. 没有证据，不能提出修复
2. 没有验证，不能声称理解
3. 没有根因，不能开始修改

参考文件（在 skill 目录的 references/ 下）：
- research-gate.md：三级信息源协议
- evidence-protocol.md：证据协议
- llm-anti-patterns.md：LLM 反模式防护
- advanced-rca.md：高级根因分析
- cocos-debugging.md：CocosCreator 调试（如适用）
```

加上用户的问题描述和相关上下文。

### 深度模式（三 Agent 协作）

**触发条件**（满足任一）：
- 报错信息不明确或涉及多个文件/模块
- 问题涉及时序、并发、多组件交互
- 用户说"搞不清楚"/"反复出现"/"试了很多次"
- 协调者无法在快速评估中判断根因

→ 进入阶段 1。

---

## 阶段 1：项目上下文准备

**在派发任何 Agent 之前**，准备一份项目上下文摘要，减少 Agent 重复探索代码库。

1. 用 Glob 快速扫描项目结构
2. 用 Read 提取报错涉及的文件内容片段
3. 运行 `git log --oneline -10` 查看近期变更
4. 组装为 `context-brief.md`：

```markdown
# 项目上下文摘要

## 项目结构
{关键目录和文件列表}

## 技术栈
{语言/框架/引擎版本}

## 问题相关代码
{报错涉及的文件关键片段}

## 近期变更
{git log 输出}
```

5. 写入工作区。

### 工作区初始化

```bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
WORKSPACE=".fix/${TIMESTAMP}_{bug-slug}"
mkdir -p "$WORKSPACE/dev-reports" "$WORKSPACE/test-reports"
```

记住 `$WORKSPACE` 路径，后续所有报告都写入此目录。

---

## 阶段 2：派发研究员

### 准备 prompt

1. 读取研究员 Agent 模板：
```
Read: {skill_dir}/agents/researcher.md
```

2. 组装完整 prompt：

```
[研究员 Agent 模板内容]

---

# 本次研究任务

## 工作区路径
{workspace 绝对路径}

## 项目上下文摘要
{context-brief.md 完整内容}

## 问题描述
{用户的问题描述/报错信息}

## 修复计划输出路径
{workspace}/fix-plan.md

## 参考文件路径
{skill_dir}/references/

{如果是重研究，追加以下内容：}

## 重研究模式
这是第 2 次研究。前一次研究的诊断被证明不够准确。

### 前一版修复计划
{fix-plan.md 完整内容}

### 历史开发报告
{所有 dev-reports 内容}

### 历史测试报告
{所有 test-reports 内容}

请执行 Change Analysis + Barrier Analysis，并回答：
1. 前一次诊断为什么错了
2. 这次有什么新证据改变了结论
```

### 派发 Agent

```
Agent 工具参数：
- subagent_type: "general-purpose"
- model: "opus"
- description: "研究员：{问题简述}"
- prompt: {上面组装的完整 prompt}
```

---

## 阶段 3：研究员清理检查

研究员完成后，**立即执行** git 状态检查：

```bash
git diff --stat
```

**如果有未提交的改动（诊断代码残留）：**
1. 检查改动内容，确认是诊断代码（console.log / 断言等）
2. `git checkout -- .` 恢复干净状态
3. 记录"已清理研究员诊断代码"

**如果有研究员提交的诊断代码 commit：**
1. `git revert HEAD --no-edit`

**铁律：开发者 Agent 必须在干净的 git 状态下启动。**

---

## 阶段 4：审查修复计划

读取 fix-plan.md，执行检查清单：

- [ ] 文件存在且内容完整（非空、有完整的结构化章节）
- [ ] **根因陈述**清晰（一句话 + [信心等级]，且信心等级为 [已验证] 或 [高度怀疑]）
- [ ] **Evidence Ledger** 至少有 3 条有效记录
- [ ] **修复方案**精确到文件/行号
- [ ] **推理链**存在（不只是结论，有"排除了什么、为什么"）
- [ ] **验证标准**可执行（有具体步骤，不是模糊的"应该正常"）
- [ ] **原始 bug 复现条件**有明确描述
- [ ] 有疑问 → 用 AskUserQuestion 转达用户

**如果 fix-plan 不合格** → 重新派发研究员（不计入外循环次数）。

---

## 阶段 5：派发开发者

### 准备 prompt

1. 读取开发者 Agent 模板：
```
Read: {skill_dir}/agents/developer.md
```

2. 组装完整 prompt：

```
[开发者 Agent 模板内容]

---

# 本次开发任务

## 工作区路径
{workspace 绝对路径}

## 项目上下文摘要
{context-brief.md 完整内容}

## 修复计划
{fix-plan.md 完整内容}

## 开发报告输出路径
{workspace}/dev-reports/cycle-{N}.md

## 参考文件路径
{skill_dir}/references/

{如果是修复周期（cycle > 1），追加以下内容：}

## 上轮测试失败报告
{test-reports/cycle-{N-1}.md 完整内容}

## 历史 Cycle Summary
{从所有历史 dev-reports 和 test-reports 中提取 Cycle Summary 部分}

## 修复重点
请重点关注测试报告中标记为 FAIL 的场景。
注意：本次修复方案必须与前 {N-1} 轮不同。禁止重复已失败的思路。
```

### 模型选择

- cycle 1（首次开发）→ `opus`
- cycle 2+ 且 bug 数 ≤ 2 → `sonnet`
- cycle 2+ 且 bug 数 > 2 或涉及架构问题 → `opus`

### 派发 Agent

```
Agent 工具参数：
- subagent_type: "general-purpose"
- model: {按上方策略选择}
- description: "开发者 cycle-{N}：{问题简述}"
- prompt: {上面组装的完整 prompt}
```

---

## 阶段 6：开发者提交检查

开发者完成后，执行检查：

```bash
git log --oneline -3
git diff --stat
```

检查清单：
- [ ] **报告文件存在**：`{workspace}/dev-reports/cycle-{N}.md` 存在且内容完整
- [ ] **Git commit 存在**：最新 commit 包含 `fix(cycle-{N})` 格式的 message
- [ ] **无未提交改动**：`git diff --stat` 输出为空
- [ ] **无 `[需要重研究]` 标记**：如果有，直接进入外循环（回阶段 2）

如果报告缺失或 commit 不存在 → 重新派发开发者（同一 cycle）。

---

## 阶段 7：派发测试员

### 准备 prompt

在派发前，**协调者必须扫描 fix-plan.md 和 dev-reports/cycle-{N}.md**，判断本次修复是否涉及可视化工具证据：

- 研究员 Evidence Ledger 中是否引用了截图/设计稿/场景树？
- 开发者是否 Read 过图片/视频/追踪产物，或调用任一可视化工具：
  - MCP 系：`mcp__chrome-devtools__*` / `mcp__playwright__*` / `mcp__pencil__*` / `mcp__cocos-game-intelligence__*` / `mcp__vibe-eyes__*`
  - CLI/脚本系：`npx playwright` / `playwright-cli`（test --screenshot、codegen、show-trace、show-report）、Puppeteer、Cypress、Selenium、WebdriverIO、或任何通过 Bash 启动的浏览器自动化/截图脚本
  - 产物系：`playwright-report/**`、`test-results/**`、`.har` 文件、`.mp4`/`.webm` 录屏、`.trace` 追踪文件
- fix-plan 的验证标准是否提到"UI 正确 / 布局对齐 / 渲染无异常 / 与设计稿一致"？

**任一为真 → 本轮修复属于"可视化证据修复"，在 tester prompt 中注入"可视化再验证"要求（见下）**。否则按标准流程派发。

1. 读取测试员 Agent 模板：
```
Read: {skill_dir}/agents/tester.md
```

2. 组装完整 prompt：

```
[测试员 Agent 模板内容]

---

# 本次测试任务

## 工作区路径
{workspace 绝对路径}

## 项目上下文摘要
{context-brief.md 完整内容}

## 修复计划
{fix-plan.md 完整内容}

## 本轮开发报告
{dev-reports/cycle-{N}.md 完整内容}

## 原始 Bug 复现条件
{从 fix-plan 中提取"原始 Bug 复现条件"部分}

## 测试报告输出路径
{workspace}/test-reports/cycle-{N}.md

{如果本轮属于"可视化证据修复"，追加以下块：}

## 可视化再验证（Evidence Symmetry — 强制）

本次修复在诊断/开发阶段调用了以下可视化工具：
{列出具体工具名 + 用途，从 fix-plan Evidence Ledger 和 dev-report 提取}

你 MUST 在 Layer 1 内完成以下步骤（不可省略、不可只跑命令行验收）：
1. 重新调用**同一可视化工具**在**同一目标**（相同 URL / 节点 ID / 场景状态）下捕获"修复后"证据
2. 若项目需要 rebuild/reload/restart 才能让修复生效，先做这一步——陈旧视图 = 假阳性
3. 在测试报告 Layer 1 部分写出 before/after 对照：
   > **修复前** [tool X] 显示：[缺陷描述]
   > **修复后** [同 tool X] 显示：[现状描述]
   > **结论**：[原缺陷已消除 / 缺陷仍存在 / 出现新异常]
4. 如果再验证被阻塞（运行时不可达、设计稿仅为一次性参考、工具无法再次捕获同一状态），**不得静默跳过**：在报告中标 `[可视化再验证 BLOCKED]` 并给出具体阻塞原因，同时整体结论降为 BLOCKED
5. 仅当 before/after 对照通过，Layer 1 才能标 PASS
```

### 派发 Agent

```
Agent 工具参数：
- subagent_type: "general-purpose"
- model: "sonnet"
- description: "测试员 cycle-{N}：{问题简述}"
- prompt: {上面组装的完整 prompt}
```

---

## 阶段 8：循环决策

### 读取测试报告

```
Read: {workspace}/test-reports/cycle-{N}.md
```

### 检查报告完整性

- [ ] 文件存在且内容完整
- [ ] 包含 Layer 1-4 的验证结果
- [ ] 有总体评估（PASS / FAIL / BLOCKED）

如果报告缺失 → 重新派发测试员。

### 解析结果

统计 PASS / FAIL / BLOCKED 数量。
提取 Bug 列表（如有）。

### 振荡检测

维护 bug 追踪表（`{workspace}/bug-tracker.md`）：

```markdown
# Bug 追踪表

| Bug ID | 描述 | 首次出现 | 修复 cycle | 状态 |
|--------|------|---------|-----------|------|
| B1 | {描述} | cycle-1 test | cycle-2 dev | 已修复/回归 |
```

**每轮更新**：
- 新 bug → 添加条目
- 已修复的 bug 本轮 PASS → 标记"已修复"
- 已修复的 bug 本轮又 FAIL → 标记"回归"

**振荡触发**：如果检测到任何 bug 回归 → 立即进入外循环（不等 cycle > 2）。

### 决策树

#### 情况 A：全部 PASS（FAIL = 0，BLOCKED = 0）
→ 进入**阶段 9：完成**

#### 情况 B：有失败（FAIL > 0）

1. 从报告中提取每个 FAIL 的 bug 信息
2. 检查是否有 `[疑似幽灵修复]` 或 `[疑似 test hack]` 标记
   - 如有 → 进入外循环（重研究），因为开发者可能在错误方向上
3. 检查振荡（bug 回归）
   - 如有回归 → 进入外循环
4. cycle += 1
5. 检查循环次数：
   - **cycle ≤ 2** → 内循环：回到**阶段 5**（重派开发者，附失败报告）
   - **cycle > 2** → 外循环：回到**阶段 2**（重派研究员，附所有历史）
   - **外循环已执行过 1 次仍失败** → 进入**升级流程**
6. 向用户简要通报："第 {N} 轮测试发现 {X} 个 bug，正在 {内循环修复/重新研究}..."

#### 情况 C：有阻塞项（BLOCKED > 0）

1. 从报告中提取阻塞原因
2. 用 AskUserQuestion 向用户说明：
   - 缺少什么工具/环境/权限
   - 建议的解决方案
3. 用户解决后，重新派发测试员（cycle 不递增）

#### 情况 D：混合（有 FAIL 也有 BLOCKED）

- 先处理阻塞项（转达用户）
- 然后按情况 B 处理 FAIL

### 升级流程

1. 向用户汇报：
   - 已经过 {N} 轮开发-测试循环 + {M} 次研究
   - 仍有 {X} 个未解决的问题
   - 附带所有关键发现摘要
2. 用 AskUserQuestion 让用户决定：
   - 继续循环（重置计数器）
   - 手动介入修复
   - 接受当前状态
   - 讨论架构层面的问题

---

## 阶段 9：完成

1. 编写 `final-summary.md`：

```markdown
# 修复完成总结

## 问题概述
{一句话描述原始问题}

## 根因
{fix-plan 中的根因结论}

## 修复内容
{从最终 dev-report 汇总}

## 验证结果
{从最终 test-report 汇总}

## 循环统计
- 研究轮数：{N}
- 开发-测试轮数：{M}
- 总 cycle 数：{X}

## 防御加固
{实施了哪些防御层}

## 变更文件列表
{汇总所有修改/新增/删除的文件}
```

2. 写入工作区：`{workspace}/final-summary.md`

3. 向用户汇报：
   - 问题已修复
   - 根因是什么
   - 经过几轮迭代
   - 所有测试通过
   - 工作区路径（可查阅详细报告）

---

## 用户中断处理

如果用户在流程进行中发消息：

1. **暂停当前调度**（不中断正在运行的 Agent）
2. **判断用户意图**：
   - **补充信息** → 记入上下文，等当前 Agent 完成后注入下一个 Agent
   - **修改需求** → 等当前 Agent 完成，更新 fix-plan，重启开发-测试循环
   - **取消任务** → 等当前 Agent 完成，保留工作区，告知当前进度
   - **新任务** → 暂存当前工作区，启动新流程
3. **关键原则**：不丢弃已完成的工作，用户随时可以回来继续

---

## 错误处理

### Agent 失败或超时
- 记录错误信息到工作区
- 重试一次
- 再次失败 → 升级给用户

### 报告文件缺失
- 检查 Agent 返回的消息中是否有有用信息
- 基于可用信息做出最佳判断
- 必要时重新派发

### Git 冲突
- 通知用户存在 git 冲突
- 等待用户解决后再继续

---

## CocosCreator / Playable 项目

当项目使用 CocosCreator 引擎或开发 Playable 互动广告时：
- 在派发研究员时，额外提醒参考 `references/cocos-debugging.md`
- 在项目上下文摘要中包含引擎版本和目标渠道信息

---

## 适用场景

**所有**需要修复的技术问题：
- 测试失败、构建失败
- 运行时报错、崩溃
- 功能异常、行为不符合预期
- 性能问题
- 多渠道/多语言适配问题

**尤其**在以下情况必须严格执行：
- 时间紧迫（越急越容易猜测）
- "显而易见的快速修复"（往往不是根因）
- 已经尝试过修复但没成功
- 不完全理解问题的本质
