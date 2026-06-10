# 用户语言协议 (User Language Protocol)

> **本协议被 fix-quick / fix-deep 等 fix 类 skill 在 sentinel / 完成报告 / 升级声明 / dev-log 摘要 等场景强制引用。**
> **目的：让对话框输出对策划友好（受众假设：用户只看过策划案，没看过任何项目代码）。**

---

## 0. 适用范围

### 引用本协议的 skill
- fix-quick（全局）
- fix-deep（全局）
- 项目层 fix-deep（dev-log 门控段）
- 其他 fix 类 skill 后续接入

### 哪些场景必须用本协议
- Phase 2 / Phase 1.5 sentinel
- 完成报告
- L1 升级声明 / L2 升级公告
- fix-deep Heavy spec 文件首节"人话摘要"
- fix-deep 项目版 Phase 1.0 dev-log 加载结果输出

### 哪些场景不用本协议
- AI 内部思考（thinking 块）
- Read / Grep / LSP 等工具调用
- TaskCreate 描述（任务管理内部）
- 错误堆栈、shell 命令原始输出

### L0 / L1 / L2 升级阶梯术语

- **L0**：首轮快修，按 fix-quick Phase 0-4 直跑
- **L1**：用户反馈"还是不行"，fix-quick 内换思路再试一次
- **L2**：两轮失败，硬停后通过 AskUserQuestion 弹三选一（升级 fix-deep / 再试一次 / 取消）
- **L3 / L4**（仅 fix-deep）：fix-deep 内部更深的多轮升级

---

## 1. 基本原则

### 1.1 受众假设
用户只看过游戏策划案，没看过任何项目代码 / 资源 / 节点树 / framework API。

### 1.2 三个铁律
1. **不出现技术名词**：文件路径、函数名、类名、Cocos 概念、算法名一律不进对话框人话区
2. **用游戏行为描述**：把"开发视角"翻译成"玩家视角"，描述玩家会做什么、看到什么、结果是什么
3. **一切技术细节进 `<details>`**：保留可审计性，但默认折叠

---

## 2. 准入词典

### 2.1 白名单（可用词）

| 类别 | 词例 |
|------|------|
| 玩家行为 | 玩家、点击、滑动、拖拽、放置、收集、释放、等待、按住、松开 |
| 游戏元素 | 关卡、角色、敌人、金币、道具、收集筐、目标点、终点、起点、障碍物 |
| 玩法状态 | 开始、进行中、暂停、胜利、失败、超时、结束、复活 |
| 视觉/交互 | 动画、特效、按钮、文字、图标、画面、镜头、震动、音效、提示 |
| 时序描述 | 之前 / 之后、同时、紧接着、过一会、立刻、第一次 / 第二次 |
| 数值描述 | 数量、距离、速度、大小、位置（"偏右 / 偏上"OK，"x 坐标"不行） |

### 2.2 黑名单（禁用词，遇到必须翻译或下沉）

| 类别 | 禁用词例 | 翻译范例 |
|------|---------|---------|
| 文件 / 路径 | `assets/scripts/...`、`.ts`、`.prefab`、`.scene`、`.meta` | 不翻译，直接进 `<details>` |
| 函数 / 方法名 | `onCoinArrive`、`scheduleOnce`、`update`、`onLoad` | "金币到达时" / "每一帧" / "关卡加载时" |
| Cocos 概念 | 节点、组件、prefab、scene、`@property`、`cid`、`UUID`、`__id__`、Sprite、Label、Node、Canvas、Widget | 用对应玩家可见的物件名（"金币图标""收集筐界面"）；纯技术细节进 `<details>` |
| 算法 / 技术 | localPosition、worldPosition、`Vec3`、回调、闭包、生命周期、状态机、定时器 | "落在父物体里的位置" / "落在场景里的位置" / "等一段时间后" |
| 框架名 | XTween、ItemCollection、AIState、HeroBootstrap、LogicConfig、LocalizedLabel | 进 `<details>`，人话区一律用玩法语言重述 |

### 2.3 边界词（视语境）

- ✅ "按钮没反应" / ❌ "Button 组件"
- ✅ "关卡界面卡住了" / ❌ "Canvas 没刷新"
- ✅ "金币图标飞错了地方" / ❌ "金币 Sprite 节点的 worldPosition 算错"
- ✅ "音效没出来" / ❌ "AudioSource 没触发"
- ✅ "事件 / 监听" 视语境（策划文档用过 → 白名单；纯代码层 → 进 details）

### 2.4 硬规则：策划案白名单覆盖

> **凡是策划案里出现过的词都自动算白名单。**
>
> 项目入口处（**策划案** `docs/game-design/<code>.md` 或 `docs/PRD/<code>.md`，**不是 dev-log**）的术语，无论原本属于黑名单还是边界词，都视为白名单。
> dev-log（`docs/game-design/dev-log/<code>.md`）写的是技术摘要不是策划语言，**不算白名单源**。

执行方式：fix 命令在 Phase 0 阶段读取**策划案**时，把里面出现的名词列入"项目特化白名单"，在 sentinel 自检时优先匹配。dev-log 内容只用于技术定位，不污染白名单。

### 2.5 自检规则

人话区每个名词过一遍黑名单 → 命中即翻译或下沉到 `<details>`。
**命中黑名单未翻译就发 = 违规，sentinel 重写。**

---

## 3. 人话三字段模板

### 3.1 字段定义

```
问题：<一句话，玩家视角，描述现在不对的事>
打算怎么改：<一句话，玩家视角，描述要让什么变成什么>
影响：<一句话，会动哪些玩法 / 不动哪些玩法>
```

### 3.2 写法约束

- 每段 ≤ 2 行（一句为主，必要时多一句补充）
- 主语用"玩家 / 角色 / 关卡 / 金币 …"等玩法名词，避免"系统 / 模块 / 流程"
- 禁止反问 / 修辞性问句 / 比喻（除非策划案里用过）
- 影响段必须正反面都说："只动 X / 不动 Y"，不能只说"只动 X"

### 3.3 反面例子

| 错误写法 | 改成 |
|---------|------|
| 问题：onCoinArrive 函数里的落点逻辑不对 | 问题：金币飞行结束后，落地位置偏右，看起来不像是落到收集筐里 |
| 打算怎么改：把 localPosition 改成 worldPosition | 打算怎么改：让金币落到收集筐里，而不是收集筐父物体的中心 |
| 影响：仅修改 GameController.onCoinArrive | 影响：只动金币飞行结束这一段，关卡其他玩法不变 |

---

## 4. 三档 Sentinel 模板

### 4.1 Light（fix-quick 默认 / fix-deep Light 级）

````
问题：<一句>
打算怎么改：<一句>
影响：<一句>

等下我会用 AskUserQuestion 弹**确认 / 改方向 / 取消** 三选一，请显式选一个。
（详见 § 6 AskUserQuestion 确认协议；不再有 60 秒推定同意）

<details>
<summary>技术细节（开发视角）</summary>

文件：<路径清单>
位置：<函数 / 字段>
根因：<开发视角的技术原因>
修法：<开发视角的具体改法>
拟清理的旧代码：<列出 或 "无取代关系">

</details>
````

### 4.2 Medium（fix-deep Medium 级）

````
问题：<一句>
打算怎么改：<一句>
影响：<一句>

⚠️ 这次改动稍大，等下我会用 AskUserQuestion 弹**确认 / 改方向 / 取消**，必须显式选一个；Medium 档不接受 Fast-Track。
（详见 § 6 AskUserQuestion 确认协议）

<details>
<summary>技术细节（开发视角）</summary>

**段 1：需求复述**
- 用户原话：「...」
- 我理解的真实诉求：...（玩家视角描述，不允许出现文件路径 / 函数名）
- 歧义点：...
- 验收标准：...

**段 2：设计路线**
- 框架调研：...
- 选定路线：...
- 变更范围（含拟清理的旧代码）：...
- 不动范围：...

</details>
````

### 4.3 Heavy（fix-deep Heavy 级）

#### 4.3.0 输出载体优先级

| 环境 | 输出载体 | 理由 |
|------|---------|------|
| Claude Code（有 `EnterPlanMode` / `ExitPlanMode` 工具） | **优先 Plan Mode** | UI 直接 approve，不让用户去 disk 找 spec；plan 文件路径由 plan mode system prompt 指定 |
| 其他 IDE / Codex / Copilot CLI | 落 spec 文件到 `.claude/specs/fix-alignment/YYYY-MM-DD-<topic>.md` | 兜底 |
| 用户明确说"用 Plan / 用 spec 文件 / 别用 plan mode" | 按用户指令 | 用户优先 |

**Plan Mode 流程**：
1. `EnterPlanMode`（system 会指定 plan 文件路径，如 `~/.claude/plans/<adjective>-<noun>.md`）
2. 把 plan 写到该路径（首节强制"人话摘要"，后续 Approach / Files / Steps / Verification / Risk）
3. 调 `ExitPlanMode`，用户 UI approve / reject
4. approve 后才执行（与 spec 文件 review 等价的对齐承诺）

**Plan 文件首节强制为"人话摘要"** —— 保留 spec 文件的语义层级（人话区先行 → 技术段在后）。

对话框里只发**人话区**，技术细节全部进 spec 文件 / Plan 文件（无 `<details>` 嵌套，所以下面用 3 反引号即可，不像 § 4.1 / § 4.2 需要 4 反引号外包）：

```
问题：<一句>
打算怎么改：<一句>
影响：<一句>
不确定的点：<一两句，玩家视角说"哪些玩法可能要你过一眼">

完整方案我写到 `.claude/specs/fix-alignment/YYYY-MM-DD-<topic>.md`
请打开看一下；spec 兜底场景下我会接着用 AskUserQuestion 弹**确认 / 改方向 / 取消**。
（Plan Mode 路径走 ExitPlanMode；详见 § 6）
```

spec 文件结构：

```
# Fix Alignment · <topic>
## 1. 人话摘要（新增首节，对应对话框三字段 + 不确定点）
## 2. 需求理解（原 § 1）
## 3. 框架调研（原 § 2）
## 4. 设计路线（原 § 3）
## 5. 变更范围（原 § 4）
```

---

## 5. 完成报告 / L1 / L2 / dev-log

### 5.0 commit 范围控制（涉及 git 时强制）

**绝对禁止 `git add -A` / `git add .` / `git add **`**。

理由：用户工作树通常有大量与本次任务**无关**的进行中改动（其他模块开发 / 临时文件 / 待整理内容）。`-A` 会把它们一并 staged，commit 后混入本次 fix 的历史，破坏单一修改语义。

**正确做法**：

1. plan / sentinel 必须显式列出"本次修改文件清单"（Heavy 级 spec § 5 变更范围、Medium 级 `<details>` 段 2、Light 级 `<details>` 文件清单）
2. `git add` 时**逐个指定文件**：`git add <file1> <file2> ...`
3. 任何"清单外"文件命中 staged → 立即 `git restore --staged <file>` 移除
4. commit 前必须 `git diff --cached --stat`（不只 stat，复杂时看完整 diff）确认 staged 内容只含清单内文件
5. **特例**：当文件本身在工作树有大量与本次无关的未 commit 改动时（典型例子：你只想改一行注释，但同文件还有 100 行用户重构），**不要 commit 该文件**，留在工作树由用户自己决定。如果坚持要 commit，必须用 `git add -p` 交互式选择 hunk —— 但 background session 不能交互，所以只能放弃 commit 该文件。

**反面案例（实际踩过）**：
- `git add -A` → 把用户 12 个无关 .ts 文件 + 1 个 prefab + 多个 meta 全 staged → commit 进去就是事故。

### 5.1 完成报告（修完后，三档统一）

````
修好了。

现在玩家会看到：<具体玩法行为>
之前那个问题：<对应原现象>，已经不会发生
顺手清理了：<可选，被取代的旧逻辑；没清理时此行不出现>

<details>
<summary>验证记录（开发视角）</summary>

- 编译：bash .vscode/cocos-compile.sh ✓ 无报错
- 截图对比：playwright-cli screenshot before / after ...
- 运行时检查：cc.find('Canvas/...') ...

</details>
````

**约束**：完成报告人话区**只能描述玩家可见行为**，不能写"修了 X 函数"或"改了 X.ts"——后者全部进 `<details>`。

### 5.2 L1 升级声明（fix-quick 第二轮）

````
上次没修好。换个思路再试一次：
- 上次以为问题出在 <人话>
- 这次怀疑实际是 <人话>，原因是 <人话证据>

打算怎么改：<新思路一句>
影响：<同上>

<details>
<summary>技术细节</summary>
（同 Light 模板的技术段）
</details>
````

### 5.3 L2 升级公告（fix-quick 两轮失败 → 弹用户选择）

公告发出后**同一轮内立即调用 `AskUserQuestion` 弹三选一**，由用户决定下一步；**不再自动切 fix-deep**。

````
试了两轮没修好。
- 第一轮以为是 <人话> → 没解决
- 第二轮以为是 <人话> → 也没解决

接下来怎么处理？等下我会用 AskUserQuestion 弹三选一：
- 升级到 fix-deep（推荐）：重新读相关文件、列至少两条新假设、严格证据对称；慢但稳
- 在 fix-quick 内再试一次：你给个新方向或新线索，我按 L1 思路换假设重走一遍
- 取消：先停手，等你后续指示

<details>
<summary>切换记录（开发视角）</summary>
- L0 假设：... → 失败原因 ...
- L1 假设：... → 失败原因 ...
- 已排除根因方向：...
</details>
````

AskUserQuestion 配置（label 名固定，不得改写）：

```
question: "fix-quick 两轮都没修好，下一步怎么处理？"
header: "L2 选择"
options:
  - label: "升级到 fix-deep"
    description: "重新读相关文件、列至少两条新假设、严格证据对称；慢但稳（推荐）"
  - label: "在 fix-quick 内再试一次"
    description: "请先给出新方向或新线索；我按 L1 思路换假设重走 Phase 0-4"
  - label: "取消"
    description: "停手，等用户进一步指示"
```

### 5.4 fix-deep Phase 1.0（dev-log 门控）输出

#### 5.4.1 dev-log 文件存在（正常流程）

````
游戏地图加载完成（这一步不影响修复方向，跳过即可）。

<details>
<summary>开发视角：dev-log 摘要</summary>

game_type: <value>
entry_files: <list>
cid_map 条目数: <n>
known_todos: <list 或 "无">

</details>
````

#### 5.4.2 dev-log 文件不存在（警告流程）

````
⚠️ 这个游戏没有地图记录。
意思是：之前没人写过哪些文件管哪些玩法，我接下来要靠地毯式搜索来定位。
风险：可能改错了地方。

等下我会用 AskUserQuestion 弹**确认（接受盲修）/ 改方向（先补 dev-log）/ 取消**。
（详见 § 6.3 dev-log 场景的 label 语义）

<details>
<summary>开发视角：警告原文</summary>

docs/game-design/dev-log/<code>.md 不存在。
1. 该游戏非 playable-dev 建立，或 dev-log 从未写入
2. 修改面文件、cid 映射、设计约束未知 → 盲修风险

继续则所有文件定位需从 Phase 1 全量 grep / Read 完成。

</details>
````

---

## 6. AskUserQuestion 确认协议（替代 60 秒超时机制）

### 6.0 为什么改为 AskUserQuestion

旧版 sentinel 的"60 秒内无回复推定同意"是 background session 时代的兜底——但在 Claude Code 等支持 `AskUserQuestion` 工具的环境下，被动等待会踩两个坑：

1. 用户在思考时被 60 秒静默"催产"，不得不在没看清细节时就被默认放行
2. 用户想"换个思路"时只能在自由文本里说，AI 易错过信号

`AskUserQuestion` 工具弹出结构化三选一，用户必须显式点一个，不存在超时推定同意。

### 6.1 标准三选一 Schema

凡是本协议要求"等用户放行"的位置，**必须立即调用 `AskUserQuestion`**，按以下 schema 提问：

```
question: 按这个方向修吗？
header: 修复确认（≤ 12 字）
multiSelect: false
options:
  - label: 确认
    description: 按当前 sentinel 描述动手修复。
  - label: 改方向
    description: 思路有问题或我有补充信息，回 Phase 1 重新分析根因。
  - label: 取消
    description: 本轮 fix 终止，不动代码。
```

### 6.2 各档对应映射

| 档位 | sentinel 文末提示语 | 工具调用 |
|------|----------------------|----------|
| Light（§ 4.1） | "等下我会用 AskUserQuestion 弹三选一确认。" | sentinel 文本发出后**同一轮**立即调用 `AskUserQuestion` |
| Medium（§ 4.2） | "等下我会用 AskUserQuestion 弹三选一，必须显式选。" | 同上，且**禁止** Fast-Track（即使用户上一轮说过 "直接改" 也得弹） |
| Heavy（§ 4.3） | Plan Mode 优先；spec 文件兜底场景才用 `AskUserQuestion` 兜底 | 优先 `EnterPlanMode` + `ExitPlanMode`；spec 文件场景在写完 spec 后追加 `AskUserQuestion` |
| dev-log 警告（§ 5.4.2） | "继续吗？" | sentinel 文本发出后同一轮立即调用 `AskUserQuestion`，三选一含义见 § 6.3 |

### 6.3 dev-log 警告场景的语义映射

dev-log 不存在时，三个 label 含义略有调整（label 名不变，description 改写）：

```
options:
  - label: 确认
    description: 接受盲修风险，继续 Phase 1 全量 grep / Read 定位。
  - label: 改方向
    description: 我手动补一下 dev-log 再回来；本轮先停。
  - label: 取消
    description: 本次 fix 终止。
```

### 6.4 红线

- **禁止**在 Claude Code 环境下沿用"60 秒推定同意"措辞
- **禁止**用对话框文本的 "回 ok / 确认 / go" 当作放行替代——必须走 `AskUserQuestion` 工具
- 用户回答"确认"前的任何代码 / 资源写操作 = 协议违规，当轮进度作废重走（红线 0 加强版）
- Plan Mode 走 `ExitPlanMode` approve 视同 "确认"；reject 视同 "改方向"

---

## 7. 自检清单

写完 sentinel / 报告 / 升级声明，**发出前**心里跑一遍：

- [ ] 人话区每个名词是否过了 § 2.2 黑名单检查？
- [ ] 命中黑名单的词是否都翻译或下沉到 `<details>` 了？
- [ ] 三字段（问题 / 打算怎么改 / 影响）是否齐全？
- [ ] 影响段是否同时说了"只动 X / 不动 Y"两面？
- [ ] 人话区每段是否 ≤ 2 行，且没有反问 / 修辞性问句 / 比喻（除非策划案里用过）？
- [ ] 所有技术细节是否都进了 `<details>` 折叠块，没有暴露在人话区？
- [ ] 完成报告人话区是否只描述玩家可见行为，没有出现"修了 X 函数 / 改了 X.ts"？
- [ ] Heavy 级 spec 文件首节是否写了"人话摘要"？
- [ ] dev-log 摘要的人话区是否没有混进 `game_type:` `cid_map` 这种 key 名？
- [ ] 是否避免输出 `[ALIGN-LEVEL: ...]` `[ALIGN-LIGHT]` `[ALIGN-MEDIUM]` `[ALIGN-GATE-OPEN]` 等内部判级标签？
- [ ] sentinel / dev-log 警告 发完后，是否在**同一轮**内调用了 `AskUserQuestion`（三选一：确认 / 改方向 / 取消）？
- [ ] 是否在文中保留了已废弃的 "60 秒推定同意 / 显式回 ok / 显式回 go" 等措辞？（必须删除）

任何一项 No = 违规，重写。
