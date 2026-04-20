---
name: quick-fix
description: "修改代码时必须使用此技能，无例外。Fix, debug, optimize, refactor, add features, adjust UI/layout, match designs, or make any change to source code files. 凡是涉及改代码、修bug、加功能、优化性能、迁移配置、修测试、调样式、对齐设计稿、还原UI布局、让代码和参考一致的请求，都必须用这个技能。即使任务描述模糊（如'改成和X一样'、'照着Y做'、'调一下布局'），只要最终会修改源文件，就必须触发。Trigger on: file paths, broken/slow/wrong behavior, UI effects, style adjustments, layout matching, design-to-code, migration, test fixes. 当用户显式写 /quick-fix 时，必须立即触发，不做任何判断。**MUST re-trigger on follow-up fix requests within the same session, including negative feedback on a prior fix.** Re-trigger phrases (中文): 还是不行 / 没修好 / 又崩了 / 同样的问题 / 还是报错 / 改了没用 / 试了还是 / 又来了 / 还有问题 / 继续修 / 再改一下 / 又发现. (English): still broken / didn't work / same issue / again / didn't fix / still failing / one more thing / also fix / keep fixing. 多轮修复按 L0→L4 阶梯逐轮加重调查深度；用户报告不相关的新 bug 则重置到 L0。不适用于纯只读任务：解释概念、review PR、查看git记录、跑审计命令、描述项目结构。"
---

# Quick Fix

## Why This Skill Exists

Random fixes waste time. Untested claims waste trust. Scope creep wastes effort. This skill enforces three simple principles that prevent all three:

1. **Evidence before action** - Read and trace the code before changing it, because memory drifts and assumptions lie.
2. **Root cause before fix** - Symptom patches create new bugs. Finding the real cause is faster than guess-and-check thrashing.
3. **Verification before claims** - "Should work" is not evidence. Run the command, read the output, then report.

Violating any of these wastes more time than following them, even under pressure.

---

## Multi-Round Escalation Ladder

Bugs that survive a first fix rarely yield to another round of the same approach. Each re-try must change **how** you investigate, not just **what** you change. This ladder is the core mechanism for ensuring each subsequent round digs deeper instead of re-running the failed one.

### Why this exists

When a first fix fails, the instinctive response — "tweak the same file a bit more" — is almost always wrong. The round-1 hypothesis was likely incorrect; repeating it in round 2 just produces a differently-wrong patch. Each level below forces a **fundamentally different investigation strategy** so later rounds actually converge instead of thrashing.

### Level Detection (run BEFORE Phase 0, every turn)

At the start of every turn where this skill triggers, classify the current round:

| User signal | Level action |
|-------------|-------------|
| First report of a bug (no prior fix in this session) | **L0** |
| User describes a genuinely different bug (different file/function/symptom from prior fixes) | **Reset to L0** |
| Negative feedback on immediately prior fix (see re-trigger phrases in description) | **Increment level by 1** (L0→L1, L1→L2, ...) |
| User confirms prior fix worked, then reports a new issue | **Reset to L0** |
| Ambiguous ("再看看这个") | Ask: "是上一个 bug 还没修好，还是新问题？" — do not proceed without user answer |

**Announce the level at the start of every response:** `[quick-fix L2] 进入深度调查模式…`

This announcement is non-negotiable. It makes the escalation contract visible to the user and commits you to the level's behavioral requirements.

### The Ladder

| Level | Context | Required Behavioral Change | Forbidden |
|-------|---------|---------------------------|-----------|
| **L0** | First attempt on this bug | Standard Phase 0–5 flow | — |
| **L1** | 2nd attempt, bug not fixed | 1. Explicitly declare: "上一轮的根因诊断是错的。"  2. Re-Read **every** file touched last round from scratch — discard all cached understanding.  3. Enumerate **≥2 alternative root-cause hypotheses** that do NOT overlap with last round's; test each with evidence before committing to one. | Reusing prior hypothesis; trusting memory of prior Reads; editing the same line as last round without new evidence |
| **L2** | 3rd attempt | 1. Expand search radius beyond the immediate file: caller chain, config, environment, build pipeline, runtime behavior.  2. Instrument component boundaries with logs/prints and ask the user to run + paste output.  3. State in writing: "bug 很可能不在我之前看的层。" | Fixing in the same file/layer as L0/L1 without first proving via instrumentation that the bug is actually there |
| **L3** | 4th attempt | 1. Treat as architectural signal.  2. Enumerate **3 competing root-cause hypotheses** with explicit cost-to-verify for each.  3. **Refuse to edit code** until the user picks one hypothesis. | Choosing a hypothesis yourself; any code edit before user picks |
| **L4** | 5th+ attempt | **Hard stop. No more fix attempts.** Produce a "Failed Attempts Log" summarizing what L0–L3 tried and ruled out. Escalate: "已连续 4 轮未修复，超出 quick-fix 范围。建议切 `/fix` 深度调查，或讨论架构重构。" | Any further code edits; any new hypothesis without fresh user direction |

### Level-Specific Gates (apply on top of existing phase gates)

- **L1+**: Phase 0's "Read all involved files" is **mandatory from scratch** — you may not rely on Reads from prior rounds. Memory is compromised evidence.
- **L2+**: Phase 2 must include **≥1 instrumentation step** (log / print / breakpoint) with real run output as evidence, not reasoning alone.
- **L3+**: Phase 3 plan must list the 3 competing hypotheses with verification costs, and Phase 4 is blocked until the user picks one.
- **L4**: No Phase 3/4/5 at this level. Only the Failed Attempts Log + escalation recommendation.

### Anti-patterns at higher levels

| Thought at L1+ | Why it's wrong |
|---------------|---------------|
| "这次稍微改下 X 应该就行" | "稍微改下"是 L0 思维。L1 要求换方法论，不是调参。 |
| "上轮读过的文件还记得" | L1+ 禁止依赖旧 Read。重读成本远低于基于错记忆再错一次的成本。 |
| "我先试试这个再说" | L3 禁止自选假设。强制用户选是因为已经证明你的自选不准。 |
| "再让我修一次" (at L4) | 4 轮未修 = 超 quick-fix 能力边界。继续尝试是给用户挖更深的坑。 |

---

## Phase 0: Collect Ground Truth

> **Multi-model dispatch available:** For complex tasks, you can delegate phases to specialized models (haiku for reading, opus for analysis, sonnet for execution). Read `references/multi-model-dispatch.md` for templates. For simple tasks, just execute all phases directly.

The goal is to understand what actually exists, not what you think exists.

**Why this matters:** Conversations are long. Files change between turns. Memory of code you read 20 messages ago may be wrong. Every minute spent re-reading saves ten minutes fixing the wrong thing.

1. **Read all involved files** - Use the Read tool on every file you plan to modify. This is non-negotiable.
2. **Trace the call chain** - Grep for functions, variables, and types involved. Follow callers and callees.
3. **Run to see real errors** (when possible) - Actual error output beats guessing what the error might be.
4. **Confirm APIs exist** - Before calling any function or using any flag, grep/LSP to verify it actually exists. Don't trust memory.
5. **Before each edit, re-Read** - If more than a few turns have passed since you last read a file, read it again.

6. **Track visual-tool usage** - If you call any of the following during diagnosis, you are on the hook for symmetric verification in Phase 5 (see item #6 there — not optional):
   - **Browser automation / E2E tooling** — whether invoked via MCP or Bash:
     - `mcp__chrome-devtools__*` (take_screenshot, take_snapshot, navigate_page + wait_for, lighthouse_audit, performance_*)
     - `mcp__playwright__*` (any browser / screenshot / snapshot / trace tool)
     - `npx playwright ...` / `playwright-cli` (test --screenshot, codegen, show-trace, show-report)
     - Puppeteer / Cypress / Selenium / WebdriverIO scripts executed via Bash
   - **Design & rendering tools**:
     - `mcp__pencil__*` (get_screenshot, snapshot_layout, export_nodes, batch_get with visual intent)
   - **Game engine / runtime capture**:
     - `mcp__cocos-game-intelligence__*` (captureNow, getSceneTree, getGameState, getKeyframe)
     - `mcp__vibe-eyes__*`
   - **Raw visual assets**: Reading image / video / trace files (`.png` / `.jpg` / `.jpeg` / `.webp` / `.gif` / `.svg` / `.mp4` / `.webm` / `.har` / `playwright-report/**`) as evidence
   - **Catch-all**: any tool — MCP, CLI, or script — whose output is a pixel buffer, DOM snapshot, scene tree, rendered artifact, or interaction trace. If in doubt, treat it as a visual tool and track it.

   **Why track now:** by Phase 5 your memory of what you invoked 20 messages ago is unreliable. Note visual-tool calls as they happen so Phase 5's conditional gate is mechanical, not a judgment call.

7. **Classify user intent** - Before proceeding, determine what the user actually wants:

   | User input pattern | Classification | Required action |
   |-------------------|---------------|-----------------|
   | Contains question words ("为什么", "怎么回事", "是不是", "why", "how come", "what causes") | **Question** | Answer the question first. Then ask: "需要我修复这个问题吗？" Do NOT proceed to Phase 1 until the user confirms they want a fix. |
   | Describes broken/wrong behavior and asks to fix it | **Fix request** | Continue to Phase 1 |
   | Vague ("看看这个", "这里有问题") | **Ambiguous** | Ask: "你希望我帮你排查原因，还是直接修复？" |

   **This step is non-negotiable.** If the user asked a question, answering it IS the task. Making code changes to a question the user didn't ask you to fix is a violation of scope.

**Gate:** You must have Read every file you plan to modify before proceeding. If user intent is "Question", answer and wait for confirmation before proceeding.

---

## Phase 1: Compare and Clarify

The goal is to make sure your understanding matches reality. When it doesn't, stop and ask.

### Step 1: Write a mandatory comparison statement

Before doing anything else in this phase, you MUST write this statement out loud:

> **用户描述的问题是：** [用用户原话概括]
> **我诊断出的问题是：** [用你自己的发现概括]

This is not optional. If you skip this step, you will make wrong assumptions and waste the user's time.

### Step 2: Compare and decide

| Situation | Action |
|-----------|--------|
| 用户描述 = 你的诊断 (X == Y) | Continue to Phase 2 |
| 用户描述 ≠ 你的诊断 (X ≠ Y) | **禁止继续。** 必须向用户展示你的发现并询问确认。 |
| Something is ambiguous or uncertain | **禁止继续。** List the specific points of confusion. |
| You discovered problem B while investigating A | **禁止继续。** "While looking at A, I found B. How should I handle B?" |
| You think something extra should be done | **禁止继续。** Don't add unrequested features. |

**The X ≠ Y rule is absolute.** If what the user described and what you found are not the same thing, you MUST stop and ask. There is no scenario where silently proceeding is acceptable — even if you're 99% sure your diagnosis is correct. Being sure is not the same as having user agreement.

### Anti-rationalization checkpoint

If you catch yourself thinking any of these, you are about to violate Phase 1:

| Your thought | Why it's wrong |
|-------------|---------------|
| "问题本质上是一样的，只是表述不同" | 那就让用户确认这一点。如果真是一样的，确认只需 10 秒。 |
| "用户可能不知道真正的问题是什么，我来帮他" | 帮助 = 解释你的发现并让用户决定，不是替用户做决定。 |
| "问一下会显得不够智能" | 不问就做错了才是真的不够智能。 |
| "已经很明显了，没必要问" | 如果 X ≠ Y，不管多明显，规则就是要问。 |
| "先修了再说，反正可以回滚" | 回滚的成本远高于一个问题的成本。 |

**Why ask instead of guess:** A wrong assumption compounds. One bad guess leads to a fix that addresses a non-problem, which either breaks something or wastes a round-trip. One clarifying question takes 30 seconds; one wrong fix takes 30 minutes to undo.

**Gate:** All uncertainties resolved before proceeding. If your comparison statement shows X ≠ Y, you have NOT passed this gate until the user responds.

---

## Phase 2: Root Cause Investigation

The goal is to find WHY the problem exists, not WHERE the symptom appears.

**Why root cause matters:** Fixing symptoms (adding try-catch, null checks, special-case ifs at the crash site) leaves the real bug alive. It will resurface in a different form, harder to trace because the symptom is now hidden.

1. **Trace the full data flow** - Follow the data from source to symptom. The fix belongs at the layer where the data first goes wrong, not where the error finally surfaces.
2. **List hypotheses, test one at a time** - For each possible cause, find the cheapest way to confirm or rule it out. Don't change multiple things simultaneously.
3. **In multi-component systems, instrument boundaries** - Log what enters and exits each component. Run once. The evidence shows exactly which layer fails.
4. **Fix the source, not the surface** - Fix the sender, not the receiver. Fix the data origin, not the render layer. Don't add if-guards around symptoms.
5. **Find working examples** - Look for similar working code in the same codebase. Compare line by line. The difference between working and broken is often the answer.

**When your hypothesis is wrong:**
- Don't quietly switch direction. Say: "My earlier analysis was wrong. The actual cause is X. I need to change approach."
- Re-examine every decision made after the wrong assumption.

**After 3+ failed fix attempts:** Stop trying fixes. This is likely an architectural problem, not a bug. Tell the user: "This has resisted 3 attempts. It may need architectural changes. Let's discuss the approach, or use `/fix` for deep investigation."

**Gate:** Root cause identified with evidence before proceeding.

---

## Phase 3: Plan and Checklist

The goal is to agree on WHAT to change before changing it, so nothing is missed or overstepped.

1. **State the fix plan clearly:**
   - Root cause (one sentence)
   - What to change (specific files and modules)
   - How to change it (strategy)
   - What NOT to change (explicit exclusions)

2. **Create a checklist** using TaskCreate - one item per change:
   ```
   [ ] Fix message routing logic in handler.ts
   [ ] Update type definitions in protocol.ts
   [ ] Update state handling in store.ts
   ```

3. **Wait for user confirmation** before executing.

**When referencing another project:** Add a column to each checklist item noting whether the reference project has this feature. If you want to deviate from the reference, ask first.

**Gate:** User has confirmed the plan.

---

## Phase 4: Execute

The goal is to follow the checklist precisely - no more, no less.

1. **Work through checklist items in order.** Mark each complete as you go.
2. **Re-Read files before each edit.** The file may have changed since Phase 0.
3. **Write complete code.** No placeholder comments like `// ... rest`, `// similar handling`, or `// TODO`. Every line must be real, working code.
4. **Preserve existing functionality.** Don't silently remove features the user didn't ask to remove.
5. **Keep types in sync.** When changing data structures, interfaces, or message formats, update all type definitions.
6. **Check imports.** After editing, verify no duplicate imports were introduced.

**Scope discipline:**
- Code decisions (how to implement) = your call, don't ask.
- Feature decisions (what to implement) = user's call, always ask.
- If you discover a new problem during execution, stop and ask the user. Don't expand scope on your own.

---

## Phase 5: Verify Before Claiming Done

The goal is to prove the work is correct with actual command output **and matching observational evidence**, not confidence. A single passing command is not full verification — all verification items must complete.

### Evidence Symmetry Principle (证据对称原则)

**The shape of your verification must match the shape of your evidence.** If you used a visualization tool to find, confirm, or investigate the problem during Phase 0–2, you are contractually required to use the same tool in Phase 5 to produce "after-fix" evidence. A UI bug discovered via screenshot cannot be closed by "build passes" — the 颗粒度 doesn't match. A rendering glitch diagnosed from a scene tree cannot be closed without a fresh scene tree.

Put another way: **how you saw the bug = how you must prove the fix**. Anything less is changing the evidence contract mid-task, which is how silent regressions slip through.

This principle applies concretely to item #6 below.

**Why this must be exhaustive:** The most common failure mode is running build, seeing it pass, and immediately claiming "done" — skipping lint, tests, and regression checks. A build that compiles is not a build that works correctly. Each verification item catches a different class of problem:

- **Build** catches syntax errors and missing dependencies
- **Lint/TypeCheck** catches type mismatches, unused variables, and style violations
- **Tests** catch behavioral regressions
- **Checklist review** catches incomplete implementations (the #1 user complaint)
- **Regression check** catches newly introduced warnings or errors
- **Visual verification** (conditional) catches "build passes but the UI still looks wrong" — the failure mode that command-line checks structurally cannot see

Skipping any one of these is like a pilot skipping items on a pre-flight checklist because the engine started fine.

### The Verification Items

Work through these **in order, all of them, every time**. Item #6 is conditional (see below) — it is either MUST or N/A, never optional.

| # | Item | Command / Action | What to check |
|---|------|------------------|---------------|
| 1 | **Build** | Project's build command | Zero errors in output |
| 2 | **Lint/TypeCheck** | Project's lint/tsc command | Zero new errors |
| 3 | **Tests** | Project's test command | All pass (or "no tests exist") |
| 4 | **Checklist review** | Re-Read modified files | Every Phase 3 checklist item is implemented |
| 5 | **Regression check** | Compare before/after | No new errors or warnings |
| 6 | **Visual verification** *(conditional MUST)* | Re-invoke the visualization tool used during diagnosis | "Before" and "after" artifacts compared; the originally-visible defect is visibly gone |

### Item #6 — Visual Verification (Conditional MUST)

**Trigger (mechanical, not a judgment call):** If you called ANY of the tools listed in Phase 0 Step 6 during this task (chrome-devtools visual tools, pencil visual tools, cocos-game-intelligence capture/scene/state tools, vibe-eyes, or Read on image files used as evidence), item #6 is **MUST** and cannot be SKIPped. If you called NONE of them, item #6 is **N/A** and the row shows "N/A — no visual tools used in diagnosis".

**Why conditional:** a pure backend logic fix has no visual surface to compare; forcing a screenshot there is theater. But for any fix you surfaced through a visual tool, command-line checks structurally cannot see the failure mode — the build compiles, the types pass, the tests (if any) run on a different layer, and the layout/rendering bug lives on without detection.

**Protocol:**

1. **List the visual tool(s) you used during diagnosis.** Name each MCP tool / CLI / script + what it showed you (e.g., "`mcp__chrome-devtools__take_screenshot` — captured the misaligned header"; "`mcp__playwright__browser_take_screenshot` — reproduced the login-page regression"; "`npx playwright test --screenshot=on` — produced the failing visual diff under `playwright-report/`"; "`mcp__pencil__get_screenshot` — the design reference I was matching against"; "`mcp__cocos-game-intelligence__captureNow` — showed the frozen sprite").

2. **Re-invoke the same tool(s)** after the fix is applied. Use the same target (same URL, same node ID, same scene), so the before/after comparison is apples-to-apples. If the project needs a rebuild/reload/restart for the visual change to land, do that first — a stale view is a false positive.

3. **Write the comparison statement** explicitly:
   > **修复前** [tool X] 显示：[what was wrong, one sentence]
   > **修复后** [same tool X] 显示：[what is now correct, one sentence]
   > **结论**：[原缺陷已消除 / 缺陷仍存在 / 出现新异常]

4. **If visual re-verification is impossible** (e.g., the runtime is no longer reachable, the design file was only a one-time reference, the tool can't re-capture the same state), **do not silently skip**. State explicitly: "visual re-verification blocked — [reason]", record item #6 as **BLOCKED**, and treat it the same as BLOCKED elsewhere: the task is not "done" until the block is resolved or the user accepts the blocker.

5. **Special cases:**
   - Design-matching tasks (pencil reference): re-invoke `get_screenshot` on both the design node and the implemented component; eyeball alignment and call out any remaining deltas honestly.
   - Browser/DOM tasks: re-run `navigate_page` + `take_screenshot` or `take_snapshot`; compare the specific region that was wrong, not the whole page.
   - Cocos/game tasks: re-run `captureNow` or `getSceneTree` in the same scene state; if the bug was timing-dependent, capture at the reproduction timestamp, not at a random moment.
   - Performance tasks (lighthouse/performance_trace): re-run the same audit/trace; the "after" number must come from the same measurement, not from a different page state.

**Anti-patterns for item #6:**

| Thought | Why it's wrong |
|---------|---------------|
| "Build passed, so the screenshot is probably fine" | Build ≠ render. That's the whole reason item #6 exists. |
| "I already saw the fix in my head" | Mental simulation is not evidence. Re-invoke the tool. |
| "Re-capturing is slow, I'll skip it" | The slow step was the diagnosis, not the re-capture. Skipping here wastes the diagnosis budget. |
| "I used a screenshot once but that was just to look around" | Even a single "look around" call counts. If you formed any part of your understanding from a visual, you owe a visual "after". |
| "I'll describe what it should look like instead" | Description is a narrative; the tool output is the artifact. Users asked for the artifact. |

### The Verification Gate (replaces the old single-command gate)

```
BEFORE saying "done", "fixed", "complete", "passes", or any synonym:

1. Have I completed ALL verification items above?
   - Items 1–5: always required.
   - Item 6: required if any visualization tool was called in this task (see Phase 0 step 6); otherwise N/A.
   - Any missing? → Go back and complete them. Do not proceed.
   - All done? → Continue to step 2.

2. Fill out the verification table:

   | # | Item | Status | Evidence |
   |---|------|--------|----------|
   | 1 | Build | ?/PASS/FAIL | (paste key output lines) |
   | 2 | Lint/TypeCheck | ?/PASS/FAIL | (paste key output lines) |
   | 3 | Tests | ?/PASS/FAIL/SKIP | (paste key output lines or "no tests") |
   | 4 | Checklist review | ?/PASS/FAIL | (which items confirmed, which missing) |
   | 5 | Regression check | ?/PASS/FAIL | (new issues found or "none") |
   | 6 | Visual verification | ?/PASS/FAIL/BLOCKED/N/A | (tool used + before/after comparison, or "N/A — no visual tools used in diagnosis") |

   Any "?" remaining? → You skipped something. Go back.
   Item 6 = N/A? → State the reason ("no visual tools were used in diagnosis"). A bare "N/A" without reason is a skipped item, not a justified one.

3. Are ALL required items PASS (with N/A or justified SKIP where applicable)?
   - Yes → Report "done" with the filled table as evidence.
   - No  → Report the actual status. List what failed. Do NOT claim done.
```

### Completion Criteria

You can only say the task is complete when **all of these are true**:
- The verification table has zero "?" entries
- All non-SKIP / non-N/A items show PASS
- Every SKIP has a stated reason (e.g., "project has no test suite")
- Every N/A for item #6 has a stated reason (e.g., "no visual tools used in diagnosis")
- The checklist review confirms every Phase 3 item was implemented
- **Evidence Symmetry holds**: if any visual tool was used in diagnosis, item #6 is PASS (not N/A, not SKIP). BLOCKED is acceptable only if you state the blocker explicitly — and BLOCKED does not equal "done", it requires a user decision.

If even one item is missing evidence, you are not done. Say what's still pending.

### Session Sentinel (end-of-round marker)

After the verification table shows all PASS, print this line **verbatim** as the last line of your response, substituting the current level:

> 本轮闭环完成（当前 L{level}）。若下一条消息为否定反馈（"还是不行" / "又崩了" / "same issue" 等），将升级到 L{level+1} 并从 Phase 0 重新开始；若是新 bug，重置 L0；若用户确认通过则结束。

**Why the sentinel matters:** It makes the escalation contract visible to both you and the user. Next turn, when you see this sentinel in your own prior message plus a negative-feedback phrase in the user's message, the level-increment decision is mechanical, not a judgment call. This is what prevents "skill was triggered once, then faded" — the sentinel carries the baton forward.

### Red flags that you're about to skip verification

- Running build, seeing PASS, and feeling done → You've done 1 of 5/6
- Using words like "should", "probably", "seems to" → No evidence yet
- Thinking "it's obvious this works" → Obvious things break all the time
- Wanting to move on because you're tired of this task → Fatigue is not evidence
- Saying "build passes, so it should be fine" → Build ≠ lint ≠ tests ≠ checklist ≠ visual
- **Having used a screenshot/scene-tree/design-file in Phase 0–2, but skipping item #6 and reporting done** → That's Evidence Symmetry violation. Command-line checks cannot see the failure mode you used visuals to find.
- Writing "visually looks correct" without a new tool invocation → Narrative ≠ artifact. Re-capture.

---

## Red Flags - Stop Immediately

If you catch yourself thinking any of these, stop and return to the appropriate phase:

| Thought | Reality | Go back to |
|---------|---------|------------|
| "Let me quickly change this and see" | No evidence before action | Phase 0 |
| "The problem is obvious" | Obvious symptom is not root cause | Phase 2 |
| "While I'm here, let me also fix..." | No user permission to expand scope | Phase 1 |
| "Should be good now" | "Should" is not evidence | Phase 5 |
| "Build passes, done!" | Build 通过 ≠ 完整验收，还有 4（或 5）项没做 | Phase 5 |
| "UI 改完跑一下 build 就行" | 用可视化工具发现的 bug，必须用可视化工具收尾。证据对称原则。 | Phase 5 item #6 |
| "截图看过一眼，大概是对的" | 一眼 ≠ 对比。重新调用同一工具、给出 before/after 才是证据 | Phase 5 item #6 |
| "I read this file earlier" | Earlier is not now. Re-Read. | Phase 0 |
| "I remember this API works like..." | Memory is not evidence. Grep it. | Phase 0 |
| "Let me add a try-catch around this" | Symptom patch, not root cause fix | Phase 2 |
| "Just this one small extra feature" | User didn't ask for it | Phase 1 |
| "One more fix attempt" (after 2+ failures) | Likely architectural problem | Escalate to user |
| "用户问的是为什么，我直接去改代码" | 提问 ≠ 修复请求。先回答，再问是否需要修 | Phase 0 |
| "虽然问题不完全一样但我确定是这个" | 确定 ≠ 用户同意。X ≠ Y 就必须问 | Phase 1 |
| "用户说还是不行，我再改一下同一个文件" | 那是 L0 思维。负反馈必须升级 L1+ 并换方法论 | Escalation Ladder |
| "已经用过 quick-fix，这次直接改吧" | skill 必须每轮重新触发，不是一次用一整场 | Level Detection |
| "上轮读过了，这次不用再读" | L1+ 禁止依赖旧 Read。重读成本最低 | Escalation Ladder |
| "再给我试一次就能修好" (at L3/L4) | 多轮未修是系统性信号，继续试是浪费用户时间 | L3/L4 gate |

---

## Escalation: /fix

quick-fix is the fast path for most code changes. When the situation exceeds its scope, tell the user:

"This problem is more complex than a quick fix. I recommend using `/fix` for deep investigation."

Escalation triggers:
- Multiple competing root cause hypotheses that can't be cheaply eliminated
- Cross-module interactions, timing issues, concurrency bugs
- 3+ fix attempts without resolution
- Need for multi-agent investigation (researcher + developer + tester)
