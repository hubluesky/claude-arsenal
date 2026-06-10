---
name: fix-quick
description: "极轻快修。修改代码时的默认技能。Fix, debug, optimize, refactor, adjust UI/layout, match designs, small changes. 修 bug / 改代码 / 调 UI / 改样式 / 微调 / typo / 对齐设计 / 小重构 / 加一点功能。Trigger on: file paths, broken behavior, UI adjustments. 当用户显式写 /fix-quick 时必须立即触发。**本技能是极轻模式**：单行对齐 sentinel（改哪几个文件 + 一句话根因 + 修法），L0 不开阶梯声明，Phase 2 模式分析跳过，证据对称降为推荐（不强制），死代码按需清理，不做多模型分派。连续 2 次失败（L2）硬停后**通过 AskUserQuestion 弹三选一让用户决定**：升级 fix-deep / 在 fix-quick 内再试一次 / 取消，**不再自动切 fix-deep**。**MUST re-trigger on follow-up fix requests within the same session**：'还是不行/没修好/又崩了/same issue/didn't fix' 等短语让本技能重新触发，按 L0→L1 阶梯逐轮加重；L2 弹用户选择。不适用于纯只读任务。Sentinel / 完成报告 / 升级声明 严格按 references/user-language-protocol.md 输出（人话三字段 + 折叠技术细节）。"
---

# fix-quick — 极轻快修

## 核心原则

1. **证据先行** — 修改前必须 Read 真实文件，不凭记忆假设
2. **根因先行** — 找到真正的错因再动手，不在症状处打补丁
3. **验证先行** — 声称完成前必须跑 build/lint/test，通过才报完成

---

## 流程 Phase 0–4

### Phase 0: Ground Truth

Read 涉及问题的文件。如果不确定哪个文件，先 Grep / Glob 定位，再 Read。

- 只读与问题**直接相关**的文件，不要全量扫项目
- 若修改涉及框架 API，用 LSP `hover` / `findReferences` 确认签名存在

### Phase 1: 根因判定

用一句话描述根因。格式：

> **根因**：`[函数/节点/配置]` 中 `[具体错误行为]`，因为 `[直接原因]`。

如果一句话说不清楚，说明需要更多 Read 或者应该升级到 fix-deep。

### Phase 2: 轻量 Sentinel

发出 sentinel 文本后**同一轮内立即调用 `AskUserQuestion`** 弹"确认 / 改方向 / 取消"三选一，用户选"确认"才执行修改（详见 protocol § 6）。

**Sentinel 必须严格按 `references/user-language-protocol.md` § 4.1 Light 模板输出**：
- 对话框人话区：问题 / 打算怎么改 / 影响（三字段，玩家视角）
- 技术细节（文件路径 / 函数名 / 根因 / 修法 / 拟清理的旧代码）放进 `<details>` 折叠块
- **sentinel 文本发出后，同一轮内立即调用 `AskUserQuestion` 工具**，三选一：确认 / 改方向 / 取消（详见 protocol § 6）
- **不再有 60 秒推定同意**；用户必须通过 AskUserQuestion 显式选择

Sentinel 范围控制：
- 改动范围 ≤ 3 个文件 → 在 `<details>` 内列文件路径
- 改动范围 > 3 个文件 → 立即停止，升级到 fix-deep
- 遇到死代码可顺手清理，把清理动作加入 `<details>` 修法描述中
- **用户 ok 之前，禁止任何代码修改**

发出前必须跑 protocol § 6 自检清单。

### Phase 3: 执行修改

按 sentinel 描述执行。改动范围严格限制在 sentinel 列出的文件内。

- 保留所有原有功能，不静默删除无关代码
- 匹配已有代码风格（引号、缩进、命名）
- 修改 TS 后必须运行 `bash .vscode/cocos-compile.sh`（Cocos 项目适用）

### Phase 4: 基础验证

验证修改不引入新问题：

- **编译**：`bash .vscode/cocos-compile.sh`（有编译步骤时）
- **Lint**：无新 warning/error
- **功能**：用 playwright-cli / Vibe-Eyes 验证核心行为
- 通过后才报告完成；未通过则回 Phase 1 重查根因

#### 完成报告格式

验证全部通过后，**严格按 `references/user-language-protocol.md` § 5.1 完成报告模板输出**：
- 人话区：现在玩家会看到 X / 之前那个问题已经不会发生 / 顺手清理了 Y（可选）
- `<details>` 块：编译记录 / 截图对比 / 运行时检查
- 人话区只描述玩家可见行为，禁止写"修了 X 函数"或"改了 X.ts"

---

## L0 / L1 / L2 阶梯

### L0（首次，默认）

直线跑 Phase 0 → 4，不加任何声明头。这是正常流程。

### L1（一次失败后）

用户反馈"还是不行 / 没修好 / 又崩了 / same issue / didn't fix"时触发。

**升级声明严格按 `references/user-language-protocol.md` § 5.2 模板输出**：
- 人话区：上次以为是 X / 这次怀疑实际是 Y / 打算怎么改 / 影响
- `<details>` 块：技术细节（同 Light 模板的技术段）

升级动作：
- 换假设（不要沿用 L0 的根因方向）
- **重新 Read** 涉及文件（不依赖 L0 的文件记忆）
- 列出 ≥ 2 条替代根因，选择证据最强的那条
- 重走 Phase 0 → 4

### L2（两次失败后）

两轮 fix-quick 均未解决问题 → **硬停，弹用户选择**。

---

## L2 硬停 Checklist

触发条件：fix-quick 已完整跑过 L0 + L1，问题仍未解决。

执行步骤（**按顺序，不可跳过**）：

1. **停止**：禁止在本轮 fix-quick 内再做任何代码修改
2. **公告**：**严格按 `references/user-language-protocol.md` § 5.3 L2 升级公告模板输出**
   - 人话区：试了两轮没修好 / 第一轮以为是 X / 第二轮以为是 Y / 给出三个选项让用户挑
   - `<details>` 块：L0/L1 假设 + 失败原因 + 已排除根因方向
3. **询问**：公告发出后**同一轮内立即调用 `AskUserQuestion`** 弹三选一：
   - **升级到 fix-deep**（推荐）— 重新读相关文件、列至少两条新假设、严格证据对称；慢但稳
   - **在 fix-quick 内再试一次** — 用户给出新方向/新线索后，按 L1 风格换思路重走一遍 fix-quick
   - **取消** — 停手，等用户进一步指示
4. **按用户选择执行**：
   - 选"升级 fix-deep" → 调用 `Skill(fix-deep)`，把 `<details>` 内的汇总作为 prompt 前缀
   - 选"再试一次" → 用户必须先给出新方向或新线索；之后按 L1 流程换假设重走 Phase 0–4
   - 选"取消" → 本轮 fix-quick 终止，不做任何代码修改

> **不允许**在用户选择前自行启动第三次修改尝试或自动切 fix-deep；用户必须通过 AskUserQuestion 显式选择。

---

## 升级到 fix-deep 的其他触发条件

以下情况**不等到 L2**，但也**不直接升级**——发出建议后通过 `AskUserQuestion` 弹三选一（升级 fix-deep / 继续 fix-quick / 取消），由用户决定：

- 改动文件超过 3 个
- 需要同时修改 framework 子模块（`assets/scripts/framework/**`）
- 涉及跨模块时序 / 并发 / 物理引擎行为
- 根因判定需要深度架构分析
- 用户明确要求"完整对齐"或"彻底排查"（此项可视为用户已选 fix-deep，无需再询问）

---

## 轻量对齐参考

Sentinel 格式详见：`references/alignment-protocol-light.md`

---

## 不适用场景

以下任务**不触发** fix-quick（纯只读，无代码修改）：

- 解释概念、review PR、查 git 记录
- 跑审计命令、描述项目结构
- 只读分析不涉及修改文件
