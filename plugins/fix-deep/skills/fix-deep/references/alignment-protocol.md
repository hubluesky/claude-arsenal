# Fix-Deep Heavy 对齐协议

本协议是 fix-deep 强制 Phase 1.5 的展开。fix-quick 使用轻量版见 `fix-quick/references/alignment-protocol-light.md`。

（以下为原 quick-fix alignment-protocol.md 全文）

---

# Alignment Protocol（对齐协议）

两个 fix 类 skill（`quick-fix` / `playable-fix`）共享的"对齐门控"协议。被各自 SKILL.md 在 Phase 0.5 / 1.5 引用。

---

## 存在理由（先讲 why，再讲 how）

Fix 类 skill 反复出现三类翻车：
1. **模糊需求不对齐就动手**——用户说"调一下布局"，agent 自己想像出改法然后改了
2. **提问被当成修复请求**——用户问"为什么 X 是这样"，agent 直接去改 X
3. **打补丁而不是按框架设计**——在症状处加 if/try-catch，不走 framework/gameplay 的原生 API

这三类错误的共同根因：**门控只是软规则，agent 会以"很明显"为由跳过**。本协议的思路是把门控**机械化**（判级规则不依赖感觉）+ **可审计**（AI 内部判级 → 按 user-language-protocol 输出 + 必须等用户放行）+ **颗粒度匹配**（轻任务轻做，重任务重做）。

---

## 红线 0：对齐先行（最高优先级）

> sentinel 发出后，agent 下一个动作必须是"等待用户回复"。在用户放行前，禁止任何代码修改、文件写入、或有副作用的工具调用（Read/Grep/LSP 等只读调查可继续）。违反此条 = skill 违规，当轮进度作废重走。

优先级：**0 > 证据先行 > 根因先行 > 验证先行**。其他 Phase 的门控（Verification Table、证据对称、Level 阶梯）都在红线 0 通过后才生效。

---

## 级别判定（机械规则）

每次触发必须先判级（AI 内部决定走哪一档模板），但**判级标签 `[ALIGN-LEVEL: ...]` 不再对用户显示**。判级仅作 AI 内部状态，对话框输出严格按 `user-language-protocol.md` 各档模板输出。

### 判定流程

从上往下扫，命中哪条就停在哪级：

1. **升 Heavy**：满足任一
   - 用户原话含：功能 / 新增 / 加一个 / 重构 / 改架构 / new feature / refactor
   - 涉及新增状态机、事件流、或跨 4+ 文件的改动
   - 改动涉及 framework/** 或 gameplay/** 子模块本身（而非使用它们）

2. **升 Medium**：满足任一
   - 将要改 `.ts` 文件（任何逻辑变更）
   - 涉及 2-3 个文件
   - import 路径命中 `framework/**` 或 `gameplay/**`
   - 关键词命中（任一）：`XTween`、`LogicConfig`、`LocalizedLabel`、`CharacterEntity`、`AIState`、`ItemCollection`、`NodeCachePool`、`Widget`、`UIBindNode`、`AssetsCache`、`HeroBootstrap`、`ItemBag`、`MoneyBag`、`playable.trackEvent`

3. **默认 Light**：以上都不命中
   - 典型：单文件 + 单字段 + 纯数值/文案/坐标微调

### Level 阶梯正交叠加

如果当前是多轮修复的 L1+（对上轮否定反馈触发），**任务级别自动上调一档**（Light→Medium，Medium→Heavy）。因为上一轮已失败，说明实际复杂度比预估高。

---

## User Intent 分类（判级前先做）

| 用户输入模式 | 分类 | 动作 |
|------------|------|------|
| 含疑问词（"为什么"、"怎么回事"、"是不是"、why、how come、what causes） | **Question** | 先回答问题，回答末尾追加："需要我修这个吗？"**不进入判级**。用户明确要修才回到本协议开头。 |
| 明确描述异常并要求修复 | **Fix** | 进入判级 |
| 模糊（"看看这个"、"这里有问题"、"调一下"） | **Ambiguous** | 先问："你希望我排查原因，还是直接修？"得到答复再分类 |

提问被当修复处理 = 越界，不论你有多确定要改什么。

---

## 需求收敛（Heavy / Medium 级 sentinel 之前必做）

写 sentinel / plan / spec **之前**，AI 不能直接铺一整套方案——会犯"猜错用户意图"的错（典型表现：用户原话有歧义，AI 选了一个解释做大量调查 + 写出 200 行 plan，结果用户说"不是这个意思"）。

### 触发条件

任一命中即必须做需求收敛：
- 用户原话含模糊指代（"把 X 的功能放到 Y 上"——"功能"指什么？"放到"是搬运还是重建？）
- 涉及**结构性**改动（节点 reparent / 文件迁移 / 重构）—— 多种合理实现路径
- 改动跨 4+ 文件，且具体改哪些文件取决于设计选择
- 你内心至少冒出 2 个不同的"可能用户想要的方案"

### 执行方式

**用 `AskUserQuestion` 多轮收敛**（每轮 1-2 个最关键问题，不是一次堆 4 个）：

1. 先 grep / Read 做最小化只读调查，搞清楚 codebase 现状
2. 列出"用户意图 / 实现方案"上的关键歧义点（≥ 2 个 candidate）
3. 用 `AskUserQuestion` 问最前置的歧义（结构层 > 数值层 > 命名层）
4. 拿到答案后再问下一层（前一层不定下来，下一层问没意义）
5. 关键设计决策定下来后，再写 sentinel / plan / spec

### 每轮问题预算

- Light：通常 0 轮（数值微调，无结构歧义）
- Medium：0-1 轮（多数情况方案明确）
- Heavy：1-3 轮（架构性改动，需要逐层敲定）

每轮 ≤ 2 个问题。3 轮还没收敛 → 停下来要求用户用文字描述清楚，不要无止境追问。

### 反面案例（实际踩过）

用户："把 Lv1 的功能放到 Car 上面，删除 Lv1。"

错误做法：直接理解为"reparent Lv1 子节点到 Car"→ 写出 reparent 方案。
用户纠正："不是搬运，是删 Lv1 在 Car 上重新实现。"

正确做法：sentinel 之前先问"功能放到 Car 上是 reparent 现有子节点 / 还是删 Lv1 在 Car 上重建？"——一个问题就能避开整套错误方案。

### 不适用场景

- Light typo（用户说错字改正，无歧义）
- 用户已给出详细文件路径 + 具体改动描述
- 用户原话本身就排除了所有歧义（"把 X 的 a 字段从 1 改成 2"）

---

## 每级产出

### Light：人话三字段 + <details>（聊天里即可）

**严格按 `~/.claude/skills/fix-quick/references/user-language-protocol.md` § 4.1 Light 模板输出**：
- 对话框人话区：问题 / 打算怎么改 / 影响（玩家视角，三字段）
- `<details>` 折叠：文件路径 / 函数 / 根因 / 修法 / 拟清理旧代码
- **不再输出 `[ALIGN-LEVEL: Light]` `[ALIGN-LIGHT]` 标签**

**放行条件**：sentinel 文本发出后**立即调用 `AskUserQuestion`** 工具，弹"确认 / 改方向 / 取消"三选一（schema 见 `~/.claude/skills/fix-quick/references/user-language-protocol.md` § 6.1）。用户显式选"确认"才放行；选"改方向"回 Phase 1；选"取消"本轮终止。**不再有 60 秒超时推定同意**。

**Phase 5 验证特权**：Light 级**自动豁免视觉验证**，无论诊断阶段是否调用过 screenshot / Vibe-Eyes / scene-tree 等视觉工具。理由是 Light 的变更本质是"数值/文案/单字段"——正确验收方式是**值检查**（Read 改后文件核对新值、或 `playwright-cli eval` 读运行时值），不是像素对比。

**反向提醒**：如果你以为是 Light，但内容里写的是"改 spriteFrame / 改 _lpos / 改节点大小 / 改 UI 布局"——那不是 Light，是误判。改到像素层面就是 Medium，必须走证据对称。重新判级。

### Medium：人话三字段 + <details>（聊天里即可，不写文件）

**严格按 `~/.claude/skills/fix-quick/references/user-language-protocol.md` § 4.2 Medium 模板输出**：
- 对话框人话区：问题 / 打算怎么改 / 影响（玩家视角，三字段）
- `<details>` 折叠包含两段：
  - 段 1 需求复述（"我理解的真实诉求"也要走人话化，不允许出现文件路径 / 函数名）
  - 段 2 设计路线（开发视角技术细节）
- **不再输出 `[ALIGN-LEVEL: Medium]` `[ALIGN-MEDIUM]` `[ALIGN-GATE-OPEN]` 标签**

**放行条件**：
- sentinel 文本发出后**立即调用 `AskUserQuestion`** 工具，弹"确认 / 改方向 / 取消"三选一（schema 见 `~/.claude/skills/fix-quick/references/user-language-protocol.md` § 6.1）
- 用户显式选"确认"才放行；选"改方向"回 Phase 1；选"取消"本轮终止
- **不再有超时推定同意**；**禁止**用对话框文本"显式回 ok / 确认 / go"代替 AskUserQuestion 工具调用
- **Fast-Track 逃生阀（仅历史保留，新版本默认禁用）**：原本设计是用户原话含"直接改 / 别问了 / fast-track / skip"等关键词允许跳过 Medium gate；新版本要求 Medium 必须走 AskUserQuestion，**Fast-Track 仅在用户**当轮**主动重申才生效**，且响应**第一行**写 `[FAST-TRACK 风险自负]`，下一轮否定反馈仍自动 Level+2 作惩罚

### Heavy：人话区 + 写 spec 文件（无逃生阀）

**对话框严格按 `~/.claude/skills/fix-quick/references/user-language-protocol.md` § 4.3 Heavy 模板输出**：
- 对话框只发人话区：问题 / 打算怎么改 / 影响 / 不确定的点 / spec 文件路径
- 对话框**无 `<details>` 块**，技术细节全部进 spec 文件
- **不再输出 `[ALIGN-LEVEL: Heavy]` 标签**

**spec 路径**：`.claude/specs/fix-alignment/YYYY-MM-DD-<topic>.md`

**spec 文件模板**：

```markdown
# Fix Alignment · <topic>
**日期**：YYYY-MM-DD
**触发级别**：Heavy
**Level**：L{n}

## 1. 人话摘要
- 问题：<一句，玩家视角>
- 打算怎么改：<一句，玩家视角>
- 影响：<一句，玩家视角>
- 不确定的点：<一两句，玩家视角>

## 2. 需求理解
- 用户原话（原文引用）
- 真实诉求（自然语言重述）
- 歧义点与已做选择
- 验收标准

## 3. 框架调研
- 搜索命中条目
- 反面模式对照
- 可复用 API/Pattern 清单
- 若自写：为什么框架不够用（≥3 行）

## 4. 设计路线
- 选定方案
- 拒绝方案 + trade-off
- 关键决策点
- 对既有架构的影响

## 5. 变更范围
- 文件清单
- 不动范围
- 回滚策略
- 被本次修复直接取代的旧代码（拟一并清理）
```

**放行条件**：
- **无 Fast-Track 逃生阀**。即使用户说"直接改"也要顶住——架构级改动跑偏代价极高。用户坚持时明确告知："Heavy 级别修复不支持 fast-track，写 spec 只需 5 分钟，改错的回滚成本是一个下午。"
- **Plan Mode 优先**（Claude Code 环境）：`EnterPlanMode` + `ExitPlanMode`，用户在 UI 上 approve = 放行，reject = 改方向
- **spec 文件兜底**（无 Plan Mode 工具的环境）：写完 spec 后**立即调用 `AskUserQuestion`** 工具，弹"确认 / 改方向 / 取消"三选一（schema 见 `~/.claude/skills/fix-quick/references/user-language-protocol.md` § 6.1）；用户选"确认"才进入执行
- spec 第 1 节"人话摘要"必须与对话框人话区**完全一致**（不能在 spec 里偷偷写更详细版本）
- **不再接受**"显式回复 / 显式通过"作为放行替代——必须走 Plan Mode UI 或 AskUserQuestion 工具

---

## 反合理化对照表

agent 出现下列念头 = 正在准备违反本协议，立刻回到判级阶段：

| 念头 | 为什么错 |
|------|---------|
| "本质一样，只是表述不同" | 让用户确认 10 秒就好，不要替用户假设 |
| "用户不知道真问题，我帮他决定" | 帮助 = 解释发现给用户选，不是替他选 |
| "问一下显得不智能" | 不问就做错了才是真的不智能 |
| "已经很明显了，没必要走流程" | 判级规则机械，不许看"明显不明显" |
| "用户问的 Why，我直接去改吧" | Question 分类禁止进入修复流程 |
| "这个应该是 Light 吧"（但命中了关键词） | 命中任一升级条件就必须升，没有"应该" |
| "这轮 Medium 级用户应该不想多等" | Fast-Track 需要用户显式触发，agent 不能自主跳 |
| "Heavy 写 spec 太慢了简化吧" | Heavy 的无逃生阀是刻意设计，简化 = 违规 |
| "先改了不对再退回来" | 回滚成本远高于对齐成本，且上下文已污染 |

---

## 与现有 Phase 的关系（各 skill 自行吸收）

- 现有 Phase 里的 "X vs Y 强制对比" 从独立门控降为本协议**内部检查项**（写在"需求复述"里）
- User Intent 分类从独立步骤升为本协议**前置步骤**
- Level 阶梯（L0-L4）与本协议**正交**：Level 阶梯管"调查深度"，本协议管"对齐颗粒度"；两者叠加生效
- Phase 5 Verification Table 不受影响，保持原样

---

## 死代码清理（Dead Code Hygiene）

### 为什么要加这条

fix skill 的"最小修改"原则本意是防止顺手重构引入风险，但在一类场景下反而有害：**当本次修复改变了实现方向——比如用新算法替代旧算法、用框架 API 替代自写实现、用新字段替代老字段——旧代码就成了 dead code**。如果 skill 只写新逻辑不清旧账，代码库会单调膨胀，下次修 bug 的人还得分辨"哪段是活的"。

"最小修改"要的是**不做无关扩展**，不是**留着被自己取代的旧实现**。后者属于本次修复的必然收尾。

### 什么算"被本次修复直接取代"（范围定义）

必须同时满足：

1. **因果可论证**：能说出"因为我把 X 改成 Y，所以 Z 不再有调用点/不再被执行"
2. **引用可验证**：通过 grep / LSP findReferences 能证明 Z 没有其他引用路径
3. **仅限变更文件内**：只清理本次 sentinel "变更范围"里已列出的文件内的旧代码。**不主动扩大搜索半径**——同文件里其他 orphan 代码（与本次修复无因果）不在清理范围内

不满足上述任一条 = 不属于本次修复范围，写进 sentinel 也不算。想做更广的清理请用户显式发起新一轮 fix。

### Sentinel 里怎么写

Medium 级 sentinel 段 2 的"变更范围"节里**必须**有两行：

```
- 新增/修改：<文件:函数/字段 清单>
- 被本次修复直接取代的旧代码（拟一并清理）：<列出；无则写"无取代关系，不清理"（必须显式写这句，不允许省略）>
```

Light 级的一段式 sentinel 通常不涉及取代旧代码（它只是改一个值）；如果 Light 修改意外触发了取代（比如发现某个字段改完后常量表里的另一项再无引用），**升格成 Medium** 再走一遍对齐。

Heavy 级 spec 文件的"变更范围"节把这一条作为必填子节。

### 判定示例

| 场景 | 是否属于"被取代" | 理由 |
|------|-----------------|------|
| 改 `WeaponUpgrader.applyLevel`，同文件里 `applyLevelOld` 再无调用点 | ✅ 是 | 因果链清晰，grep 可证，本文件内 |
| 改 `foo.ts` 的算法，发现 `bar.ts` 里有个无关的 orphan 函数 | ❌ 否 | 跨文件且无因果，属于广义死代码扫描 |
| 把 `if-chain` 改成 switch，原来的中间变量 `_tmp` 不再需要 | ✅ 是 | 同一个 switch 实现的直接衍生 |
| 新增 @property 并赋值，老的代码里有个默认值常量 `DEFAULT_X` 还在多处用 | ❌ 否 | grep 显示多处引用，不符合"无其他引用" |
| 代码改完发现 `import Foo from ...` 不再被使用 | ✅ 是 | import 语句本身就是"直接取代"的副产品 |

### 执行时机

**与本次修复一并执行**，不分离成独立 PR / 独立一轮 sentinel。理由：取代关系只在"刚改完那一刻"最清晰，拖到下一轮上下文已污染。Phase 5 验证时，**清理条目同样要过 build + test**（否则就是删错了）。

### 与 Verification Table 的关系

Phase 5 的 Verification Table 增加一项心里检查（不必额外起 row）：sentinel 里列出的"拟清理旧代码" **每一条**都得在最终 diff 里真删了；任何漏删 = 违反 sentinel 承诺 = 当轮未闭环。

### 反合理化

| 念头 | 为什么错 |
|------|---------|
| "我只改新的，旧的留着不管就好" | 那就是在制造 dead code，下次修 bug 的人多一份心智成本 |
| "删旧的超出最小修改原则" | 最小修改 = 不做无关扩展；取代关系不是无关扩展，是本次修复的必然收尾 |
| "顺手把同文件别的死代码也清了" | 那就是范围 B / C，违反对齐承诺；只做与本次因果直接相关的 |
| "不确定有没有其他引用，先留着吧" | 那就 grep / LSP findReferences 一下再决定——不许拿"不确定"当借口保留 |

---

## 快速自检清单（每次触发本协议都过一遍）

在响应开头前心里跑一遍：

- [ ] 用户是提问还是修复请求？提问就先回答。
- [ ] 判级按规则扫了吗？命中的条目能说出来吗？
- [ ] Light：sentinel 里有没有具体到"文件:字段 旧值→新值"？
- [ ] Medium：有没有真跑 `search.py` 的输出？"可复用资源"是拍脑袋还是真搜过的？
- [ ] Medium/Heavy：变更范围里是否显式写了"被本次修复直接取代的旧代码"这一行（即使是"无取代关系，不清理"也要写）？
- [ ] Heavy：spec 文件路径写对了吗？文件真写出来了吗？
- [ ] 发完 sentinel 我是不是立刻闭嘴了？（红线 0）
- [ ] 我是否在对话框输出了 `[ALIGN-LEVEL: ...]` `[ALIGN-LIGHT]` `[ALIGN-MEDIUM]` `[ALIGN-GATE-OPEN]` 等内部标签？（应该没有，这些已废弃对外露出）
- [ ] 人话区每个名词过了一遍 user-language-protocol § 2.2 黑名单？
- [ ] Heavy spec 文件第 1 节"人话摘要"是否与对话框人话区一致？

任何一项 No = 违规，回到起点重走。
